from enum import Enum

from aistory.db.safe_transactions import safe_transactions
from aistory.types.item import ItemType, Item, add_items
from aistory.types.location import Location, MLoc
from aistory.types.item import MItem


class CharacterItem:
    def __init__(self, wear: bool, item: Item):
        self.wear = wear
        self._item = item

    @property
    def item_type(self) -> 'ItemType':
        return self.item.type

    @property
    def item(self) -> 'Item':
        return self._item


class Character:
    def __init__(self, character_id: int, entry_name: str):
        """

        :param character_id:
        :param entry_name:
        """

        self.id: int = character_id
        self.entry_name: str = entry_name  #

        self._fullname: str | None = None
        self._profile: dict | None = None
        self._location: Location | None = None
        self._status: str | None = None
        self._items: list[CharacterItem] | None = None

    def _update_from_database(self):
        def _callback1(cursor):
            cursor.execute('''SELECT character_fullname, character_profile, character_location, character_status 
                FROM characters 
                WHERE character_id = %s''', (self.id,))

            res = cursor.fetchone()
            self._fullname = res[0]
            self._profile = res[1]
            self._location = MLoc[res[2]]
            self._status = res[3]

        safe_transactions(f'getting {self.entry_name}\'s profile', _callback1)

        def _callback2(cursor):
            cursor.execute(
                '''SELECT
                    s.wear,
                    s.item_id,
                    i.item_type,
                    it.type_name
                FROM "SlotTable" s
                LEFT JOIN items i ON i.item_id = s.item_id
                LEFT JOIN item_types_table it ON it.type_id =  i.item_type
                WHERE s.character_id = %s''', (self.id,))

            res = cursor.fetchall()
            items = [CharacterItem(wear, add_items(item_id, MItem[item_type])) for wear, item_id, item_type, _ in res]
            # print(items)
            self._items = items

        safe_transactions(f'getting {self.entry_name}\'s items (in SlotTable)', _callback2)

    @property
    def fullname(self) -> 'str':
        if self._fullname is None:
            self._update_from_database()
        return self._fullname

    @property
    def profile(self) -> 'dict':
        if self._profile is None:
            self._update_from_database()
        return self._profile

    @property
    def location(self) -> 'Location':
        if self._location is None:
            self._update_from_database()
        return self._location

    @property
    def status(self) -> 'str':
        if self._status is None:
            self._update_from_database()
        return self._status

    @property
    def items(self) -> list[CharacterItem]:
        if self._items is None:
            self._update_from_database()
        return self._items

    @staticmethod
    def get_profile_description(chr_id: int) -> 'str':
        character = MChr[chr_id]

        res = f'### Profile of {character.entry_name}\n'
        res += f'Full Name: {character.fullname}\n'
        res += f'Gender: {character.profile['gender']}\n'
        res += f'Age: {character.profile['age']}\n'
        res += f'Race: {character.profile['race']}\n'
        res += f'Appearance: {character.profile['appearance']}\n'
        res += 'Hobbies:\n'
        for hobby in character.profile['hobbies']:
            res += '\t- ' + hobby + '\n'
        res += 'Ideals:\n'
        for ideal in character.profile['ideals']:
            res += '\t- ' + ideal + '\n'
        res += f'Personality: {character.profile['personality']}\n'
        res += f'Occupation: {character.profile['occupation']}\n'
        res += f'Residence: {character.profile['residence']}\n'
        res += f'Notes: {character.profile['final_notes']}\n'
        res += '\n\n'

        return res

    @staticmethod
    def get_items_description(chr_id: int, add_description=True) -> 'str':
        character = MChr[chr_id]

        def _item_desc(item_type: ItemType):
            return f' - {item_type.description}' if add_description else ''

        res = f'### Description of What Items {character.entry_name} Carries\n'
        res += 'Weared:\n'
        for item in character.items:
            if item.wear: res += f'\t- {item.item_type.entry_name}{_item_desc(item.item_type)}\n'
        res += 'Kept Close:\n'
        for item in character.items:
            if not item.wear: res += f'\t- {item.item_type.entry_name}{_item_desc(item.item_type)}\n'
        res += '\n\n'

        return res


# MARKER_START
class EChr(Enum):
    Ginny = 0
    Kael = 1
    Veyla = 2


MChr: dict[int, Character] = {
    0: Character(0, "Ginny"),
    1: Character(1, "Kael"),
    2: Character(2, "Veyla"),
}


# MARKER_END
