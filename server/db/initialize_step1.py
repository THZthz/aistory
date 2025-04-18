import tomllib
from functools import reduce
import re
import os
from typing import Callable, List, Dict, Any, LiteralString, TypedDict
import time

from aistory.constants import PATH
from aistory.db.id_alloc import IDGen
from aistory.db.embedding import Embedding
from aistory.db.safe_transactions import safe_transactions
from aistory.types.item import ItemClass


def time_str() -> 'str':
    current_time = time.localtime()
    return time.strftime('%H:%M:%S', current_time)  # %Y-%m-%d


def _create_all_tables(cursor):
    print(time_str() + ' - Creating tables...')

    # Create wiki table.
    cursor.execute('''CREATE TABLE wikis_table 
    (
        name VARCHAR(64) NOT NULL UNIQUE,
        desc_embedding vector(768), -- Our mGTE can only generate embeddings with dimension between [128, 768].                                                                                  
        description TEXT NOT NULL
    )''')

    # Create table for items' category.
    cursor.execute('''CREATE TABLE item_categories_table 
    (
        category_id INTEGER NOT NULL UNIQUE,                                                                                           
        category_parent INTEGER NULL REFERENCES item_categories_table (category_id),                                                                                                   
        category_name VARCHAR(64) NOT NULL,                                                                                            
        category_level SMALLINT NOT NULL                                                     
    )''')

    # Create table for types of items. To represent a real item, you need to insert an instance into 'items_table'.
    cursor.execute(f'''CREATE TABLE item_types_table 
    (
        type_id INTEGER NOT NULL UNIQUE PRIMARY KEY,                                                                                                                  
        type_name VARCHAR(32) NOT NULL,                                                                                                            
        category_id INTEGER NOT NULL REFERENCES item_categories_table (category_id),                                                                                                         
        type_quality VARCHAR(32) NOT NULL CHECK (type_quality IN ('common', 'uncommon', 'rare' ,'exquisite', 'legendary')),                                                                                                    
        type_description TEXT,                                                                                                                     
        type_attributes JSON                                                                
    )''')

    # Create table for items.
    cursor.execute('''CREATE TABLE items_table  
    (
        item_id SERIAL NOT NULL UNIQUE PRIMARY KEY,
        item_type INTEGER NOT NULL REFERENCES item_types_table (type_id),
        item_count INTEGER DEFAULT 1,
        item_attributes JSON                                                                     
    )''')

    # This table is used to store the information about all levels of locations.
    cursor.execute('''CREATE TABLE locations_table 
    (
        location_id SERIAL PRIMARY KEY,
        -- This is a strict requirement: locations' name cannot repeat.
        -- We can use its name as a replacement for id.
        name VARCHAR(128) NOT NULL UNIQUE,
        description TEXT  NOT NULL DEFAULT '',
        main_type VARCHAR(32) NOT NULL CHECK (main_type IN 
            ('city', 'district', 'street_network', 'plot', 'structure', 'space')),
        subtype VARCHAR(32) NOT NULL
    )''')

    # Trigger used to confirm the validity of "subtype".
    cursor.execute('''CREATE OR REPLACE FUNCTION validate_subtype()
        RETURNS TRIGGER AS $$
        DECLARE
            valid_subtype BOOLEAN;
        BEGIN
            -- Check if the subtype is valid for the given main_type
            valid_subtype := CASE
                WHEN NEW.main_type = 'city' AND NEW.subtype = 'city' THEN TRUE
        
                WHEN NEW.main_type = 'district' AND NEW.subtype IN (
                    'residential', 'commercial', 'industrial', 'civic',
                    'religious', 'military', 'fringe', 'green_zones'
                ) THEN TRUE
        
                WHEN NEW.main_type = 'street_network' AND NEW.subtype IN (
                    'main_streets', 'alleys', 'squares', 'bridges_ferries',
                    'city_walls', 'underground_passages'
                ) THEN TRUE
        
                WHEN NEW.main_type = 'plot' AND NEW.subtype IN (
                    'building_plots', 'sacred_communal_plots', 'mixed_use_plots',
                    'resource_plots', 'public_service_plots'
                ) THEN TRUE
        
                WHEN NEW.main_type = 'structure' AND NEW.subtype IN (
                    'buildings', 'functional', 'auxiliary', 'defensive', 'open_structures'
                ) THEN TRUE
        
                WHEN NEW.main_type = 'space' AND NEW.subtype IN (
                    'floors', 'rooms', 'passages', 'open_areas', 'mobile_ephemeral'
                ) THEN TRUE
        
                ELSE FALSE
            END;
        
            IF NOT valid_subtype THEN
                RAISE EXCEPTION 'Invalid subtype "%" for main_type "%"', NEW.subtype, NEW.main_type;
            END IF;
        
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql''')

    # Create the trigger.
    cursor.execute('''CREATE TRIGGER check_subtype_validity 
        BEFORE INSERT OR UPDATE ON locations_table 
        FOR EACH ROW EXECUTE FUNCTION validate_subtype()''')

    # Create table for characters.
    cursor.execute('''CREATE TABLE characters_table  
    (
        character_id INTEGER NOT NULL UNIQUE PRIMARY KEY,                                                                        
        character_fullname VARCHAR(32) NOT NULL,                                                                     
        character_profile JSON NOT NULL,                                                                             
        character_location INTEGER NOT NULL REFERENCES locations_table (location_id),                                                    
        character_status VARCHAR(512) NOT NULL                                                
    )''')

    # Create table for containers.
    cursor.execute(f'''CREATE TABLE containers_table  
    (
        container_id SERIAL NOT NULL UNIQUE,                                                                         
        lock_type VARCHAR(32) DEFAULT 'no_lock' CHECK (lock_type IN 
            ('no_lock', 'normal_lock', 'hard_lock', 'normal_magic_lock', 'hard_magic_lock')),                                                            
        container_owner INTEGER NULL REFERENCES characters_table  (character_id),     
        -- If 'container_location' is null, then the owner is carrying it.                                                                     
        container_location INTEGER NULL REFERENCES locations_table  (location_id)                                
    )''')

    cursor.execute('''CREATE TABLE equipped_table 
    (
        character_id INTEGER NOT NULL REFERENCES characters_table (character_id),
        item_id INTEGER NOT NULL REFERENCES items_table (item_id)
    )''')

    # What is inside the container?
    cursor.execute(f'''CREATE TABLE container_contents_table 
    (
        container_id INTEGER NOT NULL REFERENCES containers_table (container_id),                         
        item_id INTEGER NOT NULL REFERENCES items_table (item_id)                                
    )''')

    # Create table for storing memories.
    cursor.execute(f'''CREATE TABLE memories_table 
    (
        memory_id INTEGER NOT NULL UNIQUE PRIMARY KEY,                                                                                    
        memory_type VARCHAR(32) NOT NULL CHECK (memory_type IN ('observation', 'reflection', 'plan')),                                                                                 
        memory_owner INTEGER NOT NULL REFERENCES characters_table (character_id),                                                                                 
        memory_content TEXT NOT NULL,                                                                                         
        memory_embedding vector(768)                                                               
    )''')

    print(time_str() + ' - Successfully created all tables.')


