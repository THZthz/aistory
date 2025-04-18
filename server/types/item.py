from typing import Literal
from aenum import Enum
from enum import Enum as OEnum

from db.safe_transactions import safe_transactions


def enum_str_prefix(prefix):
    def decorator(enum_class):
        def __int__(self):
            return int(self.value)

        def __str__(self):
            return f"{prefix}_{self.name}"

        enum_class.__int__ = __int__
        enum_class.__str__ = __str__

        return enum_class

    return decorator


@enum_str_prefix("Item")
class ItemClass(OEnum):
    Equipment = 1
    Consumable = 2
    Valuables = 3
    Text = 4
    Material = 5
    Miscellaneous = 6

    @enum_str_prefix("Item_Equipment")
    class EquipmentClass(OEnum):
        HeadGear = 7
        TorsoGear = 8
        LegWear = 9
        FootWear = 10
        HandGear = 11
        Accessories = 12  # No subclass
        Weapon = 13

        @enum_str_prefix("Item_Equipment_HeadGear")
        class HeadGearClass(OEnum):
            Coverings = 14
            Hats = 15
            Helms = 16
            Special = 17

        @enum_str_prefix("Item_Equipment_TorsoGear")
        class TorsoGearClass(OEnum):
            UnderGarments = 18
            MidLayers = 19
            OuterWear = 20
            Special = 21

        @enum_str_prefix("Item_Equipment_LegWear")
        class LegWearClass(OEnum):
            UnderGarments = 22
            OuterLayers = 23
            Utility = 24

        @enum_str_prefix("Item_Equipment_FootWear")
        class FootWearClass(OEnum):
            Basic = 25
            Armored = 26
            Special = 27

        @enum_str_prefix("Item_Equipment_HandGear")
        class HandGearClass(OEnum):
            Protective = 28
            Utility = 29
            Special = 30

        @enum_str_prefix("Item_Equipment_Weapon")
        class WeaponClass(OEnum):
            OneHanded = 31
            TwoHanded = 32
            Shield = 33
            DualWield = 34

    @enum_str_prefix("Item_Consumable")
    class ConsumableClass(OEnum):
        Provision = 35
        Potion = 36
        Scroll = 37

    @enum_str_prefix("Item_Material")
    class MaterialClass(OEnum):
        Remain = 38
        Mineral = 39
        Botanical = 40

    @enum_str_prefix("Item_Miscellaneous")
    class MiscellaneousClass(OEnum):
        Container = 41
        Trap = 42
        Corpse = 43
        Decoration = 44
        Other = 45


VItemCls: dict[int, ItemClass] = {
    1: ItemClass.Equipment,
    2: ItemClass.Consumable,
    3: ItemClass.Valuables,
    4: ItemClass.Text,
    5: ItemClass.Material,
    6: ItemClass.Miscellaneous,
    7: ItemClass.EquipmentClass.HeadGear,
    8: ItemClass.EquipmentClass.TorsoGear,
    9: ItemClass.EquipmentClass.LegWear,
    10: ItemClass.EquipmentClass.FootWear,
    11: ItemClass.EquipmentClass.HandGear,
    12: ItemClass.EquipmentClass.Accessories,
    13: ItemClass.EquipmentClass.Weapon,
    14: ItemClass.EquipmentClass.HeadGearClass.Coverings,
    15: ItemClass.EquipmentClass.HeadGearClass.Hats,
    16: ItemClass.EquipmentClass.HeadGearClass.Helms,
    17: ItemClass.EquipmentClass.HeadGearClass.Special,
    18: ItemClass.EquipmentClass.TorsoGearClass.UnderGarments,
    19: ItemClass.EquipmentClass.TorsoGearClass.MidLayers,
    20: ItemClass.EquipmentClass.TorsoGearClass.OuterWear,
    21: ItemClass.EquipmentClass.TorsoGearClass.Special,
    22: ItemClass.EquipmentClass.LegWearClass.UnderGarments,
    23: ItemClass.EquipmentClass.LegWearClass.OuterLayers,
    24: ItemClass.EquipmentClass.LegWearClass.Utility,
    25: ItemClass.EquipmentClass.FootWearClass.Basic,
    26: ItemClass.EquipmentClass.FootWearClass.Armored,
    27: ItemClass.EquipmentClass.FootWearClass.Special,
    28: ItemClass.EquipmentClass.HandGearClass.Protective,
    29: ItemClass.EquipmentClass.HandGearClass.Utility,
    30: ItemClass.EquipmentClass.HandGearClass.Special,
    31: ItemClass.EquipmentClass.WeaponClass.OneHanded,
    32: ItemClass.EquipmentClass.WeaponClass.TwoHanded,
    33: ItemClass.EquipmentClass.WeaponClass.Shield,
    34: ItemClass.EquipmentClass.WeaponClass.DualWield,
    35: ItemClass.ConsumableClass.Provision,
    36: ItemClass.ConsumableClass.Potion,
    37: ItemClass.ConsumableClass.Scroll,
    38: ItemClass.MaterialClass.Remain,
    39: ItemClass.MaterialClass.Mineral,
    40: ItemClass.MaterialClass.Botanical,
    41: ItemClass.MiscellaneousClass.Container,
    42: ItemClass.MiscellaneousClass.Trap,
    43: ItemClass.MiscellaneousClass.Corpse,
    44: ItemClass.MiscellaneousClass.Decoration,
    45: ItemClass.MiscellaneousClass.Other,
}


