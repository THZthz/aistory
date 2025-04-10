from aenum import Enum

from aistory.db.safe_transactions import safe_transactions


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
                FROM "LocationsTable" WHERE location_id = %s''', (self.id,))

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



# MARKER_START
class ELoc(Enum):
    FenmireDuchies = 0
    Gallowrest = 1
    Gallowrest_WestDocks = 2
    HollowLanten = 3
    HollowLanten_GroundFloor = 4


MLoc: dict[int, Location] = {
    0: Location(0, "FenmireDuchies"),
    1: Location(1, "Gallowrest"),
    2: Location(2, "Gallowrest_WestDocks"),
    3: Location(3, "HollowLanten"),
    4: Location(4, "HollowLanten_GroundFloor"),
}

# MARKER_END
