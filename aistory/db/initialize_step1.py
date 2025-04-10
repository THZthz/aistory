import tomllib
import json
from functools import reduce
import re
import os
import torch
from typing import Callable
import time

from aistory.constants import Memories, PATH
from aistory.db.id_alloc import IDGen
from aistory.db.embedding import Embedding
from aistory.db.safe_transactions import safe_transactions
from aistory.types.item import Locks, Qualities, ItemClass


def time_str() -> 'str':
    current_time = time.localtime()
    return time.strftime('%H:%M:%S', current_time)  # %Y-%m-%d


def _create_all_tables(cursor):
    # Create wiki table.
    cursor.execute('''CREATE TABLE "WikiTable" (
        name VARCHAR(64) NOT NULL UNIQUE,
        name_embedding vector(128),                                                                                   
        desc_embedding vector(768),                                                                                   
        description TEXT NOT NULL
    )''')

    # Create table for items' category.
    cursor.execute('''CREATE TABLE "ItemCategoriesTable" (
        category_id INTEGER NOT NULL UNIQUE,                                                                                           
        category_parent INTEGER NULL,                                                                                                  
        category_name VARCHAR(50) NOT NULL,                                                                                            
        category_description TEXT,                                                                                                     
        category_level SMALLINT NOT NULL,                                                                                              
        FOREIGN KEY (category_parent) REFERENCES "ItemCategoriesTable" (category_id)                                                            
    )''')

    # Create table for types of items.
    cursor.execute(f'''CREATE TABLE "ItemTypesTable" (
        type_id INTEGER NOT NULL,                                                                                                                  
        type_name VARCHAR(32) NOT NULL,                                                                                                            
        category_id INTEGER NOT NULL,                                                                                                         
        type_quality SMALLINT NOT NULL CHECK (type_quality IN (                                                                                         
            {Qualities.Common.value},                                                                                                         
            {Qualities.Uncommon.value},                                                                                                       
            {Qualities.Rare.value},                                                                                                           
            {Qualities.Exquisite.value},                                                                                                      
            {Qualities.Legendary.value})),                                                                                                    
        type_description TEXT,                                                                                                                     
        type_attributes JSON,                                                                                                                      
        UNIQUE (type_id),                                                                                                                          
        PRIMARY KEY (type_id),                                                                                                                     
        FOREIGN KEY (category_id) REFERENCES "ItemCategoriesTable" (category_id)                                                                       
    )''')

    # Create table for items.
    cursor.execute('''CREATE TABLE "ItemsTable" (
        item_id INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
        item_type INTEGER NOT NULL,
        item_count INTEGER DEFAULT 1,
        item_attributes JSON,                                                                                                              
        UNIQUE (item_id),                                                                                                                          
        PRIMARY KEY (item_id),      
        FOREIGN KEY (item_type) REFERENCES "ItemTypesTable" (type_id)                                                                       
    )''')

    # Create table for locations.
    cursor.execute(f'''CREATE TABLE "LocationsTable" (
        location_id INTEGER,                                                                                                 
        location_name VARCHAR(64) NOT NULL,                                                                                  
        location_type VARCHAR(32) NOT NULL,                                                                                  
        location_description TEXT NOT NULL,                                                                                  
        location_path LTREE NOT NULL,                                                                                        
        UNIQUE (location_path),                                                                                               
        PRIMARY KEY (location_id)                                                                                            
    )''')

    # Create indexes.
    cursor.execute('''CREATE INDEX idx_location_path ON "LocationsTable" USING GIST (location_path)''')

    # Create table for characters.
    cursor.execute('''CREATE TABLE "CharacterTable" (
        character_id INTEGER NOT NULL UNIQUE,                                                                        
        character_fullname VARCHAR(32) NOT NULL,                                                                     
        character_profile JSON NOT NULL,                                                                             
        character_location INTEGER NOT NULL,                                                    
        character_status VARCHAR(512) NOT NULL,                                                             
        PRIMARY KEY (character_id),                                                                                  
        FOREIGN KEY (character_location) REFERENCES "LocationsTable" (location_id)                                                    
    )''')

    # Create table for representing what people wears.
    cursor.execute('''CREATE TABLE "SlotTable" (
        character_id INTEGER NOT NULL REFERENCES "CharacterTable" (character_id),                                    
        item_id INTEGER NOT NULL REFERENCES "ItemsTable" (item_id),
        wear BOOLEAN NOT NULL, -- When not weared, this item is stored closely.        
        UNIQUE (character_id, item_id)                               
    )''')

    # Create table for containers.
    cursor.execute(f'''CREATE TABLE "ContainerTable" (
        container_id INTEGER NOT NULL,                                                                         
        lock_type SMALLINT DEFAULT {Locks.No.value} CHECK (lock_type IN (                               
            {Locks.No.value},                                                                     
            {Locks.Normal.value},                                                                 
            {Locks.Hard.value},                                                                   
            {Locks.MagicNormal.value},                                                            
            {Locks.MagicHard.value})),                                                            
        container_owner INTEGER NULL,                                                                          
        container_location INTEGER NULL, -- if NULL, then the owner is carrying it.                            
        UNIQUE (container_id),                                                                                 
        PRIMARY KEY (container_id),                                                                            
        FOREIGN KEY (container_owner) REFERENCES "CharacterTable" (character_id),                                          
        FOREIGN KEY (container_location) REFERENCES "LocationsTable" (location_id)                                        
    )''')

    # What is inside the container?
    cursor.execute(f'''CREATE TABLE "ContainerContentTable" (
        container_id INTEGER NOT NULL REFERENCES "ContainerTable" (container_id),                         
        item_id INTEGER NOT NULL REFERENCES "ItemsTable" (item_id)                                
    )''')

    # Create table for storing memories.
    cursor.execute(f'''CREATE TABLE "MemoryTable" (
        memory_id INTEGER NOT NULL UNIQUE,                                                                                    
        memory_type SMALLINT NOT NULL CHECK (memory_type IN (                                                                        
            {Memories.Observation.value},                                                                            
            {Memories.Reflection.value},                                                                             
            {Memories.Plan.value})),                                                                                 
        memory_owner INTEGER NOT NULL,                                                                                 
        memory_content TEXT NOT NULL,                                                                                         
        memory_embedding vector(768),                                                                                         
        PRIMARY KEY (memory_id),                                                                                              
        FOREIGN KEY (memory_owner) REFERENCES "CharacterTable" (character_id)                                                                
    )''')

    print(time_str() + ' - Successfully created all tables.')


