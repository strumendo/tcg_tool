"""
Deck Builder Module - Build decks with filters and real-time matchup analysis

This module provides:
- Interactive deck building with ability filters
- Real-time matchup percentages against meta decks
- Gameplay guides against top decks
- Card suggestions based on synergies
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from models import Card, CardType, Deck, CardFunction
from abilities_database import (
    AbilityCategory, PokemonCard, PokemonAbility,
    POKEMON_DATABASE, ABILITY_DESCRIPTIONS, DECK_TEMPLATES,
    get_pokemon_by_ability, search_pokemon, get_all_ability_categories,
    get_counters_for_ability, get_legal_pokemon
)
from meta_database import (
    META_DECKS, MetaDeck, CardEntry, MATCHUPS,
    get_matchup, get_deck_matchups, calculate_meta_score
)


# =============================================================================
# DECK BUILDER STATE
# =============================================================================

@dataclass
class DeckBuilderCard:
    """A card in the deck builder."""
    name_en: str
    name_pt: str
    set_code: str
    set_number: str
    quantity: int
    card_type: str  # "pokemon", "trainer", "energy"
    hp: int = 0
    energy_type: str = ""
    abilities: list[AbilityCategory] = field(default_factory=list)
    is_ex: bool = False
    is_mega: bool = False
    is_tera: bool = False


@dataclass
class DeckBuilderState:
    """Current state of the deck builder."""
    cards: list[DeckBuilderCard] = field(default_factory=list)
    deck_name: str = "My Custom Deck"
    primary_type: Optional[str] = None
    archetype: Optional[str] = None

    @property
    def total_cards(self) -> int:
        return sum(c.quantity for c in self.cards)

    @property
    def pokemon_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == "pokemon")

    @property
    def trainer_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == "trainer")

    @property
    def energy_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == "energy")

    @property
    def is_valid(self) -> bool:
        """Check if deck has exactly 60 cards."""
        return self.total_cards == 60

    @property
    def main_attackers(self) -> list[DeckBuilderCard]:
        """Get main attackers (ex, Mega, high HP Pokemon)."""
        return [c for c in self.cards
                if c.card_type == "pokemon" and (c.is_ex or c.is_mega or c.hp >= 200)]

    @property
    def deck_abilities(self) -> list[AbilityCategory]:
        """Get all abilities present in the deck."""
        abilities = []
        for card in self.cards:
            abilities.extend(card.abilities)
        return list(set(abilities))

    def get_energy_types(self) -> list[str]:
        """Get all energy types in deck."""
        types = set()
        for card in self.cards:
            if card.energy_type:
                types.add(card.energy_type)
        return list(types)


# =============================================================================
# MATCHUP CALCULATOR
# =============================================================================

@dataclass
class MatchupResult:
    """Result of matchup analysis."""
    opponent_name: str
    opponent_id: str
    win_rate: float
    confidence: str  # "High", "Medium", "Low"
    key_factors: list[str]
    key_factors_pt: list[str]
    tips_en: list[str]
    tips_pt: list[str]


# Type weakness chart
TYPE_WEAKNESSES = {
    "fire": "water",
    "water": "lightning",
    "lightning": "fighting",
    "fighting": "psychic",
    "psychic": "darkness",
    "darkness": "fighting",
    "grass": "fire",
    "metal": "fire",
    "dragon": "dragon",
    "fairy": "metal",
    "colorless": None
}

TYPE_RESISTANCES = {
    "psychic": "fighting",
    "darkness": "psychic",
    "metal": "grass",
    "fairy": "darkness",
    "dragon": None
}


def calculate_type_advantage(attacker_types: list[str], defender_weakness: str) -> float:
    """Calculate type advantage multiplier."""
    if not defender_weakness:
        return 1.0
    for t in attacker_types:
        if t.lower() == defender_weakness.lower():
            return 1.3  # 30% advantage
    return 1.0


def calculate_matchup_vs_meta_deck(
    custom_deck: DeckBuilderState,
    meta_deck: MetaDeck,
    lang: str = "en"
) -> MatchupResult:
    """Calculate matchup against a meta deck."""

    # Base win rate starts at 50%
    win_rate = 50.0
    factors_en = []
    factors_pt = []
    tips_en = []
    tips_pt = []

    # Get deck characteristics
    custom_types = custom_deck.get_energy_types()
    custom_abilities = custom_deck.deck_abilities

    # 1. Type advantage analysis
    for attacker in custom_deck.main_attackers:
        if attacker.energy_type:
            for key_pokemon in meta_deck.key_pokemon:
                # Check if we hit weakness
                meta_card = None
                for card_id, card in POKEMON_DATABASE.items():
                    if key_pokemon.lower() in card.name_en.lower():
                        meta_card = card
                        break

                if meta_card and meta_card.weakness:
                    if attacker.energy_type.lower() == meta_card.weakness.lower():
                        win_rate += 8
                        factors_en.append(f"{attacker.name_en} hits {key_pokemon}'s weakness")
                        factors_pt.append(f"{attacker.name_pt} acerta fraqueza de {key_pokemon}")
                        break

    # 2. Check if opponent hits our weakness
    for meta_type in meta_deck.energy_types:
        for attacker in custom_deck.main_attackers:
            weakness = TYPE_WEAKNESSES.get(attacker.energy_type.lower() if attacker.energy_type else "")
            if weakness and meta_type.lower() == weakness.lower():
                win_rate -= 10
                factors_en.append(f"Weak to {meta_type} attacks")
                factors_pt.append(f"Fraco contra ataques {meta_type}")
                tips_en.append(f"Consider adding damage reduction or Safeguard Pokemon")
                tips_pt.append(f"Considere adicionar reducao de dano ou Pokemon Safeguard")
                break

    # 3. Ability interactions
    if AbilityCategory.SAFEGUARD in custom_abilities:
        # Safeguard is great vs ex-heavy decks
        ex_count = sum(1 for p in meta_deck.key_pokemon if "ex" in p.lower())
        if ex_count >= 2:
            win_rate += 10
            factors_en.append("Safeguard blocks their main attackers")
            factors_pt.append("Safeguard bloqueia os atacantes principais")

    if AbilityCategory.BENCH_BARRIER in custom_abilities:
        # Check if meta deck has spread damage
        if meta_deck.id in ["dragapult", "grimmsnarl"]:
            win_rate += 12
            factors_en.append("Bench Barrier counters their spread damage")
            factors_pt.append("Bench Barrier anula dano espalhado")

    if AbilityCategory.SPREAD_DAMAGE in custom_abilities:
        # Spread is weaker vs bench barrier decks
        if meta_deck.id == "gholdengo":
            win_rate -= 5
            factors_en.append("Gholdengo doesn't rely on bench")
            factors_pt.append("Gholdengo nao depende do banco")
        else:
            win_rate += 5
            factors_en.append("Spread damage chips multiple targets")
            factors_pt.append("Dano espalhado acerta multiplos alvos")

    if AbilityCategory.ENERGY_ACCEL in custom_abilities:
        win_rate += 5
        factors_en.append("Energy acceleration provides speed advantage")
        factors_pt.append("Aceleracao de energia fornece vantagem de velocidade")

    if AbilityCategory.DRAW_POWER in custom_abilities:
        win_rate += 3
        factors_en.append("Draw power improves consistency")
        factors_pt.append("Poder de compra melhora consistencia")

    if AbilityCategory.SEARCH in custom_abilities:
        win_rate += 5
        factors_en.append("Search ability ensures key cards")
        factors_pt.append("Habilidade de busca garante cartas-chave")

    # 4. Deck-specific adjustments
    if meta_deck.id == "gholdengo":
        if any(c.energy_type and c.energy_type.lower() == "fire" for c in custom_deck.main_attackers):
            win_rate += 15
            factors_en.append("Fire type is super effective vs Metal")
            factors_pt.append("Tipo Fogo e super efetivo contra Metal")
            tips_en.append("Prioritize getting Fire attackers set up quickly")
            tips_pt.append("Priorize montar atacantes de Fogo rapidamente")

    if meta_deck.id == "dragapult":
        if AbilityCategory.BENCH_BARRIER not in custom_abilities:
            win_rate -= 8
            tips_en.append("Consider adding Manaphy or Jirachi for bench protection")
            tips_pt.append("Considere adicionar Manaphy ou Jirachi para protecao do banco")

    if meta_deck.id == "gardevoir":
        if any(c.energy_type and c.energy_type.lower() == "darkness" for c in custom_deck.main_attackers):
            win_rate += 12
            factors_en.append("Darkness hits Psychic weakness")
            factors_pt.append("Escuridao acerta fraqueza Psiquica")

    if meta_deck.id == "charizard":
        if any(c.energy_type and c.energy_type.lower() == "water" for c in custom_deck.main_attackers):
            win_rate += 12
            factors_en.append("Water extinguishes Fire")
            factors_pt.append("Agua apaga Fogo")

    # 5. Speed/consistency analysis
    has_search = AbilityCategory.SEARCH in custom_abilities
    has_draw = AbilityCategory.DRAW_POWER in custom_abilities
    has_accel = AbilityCategory.ENERGY_ACCEL in custom_abilities

    if meta_deck.tier == 1:
        if not has_search and not has_draw:
            win_rate -= 8
            tips_en.append("Add consistency cards (Iono, Professor's Research, Pidgeot ex)")
            tips_pt.append("Adicione cartas de consistencia (Iono, Pesquisa do Professor, Pidgeot ex)")

    # Clamp win rate to reasonable bounds
    win_rate = max(15, min(85, win_rate))

    # Determine confidence
    if len(factors_en) >= 3:
        confidence = "High"
    elif len(factors_en) >= 1:
        confidence = "Medium"
    else:
        confidence = "Low"

    return MatchupResult(
        opponent_name=meta_deck.name_en if lang == "en" else meta_deck.name_pt,
        opponent_id=meta_deck.id,
        win_rate=win_rate,
        confidence=confidence,
        key_factors=factors_en if lang == "en" else factors_pt,
        key_factors_pt=factors_pt,
        tips_en=tips_en,
        tips_pt=tips_pt
    )


def analyze_all_matchups(
    custom_deck: DeckBuilderState,
    lang: str = "en"
) -> list[MatchupResult]:
    """Analyze matchups against all meta decks."""
    results = []
    for deck_id, meta_deck in META_DECKS.items():
        result = calculate_matchup_vs_meta_deck(custom_deck, meta_deck, lang)
        results.append(result)

    # Sort by win rate descending
    results.sort(key=lambda x: -x.win_rate)
    return results


def calculate_overall_meta_score(matchups: list[MatchupResult]) -> float:
    """Calculate overall meta viability score weighted by meta share."""
    total_weighted = 0.0
    total_weight = 0.0

    for matchup in matchups:
        if matchup.opponent_id in META_DECKS:
            meta_share = META_DECKS[matchup.opponent_id].meta_share
            total_weighted += matchup.win_rate * meta_share
            total_weight += meta_share

    if total_weight == 0:
        return 50.0

    return total_weighted / total_weight


# =============================================================================
# GAMEPLAY GUIDE GENERATOR
# =============================================================================

@dataclass
class GameplayGuide:
    """Gameplay guide for a specific matchup."""
    opponent_name: str
    win_rate: float
    difficulty: str  # "Easy", "Medium", "Hard"

    # Early game
    early_game_priority_en: list[str]
    early_game_priority_pt: list[str]

    # Mid game
    mid_game_strategy_en: list[str]
    mid_game_strategy_pt: list[str]

    # Late game
    late_game_focus_en: list[str]
    late_game_focus_pt: list[str]

    # Key cards to watch
    key_threats_en: list[str]
    key_threats_pt: list[str]

    # What to Boss/target
    priority_targets_en: list[str]
    priority_targets_pt: list[str]


# Generic strategy templates based on archetype
STRATEGY_TEMPLATES = {
    "gholdengo": {
        "threats": ["Gholdengo ex", "Genesect V"],
        "targets": ["Gimmighoul before it evolves", "Genesect V for easy prizes"],
        "early_en": ["Set up your attackers quickly", "Don't bench too many Pokemon - limits their Coin Bonus draws"],
        "early_pt": ["Monte seus atacantes rapidamente", "Nao coloque muitos Pokemon no banco - limita draws do Coin Bonus"],
        "mid_en": ["Trade efficiently - they need 2 attacks to KO most ex", "Use Boss's Orders on Gimmighoul"],
        "mid_pt": ["Troque eficientemente - eles precisam de 2 ataques para KO na maioria dos ex", "Use Boss's Orders no Gimmighoul"],
        "late_en": ["One-shot Gholdengo if possible", "They struggle to recover once behind"],
        "late_pt": ["Nocauteie Gholdengo em um golpe se possivel", "Eles tem dificuldade de recuperar quando atras"]
    },
    "dragapult": {
        "threats": ["Dragapult ex", "Dreepy spread damage"],
        "targets": ["Drakloak to prevent evolution", "Dreepy early game"],
        "early_en": ["Get Manaphy/bench protection ASAP", "Limit bench to essential Pokemon only"],
        "early_pt": ["Pegue Manaphy/protecao de banco RAPIDO", "Limite o banco apenas a Pokemon essenciais"],
        "mid_en": ["Heal or recover damaged Pokemon", "Don't let damage accumulate"],
        "mid_pt": ["Cure ou recupere Pokemon danificados", "Nao deixe dano acumular"],
        "late_en": ["One big attacker is better than many damaged ones", "Boss weakened Dragapult"],
        "late_pt": ["Um atacante forte e melhor que varios danificados", "Boss Dragapult enfraquecido"]
    },
    "gardevoir": {
        "threats": ["Gardevoir ex", "Mega Gardevoir ex", "Scream Tail"],
        "targets": ["Ralts before it evolves", "Kirlia with damage"],
        "early_en": ["Pressure Ralts line aggressively", "They need time to set up"],
        "early_pt": ["Pressione linha de Ralts agressivamente", "Eles precisam de tempo para montar"],
        "mid_en": ["Spread damage to punish Psychic Embrace", "Watch for Scream Tail walls"],
        "mid_pt": ["Espalhe dano para punir Psychic Embrace", "Cuidado com paredes de Scream Tail"],
        "late_en": ["They have infinite energy - focus on taking KOs", "Boss benched Gardevoir ex"],
        "late_pt": ["Eles tem energia infinita - foque em pegar KOs", "Boss Gardevoir ex no banco"]
    },
    "charizard": {
        "threats": ["Charizard ex", "Mega Charizard Y ex", "Pidgeot ex"],
        "targets": ["Pidgey/Pidgeotto to cut off Quick Search", "Charmander early"],
        "early_en": ["Rush them before Charizard evolves", "Target Pidgey line first"],
        "early_pt": ["Ataque rapido antes de Charizard evoluir", "Mire linha de Pidgey primeiro"],
        "mid_en": ["Without Pidgeot, they lose consistency", "Watch for Burning Darkness scaling"],
        "mid_pt": ["Sem Pidgeot, eles perdem consistencia", "Cuidado com Burning Darkness escalando"],
        "late_en": ["Their damage increases as you take prizes", "Consider N/Iono to disrupt"],
        "late_pt": ["O dano deles aumenta conforme voce pega premios", "Considere N/Iono para atrapalhar"]
    },
    "raging_bolt": {
        "threats": ["Raging Bolt ex", "Ogerpon ex (Teal Mask)"],
        "targets": ["Ogerpon ex for easy prizes", "Raging Bolt with low energy"],
        "early_en": ["They're fast - match their speed", "Ogerpon accelerates their setup"],
        "early_pt": ["Eles sao rapidos - iguale a velocidade", "Ogerpon acelera o setup deles"],
        "mid_en": ["Dragon type means no weakness to exploit", "Trade 2-for-2 if needed"],
        "mid_pt": ["Tipo Dragao significa sem fraqueza para explorar", "Troque 2-por-2 se necessario"],
        "late_en": ["They run out of steam eventually", "Boss to break their momentum"],
        "late_pt": ["Eles ficam sem recursos eventualmente", "Boss para quebrar o momentum"]
    },
    "grimmsnarl": {
        "threats": ["Marnie's Grimmsnarl ex", "Froslass", "Mega Froslass ex", "Munkidori"],
        "targets": ["Snorunt before Froslass", "Munkidori to stop damage movement"],
        "early_en": ["Get bench protection if you have abilities", "Limit benched Pokemon with abilities"],
        "early_pt": ["Pegue protecao de banco se tiver habilidades", "Limite Pokemon no banco com habilidades"],
        "mid_en": ["Heal frequently to deny Munkidori targets", "Watch Spikemuth Gym damage"],
        "mid_pt": ["Cure frequentemente para negar alvos do Munkidori", "Cuidado com dano do Ginasio Spikemuth"],
        "late_en": ["They win through attrition - be aggressive", "KO Froslass to stop spread"],
        "late_pt": ["Eles vencem por atrito - seja agressivo", "KO Froslass para parar spread"]
    },
    "mega_dragonite": {
        "threats": ["Mega Dragonite ex", "Dragonite V"],
        "targets": ["Dratini before it evolves", "Dragonite V for 2 prizes"],
        "early_en": ["Pressure evolution line early", "They need time to set up Mega"],
        "early_pt": ["Pressione linha de evolucao cedo", "Eles precisam de tempo para montar Mega"],
        "mid_en": ["Sky Transport makes them slippery", "Don't overcommit to one target"],
        "mid_pt": ["Sky Transport os torna escorregadios", "Nao se comprometa demais com um alvo"],
        "late_en": ["330 damage OHKOs most things", "Have a response ready"],
        "late_pt": ["330 de dano nocauteia a maioria", "Tenha uma resposta pronta"]
    },
    "joltik_box": {
        "threats": ["Various Joltik attackers", "Electrode ex"],
        "targets": ["Electrode ex for energy denial", "Active Joltik"],
        "early_en": ["They're flexible - identify their plan", "Electrode gives them energy burst"],
        "early_pt": ["Eles sao flexiveis - identifique o plano", "Electrode da burst de energia"],
        "mid_en": ["Trade favorably against single-prize Pokemon", "Boss their support Pokemon"],
        "mid_pt": ["Troque favoravelmente contra Pokemon de premio unico", "Boss Pokemon de suporte"],
        "late_en": ["They run out of attackers eventually", "Maintain prize lead"],
        "late_pt": ["Eles ficam sem atacantes eventualmente", "Mantenha lideranca de premios"]
    },
    "flareon": {
        "threats": ["Flareon ex", "Eevee"],
        "targets": ["Eevee before evolution", "Support Pokemon"],
        "early_en": ["Rush Eevee before it evolves", "They need specific conditions"],
        "early_pt": ["Ataque Eevee antes de evoluir", "Eles precisam de condicoes especificas"],
        "mid_en": ["Watch for type matchups - Fire hits Metal hard", "Don't feed them KOs"],
        "mid_pt": ["Cuidado com matchups de tipo - Fogo acerta Metal forte", "Nao de KOs de graca"],
        "late_en": ["They're more predictable late game", "Set up 2HKO sequences"],
        "late_pt": ["Eles sao mais previsiveis no late game", "Monte sequencias de 2HKO"]
    }
}


def generate_gameplay_guide(
    custom_deck: DeckBuilderState,
    meta_deck: MetaDeck,
    matchup_result: MatchupResult,
    lang: str = "en"
) -> GameplayGuide:
    """Generate a gameplay guide for a specific matchup."""

    deck_id = meta_deck.id
    template = STRATEGY_TEMPLATES.get(deck_id, STRATEGY_TEMPLATES["gholdengo"])

    # Determine difficulty based on win rate
    if matchup_result.win_rate >= 60:
        difficulty = "Easy" if lang == "en" else "Facil"
    elif matchup_result.win_rate >= 45:
        difficulty = "Medium" if lang == "en" else "Medio"
    else:
        difficulty = "Hard" if lang == "en" else "Dificil"

    # Build priority targets based on deck's abilities
    priority_targets_en = template["targets"].copy()
    priority_targets_pt = template["targets"].copy()

    # Customize based on deck's abilities
    early_en = template["early_en"].copy()
    early_pt = template["early_pt"].copy()
    mid_en = template["mid_en"].copy()
    mid_pt = template["mid_pt"].copy()
    late_en = template["late_en"].copy()
    late_pt = template["late_pt"].copy()

    # Add deck-specific advice based on abilities
    if AbilityCategory.SAFEGUARD in custom_deck.deck_abilities:
        early_en.append("Get Safeguard Pokemon active early to wall their ex attackers")
        early_pt.append("Coloque Pokemon Safeguard ativo cedo para bloquear atacantes ex")

    if AbilityCategory.BENCH_BARRIER in custom_deck.deck_abilities:
        early_en.append("Bench your Manaphy/Jirachi immediately for protection")
        early_pt.append("Coloque Manaphy/Jirachi no banco imediatamente para protecao")

    if AbilityCategory.SPREAD_DAMAGE in custom_deck.deck_abilities:
        mid_en.append("Spread damage to set up multi-KO turns")
        mid_pt.append("Espalhe dano para preparar turnos de multiplos KOs")

    if AbilityCategory.ENERGY_ACCEL in custom_deck.deck_abilities:
        early_en.append("Prioritize energy acceleration to attack faster")
        early_pt.append("Priorize aceleracao de energia para atacar mais rapido")

    return GameplayGuide(
        opponent_name=meta_deck.name_en if lang == "en" else meta_deck.name_pt,
        win_rate=matchup_result.win_rate,
        difficulty=difficulty,
        early_game_priority_en=early_en,
        early_game_priority_pt=early_pt,
        mid_game_strategy_en=mid_en,
        mid_game_strategy_pt=mid_pt,
        late_game_focus_en=late_en,
        late_game_focus_pt=late_pt,
        key_threats_en=template["threats"],
        key_threats_pt=template["threats"],
        priority_targets_en=priority_targets_en,
        priority_targets_pt=priority_targets_pt
    )


def generate_all_guides(
    custom_deck: DeckBuilderState,
    matchups: list[MatchupResult],
    lang: str = "en"
) -> list[GameplayGuide]:
    """Generate gameplay guides for all meta matchups."""
    guides = []
    for matchup in matchups:
        if matchup.opponent_id in META_DECKS:
            guide = generate_gameplay_guide(
                custom_deck,
                META_DECKS[matchup.opponent_id],
                matchup,
                lang
            )
            guides.append(guide)
    return guides


# =============================================================================
# CARD SUGGESTIONS
# =============================================================================

def suggest_cards_for_deck(
    current_deck: DeckBuilderState,
    lang: str = "en"
) -> dict[str, list[tuple[str, str]]]:
    """Suggest cards to improve the deck."""
    suggestions = {
        "consistency": [],
        "offense": [],
        "defense": [],
        "tech": []
    }

    current_abilities = current_deck.deck_abilities

    # Check for missing consistency
    if AbilityCategory.DRAW_POWER not in current_abilities:
        suggestions["consistency"].append((
            "Kirlia (SVI 68)" if lang == "en" else "Kirlia (SVI 68)",
            "Refinement ability for draw power" if lang == "en" else "Habilidade Refinement para compra"
        ))
        suggestions["consistency"].append((
            "Bibarel (BRS 121)" if lang == "en" else "Bibarel (BRS 121)",
            "Industrious Incisors draws to 5 cards" if lang == "en" else "Incisivos Industriosos compra ate 5 cartas"
        ))

    if AbilityCategory.SEARCH not in current_abilities:
        suggestions["consistency"].append((
            "Pidgeot ex (OBF 164)" if lang == "en" else "Pidgeot ex (OBF 164)",
            "Quick Search finds any card every turn" if lang == "en" else "Quick Search acha qualquer carta todo turno"
        ))

    # Check for missing bench protection
    if AbilityCategory.BENCH_BARRIER not in current_abilities:
        suggestions["defense"].append((
            "Jirachi (PAR 126)" if lang == "en" else "Jirachi (PAR 126)",
            "Stellar Veil protects bench from effects" if lang == "en" else "Veu Estelar protege banco de efeitos"
        ))

    # Check for Safeguard options
    if AbilityCategory.SAFEGUARD not in current_abilities:
        suggestions["defense"].append((
            "Mimikyu (PAL 97)" if lang == "en" else "Mimikyu (PAL 97)",
            "Safeguard blocks ex/V damage completely" if lang == "en" else "Safeguard bloqueia dano de ex/V completamente"
        ))

    # Energy acceleration options based on type
    if AbilityCategory.ENERGY_ACCEL not in current_abilities:
        types = current_deck.get_energy_types()
        if "Psychic" in types:
            suggestions["consistency"].append((
                "Gardevoir ex (SVI 86)" if lang == "en" else "Gardevoir ex (SVI 86)",
                "Infinite Psychic energy from discard" if lang == "en" else "Energia Psiquica infinita do descarte"
            ))
        if "Grass" in types:
            suggestions["consistency"].append((
                "Ogerpon ex Teal (TWM 25)" if lang == "en" else "Ogerpon ex Turquesa (TWM 25)",
                "Attach Grass energy and draw" if lang == "en" else "Anexa energia Planta e compra"
            ))
        if "Fire" in types:
            suggestions["consistency"].append((
                "Charizard ex (OBF 125)" if lang == "en" else "Charizard ex (OBF 125)",
                "Infernal Reign attaches 3 Fire energy" if lang == "en" else "Reinado Infernal anexa 3 energias Fogo"
            ))

    # Tech suggestions based on meta
    suggestions["tech"].append((
        "Munkidori (TWM 95)" if lang == "en" else "Munkidori (TWM 95)",
        "Move damage counters for strategic KOs" if lang == "en" else "Move contadores de dano para KOs estrategicos"
    ))

    # Mega options from Ascended Heroes
    suggestions["offense"].append((
        "Mega Dragonite ex (ASC 142)" if lang == "en" else "Mega Dragonite ex (ASC 142)",
        "330 damage + Sky Transport pivoting" if lang == "en" else "330 de dano + pivoteamento Sky Transport"
    ))

    return suggestions


# =============================================================================
# DECK BUILDER INTERFACE HELPERS
# =============================================================================

def add_pokemon_to_deck(
    deck: DeckBuilderState,
    pokemon_key: str,
    quantity: int = 1
) -> bool:
    """Add a Pokemon from database to deck."""
    if pokemon_key not in POKEMON_DATABASE:
        return False

    pokemon = POKEMON_DATABASE[pokemon_key]

    # Check 4-card limit (except basic energy)
    existing = next((c for c in deck.cards if c.name_en == pokemon.name_en), None)
    if existing:
        if existing.quantity + quantity > 4:
            return False
        existing.quantity += quantity
    else:
        abilities = [a.category for a in pokemon.abilities]
        abilities.extend(pokemon.attack_categories)

        card = DeckBuilderCard(
            name_en=pokemon.name_en,
            name_pt=pokemon.name_pt,
            set_code=pokemon.set_code,
            set_number=pokemon.set_number,
            quantity=quantity,
            card_type="pokemon",
            hp=pokemon.hp,
            energy_type=pokemon.energy_type,
            abilities=list(set(abilities)),
            is_ex=pokemon.is_ex,
            is_mega=pokemon.is_mega,
            is_tera=pokemon.is_tera
        )
        deck.cards.append(card)

    return True


def add_trainer_to_deck(
    deck: DeckBuilderState,
    name_en: str,
    name_pt: str,
    set_code: str,
    set_number: str,
    quantity: int = 1
) -> bool:
    """Add a trainer card to deck."""
    existing = next((c for c in deck.cards if c.name_en == name_en), None)
    if existing:
        if existing.quantity + quantity > 4:
            return False
        existing.quantity += quantity
    else:
        card = DeckBuilderCard(
            name_en=name_en,
            name_pt=name_pt,
            set_code=set_code,
            set_number=set_number,
            quantity=quantity,
            card_type="trainer"
        )
        deck.cards.append(card)
    return True


def add_energy_to_deck(
    deck: DeckBuilderState,
    energy_type: str,
    quantity: int = 1,
    is_basic: bool = True
) -> bool:
    """Add energy to deck."""
    name_en = f"Basic {energy_type} Energy" if is_basic else f"{energy_type} Energy"
    name_pt = f"Energia {energy_type} Basica" if is_basic else f"Energia {energy_type}"

    existing = next((c for c in deck.cards if c.name_en == name_en), None)
    if existing:
        existing.quantity += quantity
    else:
        card = DeckBuilderCard(
            name_en=name_en,
            name_pt=name_pt,
            set_code="SVE",
            set_number="1",
            quantity=quantity,
            card_type="energy",
            energy_type=energy_type
        )
        deck.cards.append(card)
    return True


def remove_card_from_deck(
    deck: DeckBuilderState,
    name_en: str,
    quantity: int = 1
) -> bool:
    """Remove cards from deck."""
    card = next((c for c in deck.cards if c.name_en == name_en), None)
    if not card:
        return False

    card.quantity -= quantity
    if card.quantity <= 0:
        deck.cards.remove(card)
    return True


def get_deck_summary(deck: DeckBuilderState, lang: str = "en") -> str:
    """Get a formatted summary of the deck."""
    lines = []
    lines.append(f"{'=' * 50}")
    lines.append(f"  {deck.deck_name}")
    lines.append(f"{'=' * 50}")
    lines.append("")

    # Card counts
    total = deck.total_cards
    status = "Valid" if deck.is_valid else f"Invalid ({total}/60)"
    status_pt = "Valido" if deck.is_valid else f"Invalido ({total}/60)"

    lines.append(f"{'Status:':15} {status if lang == 'en' else status_pt}")
    lines.append(f"{'Pokemon:':15} {deck.pokemon_count}")
    lines.append(f"{'Trainers:':15} {deck.trainer_count}")
    lines.append(f"{'Energy:':15} {deck.energy_count}")
    lines.append(f"{'Total:':15} {total}/60")
    lines.append("")

    # Abilities in deck
    abilities = deck.deck_abilities
    if abilities:
        lines.append("Deck Abilities:" if lang == "en" else "Habilidades do Deck:")
        for ability in abilities:
            desc = ABILITY_DESCRIPTIONS.get(ability, {})
            lines.append(f"  - {ability.value}: {desc.get(lang, '')}")
    lines.append("")

    # Energy types
    types = deck.get_energy_types()
    if types:
        lines.append(f"{'Energy Types:' if lang == 'en' else 'Tipos de Energia:'} {', '.join(types)}")

    return "\n".join(lines)


def get_matchup_display(matchups: list[MatchupResult], lang: str = "en") -> str:
    """Get a formatted display of matchups."""
    lines = []
    lines.append("")
    lines.append(f"{'=' * 60}")
    lines.append("  MATCHUP ANALYSIS" if lang == "en" else "  ANALISE DE MATCHUPS")
    lines.append(f"{'=' * 60}")
    lines.append("")

    header = f"{'Opponent':<25} {'Win%':>8} {'Confidence':>12}"
    header_pt = f"{'Oponente':<25} {'Vit%':>8} {'Confianca':>12}"
    lines.append(header if lang == "en" else header_pt)
    lines.append("-" * 50)

    for m in matchups:
        indicator = "+" if m.win_rate >= 55 else "-" if m.win_rate < 45 else "="
        lines.append(f"{m.opponent_name:<25} {m.win_rate:>7.1f}% {indicator:>2} {m.confidence:>9}")

    # Overall score
    overall = calculate_overall_meta_score(matchups)
    lines.append("-" * 50)
    overall_label = "Overall Meta Score:" if lang == "en" else "Pontuacao Meta Geral:"
    lines.append(f"{overall_label} {overall:.1f}%")

    # Rating
    if overall >= 55:
        rating = "Strong meta choice" if lang == "en" else "Escolha forte no meta"
    elif overall >= 50:
        rating = "Viable meta deck" if lang == "en" else "Deck viavel no meta"
    elif overall >= 45:
        rating = "Risky meta choice" if lang == "en" else "Escolha arriscada no meta"
    else:
        rating = "Weak meta position" if lang == "en" else "Posicao fraca no meta"

    lines.append(f"Rating: {rating}")
    lines.append("")

    return "\n".join(lines)


def get_guide_display(guide: GameplayGuide, lang: str = "en") -> str:
    """Get a formatted display of a gameplay guide."""
    lines = []
    lines.append(f"\n{'=' * 60}")
    lines.append(f"  VS {guide.opponent_name.upper()}")
    lines.append(f"  Win Rate: {guide.win_rate:.0f}% | Difficulty: {guide.difficulty}")
    lines.append(f"{'=' * 60}")

    lines.append(f"\n{'KEY THREATS' if lang == 'en' else 'AMEACAS PRINCIPAIS'}:")
    for threat in (guide.key_threats_en if lang == "en" else guide.key_threats_pt):
        lines.append(f"  ! {threat}")

    lines.append(f"\n{'PRIORITY TARGETS' if lang == 'en' else 'ALVOS PRIORITARIOS'}:")
    for target in (guide.priority_targets_en if lang == "en" else guide.priority_targets_pt):
        lines.append(f"  > {target}")

    lines.append(f"\n{'EARLY GAME' if lang == 'en' else 'INICIO DE JOGO'}:")
    for tip in (guide.early_game_priority_en if lang == "en" else guide.early_game_priority_pt):
        lines.append(f"  - {tip}")

    lines.append(f"\n{'MID GAME' if lang == 'en' else 'MEIO DE JOGO'}:")
    for tip in (guide.mid_game_strategy_en if lang == "en" else guide.mid_game_strategy_pt):
        lines.append(f"  - {tip}")

    lines.append(f"\n{'LATE GAME' if lang == 'en' else 'FINAL DE JOGO'}:")
    for tip in (guide.late_game_focus_en if lang == "en" else guide.late_game_focus_pt):
        lines.append(f"  - {tip}")

    return "\n".join(lines)