def create_all_tables():
    safe_transactions("creating all tables", _create_all_tables)


def _drop_all_tables(cursor):
    cursor.execute('''CREATE EXTENSION IF NOT EXISTS vector''')
    cursor.execute('''CREATE EXTENSION IF NOT EXISTS ltree''')

    cursor.execute('''DROP TABLE IF EXISTS wikis_table CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS characters_table CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS equipped_table CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS containers_table  CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS container_contents_table CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS item_categories_table CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS item_types_table CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS items_table  CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS memories_table CASCADE''')
    cursor.execute('''DROP TABLE IF EXISTS locations_table  CASCADE''')

    print(time_str() + ' - Successfully dropped all tables.')


def drop_all_tables():
    safe_transactions("drapping all tables", _drop_all_tables)


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

    # Save backup.
    with open(file_path + '.bak', 'w', encoding='utf-8') as file:
        file.write(content)

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


def _walk_all_profiles(callback: Callable):
    base_dir = PATH('database/profiles')
    for file_name in os.listdir(base_dir):
        # Omit directories.
        if not os.path.isfile(os.path.join(base_dir, file_name)): continue

        with open(os.path.join(base_dir, file_name), 'rb') as file:
            callback(file)


def _update_character_ids():
    id_gen = IDGen('non-existent')

    chr_records: list[tuple[int, str]] = []

    def callback(file):
        toml = tomllib.load(file)

        chr_id = id_gen.get()
        chr_entry = toml['Profile'][list(toml['Profile'].keys())[0]]['short_name']
        assert len(toml['Profile'].keys()) == 1
        chr_records.append((chr_id, chr_entry))

    # Read all pre-defined characters.
    _walk_all_profiles(callback)

    code = _get_mappins_code(chr_records, 'EChr', 'MChr', 'Character')
    _process_file(PATH('aistory/types/character.py'), replacement_text=code)