def quality_str(quality: Literal['common', 'uncommon', 'rare' ,'exquisite', 'legendary']) -> 'str':
    d = {
        'common': 'ironwood',
        'uncommon': 'silvervein',
        'rare': 'goldleaf',
        'exquisite': 'duskforged',
        'legendary': 'dawnborn',
    }
    return d[quality]


class ItemType:
    def __init__(self, type_id: int, entry_name: str):
        self.id = type_id
        self.entry_name = entry_name

        self._fullname: str | None = None
        self._description: str | None = None
        self._category: ItemClass | None = None
        self._quality: Qualities | None = None
        self._attributes: object | None = None

    def _update_from_database(self):
        def _callback1(cursor):
            cursor.execute('''SELECT type_name, category_id, type_quality, type_description, type_attributes 
                FROM item_types_table WHERE type_id = %s''', (self.id,))
            res = cursor.fetchone()

            self._fullname = res[0]
            self._category = VItemCls[res[1]]
            self._quality = Qualities(res[2])
            self._description = res[3]
            self._attributes = res[4]

        safe_transactions(f'getting information of {self.id} - {self.entry_name}', _callback1)

    @property
    def fullname(self) -> 'str':
        if self._fullname is None:
            self._update_from_database()
        return self._fullname

    @property
    def description(self) -> 'str':
        if self._description is None:
            self._update_from_database()
        return self._description

    @property
    def category(self) -> 'ItemClass':
        if self._category is None:
            self._update_from_database()
        return self._category

    @property
    def quality(self) -> 'Qualities':
        if self._quality is None:
            self._update_from_database()
        return self._quality

    @property
    def attributes(self) -> object:
        if self._attributes is None:
            self._update_from_database()
        return self._attributes


class Item:
    def __init__(self, item_id: int, item_type: ItemType):
        self.id = item_id
        self.type = item_type


MItems: dict[int, Item] = {}


def add_items(item_id: int, item_type: ItemType):
    assert not item_id in MItems
    item = Item(item_id, item_type)
    MItems[item_id] = item
    return item


