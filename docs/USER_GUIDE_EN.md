# USER_GUIDE_EN.md - TCG Tool v3.0 User Guide

**Author:** Bruno Strumendo
**Last Updated:** February 15, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Dashboard](#dashboard)
3. [Deck Management](#deck-management)
4. [Meta Game](#meta-game)
5. [Deck Analysis](#deck-analysis)
6. [Card Search](#card-search)
7. [Collection](#collection)
8. [Battles](#battles)
9. [AI Chat](#ai-chat)
10. [Simulation](#simulation)
11. [Tournaments & News](#tournaments--news)

---

## Overview

### What is TCG Tool?

**TCG Tool v3.0** is a comprehensive platform for **Pokemon Trading Card Game (TCG)** players. It offers:

- **Deck Management**: Create, import, and organize your decks
- **Competitive Analysis**: Compare decks with current meta
- **AI Assistant**: Get personalized strategic suggestions
- **Rotation Analysis**: Check the impact of the March 2026 rotation
- **Personal Collection**: Manage your cards and identify missing cards
- **Battles**: Record matches and get AI analysis
- **Simulator**: Test play sequences
- **Tournament Calendar**: Track official events
- **News Feed**: Stay updated with PokeBeach

### Who is it for?

- **Competitive Players**: Meta analysis, matchups, and tournament statistics
- **Beginners**: Deck suggestions and AI chat to learn strategies
- **Collectors**: Collection management and missing card tracking
- **Content Creators**: Battle video analysis with AI

### Platform Access

- **Web App**: http://localhost:3000 (development) or https://tcgtool.example.com (production)
- **API Docs**: http://localhost:8000/docs

---

## Dashboard

The home page displays a summary of your activities:

### Dashboard Sections

#### 1. Quick Summary

| Card | Information |
|------|------------|
| **My Decks** | Total saved decks |
| **Win Rate** | Win rate from last 20 battles |
| **Next Tournament** | Closest event on calendar |
| **Cards in Collection** | Total unique cards |

#### 2. Current Meta

Displays the **Top 8 Meta Decks** with:
- Deck name
- Tier (S, A, B)
- Usage rate (% in tournaments)
- Overall win rate

**Example:**
```
┌─────────────────────────────────────────┐
│ 1. Charizard ex / Pidgeot ex    [Tier S]│
│    Usage: 18.5% | Win Rate: 54.2%       │
├─────────────────────────────────────────┤
│ 2. Lugia VSTAR / Archeops       [Tier S]│
│    Usage: 15.3% | Win Rate: 52.8%       │
└─────────────────────────────────────────┘
```

#### 3. Recent Activities

- Last decks created/edited
- Recorded battles (last 5)
- Cards added to collection

#### 4. Quick Suggestions

The system suggests actions based on:
- Decks with cards rotating in March 2026
- Missing cards to complete meta decks
- Upcoming tournaments

---

## Deck Management

Access: **Menu > Decks** or `/decks`

### Create Deck Manually

1. Click **"New Deck"**
2. Fill in:
   - **Deck Name**: e.g., "Charizard ex / Pidgeot ex"
   - **Format**: Standard, Expanded, Limitless
   - **Description** (optional)
3. Add cards:
   - Use **quick search** to find cards
   - Click **"+ Add"**
   - Set **quantity** (1-4 for regular cards, up to 60 for basic energies)
4. Click **"Save Deck"**

**Shortcuts:**
- `Ctrl + S`: Save deck
- `Ctrl + F`: Focus on card search

### Import Deck

TCG Tool accepts the **PTCGO/TCG Live** format:

#### Step by Step

1. In TCG Live, select your deck
2. Click **"Export"** and copy the text
3. In TCG Tool, click **"Import Deck"**
4. Paste the text in the field
5. Click **"Import"**

**Accepted format example:**
```
Pokémon: 14
2 Charmander OBF 26
2 Charmeleon OBF 27
3 Charizard ex OBF 125
2 Pidgey OBF 162
2 Pidgeot ex OBF 164

Trainer: 32
4 Professor's Research SVI 189
4 Boss's Orders PAL 172
3 Ultra Ball SVI 196
2 Nest Ball SVI 181
2 Rare Candy SVI 191
...

Energy: 14
10 Fire Energy SVE 2
4 Double Turbo Energy BRS 151
```

#### Auto Detection

The system automatically detects:
- **Card type** (Pokemon, Trainer, Energy)
- **Trainer subtype** (Supporter, Item, Stadium, Tool)
- **Regulation** (Mark G, H, I)
- **Card images** in Portuguese and English

### View Deck

When opening a deck, you see:

#### 1. General Information
- Deck name
- Format
- Total cards (should be 60)
- Creation/edit date

#### 2. Card List with Images

Cards are displayed in a **visual grid** with:
- Card image
- Name in Portuguese
- Quantity (x2, x3, etc.)
- Set code (OBF 125)

**Filters:**
- By type: Pokemon / Trainer / Energy
- By subtype: Supporter / Item / Stadium
- By regulation: G / H / I

#### 3. Deck Statistics

```
┌─────────────────────────────────┐
│ Composition:                    │
│ • Pokemon: 14 cards (23%)       │
│ • Trainer: 32 cards (53%)       │
│ • Energy: 14 cards (23%)        │
├─────────────────────────────────┤
│ Rotation Impact:                │
│ • Rotating: 18 cards (30%)      │
│ • Severity: MODERATE            │
└─────────────────────────────────┘
```

### Export Deck

1. Open the deck
2. Click **"Export"**
3. Choose format:
   - **PTCGO/TCG Live** (text)
   - **JSON** (complete backup)
   - **Image** (visual for sharing)

### Check Missing Cards

1. Open the deck
2. Click **"Missing Cards"**
3. The system compares with your **Collection**
4. Shows list of cards you don't own

**Example:**
```
Missing Cards (8):
✗ Charizard ex OBF 125 (3x)
✗ Pidgeot ex OBF 164 (2x)
✗ Boss's Orders PAL 172 (4x)
...
```

### Edit Deck

1. Open the deck
2. Click **"Edit"**
3. Add/remove cards
4. Change quantities
5. Click **"Save"**

### Delete Deck

1. Open the deck
2. Click **"⋮"** (menu) > **"Delete"**
3. Confirm the action

---

## Meta Game

Access: **Menu > Meta** or `/meta`

### Tier List

View competitive decks organized by tier:

#### Tier S (Top Tier)
Decks with highest usage and win rate in tournaments.

**Example:**
```
┌──────────────────────────────────────────┐
│ Charizard ex / Pidgeot ex                │
│ Usage: 18.5% | Win Rate: 54.2%           │
│ Favorable against: Lugia, Mew VMAX       │
│ Unfavorable against: Miraidon ex         │
└──────────────────────────────────────────┘
```

#### Tier A
Competitive decks with specific favorable matchups.

#### Tier B
Viable decks but with less meta presence.

### Matchup Matrix

View all matchups between meta decks:

**Matrix Example:**
```
                Charizard  Lugia  Miraidon  Mew VMAX
Charizard ex       50%     55%     45%       52%
Lugia VSTAR        45%     50%     48%       60%
Miraidon ex        55%     52%     50%       58%
Mew VMAX           48%     40%     42%       50%
```

**Legend:**
- 🟢 **55%+**: Favorable matchup
- 🟡 **46-54%**: Even matchup
- 🔴 **45% or less**: Unfavorable matchup

### Meta Deck Details

When clicking on a meta deck, you see:

#### 1. Complete Decklist (60 cards)

Detailed list with images of all cards.

#### 2. Tournament Statistics

- **Top 8s**: Number of top 8 finishes in last 3 months
- **Conversion Rate**: % of top 8s that won the tournament
- **Known Players**: Names of players using the deck

#### 3. Detailed Matchups

For each matchup, see:
- Win rate
- Recommended strategy
- Suggested tech cards

**Example:**
```
vs. Miraidon ex (45% - Unfavorable)
─────────────────────────────────────
Strategy:
• Prioritize Pidgeot ex to search Boss's Orders
• Save Rare Candy for quick evolution
• Use Radiant Charizard as alternative attacker

Tech Cards:
• Hisuian Heavy Ball (search Pidgeot ex)
• Counter Catcher (when losing)
```

#### 4. Deck Variations

List of popular variations (e.g., build with Dusknoir, build with Arcanine ex).

---

## Deck Analysis

Access: **Open a Deck > "Analyze"** or `/decks/[id]/analysis`

### Rotation Analysis (March 2026)

Check the impact of the **March 2026 rotation** (cards with regulation G leave the format):

#### Rotation Report

```
┌─────────────────────────────────────────┐
│ ROTATION ANALYSIS - MARCH 2026          │
├─────────────────────────────────────────┤
│ Impact: MODERATE (30% of deck)          │
│                                         │
│ Rotating Cards (18):                    │
│ ✗ Charizard ex OBF 125 (3x)            │
│ ✗ Pidgeot ex OBF 164 (2x)              │
│ ✗ Professor's Research SVI 189 (4x)    │
│ ✗ Boss's Orders PAL 172 (4x)           │
│ ✗ Ultra Ball SVI 196 (3x)              │
│ ✗ Rare Candy SVI 191 (2x)              │
│                                         │
│ Legal Cards (42):                       │
│ ✓ Arcanine ex TEF 123 (2x)             │
│ ✓ Canceling Cologne ASC 136 (2x)       │
│ ✓ Earthen Vessel SFA 96 (2x)           │
│ ...                                     │
└─────────────────────────────────────────┘
```

#### Suggested Substitutions

The system automatically suggests substitutions:

**Example:**
```
Charizard ex OBF 125 → Charizard ex TEF 125
  • Same mechanics, new legal expansion
  • Similar win rate in tournaments

Professor's Research SVI 189 → Professor's Research TEF 190
  • Reprint of the same card in legal set

Ultra Ball SVI 196 → Nest Ball TEF 181
  • Similar function (search Basic Pokemon)
  • Doesn't discard cards
```

### Deck Comparison

Compare your deck with:
1. **Meta Deck** (e.g., standard Charizard ex)
2. **Another Deck of Yours**
3. **Imported Deck**

#### Comparison Report

```
┌─────────────────────────────────────────┐
│ YOUR DECK vs. CHARIZARD EX META         │
├─────────────────────────────────────────┤
│ Similarity: 78%                         │
│                                         │
│ Cards in Common (47):                   │
│ ✓ Charizard ex OBF 125 (3x)            │
│ ✓ Pidgeot ex OBF 164 (2x)              │
│ ...                                     │
│                                         │
│ Differences:                            │
│ You have:                               │
│ • Arcanine ex TEF 123 (2x)             │
│ • Counter Catcher PAR 160 (2x)         │
│                                         │
│ Meta Deck has:                          │
│ • Radiant Charizard CRZ 20 (1x)        │
│ • Super Rod PAL 188 (1x)               │
└─────────────────────────────────────────┘
```

#### Estimated Matchup

The system estimates the matchup based on:
- Card composition
- Tournament data
- Historical win rates

**Example:**
```
Estimated Matchup:
🟢 Favorable against Lugia VSTAR (58%)
🟡 Even against Miraidon ex (51%)
🔴 Unfavorable against Mew VMAX (44%)
```

### Substitution Suggestions

The system analyzes your deck and suggests improvements:

#### By Category

**1. Consistency:**
```
+ Add Nest Ball TEF 181 (2x)
  • Improves initial setup
  • Used in 95% of Charizard decks
```

**2. Tech Cards:**
```
+ Add Counter Catcher PAR 160 (1x)
  • Useful when losing
  • Popular tech against Lugia
```

**3. Suggested Removals:**
```
- Remove Potion SVI 194 (2x)
  • Low competitive impact
  • Used in only 5% of meta decks
```

---

## Card Search

Access: **Menu > Cards** or `/cards`

### Search Cards

Use the search bar with advanced filters:

#### Available Filters

| Filter | Options |
|--------|---------|
| **Name** | Free text |
| **Type** | Pokemon, Trainer, Energy |
| **Subtype** | Supporter, Item, Stadium, Tool, Basic, Special |
| **Regulation** | F, G, H, I |
| **Set** | SVI, PAL, OBF, MEW, PAR, TEF, TWM, etc. |
| **Rarity** | Common, Uncommon, Rare, Ultra Rare |
| **HP** | 30-340 HP (Pokemon) |
| **Pokemon Type** | Fire, Water, Grass, Lightning, etc. |

**Search Example:**
```
Name: "Boss's Orders"
Type: Trainer
Subtype: Supporter
Regulation: G, H, I
```

**Result:**
```
┌─────────────────────────────────────────┐
│ Boss's Orders (Ghetsis)                 │
│ PAL 172 | Supporter | Regulation G      │
│ [Card Image]                            │
│                                         │
│ Effect:                                 │
│ "Choose 1 of your opponent's Benched    │
│  Pokemon and switch it with the Active  │
│  Pokemon."                              │
│                                         │
│ Statistics:                             │
│ • Used in 85% of competitive decks      │
│ • Win rate: 52.3% (when played)         │
└─────────────────────────────────────────┘
```

### View Card Details

When clicking on a card, see:

#### 1. Complete Information
- Name in PT and EN
- Front/back image
- HP, type, weakness, resistance, retreat cost (Pokemon)
- Complete effect (text in Portuguese)
- Artist, set number

#### 2. Legality
- Standard Format: ✓ Legal / ✗ Rotated
- Expanded Format: ✓ Legal
- Limitless Format: ✓ Legal

#### 3. Alternatives

Similar cards or alternative versions:

**Example for Boss's Orders:**
```
Alternative Versions:
• Boss's Orders (Lysandre) PAF 172 (Regulation G)
• Boss's Orders (Ghetsis) TEF 190 (Regulation H)
• Boss's Orders (Cyrus) TWM 172 (Regulation H)
```

#### 4. Usage Statistics

```
Tournament Usage (last 3 months):
• Top 8: 92% of decks
• Average copies: 3.2x per deck
• Main decks:
  1. Charizard ex (4x) - 95% of decks
  2. Lugia VSTAR (4x) - 98% of decks
  3. Miraidon ex (4x) - 100% of decks
```

---

## Collection

Access: **Menu > Collection** or `/collection`

### Add Cards to Collection

#### Method 1: Manual Search

1. Use **card search**
2. Click **"+ Add to Collection"**
3. Set the **quantity** you own
4. Click **"Save"**

#### Method 2: Bulk Import

1. Click **"Import Collection"**
2. Paste a card list (PTCGO format)
3. The system adds all cards

#### Method 3: Card Scan (Mobile)

1. Open the Android app
2. Click **"Scan"**
3. Take a photo of the card
4. Confirm detection
5. Set quantity

### View Collection

#### Visual Grid

See all your cards in a grid with images:

**Filters:**
- By set (SVI, PAL, OBF, etc.)
- By type (Pokemon, Trainer, Energy)
- By rarity
- Missing only (cards you don't have)

#### Statistics

```
┌─────────────────────────────────────────┐
│ COLLECTION SUMMARY                      │
├─────────────────────────────────────────┤
│ Total Cards: 1,248                      │
│ Unique Cards: 342                       │
│                                         │
│ By Type:                                │
│ • Pokemon: 189 (55%)                    │
│ • Trainer: 128 (37%)                    │
│ • Energy: 25 (7%)                       │
│                                         │
│ By Rarity:                              │
│ • Ultra Rare: 23                        │
│ • Rare: 67                              │
│ • Uncommon: 142                         │
│ • Common: 110                           │
└─────────────────────────────────────────┘
```

### View Missing Cards by Deck

1. Select a **Meta Deck** or **Your Deck**
2. The system compares with your collection
3. Shows list of cards you still need

**Example:**
```
Missing Cards for Charizard ex:
✗ Charizard ex OBF 125 (need: 3, have: 1)
✗ Pidgeot ex OBF 164 (need: 2, have: 0)
✗ Rare Candy SVI 191 (need: 2, have: 1)

Total Missing: 7 cards
Progress: 88% complete
```

### Mark Cards as "For Trade"

1. Open a card in collection
2. Click **"Mark for Trade"**
3. The card appears in **"My Trade Cards"**

---

## Battles

Access: **Menu > Battles** or `/battles`

### Record Battle

#### Step by Step

1. Click **"New Battle"**
2. Fill in:
   - **Your Deck**: Select from list
   - **Opponent Deck**: Select meta deck or create custom
   - **Result**: Win / Loss
   - **Format**: Standard, Expanded, Limitless
   - **Tournament** (optional): Event name
   - **Date/Time**: Automatic or manual
3. Add **notes** (optional):
   - Key plays
   - Misplays
   - Luck/unlucky moments
4. **Video Upload** (optional):
   - Local file (MP4, MOV)
   - YouTube/Twitch link
5. Click **"Save Battle"**

### AI Analysis

If you uploaded a video, click **"Analyze with AI"**:

#### Analysis Process

1. **Frame Extraction**: AI analyzes key frames from video
2. **Card Detection**: Recognizes cards played
3. **Play Sequence**: Recreates the match log
4. **Strategic Analysis**: Identifies optimal plays and errors

**Result:**
```
┌─────────────────────────────────────────┐
│ AI ANALYSIS - BATTLE #42                │
├─────────────────────────────────────────┤
│ Duration: 18min 34s                     │
│ Winning Turn: Turn 9                    │
│                                         │
│ Key Plays:                              │
│ ✓ T2: Boss's Orders on Pidgey (optimal) │
│ ✓ T5: Rare Candy + Charizard ex (optimal)│
│ ✗ T7: Attacked with Charizard instead  │
│       of using Boss's Orders (error)    │
│                                         │
│ Suggestions:                            │
│ • On T7, Boss's Orders on Radiant       │
│   Greninja would guarantee KO           │
│ • Consider playing Ultra Ball earlier   │
│   to search Pidgeot ex                  │
└─────────────────────────────────────────┘
```

### Statistics

View your overall statistics:

#### Global Summary

```
┌─────────────────────────────────────────┐
│ GENERAL STATISTICS                      │
├─────────────────────────────────────────┤
│ Total Battles: 87                       │
│ Wins: 54 (62.1%)                        │
│ Losses: 33 (37.9%)                      │
│                                         │
│ Win Rate by Deck:                       │
│ • Charizard ex: 68% (34W / 16L)         │
│ • Lugia VSTAR: 58% (11W / 8L)           │
│ • Miraidon ex: 53% (9W / 8L)            │
└─────────────────────────────────────────┘
```

#### Specific Matchups

```
Your Charizard ex vs. Meta Decks:
🟢 vs. Lugia VSTAR: 75% (9W / 3L)
🟢 vs. Mew VMAX: 66% (8W / 4L)
🟡 vs. Gardevoir ex: 50% (5W / 5L)
🔴 vs. Miraidon ex: 40% (6W / 9L)
```

#### Charts

- Win rate over time (line)
- Distribution of decks used (pie)
- Most played matchups (bar)

---

## AI Chat

Access: **Menu > AI Chat** or `/chat`

### Ask Questions about Strategy

The AI assistant answers questions about:
- Deck strategies
- Specific matchups
- Tech cards
- Game decisions

#### Question Examples

**Question 1:**
```
User: What's the best strategy against Miraidon ex
      using Charizard ex?

AI: Against Miraidon ex, the key is:

1. Quick Setup:
   • Prioritize evolving Pidgeot ex on T2
   • Use Rare Candy to accelerate Charizard ex

2. Prize Management:
   • Avoid leaving vulnerable Pokemon ex on Bench
   • Use Radiant Charizard as alternative attacker
     (1 prize instead of 2)

3. Boss's Orders:
   • Priority target: Miraidon ex with energy (2 KO)
   • Secondary target: Iron Hands ex (setup)

4. Recommended Tech Cards:
   • Counter Catcher (when losing)
   • Earthen Vessel (accelerate energy)

Expected win rate: 45-48% (unfavorable matchup)
```

**Question 2:**
```
User: Is it worth playing Dusknoir in my
      Charizard ex deck?

AI: Dusknoir (ASC 111) is an interesting tech:

Advantages:
✓ "Cursed Blast" ability deals 40 damage
  upon entering play
✓ Useful to hit specific KO numbers
✓ Counter for spread damage decks

Disadvantages:
✗ Takes 3 slots (Duskull + Dusclops + Dusknoir)
✗ Reduces deck consistency
✗ Slow (Stage 2 evolution)

Recommendation:
Only if you face a lot of Snorlax/Mew VMAX
(which depend on exact HP). In most cases,
prefer adding more draw/search.

Tournament usage: 12% of Charizard ex top 8s
```

### Select Deck Context

For personalized answers:

1. Click **"Select Deck"**
2. Choose one of your decks
3. AI now considers your specific decklist

**Example with Context:**
```
User: [With Charizard ex deck selected]
      Which cards should I replace after rotation?

AI: Analyzing your Charizard ex:

Rotating Cards:
1. Professor's Research SVI 189 (4x)
   → Replace with: Professor's Research TEF 190

2. Boss's Orders PAL 172 (4x)
   → Replace with: Boss's Orders TEF 190

3. Ultra Ball SVI 196 (3x)
   → Replace with: Nest Ball TEF 181 (2x)
                   + Arven TEF 186 (1x)

Your deck will be 95% legal after these changes.
```

### Quick Suggestions

Common question buttons:

- 📊 "What's the best deck for beginners?"
- 🔄 "How to replace rotating cards?"
- ⚔️ "Which deck against current meta?"
- 💡 "Tech cards for my deck?"
- 📈 "How to improve consistency?"

---

## Simulation

Access: **Menu > Simulation** or `/simulation`

### Simulate Play Sequence

Test plays before executing them in real matches.

#### Step by Step

1. Select **Your Deck**
2. Select **Opponent Deck**
3. Configure **Initial State**:
   - Cards in hand
   - Active/Bench Pokemon (yours and opponent's)
   - Attached energies
   - Remaining prize cards
4. Click **"Start Simulation"**

#### Simulation Interface

```
┌─────────────────────────────────────────┐
│ SIMULATOR - TURN 5 (You)                │
├─────────────────────────────────────────┤
│ Hand (6 cards):                         │
│ • Boss's Orders                         │
│ • Ultra Ball                            │
│ • Rare Candy                            │
│ • Charmeleon                            │
│ • Fire Energy                           │
│ • Professor's Research                  │
│                                         │
│ Active: Charmander (60 HP)              │
│ Bench: Pidgey, Pidgey                   │
│                                         │
│ Available Actions:                      │
│ [1] Play Professor's Research           │
│ [2] Play Ultra Ball (search card)       │
│ [3] Evolve Charmander → Charmeleon      │
│ [4] Attach Fire Energy                  │
│ [5] Attack with Charmander              │
│ [6] Retreat to Bench                    │
└─────────────────────────────────────────┘
```

#### AI Analysis

After each play, the AI suggests:
- **Optimal Play**: Statistically best action
- **Alternatives**: Other viable options
- **Probabilities**: Success chance

**Example:**
```
AI Analysis:
✓ Optimal Play: [1] Professor's Research
  • Refreshes hand (6 → 7 cards)
  • Increases chance of finding Pidgeot ex (78%)

Alternatives:
• [2] Ultra Ball → search Pidgey
  • Guaranteed, but discards 2 cards
  • Recommended if hand is bad

Avoid:
✗ [5] Attack with Charmander
  • Insufficient damage (30 HP)
  • Wastes turn
```

---

## Tournaments & News

Access: **Menu > Tournaments** or `/tournaments`

### Tournament Calendar

View official and local events:

#### Filters

- **Format**: Standard, Expanded, Limitless
- **Level**: Regional, International, World Championships, Local
- **Location**: By country/city
- **Date**: Next 7/30/90 days

#### List Example

```
┌─────────────────────────────────────────┐
│ UPCOMING TOURNAMENTS                    │
├─────────────────────────────────────────┤
│ 📅 02/22/2026 | Regional São Paulo      │
│    Format: Standard | Players: ~250    │
│    Location: Expo Center Norte          │
│    [View Details] [Add to Calendar]    │
├─────────────────────────────────────────┤
│ 📅 03/08/2026 | International LATAM     │
│    Format: Standard | Players: ~800    │
│    Location: Mexico City Convention Center│
│    [View Details] [Add to Calendar]    │
└─────────────────────────────────────────┘
```

#### Calendar Integration

1. Click **"Add to Calendar"**
2. Event is added to **Google Calendar** or **iCal** (Android)
3. Get notifications before tournament

### News Feed (PokeBeach)

Stay updated with the latest news:

#### Categories

- **Reveals**: New cards announced
- **Metagame**: Deck and tournament analyses
- **Products**: New sets, special products
- **Competitive**: Tournament results, tier lists

#### News Example

```
┌─────────────────────────────────────────┐
│ 🆕 Revealed: Mewtwo ex from Journey to Go│
│ 2 hours ago | PokeBeach                 │
├─────────────────────────────────────────┤
│ [Card Image]                            │
│                                         │
│ Mewtwo ex - 220 HP                      │
│ Psychic Energy x2 | Psycho Sphere: 120 │
│                                         │
│ Analysis:                               │
│ "Mewtwo ex could revitalize Psychic    │
│  decks in post-rotation format..."     │
│                                         │
│ [Read More] [Share]                     │
└─────────────────────────────────────────┘
```

#### Notifications

Configure alerts for:
- New card reveals
- Specific tournament results
- Meta analyses

---

## Frequently Asked Questions

### 1. How do I update my deck after rotation?

Use **Deck Analysis > Rotation** to see rotating cards and automatic substitution suggestions.

### 2. Can I import decks from TCG Live?

Yes! Use **Decks > Import** and paste the exported text from TCG Live (PTCGO format).

### 3. Does video analysis work in Portuguese?

Yes, the AI recognizes cards in Portuguese and English automatically.

### 4. Is my collection synced on mobile?

Yes, if you log in with the same account, the collection is synced between web and mobile.

### 5. How do I compare my deck with the meta?

Open your deck and click **"Analyze" > "Compare with Meta"**. Select a meta deck and see the differences.

---

## Support

For questions or issues:

- **Email**: strumendo@gmail.com
- **GitHub Issues**: https://github.com/strumendo/tcg-tool/issues
- **Discord**: [Coming soon]

---

**Guide Version:** 3.0.0
**Last Updated:** February 15, 2026
**Author:** Bruno Strumendo
