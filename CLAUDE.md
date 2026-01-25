# CLAUDE.md - AI Assistant Guide for TCG Tool

## Project Overview

This is a **Pokemon Trading Card Game (TCG) deck analyzer** with bilingual support (English/Portuguese). It provides:

- **CLI Tool**: Interactive deck analysis, rotation checking, matchup comparison
- **Android App**: Native mobile app built with Kivy for browsing meta decks
- **Meta Database**: Top 8 competitive decks with complete card lists and matchup data

The tool focuses on the **March 2026 rotation** (Regulation Mark G cards rotating out) and competitive meta analysis.

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| CLI UI | `rich` (tables, panels, colors) |
| HTTP Client | `httpx` (async) |
| Mobile | Kivy + Buildozer (Android) |
| Database | SQLite (card cache) |
| APIs | TCGdex (primary), Pokemon TCG API (fallback) |

## Repository Structure

```
tcg_tool/
├── main.py              # CLI entry point, interactive menu
├── meta_database.py     # Top 8 meta decks + matchup data (bilingual)
├── deck_suggest.py      # Deck suggestion engine
├── deck_parser.py       # PTCGO format parser
├── rotation_checker.py  # Rotation impact analysis
├── deck_compare.py      # Deck comparison & matchup analysis
├── substitution.py      # Card substitution logic
├── card_api.py          # TCGdex/Pokemon TCG API integration
├── models.py            # Dataclasses (Card, Deck, Substitution)
├── database.py          # SQLite cache layer
├── requirements.txt     # Python dependencies (httpx, rich)
├── example_deck.txt     # Sample Charizard ex deck
├── example_opponent.txt # Sample opponent deck
└── android_app/         # Android application
    ├── main.py          # Kivy app (5 screens)
    ├── meta_data.py     # Offline meta database
    ├── buildozer.spec   # Android build config
    └── README.md        # Build instructions
```

## Key Modules

### `main.py` (CLI Entry Point)
- Interactive menu with 6 options + language toggle
- Command-line argument parsing (-r, -c, -s, -m, --matchups, --lang)
- Global `CURRENT_LANGUAGE` variable for UI strings
- Uses Rich for formatted output

### `meta_database.py` (Core Data)
- 8 complete meta decks with 60 cards each
- 28 matchup relationships with win rates
- `Language` enum (EN, PT) for bilingual support
- Key classes: `MetaDeck`, `CardEntry`, `MatchupData`

### `models.py` (Data Models)
- `Card`: name, card_type, set_code, regulation_mark, functions
- `Deck`: list of cards with computed properties (rotation_impact)
- `CardType` enum: POKEMON, TRAINER, ENERGY
- `CardFunction` enum: DRAW, SEARCH, RECOVERY, SWITCHING, etc.

### `deck_parser.py` (Format Parsing)
- Parses PTCGO/Pokemon TCG Live export format
- Regex: `(\d+)\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)`
- Auto-detects card types and trainer subtypes
- Normalizes set codes (OBF -> sv3)

### `card_api.py` (API Integration)
- TCGdex: `https://api.tcgdex.net/v2` (primary, 10+ languages)
- Pokemon TCG API: `https://api.pokemontcg.io/v2` (fallback, English)
- Automatic fallback on API failure
- 30-60 second timeout

## Development Conventions

### Code Style
- Python dataclasses for data models
- Type hints throughout
- Bilingual strings: always provide both `_en` and `_pt` variants
- Use Rich for CLI output (Console, Table, Panel)

### Bilingual Support Pattern
```python
from meta_database import Language, get_translation

# In functions, accept lang parameter
def my_function(lang: Language = Language.EN):
    title = get_translation("title_key", lang)
    # or
    text = "English text" if lang == Language.EN else "Texto em Portugues"
```

### Adding New Meta Decks
1. Add to `META_DECKS` dict in `meta_database.py`
2. Include all 60 cards with bilingual names
3. Add matchup data to `MATCHUP_DATA` dict
4. Update `android_app/meta_data.py` with same data

### Regulation Mark System
| Mark | Status | Notes |
|------|--------|-------|
| G | Rotating Mar 2026 | SVI, PAL, OBF, MEW, PAR, PAF |
| H | Legal | TEF, TWM, SFA, SCR, SSP |
| I | Legal | PRE, JTG, ASC, DRI, MEV |
| F or earlier | Already illegal | Sword & Shield era |

### Set Code Mappings (in `deck_parser.py`)
```
SVI -> sv1, PAL -> sv2, OBF -> sv3, MEW -> sv3.5
PAR -> sv4, PAF -> sv4.5, TEF -> sv5, TWM -> sv6
SFA -> sv6.5, SCR -> sv7, SSP -> sv8, PRE -> svp
JTG -> sv9, ASC -> sv10, DRI -> sv11
```

