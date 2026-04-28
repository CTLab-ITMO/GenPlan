from enum import Enum


class Type(Enum):
    TWO_DIMENSIONAL = "2D"
    THREE_DIMENSIONAL = "3D"

    @classmethod
    def parse(cls, s: str) -> "Type":
        t = s.strip().lower()
        aliases = {
            "2d": cls.TWO_DIMENSIONAL,
            "3d": cls.THREE_DIMENSIONAL,
        }

        if t in aliases:
            return aliases[t]

        raise ValueError(f"Unknown type of result: {s!r}")
