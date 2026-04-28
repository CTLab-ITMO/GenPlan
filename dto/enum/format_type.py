from enum import Enum

from config import SVG_PATH, GIF_PATH, GLTF_PATH, IFC_PATH, OBJ_PATH


class FormatType(Enum):
    SHOW = None # You don't need a path for the display
    SVG = SVG_PATH
    GIF = GIF_PATH
    GLTF = GLTF_PATH
    IFC = IFC_PATH
    OBJ = OBJ_PATH

    @property
    def path(self) -> str:
        return self.value

    @classmethod
    def parse(cls, s: str) -> "FormatType":
        t = s.strip().lower()
        aliases = {
            "show": cls.SHOW,
            "svg": cls.SVG,
            ".svg": cls.SVG,
            "gif": cls.GIF,
            ".gif": cls.GIF,
            "gltf": cls.GLTF,
            ".gltf": cls.GLTF,
            "ifc": cls.IFC,
            ".ifc": cls.IFC,
            "obj": cls.OBJ,
            ".obj": cls.OBJ,
        }

        if t in aliases:
            return aliases[t]

        raise ValueError(f"Unknown model format: {s!r}")
