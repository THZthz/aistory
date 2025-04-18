import json
import tomllib
from functools import reduce
from psycopg2.extras import execute_values

from aistory.constants import PATH
from aistory.db.initialize_step1 import _walk_all_profiles, time_str
from aistory.db.safe_transactions import safe_transactions
from aistory.types.location import ELoc
from aistory.types.character import EChr
from aistory.types.item import EItem, ItemClass


def _update_items(cursor):
    # Load from TOML file.
    items_catalog = tomllib.load(open(PATH('database/wikis/item_types.toml'), 'rb'))['wiki_entries']['Items']

    # Insert pre-defined items into the ItemTable based on TOML file.
    def get_category_id(path, separator='.'):
        paths = path.split(separator)
        ret = reduce(lambda x, k: getattr(x, k + 'Class'), paths[1:-1], ItemClass)
        return ret[paths[-1]].value

    def get_quality(path, separator='.'):
        paths = path.split(separator)
        return Qualities[paths[-1]].value

    def insert_catalog():
        stmt = '''INSERT INTO item_types_table (type_id, type_name, category_id, type_quality, type_description, type_attributes)                                 
                VALUES (%s, %s, %s, %s, %s, %s)'''

        # Parse records.
        items_records = []

        for item in items_catalog:
            name = items_catalog[item]['name']
            desc = items_catalog[item]['description']
            quality = items_catalog[item]['quality']
            cls = items_catalog[item]['class']
            items_record = (EItem[item].value, name, get_category_id(cls), get_quality(quality), desc, '{}')
            items_records.append(items_record)

        # Bulk insert.
        cursor.executemany(stmt, items_records)

    insert_catalog()

    print(time_str() + ' - Successfully updated ItemTypesTable.')


def update_items():
    safe_transactions("updating ItemTypesTable", lambda cursor: _update_items(cursor))


def _update_locations(cursor):
    # Load from TOML file.
    locations_catalog = tomllib.load(open(PATH('database/wikis/locations.toml'), 'rb'))['wiki_entries']['Locations']

    loc_records = []
    for loc_entry in locations_catalog:
        loc_id = ELoc[loc_entry].value
        loc_name = locations_catalog[loc_entry]['name']
        loc_type = locations_catalog[loc_entry]['type']
        loc_desc = locations_catalog[loc_entry]['description']
        loc_path = locations_catalog[loc_entry]['path']
        loc_records.append((loc_id, loc_name, loc_type, loc_desc, loc_path))

    cursor.executemany('''INSERT INTO locations (location_id, location_name, location_type, location_description, location_path) 
        VALUES (%s, %s, %s, %s, %s)''', loc_records)

    print(time_str() + ' - Successfully updated LocationsTable.')


def update_locations():
    safe_transactions("updating LocationsTable", lambda cursor: _update_locations(cursor))


def _insert_characters(cursor):
    def callback(file):
        toml = tomllib.load(file)

        profile = toml['Profile'][list(toml['Profile'].keys())[0]]
        assert len(toml['Profile'].keys()) == 1

        chr_id = EChr[profile['short_name']].value
        cursor.execute('''INSERT INTO characters 
            (character_id, character_fullname, character_profile, character_location, character_status)
            VALUES (%s, %s, %s, %s, %s)''', (chr_id,
                                             profile['name'],
                                             json.dumps(profile),
                                             ELoc[profile['location'].split('.')[-1]].value,
                                             profile['status']))

        print(time_str() + f' - Successfully updated CharacterTable - {profile['short_name']}.')

        # Add initial items.
        equipped_records = []
        for equipped_name in profile['equipped_items']:
            item_type = EItem[equipped_name.split('.')[-1]].value
            equipped_records.append((item_type, 'TRUE'))
        for equipped_name in profile['intimate_items']:
            item_type = EItem[equipped_name.split('.')[-1]].value
            equipped_records.append((item_type, 'FALSE'))
        # print(equipped_records)

        if len(equipped_records) == 0:
            print(time_str() + f' - {profile['short_name']} carries no items, quiting.')
            return

        # We need to insert into ItemsTable to get an id.
        ids = execute_values(
            cursor,
            f'''INSERT INTO items (item_type) VALUES {'%s'} RETURNING item_id''',
            [(item_type,) for item_type, _ in equipped_records],
            fetch=True
        )
        ids = [row[0] for row in ids]
        print(f' - {profile['short_name']} ids:')
        print(ids)

        print(time_str() + f' - Successfully updated ItemsTable - {profile['short_name']}.')

        assert len(ids) == len(equipped_records)
        for i in range(len(ids)):
            equipped_records[i] = (ids[i], equipped_records[i][1])
        cursor.executemany(f'''INSERT INTO "SlotTable" (character_id, item_id, wear) VALUES ({chr_id}, %s, %s)''',
                           equipped_records)
        # print(equipped_records)

        print(time_str() + f' - Successfully updated SlotTable - {profile['short_name']}.')

    # Read all pre-defined characters.
    _walk_all_profiles(callback)


def update_characters():
    safe_transactions('updating CharacterTable and SlotTable', lambda cursor: _insert_characters(cursor))


def _update_location_network(cursor):
    with open(PATH('database/wikis/config/location_network.json'), 'rb') as file:
        loc_network = json.load(file)['networks']
        loc_records = []
        for loc in loc_network:
            loc_a_id = ELoc[loc['loc_a'].split('.')[-1]].value
            loc_b_id = ELoc[loc['loc_b'].split('.')[-1]].value
            loc_records.append((loc_a_id, loc_b_id, loc['travel_time'], loc['description']))

        cursor.executemany('''INSERT INTO location_connections (from_id, to_id, travel_time, description)
            VALUES (%s, %s, %s, %s)''', loc_records)
        cursor.executemany('''INSERT INTO location_connections (to_id, from_id, travel_time, description)
            VALUES (%s, %s, %s, %s)''', loc_records)


def update_location_network():
    safe_transactions('updating LocConnectionsTable', lambda cursor: _update_location_network(cursor))


def initialize_step2():
    update_items()
    update_locations()
    update_characters()
    # update_location_network()