def create_all_tables():
    safe_transactions("creating all tables", lambda cursor: _create_all_tables(cursor))


def _drop_all_tables(cursor):
    """
    Reset the whole database -- be careful!
    :return:
    """

    cursor.execute('''DROP TABLE IF EXISTS "WikiTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "CharacterTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "ContainerContentTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "ContainerTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "ItemCategoriesTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "ItemTypesTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "ItemsTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "SlotTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "MemoryTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "LocationsTable" CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS "LocationConnectionsTable" CASCADE''')

    print(time_str() + ' - Successfully dropped all tables.')


def drop_all_tables():
    safe_transactions("drapping all tables", lambda cursor: _drop_all_tables(cursor))


def _process_file(file_path, start_marker="# MARKER_START\n", end_marker="# MARKER_END\n", replacement_text=""):
    """
    Process a file to replace text between special markers.
    :param file_path: Path to the file to process
    :param start_marker: Starting marker pattern
    :param end_marker: Ending marker pattern
    :param replacement_text: Text to put between markers (empty string clears the content)
    :return:
    """

    # Read the file content.
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # # Save backup.
    # with open(file_path + '.bak', 'w', encoding='utf-8') as file:
    #     file.write(content)

    # Create a regular expression pattern to find text between markers.
    pattern = re.compile(re.escape(start_marker) + r'(.*?)' + re.escape(end_marker), re.DOTALL)

    # Replace the content between markers.
    new_content = pattern.sub(start_marker + replacement_text + end_marker, content)
    # print(new_content)

    # Write the modified content back to the file.
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)

    print(time_str() + f" - Successfully processed {file_path}.")


