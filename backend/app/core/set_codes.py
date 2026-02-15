"""
Set code mappings and regulation mark data for Pokemon TCG.

Maps set abbreviations (used in PTCGO/TCG Live exports) to TCGdex set IDs,
and tracks regulation marks for rotation legality checking.

No framework dependencies -- pure Python only.
"""


# ---------------------------------------------------------------------------
# Set abbreviation -> TCGdex set ID
# ---------------------------------------------------------------------------
SET_CODE_MAP: dict[str, str] = {
    # Scarlet & Violet era
    "SVI": "sv1",       # Scarlet & Violet Base
    "PAL": "sv2",       # Paldea Evolved
    "OBF": "sv3",       # Obsidian Flames
    "MEW": "sv3pt5",    # 151
    "PAR": "sv4",       # Paradox Rift
    "PAF": "sv4pt5",    # Paldean Fates
    "TEF": "sv5",       # Temporal Forces
    "TWM": "sv6",       # Twilight Masquerade
    "SFA": "sv6pt5",    # Shrouded Fable
    "SCR": "sv7",       # Stellar Crown
    "SSP": "sv8",       # Surging Sparks
    "PRE": "sv8pt5",    # Prismatic Evolutions
    "JTG": "sv9",       # Journey Together
    "ASC": "sv9pt5",    # Ascended Heroes
    "DRI": "sv10",      # Destined Rivals
    "MEV": "sv11",      # Mega Evolution
    # Special / promo / misc sets
    "MEE": "sve",       # Basic Energy (SV Energy)
    "SVE": "sve",       # SV Energy (alternate abbreviation)
    "MEG": "svmeg",     # Mega cards (special)
    "PFL": "svpfl",     # Paldean Fates Legacy
    "M3":  "svm3",      # Miscellaneous
    # Sword & Shield era (already rotating or rotated)
    "SSH": "swsh1",
    "RCL": "swsh2",
    "DAA": "swsh3",
    "VIV": "swsh4",
    "BST": "swsh5",
    "CRE": "swsh6",
    "EVS": "swsh7",
    "FST": "swsh8",
    "BRS": "swsh9",
    "ASR": "swsh10",
    "LOR": "swsh11",
    "SIT": "swsh12",
    "CRZ": "swsh12pt5",
}


# ---------------------------------------------------------------------------
# Set code (abbreviation OR tcgdex ID) -> regulation mark
#
# G = rotating March 2026
# H = safe (legal post-rotation)
# I = new sets (legal post-rotation)
# D/E/F = already rotated / illegal
# ---------------------------------------------------------------------------
REGULATION_MARKS: dict[str, str] = {
    # G regulation -- rotating March 2026
    "SVI": "G", "sv1": "G",
    "PAL": "G", "sv2": "G",
    "OBF": "G", "sv3": "G",
    "MEW": "G", "sv3pt5": "G",
    "PAR": "G", "sv4": "G",
    "PAF": "G", "sv4pt5": "G",
    # H regulation -- safe
    "TEF": "H", "sv5": "H",
    "TWM": "H", "sv6": "H",
    "SFA": "H", "sv6pt5": "H",
    "SCR": "H", "sv7": "H",
    "SSP": "H", "sv8": "H",
    # Basic Energy -- always legal (mark H)
    "SVE": "H", "sve": "H",
    "MEE": "H",
    # I regulation -- new sets
    "PRE": "I", "sv8pt5": "I",
    "JTG": "I", "sv9": "I",
    "ASC": "I", "sv9pt5": "I",
    "DRI": "I", "sv10": "I",
    "MEV": "I", "sv11": "I",
    "MEG": "I", "svmeg": "I",
    "PFL": "I", "svpfl": "I",
    "M3":  "I", "svm3": "I",
    # Sword & Shield era
    "swsh1": "D", "swsh2": "D", "swsh3": "D", "swsh4": "D",
    "swsh5": "E", "swsh6": "E", "swsh7": "E", "swsh8": "E",
    "swsh9": "F", "swsh10": "F", "swsh11": "F", "swsh12": "F",
    "swsh12pt5": "F",
    "SSH": "D", "RCL": "D", "DAA": "D", "VIV": "D",
    "BST": "E", "CRE": "E", "EVS": "E", "FST": "E",
    "BRS": "F", "ASR": "F", "LOR": "F", "SIT": "F", "CRZ": "F",
}


def normalize_set_code(code: str) -> str:
    """Normalize a set abbreviation to its TCGdex set ID.

    If the code is already a TCGdex ID or unknown, it is returned unchanged.
    """
    code_upper = code.upper().strip()
    return SET_CODE_MAP.get(code_upper, code)


def get_regulation_mark(set_code: str) -> str:
    """Return the regulation mark for a given set code.

    Looks up both the raw code and its normalized form.
    Returns ``"?"`` when the mark is unknown.
    """
    # Try the raw code first (handles abbreviations directly)
    mark = REGULATION_MARKS.get(set_code)
    if mark:
        return mark

    # Try the uppercase form
    mark = REGULATION_MARKS.get(set_code.upper())
    if mark:
        return mark

    # Try the normalized (TCGdex) form
    normalized = normalize_set_code(set_code)
    return REGULATION_MARKS.get(normalized, "?")
