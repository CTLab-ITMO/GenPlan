from enum import Enum


class RectType(Enum):
    UNKNOWN = -1
    WALL = 0
    DOOR = 1
    WINDOW = 2