def _get_mappins_code(records: list[tuple[int, str]], enum_name: str, dict_name: str, class_name: str) -> 'str':
    res = f'class {enum_name}(Enum):\n'
    for idx, entry in records:
        res += f'''    {entry} = {idx}\n'''
    res += '\n\n'

    res += f'''{dict_name}: dict[int, {class_name}] = {{\n'''
    for idx, entry in records:
        res += f'''    {idx}: {class_name}({idx}, "{entry}"),\n'''
    res += '}\n\n\n'

    return res


def _walk_all_profiles(pattern: str, callback: Callable):
    base_dir = PATH('database/')
    for file_name in os.listdir(base_dir):
        # Omit directories.
        if not os.path.isfile(os.path.join(base_dir, file_name)): continue

        # Search for toml files.
        match = re.search(pattern, file_name)
        if match is None: continue

        with open(os.path.join(base_dir, file_name), 'rb') as file_path:
            callback(file_path)


def _update_character_ids():
    id_gen = IDGen('non-existent')

    chr_records: list[tuple[int, str]] = []

    def callback(file_path):
        toml = tomllib.load(file_path)

        chr_id = id_gen.get()
        chr_entry = toml['Profile'][list(toml['Profile'].keys())[0]]['short_name']
        assert len(toml['Profile'].keys()) == 1
        chr_records.append((chr_id, chr_entry))

    # Read all pre-defined characters.
    _walk_all_profiles(r'profile\.\w+?\.toml', lambda file_path: callback(file_path))

    code = _get_mappins_code(chr_records, 'EChr', 'MChr', 'Character')
    _process_file(PATH('aistory/types/character.py'), replacement_text=code)

def _update_locations_id():
    with open(PATH('database/catalog.locations.toml'), 'rb') as file:
        locations_catalog = tomllib.load(file)['Catalog']['Locations']

        id_gen = IDGen('non-existent')
        loc_records: list[tuple[int, str]] = []
        for loc_entry in locations_catalog:
            loc_id = id_gen.get()
            loc_records.append((loc_id, loc_entry))

        code = _get_mappins_code(loc_records, 'ELoc', 'MLoc', 'Location')
        _process_file(PATH('aistory/types/location.py'), replacement_text=code)


def _update_items_id():
    with open(PATH('database/catalog.items.toml'), 'rb') as file:
        items_catalog = tomllib.load(file)['Catalog']['Items']

        id_gen = IDGen('non-existent')
        item_records: list[tuple[int, str]] = []
        for item_entry in items_catalog:
            item_id = id_gen.get()
            item_records.append((item_id, item_entry))

        code = _get_mappins_code(item_records, 'EItem', 'MItem', 'ItemType')
        _process_file(PATH('aistory/types/item.py'), replacement_text=code)


def update_ids():
    _update_locations_id()
    _update_character_ids()
    _update_items_id()

    print(time_str() + ' - Successfully updated all indexes.')


def _update_wikis(cursor):
    # Get embedding model.
    embedding = Embedding()

    # Get list of wiki TOML files.
    base_dir = PATH('database/')
    files = [os.path.join(base_dir, file) for file in os.listdir(base_dir) if
             not re.search(r'wiki\.\w+?\.toml', file) is None]
    files = [file for file in files if os.path.isfile(file)]

    # Loop through wiki files and load wikis into database.
    batch_size = 256
    for file in files:
        wiki = tomllib.load(open(file, 'rb'))['Wiki']
        wiki_names = []
        wiki_descriptions = []

        def generate_embedding_batach():
            # Return if empty.
            if len(wiki_names) == 0:
                return

            # Get sentence embeddings.
            name_embs = embedding.encode(wiki_names, 128, return_dense=True)['dense_embeddings']
            desc_embs = embedding.encode(wiki_descriptions, 768, return_dense=True)['dense_embeddings']
            assert len(name_embs) == len(desc_embs) == len(wiki_names) == len(wiki_descriptions)

            # Combine to make records.
            wiki_records = []
            for i in range(len(name_embs)):
                wiki_records.append((wiki_names[i],
                                     wiki_descriptions[i],
                                     name_embs[i].tolist(),
                                     desc_embs[i].tolist()))

            # Add to WikiTable.
            cursor.executemany('''INSERT INTO "WikiTable" (name, description, name_embedding, desc_embedding)
                        VALUES (%s, %s, %s, %s)''', wiki_records)

            # Clear.
            wiki_names.clear()
            wiki_descriptions.clear()

        def get_wiki_recursive(o, path):
            keys = o.keys()
            wiki_names.append(path)
            wiki_descriptions.append(o['description'])

            # Generate embedding in batch.
            if len(wiki_names) == batch_size:
                generate_embedding_batach()

            # Break when we reach the leaf.
            if len(keys) == 1:
                return

            for index in o.keys():
                if not index == 'description':
                    get_wiki_recursive(o[index], path + '.' + index)

        for wiki_index in wiki:
            get_wiki_recursive(wiki[wiki_index], wiki_index)

        generate_embedding_batach()

    print(time_str() + ' - Successfully updated WikiTable.')