## Running the Project

### CLI Tool
```bash
# Install dependencies
pip install -r requirements.txt

# Interactive mode
python main.py

# Analyze deck file
python main.py deck.txt

# Rotation analysis only
python main.py deck.txt -r

# Browse meta decks
python main.py -m

# View matchup matrix
python main.py --matchups

# Set language
python main.py --lang pt
```

### Android App (Desktop Testing)
```bash
pip install kivy
python android_app/main.py
```

### Android APK Build
```bash
cd android_app
pip install buildozer kivy cython
buildozer android debug
# Output: bin/tcgmeta-*.apk
```

## Testing

### Manual Testing Commands
```bash
# Test deck parsing
python main.py example_deck.txt

# Test rotation analysis
python main.py example_deck.txt -r

# Test deck comparison
python main.py example_deck.txt --vs example_opponent.txt

# Test suggestion
python main.py -s Charizard

# Test meta browsing
python main.py -m
```

### Example Deck Files
- `example_deck.txt`: Charizard ex / Pidgeot ex (competitive deck)
- `example_opponent.txt`: Opponent deck for comparison testing

## Common Tasks

### Adding a New Feature
1. Identify which module(s) need changes
2. Follow existing patterns (dataclasses, bilingual support)
3. Update `main.py` menu if adding user-facing option
4. Add CLI argument if needed

### Updating Meta Data
1. Edit `meta_database.py` (CLI) and `android_app/meta_data.py` (mobile)
2. Both files must stay in sync for consistency
3. Update matchup data if adding/modifying decks

### API Changes
- All API logic in `card_api.py`
- Implement fallback pattern (TCGdex -> Pokemon TCG API)
- Cache results via `database.py` to minimize API calls

### UI Changes
- CLI: Edit Rich components in `main.py`
- Android: Edit Kivy widgets in `android_app/main.py`
- Color palette defined in android_app/main.py `get_color_from_hex()`

## Important Considerations

### Data Consistency
- `meta_database.py` and `android_app/meta_data.py` contain duplicate data
- Changes must be applied to both files
- Card names must have both English and Portuguese versions

### API Rate Limiting
- TCGdex is primary; no known rate limits but be respectful
- Pokemon TCG API requires API key for heavy usage
- SQLite cache in `cards.db` reduces repeat calls

### Rotation Logic
- Basic energies are ALWAYS legal regardless of set
- Cards detected via `regulation_mark` field
- Severity levels: NONE (0%), LOW (1-20%), MODERATE (21-40%), HIGH (41-60%), CRITICAL (61%+)

### Android Build Notes
- First build downloads Android SDK/NDK (~30 min)
- Use Python 3.10/3.11 (3.12+ has distutils issues)
- Java 17 required
- Supports foldable devices (Samsung Z Fold)

## Architecture Decisions

1. **Modular Design**: Each concern (parsing, rotation, comparison) in separate file
2. **Bilingual First**: All user-facing strings support EN/PT
3. **Offline Mobile**: Android app embeds all meta data for offline use
4. **API Fallback**: Primary API failure gracefully falls back to secondary
5. **Local Caching**: SQLite cache reduces API dependency
6. **Rich CLI**: Beautiful terminal UI using Rich library
7. **Cross-Platform Mobile**: Kivy enables Python-based Android app

## Dependencies

### Production
- `httpx>=0.28.0` - Async HTTP client
- `rich>=14.0.0` - Terminal formatting

### Android Build
- `kivy` - Cross-platform UI framework
- `buildozer` - Android packaging tool
- `cython` - Python to C compiler

## Git Workflow

- Main branch: `main`
- Feature branches: `claude/feature-name-*` for AI-assisted development
- Commits should be atomic and descriptive
- Test locally before pushing

## Quick Reference

### Card Types
- `POKEMON`: Pokemon cards (detect by name patterns like "ex", "V", "VSTAR")
- `TRAINER`: Supporter, Item, Stadium, Tool
- `ENERGY`: Basic and Special energy

### Matchup Indicators
- **Favored**: 55%+ win rate
- **Even**: 46-54% win rate
- **Unfavored**: 45% or below

### Key Functions to Know
| File | Function | Purpose |
|------|----------|---------|
| `main.py` | `run_browse_meta_decks()` | Navigate meta deck list |
| `deck_parser.py` | `parse_deck(text)` | Convert PTCGO format to Deck object |
| `rotation_checker.py` | `analyze_rotation(deck)` | Generate rotation report |
| `deck_compare.py` | `compare_decks(a, b)` | Compare two decks |
| `meta_database.py` | `get_matchup(a, b)` | Get win rate between decks |
| `card_api.py` | `fetch_card_tcgdex()` | Fetch card from API |