def _update_locations_id():
    with open(PATH('database/wikis/locations.toml'), 'rb') as file:
        locations_catalog = tomllib.load(file)['wiki_entries']['Locations']

        id_gen = IDGen('non-existent')
        loc_records: list[tuple[int, str]] = []
        for loc_entry in locations_catalog:
            loc_id = id_gen.get()
            loc_records.append((loc_id, loc_entry))

        code = _get_mappins_code(loc_records, 'ELoc', 'MLoc', 'Location')
        _process_file(PATH('aistory/types/location.py'), replacement_text=code)


def _update_items_id():
    with open(PATH('database/wikis/item_types.toml'), 'rb') as file:
        items_catalog = tomllib.load(file)['wiki_entries']['Items']

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


def parse_tree_structure(tree_text):
    """
    Parse a tree-like text structure into a nested dictionary.

    Args:
        tree_text (str): Multi-line string representing the tree structure.

    Returns:
        dict: Nested dictionary representing the hierarchical structure.
    """

    tree_lines = tree_text.splitlines()

    # Process root node (first line)
    root_parts = [p.strip() for p in tree_lines[0].split(' - ', 1)]
    root_name = root_parts[0]
    root_desc = root_parts[1] if len(root_parts) > 1 else None
    result = {root_name: {'description': root_desc, 'children': {}}}
    stack = [(0, root_name, result[root_name])]  # (level, name, node)

    for line in tree_lines[1:]:
        if not line.strip():
            continue  # skip empty lines

        # Calculate indentation level (count leading '│' and spaces)
        line_content = line.lstrip('│ ')
        level = 1 + (len(line) - len(line_content)) // 4  # 4 chars per level

        # Clean up the line content
        parts = [p.strip() for p in line_content.split(' - ', 1)]
        name = parts[0]
        description = parts[1] if len(parts) > 1 else None

        # Remove any parenthetical notes from the name
        if '(' in name:
            name = name.split('(')[0].strip()

        if name[0] == '├' or name[0] == '└':
            name = name[4:]

        # Create the node
        node = {'description': description}
        if level == 0:
            # Root node
            result[name] = node
            stack = [(level, name, result[name])]
        else:
            # Find the parent level
            while stack and stack[-1][0] >= level:
                stack.pop()

            if stack:
                parent_level, parent_name, parent_node = stack[-1]
                # Initialize 'children' if not exists
                if 'children' not in parent_node:
                    parent_node['children'] = {}
                # Add current node to parent's children
                parent_node['children'][name] = node
                stack.append((level, name, node))

    return result


class HeadingNode:
    """Represents a Markdown heading with its content and children"""

    def __init__(self, level: int, title: str, content: str = ""):
        self.level = level  # Heading level (1-6)
        self.title = title  # Heading text
        self.content = content  # Content under this heading
        self.children = []  # Child headings (nested structure)

    def add_child(self, node: 'HeadingNode') -> None:
        """Add a child heading to this node"""
        self.children.append(node)

    def __repr__(self) -> str:
        return f"HeadingNode(level={self.level}, title='{self.title}')"


class FlatStructure(TypedDict):
    h1: list[HeadingNode]
    h2: list[HeadingNode]
    h3: list[HeadingNode]
    h4: list[HeadingNode]
    h5: list[HeadingNode]
    h6: list[HeadingNode]


class TitlesDict(TypedDict):
    root_nodes: list[HeadingNode]
    flat_structure: FlatStructure


