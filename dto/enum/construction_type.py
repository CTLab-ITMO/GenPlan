from enum import Enum


class ConstructionType(Enum):
    COMBINED = -1
    WALL = 0
    DOOR = 1
    WINDOW = 2
    ROOF = 3
    FITTINGS = 4
    FLOOR = 5
    CEILING = 6
    BEAM = 7