# MARKER_START
class EItem(Enum):
    RaggedPouch = 0
    RavenfeatherBroadbrim = 1
    ShadowstitchDoublet = 2
    ThiefsCloak = 3
    MutedLeatherBreeches = 4
    CatstepSoftboots = 5
    GamblersGloves = 6
    ChainOfTheHushed = 7
    RingOfFalsehoods = 8
    WidowsKiss = 9
    ShadowfangDaggers = 10
    RavenspeakBrew = 11
    MemoryfadeAsh = 12
    ElfToothDice = 13
    MutenessStone = 14
    BalladsOfTheDead = 15
    ScorchedMap = 16
    OldbloodInk = 17
    HushmossPowder = 18
    RavenquillPen = 19
    TatteredCowl = 20
    DriftersCoat = 21
    GreyLinenshirt = 22
    StrawBoundLeggings = 23
    ThinWornBreeches = 24
    CloutedBoots = 25
    SackclothGloves = 26
    CarvenSweetBox = 27
    ClaspKnife = 28
    CrookdStaff = 29
    BlackRyeCake = 30
    BrackenWaterskin = 31
    SlickWornPennies = 32
    WitchBead = 33
    BlankLeafBook = 34
    FadedBalladScrap = 35
    MarshMoss = 36
    BloodRustStone = 37
    RagDoll = 38
    BirdBoneWhistle = 39
    FrayedGoldRobe = 40
    BellTowerCloak = 41
    SanctuarySickle = 42
    PebblePouch = 43
    InkStainedHandwraps = 44
    BrokenHymnal = 45
    LastCandle = 46
    BindingCord = 47
    MistwoodRootTea = 48
    CrowFeatherQuill = 49


MItem: dict[int, ItemType] = {
    0: ItemType(0, "RaggedPouch"),
    1: ItemType(1, "RavenfeatherBroadbrim"),
    2: ItemType(2, "ShadowstitchDoublet"),
    3: ItemType(3, "ThiefsCloak"),
    4: ItemType(4, "MutedLeatherBreeches"),
    5: ItemType(5, "CatstepSoftboots"),
    6: ItemType(6, "GamblersGloves"),
    7: ItemType(7, "ChainOfTheHushed"),
    8: ItemType(8, "RingOfFalsehoods"),
    9: ItemType(9, "WidowsKiss"),
    10: ItemType(10, "ShadowfangDaggers"),
    11: ItemType(11, "RavenspeakBrew"),
    12: ItemType(12, "MemoryfadeAsh"),
    13: ItemType(13, "ElfToothDice"),
    14: ItemType(14, "MutenessStone"),
    15: ItemType(15, "BalladsOfTheDead"),
    16: ItemType(16, "ScorchedMap"),
    17: ItemType(17, "OldbloodInk"),
    18: ItemType(18, "HushmossPowder"),
    19: ItemType(19, "RavenquillPen"),
    20: ItemType(20, "TatteredCowl"),
    21: ItemType(21, "DriftersCoat"),
    22: ItemType(22, "GreyLinenshirt"),
    23: ItemType(23, "StrawBoundLeggings"),
    24: ItemType(24, "ThinWornBreeches"),
    25: ItemType(25, "CloutedBoots"),
    26: ItemType(26, "SackclothGloves"),
    27: ItemType(27, "CarvenSweetBox"),
    28: ItemType(28, "ClaspKnife"),
    29: ItemType(29, "CrookdStaff"),
    30: ItemType(30, "BlackRyeCake"),
    31: ItemType(31, "BrackenWaterskin"),
    32: ItemType(32, "SlickWornPennies"),
    33: ItemType(33, "WitchBead"),
    34: ItemType(34, "BlankLeafBook"),
    35: ItemType(35, "FadedBalladScrap"),
    36: ItemType(36, "MarshMoss"),
    37: ItemType(37, "BloodRustStone"),
    38: ItemType(38, "RagDoll"),
    39: ItemType(39, "BirdBoneWhistle"),
    40: ItemType(40, "FrayedGoldRobe"),
    41: ItemType(41, "BellTowerCloak"),
    42: ItemType(42, "SanctuarySickle"),
    43: ItemType(43, "PebblePouch"),
    44: ItemType(44, "InkStainedHandwraps"),
    45: ItemType(45, "BrokenHymnal"),
    46: ItemType(46, "LastCandle"),
    47: ItemType(47, "BindingCord"),
    48: ItemType(48, "MistwoodRootTea"),
    49: ItemType(49, "CrowFeatherQuill"),
}


# MARKER_END


if __name__ == '__main__':
    for idx in VItemCls:
        category = VItemCls[idx]
        assert category.value == idx