def parse_markdown_titles(markdown_text: str) -> TitlesDict:
    """
    Parse Markdown text and extract headings with nested structure

    Args:
        markdown_text: Text in Markdown format

    Returns:
        A dictionary containing:
        - 'root_nodes': Top-level headings (h1)
        - 'flat_structure': Flattened view of all headings by level
    """

    # Initialize result structures
    root_nodes = []
    flat_structure = {
        "h1": [],
        "h2": [],
        "h3": [],
        "h4": [],
        "h5": [],
        "h6": [],
    }

    # Stack to track current parent nodes
    node_stack = []

    # Split text into lines for processing
    lines = markdown_text.split('\n')
    current_content = []

    for line in lines:
        # Check if line is a heading
        heading_match = re.match(r'^(#{1,6}) (.*)$', line.strip())
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2)

            # Create new node
            new_node = HeadingNode(level, title, '\n'.join(current_content).strip())
            current_content = []

            # Add to flat structure
            flat_structure[f"h{level}"].append(new_node)

            # Handle nesting
            if not node_stack:
                root_nodes.append(new_node)
                node_stack.append(new_node)
            else:
                # Find the appropriate parent
                while node_stack and node_stack[-1].level >= level:
                    node_stack.pop()

                if node_stack:
                    node_stack[-1].add_child(new_node)
                else:
                    root_nodes.append(new_node)

                node_stack.append(new_node)
        else:
            # Accumulate content
            if line.strip() or current_content:
                current_content.append(line)

    return {
        "root_nodes": root_nodes,
        "flat_structure": flat_structure
    }


def print_nested_structure(nodes: List[HeadingNode], indent: int = 0) -> None:
    """
    Print the heading structure with proper indentation to show nesting

    Args:
        nodes: List of HeadingNodes to print
        indent: Current indentation level
    """
    for node in nodes:
        print('  ' * indent + f"h{node.level}: {node.title}")
        if node.content:
            content_preview = ' '.join(node.content.split()[:10])
            print('  ' * (indent + 1) + f"Content: {content_preview}...")
        print_nested_structure(node.children, indent + 1)


def print_flat_structure(parsed_data: Dict) -> None:
    """
    Print headings grouped by level

    Args:
        parsed_data: Result from parse_markdown_titles
    """
    for level in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        entries = parsed_data["flat_structure"][level]
        if entries:
            print(f"\n{level.upper()} Headings ({len(entries)}):")
            for entry in entries:
                print(f"  - Title: {entry.title}")
                if entry.content:
                    print(f"    Content preview: {entry.content[:50]}...")


def _update_wikis(cursor):
    # Get embedding model.
    embedding = Embedding()

    # Get list of wiki TOML files.
    base_dir = PATH('data/')
    files = [os.path.join(base_dir, file) for file in os.listdir(base_dir)]
    files = [file for file in files if os.path.isfile(file)]

    # Loop through wiki files and load wikis into database.
    for file in files:
        print(time_str() + f' - Processing {file}.')
        with open(file, 'r', encoding='utf-8') as f:
            file_content = f.read()
            flat_structure = parse_markdown_titles(file_content)['flat_structure']
            wiki = [item for sublist in flat_structure.values() for item in sublist]

            # Return if empty.
            if not len(wiki) == 0:
                # Get sentence embeddings.
                # TODO: MIXED scores?
                desc_embs = embedding.encode([w.content for w in wiki], 768, return_dense=True)['dense_embeddings']

                # Combine to make records.
                wiki_records = []
                for i in range(len(desc_embs)):
                    wiki_records.append((wiki[i].title,
                                         wiki[i].content,
                                         desc_embs[i].tolist()))

                # Add to wikis_table.
                cursor.executemany('''INSERT INTO wikis_table (name, description, desc_embedding)
                                        VALUES (%s, %s, %s)''', wiki_records)

    print(time_str() + ' - Successfully updated wikis_table.')


def update_wikis():
    safe_transactions('updating wikis_table', _update_wikis)


def _insert_items_categories(cursor):
    def gen_records(enum_class, level, parent_id=0):
        items_records = []
        for category in enum_class:
            if parent_id == 0:
                items_record = (int(category), category.name, level)
            else:
                items_record = (int(category), parent_id, category.name, level)
            items_records.append(items_record)
        return items_records

    def insert_data(stmt, enum_class, level, parent_id=0):
        cursor.executemany(stmt, gen_records(enum_class, level, parent_id))

    stmt_1 = '''INSERT INTO item_categories_table (category_id, category_name, category_level) VALUES (%s, %s, %s)'''
    stmt_2 = '''INSERT INTO item_categories_table (category_id, category_parent, category_name, category_level) VALUES (%s, %s, %s, %s)'''

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
    safe_transactions('updating ItemCategoriesTable', _insert_items_categories)


def initialize_step1():
    drop_all_tables()
    create_all_tables()
    update_ids()
    update_wikis()
    insert_items_categories()
