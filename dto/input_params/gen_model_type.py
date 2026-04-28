from enum import Enum


class Type(Enum):
    FLUX = "Flux"
    AURA_FLOW = "AuraFlow"
    SDXL = "SDXL"
    FALLBACK = "Fallback"

    @classmethod
    def parse(cls, s: str) -> "Type":
        t = s.strip().lower()
        aliases = {
            "flux": cls.FLUX,
            "auraflow": cls.AURA_FLOW,
            "sdxl": cls.SDXL,
            "fallback": cls.FALLBACK,
        }

        if t in aliases:
            return aliases[t]

        raise ValueError(f"Unknown model type: {s!r}")
