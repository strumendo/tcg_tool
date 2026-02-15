"""
Pokemon TCG type weakness and resistance chart.

No framework dependencies -- pure Python only.
"""
from typing import Optional


# ---------------------------------------------------------------------------
# Weakness chart (attacker_type -> defending_type it is weak to)
#
# In the TCG, weakness means the *defending* Pokemon takes double damage
# from attacks of the weakness type.  This dict maps each energy / Pokemon
# type to the type it is *weak* to.
# ---------------------------------------------------------------------------

TYPE_WEAKNESSES: dict[str, Optional[str]] = {
    "grass":     "fire",
    "fire":      "water",
    "water":     "lightning",
    "lightning": "fighting",
    "fighting":  "psychic",
    "psychic":   "darkness",
    "darkness":  "fighting",
    "metal":     "fire",
    "dragon":    "dragon",
    "colorless": None,
    "fairy":     "metal",
}


# ---------------------------------------------------------------------------
# Resistance chart (type -> type it resists, i.e. takes reduced damage from)
# ---------------------------------------------------------------------------

TYPE_RESISTANCES: dict[str, Optional[str]] = {
    "grass":     "water",
    "fire":      None,
    "water":     None,
    "lightning": "metal",
    "fighting":  None,
    "psychic":   "fighting",
    "darkness":  None,
    "metal":     "grass",
    "dragon":    None,
    "colorless": "fighting",
    "fairy":     "darkness",
}


def get_weakness(energy_type: str) -> Optional[str]:
    """Return the type that *energy_type* is weak to, or ``None``."""
    return TYPE_WEAKNESSES.get(energy_type.lower())


def get_resistance(energy_type: str) -> Optional[str]:
    """Return the type that *energy_type* resists, or ``None``."""
    return TYPE_RESISTANCES.get(energy_type.lower())