def update_wikis():
    safe_transactions('updating WikiTable', lambda cursor: _update_wikis(cursor))


def _insert_items_categories(cursor):
    items_wiki = tomllib.load(open(PATH('database/wiki.items.toml'), 'rb'))

    # Insert pre-defined categories of items.
    def get_value(d, path, separator='_'):
        return reduce(lambda x, k: x[k], path.split(separator), d)

    def gen_records(enum_class, level, parent_id=0):
        items_records = []
        for category in enum_class:
            desc = get_value(items_wiki['Wiki'], str(category))['description']
            if parent_id == 0:
                items_record = (int(category), category.name, desc, level)
            else:
                items_record = (int(category), parent_id, category.name, desc, level)
            items_records.append(items_record)
        return items_records

    def insert_data(stmt, enum_class, level, parent_id=0):
        cursor.executemany(stmt, gen_records(enum_class, level, parent_id))

    stmt_1 = '''INSERT INTO "ItemCategoriesTable" (category_id, category_name, category_description, category_level) VALUES (%s, %s, %s, %s)'''
    stmt_2 = '''INSERT INTO "ItemCategoriesTable" (category_id, category_parent, category_name, category_description, category_level) VALUES (%s, %s, %s, %s, %s)'''

    # Insert root.
    insert_data(stmt_1, ItemClass, 1)

    # Insert equipments.
    insert_data(stmt_2, ItemClass.EquipmentClass, 2, ItemClass.Equipment.value)
    insert_data(stmt_2, ItemClass.EquipmentClass.HeadGearClass, 3, ItemClass.EquipmentClass.HeadGear.value)
    insert_data(stmt_2, ItemClass.EquipmentClass.TorsoGearClass, 3, ItemClass.EquipmentClass.TorsoGear.value)
    insert_data(stmt_2, ItemClass.EquipmentClass.LegWearClass, 3, ItemClass.EquipmentClass.LegWear.value)
    insert_data(stmt_2, ItemClass.EquipmentClass.FootWearClass, 3, ItemClass.EquipmentClass.FootWear.value)
    insert_data(stmt_2, ItemClass.EquipmentClass.HandGearClass, 3, ItemClass.EquipmentClass.HandGear.value)
    insert_data(stmt_2, ItemClass.EquipmentClass.WeaponClass, 3, ItemClass.EquipmentClass.Weapon.value)

    # Insert consumables.
    insert_data(stmt_2, ItemClass.ConsumableClass, 2, ItemClass.Consumable.value)

    # Insert materials.
    insert_data(stmt_2, ItemClass.MaterialClass, 2, ItemClass.Material.value)

    # Insert miscellaneous items.
    insert_data(stmt_2, ItemClass.MiscellaneousClass, 2, ItemClass.Miscellaneous.value)

    print(time_str() + ' - Successfully updated ItemCategoriesTable.')


def insert_items_categories():
    safe_transactions('updating ItemCategoriesTable', lambda cursor: _insert_items_categories(cursor))


def initialize_step1():
    drop_all_tables()
    create_all_tables()
    update_ids()
    update_wikis()
    insert_items_categories()
