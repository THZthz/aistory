from aenum import Enum

from db.safe_transactions import safe_transactions


class Location:
    def __init__(self, loc_id: int, entry_name: str):
        self.id = loc_id
        self.entry_name = entry_name

        self._fullname: str | None = None
        self._type: str | None = None
        self._description: str | None = None
        self._path: str | None = None

    def _update_from_database(self):
        def _callback(cursor):
            cursor.execute('''SELECT location_name, location_type, location_description, location_path 
                FROM locations WHERE location_id = %s''', (self.id,))

            res = cursor.fetchone()
            self._fullname = res[0]
            self._type = res[1]
            self._description = res[2]
            self._path = res[3]

        safe_transactions(f'getting {self.entry_name} information from LocationsTable', _callback)

    @property
    def fullname(self) -> str:
        if self._fullname is None:
            self._update_from_database()
        return self._fullname

    @property
    def type(self) -> str:
        if self._type is None:
            self._update_from_database()
        return self._type

    @property
    def description(self) -> str:
        if self._description is None:
            self._update_from_database()
        return self._description

    @property
    def path(self) -> str:
        if self._path is None:
            self._update_from_database()
        return self._path


def get_all_locations_start_with(prefix: str) -> list[Location]:
    return []


# MARKER_START
class ELoc(Enum):
    FenmireDuchies = 0
    Gallowrest = 1
    Gallowrest_WestDocks = 2
    Gallowrest_HighGallows = 3
    Gallowrest_WestDocks_FishgutAlley = 4
    Gallowrest_Nightmarket = 5
    HollowLanten = 6
    HollowLanten_GroundFloor = 7
    HollowLanten_SecondFloor = 8
    HollowLanten_ThirdFloor = 9
    HollowLanten_Cellar = 10
    Leechwarrens = 11
    LeechmongersDen = 12
    TithingPool = 13
    ChirurgeonsRow = 14
    BlackBargain = 15
    Bonewalk = 16
    Deepwell = 17
    LeechmongersDen_Backroom = 18
    TithingPool_Bloodledge = 19
    ChirurgeonsRow_AmputationStall = 20
    BlackBargain_OathNiche = 21
    Bonewalk_Knucklepost = 22
    Deepwell_Ladle7 = 23
    TithingPool_WeepingDrain = 24


MLoc: dict[int, Location] = {
    0: Location(0, "FenmireDuchies"),
    1: Location(1, "Gallowrest"),
    2: Location(2, "Gallowrest_WestDocks"),
    3: Location(3, "Gallowrest_HighGallows"),
    4: Location(4, "Gallowrest_WestDocks_FishgutAlley"),
    5: Location(5, "Gallowrest_Nightmarket"),
    6: Location(6, "HollowLanten"),
    7: Location(7, "HollowLanten_GroundFloor"),
    8: Location(8, "HollowLanten_SecondFloor"),
    9: Location(9, "HollowLanten_ThirdFloor"),
    10: Location(10, "HollowLanten_Cellar"),
    11: Location(11, "Leechwarrens"),
    12: Location(12, "LeechmongersDen"),
    13: Location(13, "TithingPool"),
    14: Location(14, "ChirurgeonsRow"),
    15: Location(15, "BlackBargain"),
    16: Location(16, "Bonewalk"),
    17: Location(17, "Deepwell"),
    18: Location(18, "LeechmongersDen_Backroom"),
    19: Location(19, "TithingPool_Bloodledge"),
    20: Location(20, "ChirurgeonsRow_AmputationStall"),
    21: Location(21, "BlackBargain_OathNiche"),
    22: Location(22, "Bonewalk_Knucklepost"),
    23: Location(23, "Deepwell_Ladle7"),
    24: Location(24, "TithingPool_WeepingDrain"),
}


# MARKER_END
