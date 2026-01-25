"""
Pokemon Abilities Database - Categorized abilities for deck building filters

This module contains:
- Ability categories with descriptions
- Pokemon cards organized by their abilities
- Search and filter functions for deck building
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AbilityCategory(str, Enum):
    """Categories of Pokemon abilities for filtering."""
    # Defensive abilities
    SAFEGUARD = "safeguard"           # Prevents damage from ex/V Pokemon
    BENCH_BARRIER = "bench_barrier"    # Protects benched Pokemon
    DAMAGE_REDUCTION = "damage_reduction"  # Reduces incoming damage
    TYPE_IMMUNITY = "type_immunity"    # Immune to certain types
    EFFECT_BLOCK = "effect_block"      # Blocks effects of attacks

    # Offensive abilities
    DAMAGE_BOOST = "damage_boost"      # Increases attack damage
    SPREAD_DAMAGE = "spread_damage"    # Damages multiple Pokemon
    SNIPE = "snipe"                    # Hits benched Pokemon
    EXTRA_PRIZE = "extra_prize"        # Takes extra prizes

    # Energy abilities
    ENERGY_ACCEL = "energy_accel"      # Accelerates energy attachment
    ENERGY_TRANSFER = "energy_transfer"  # Moves energy between Pokemon
    ENERGY_DENIAL = "energy_denial"    # Removes opponent's energy
    FREE_RETREAT = "free_retreat"      # Reduces/removes retreat cost

    # Draw/Search abilities
    DRAW_POWER = "draw_power"          # Draws cards
    SEARCH = "search"                  # Searches deck for cards
    RECOVERY = "recovery"              # Recovers cards from discard

    # Setup abilities
    EVOLUTION_SUPPORT = "evolution_support"  # Helps evolution
    POKEMON_SEARCH = "pokemon_search"  # Searches for Pokemon
    ITEM_LOCK = "item_lock"            # Prevents item usage
    ABILITY_LOCK = "ability_lock"      # Prevents abilities

    # Utility abilities
    SWITCHING = "switching"            # Switches Pokemon
    HEALING = "healing"                # Heals damage
    HAND_DISRUPTION = "hand_disruption"  # Disrupts opponent's hand
    MILL = "mill"                      # Discards from deck

    # Special mechanics
    TERA = "tera"                      # Tera Pokemon mechanic
    MEGA = "mega"                      # Mega Evolution mechanic
    VSTAR_POWER = "vstar_power"        # VSTAR Power abilities
    ANCIENT = "ancient"                # Ancient trait
    FUTURE = "future"                  # Future trait


@dataclass
class PokemonAbility:
    """Represents a Pokemon's ability."""
    name: str
    name_pt: str
    effect_en: str
    effect_pt: str
    category: AbilityCategory


@dataclass
class PokemonCard:
    """Represents a Pokemon card with its abilities."""
    name_en: str
    name_pt: str
    set_code: str
    set_number: str
    hp: int
    energy_type: str
    stage: str  # Basic, Stage 1, Stage 2, V, VSTAR, VMAX, ex
    abilities: list[PokemonAbility] = field(default_factory=list)
    attack_categories: list[AbilityCategory] = field(default_factory=list)
    weakness: Optional[str] = None
    resistance: Optional[str] = None
    retreat_cost: int = 0
    regulation_mark: str = "H"
    is_ex: bool = False
    is_tera: bool = False
    is_mega: bool = False


# =============================================================================
# POKEMON CARDS DATABASE - Organized by ability categories
# =============================================================================

POKEMON_DATABASE: dict[str, PokemonCard] = {}

# -----------------------------------------------------------------------------
# SAFEGUARD POKEMON - Prevents damage from ex/V Pokemon
# -----------------------------------------------------------------------------

POKEMON_DATABASE["miltank_asr_126"] = PokemonCard(
    name_en="Miltank",
    name_pt="Miltank",
    set_code="ASR",
    set_number="126",
    hp=110,
    energy_type="Colorless",
    stage="Basic",
    abilities=[
        PokemonAbility(
            name="Miracle Body",
            name_pt="Corpo Milagroso",
            effect_en="Prevent all damage done to this Pokemon by attacks from your opponent's Pokemon V.",
            effect_pt="Previna todo o dano causado a este Pokemon por ataques dos Pokemon V do oponente.",
            category=AbilityCategory.SAFEGUARD
        )
    ],
    weakness="Fighting",
    retreat_cost=2,
    regulation_mark="F"
)

POKEMON_DATABASE["mimikyu_pal_97"] = PokemonCard(
    name_en="Mimikyu",
    name_pt="Mimikyu",
    set_code="PAL",
    set_number="97",
    hp=70,
    energy_type="Psychic",
    stage="Basic",
    abilities=[
        PokemonAbility(
            name="Safeguard",
            name_pt="Salvaguarda",
            effect_en="Prevent all damage done to this Pokemon by attacks from your opponent's Pokemon ex and Pokemon V.",
            effect_pt="Previna todo o dano causado a este Pokemon por ataques dos Pokemon ex e Pokemon V do oponente.",
            category=AbilityCategory.SAFEGUARD
        )
    ],
    weakness="Darkness",
    resistance="Fighting",
    retreat_cost=1,
    regulation_mark="H"
)

POKEMON_DATABASE["eiscue_pal_48"] = PokemonCard(
    name_en="Eiscue",
    name_pt="Eiscue",
    set_code="PAL",
    set_number="48",
    hp=120,
    energy_type="Water",
    stage="Basic",
    abilities=[
        PokemonAbility(
            name="Ice Face",
            name_pt="Cara de Gelo",
            effect_en="If this Pokemon has full HP, it takes 90 less damage from attacks.",
            effect_pt="Se este Pokemon tiver HP cheio, ele recebe 90 menos de dano de ataques.",
            category=AbilityCategory.DAMAGE_REDUCTION
        )
    ],
    attack_categories=[AbilityCategory.SNIPE],
    weakness="Metal",
    retreat_cost=2,
    regulation_mark="H"
)

# -----------------------------------------------------------------------------
# BENCH BARRIER POKEMON - Protects benched Pokemon
# -----------------------------------------------------------------------------

POKEMON_DATABASE["manaphy_brs_41"] = PokemonCard(
    name_en="Manaphy",
    name_pt="Manaphy",
    set_code="BRS",
    set_number="41",
    hp=70,
    energy_type="Water",
    stage="Basic",
    abilities=[
        PokemonAbility(
            name="Wave Veil",
            name_pt="Veu de Onda",
            effect_en="Prevent all damage done to your Benched Pokemon by attacks from your opponent's Pokemon.",
            effect_pt="Previna todo o dano causado aos seus Pokemon no Banco por ataques dos Pokemon do oponente.",
            category=AbilityCategory.BENCH_BARRIER
        )
    ],
    weakness="Lightning",
    retreat_cost=1,
    regulation_mark="F"
)

POKEMON_DATABASE["jirachi_par_126"] = PokemonCard(
    name_en="Jirachi",
    name_pt="Jirachi",
    set_code="PAR",
    set_number="126",
    hp=70,
    energy_type="Psychic",
    stage="Basic",
    abilities=[
        PokemonAbility(
            name="Stellar Veil",
            name_pt="Veu Estelar",
            effect_en="Prevent all effects of attacks from your opponent's Pokemon done to your Benched Pokemon.",
            effect_pt="Previna todos os efeitos de ataques dos Pokemon do oponente feitos aos seus Pokemon no Banco.",
            category=AbilityCategory.BENCH_BARRIER
        )
    ],
    weakness="Darkness",
    resistance="Fighting",
    retreat_cost=1,
    regulation_mark="H"
)

# -----------------------------------------------------------------------------
# DRAW POWER POKEMON - Draws cards
# -----------------------------------------------------------------------------

POKEMON_DATABASE["genesect_v_fsi_185"] = PokemonCard(
    name_en="Genesect V",
    name_pt="Genesect V",
    set_code="FSI",
    set_number="185",
    hp=190,
    energy_type="Metal",
    stage="Basic V",
    abilities=[
        PokemonAbility(
            name="Fusion Strike System",
            name_pt="Sistema Golpe Fusao",
            effect_en="Once during your turn, you may draw cards until you have as many cards in your hand as you have Fusion Strike Pokemon in play.",
            effect_pt="Uma vez durante seu turno, voce pode comprar cartas ate ter tantas cartas na mao quanto Pokemon Golpe Fusao voce tem em jogo.",
            category=AbilityCategory.DRAW_POWER
        )
    ],
    weakness="Fire",
    resistance="Grass",
    retreat_cost=2,
    regulation_mark="E"
)

POKEMON_DATABASE["kirlia_svi_68"] = PokemonCard(
    name_en="Kirlia",
    name_pt="Kirlia",
    set_code="SVI",
    set_number="68",
    hp=80,
    energy_type="Psychic",
    stage="Stage 1",
    abilities=[
        PokemonAbility(
            name="Refinement",
            name_pt="Refinamento",
            effect_en="Once during your turn, you may discard a card from your hand. If you do, draw 2 cards.",
            effect_pt="Uma vez durante seu turno, voce pode descartar uma carta da sua mao. Se fizer isso, compre 2 cartas.",
            category=AbilityCategory.DRAW_POWER
        )
    ],
    weakness="Metal",
    resistance="Fighting",
    retreat_cost=1,
    regulation_mark="H"
)

POKEMON_DATABASE["bidoof_cro_111"] = PokemonCard(
    name_en="Bidoof",
    name_pt="Bidoof",
    set_code="CRO",
    set_number="111",
    hp=60,
    energy_type="Colorless",
    stage="Basic",
    abilities=[
        PokemonAbility(
            name="Carefree Countenance",
            name_pt="Semblante Despreocupado",
            effect_en="If this Pokemon is in the Active Spot, it takes 60 less damage from attacks.",
            effect_pt="Se este Pokemon estiver no Ponto Ativo, ele recebe 60 menos de dano de ataques.",
            category=AbilityCategory.DAMAGE_REDUCTION
        )
    ],
    weakness="Fighting",
    retreat_cost=1,
    regulation_mark="H"
)

POKEMON_DATABASE["bibarel_brs_121"] = PokemonCard(
    name_en="Bibarel",
    name_pt="Bibarel",
    set_code="BRS",
    set_number="121",
    hp=120,
    energy_type="Colorless",
    stage="Stage 1",
    abilities=[
        PokemonAbility(
            name="Industrious Incisors",
            name_pt="Incisivos Industriosos",
            effect_en="Once during your turn, you may draw cards until you have 5 cards in your hand.",
            effect_pt="Uma vez durante seu turno, voce pode comprar cartas ate ter 5 cartas na sua mao.",
            category=AbilityCategory.DRAW_POWER
        )
    ],
    weakness="Fighting",
    retreat_cost=2,
    regulation_mark="F"
)

# -----------------------------------------------------------------------------
# ENERGY ACCELERATION POKEMON
# -----------------------------------------------------------------------------

POKEMON_DATABASE["gardevoir_ex_svi_86"] = PokemonCard(
    name_en="Gardevoir ex",
    name_pt="Gardevoir ex",
    set_code="SVI",
    set_number="86",
    hp=310,
    energy_type="Psychic",
    stage="Stage 2 ex",
    abilities=[
        PokemonAbility(
            name="Psychic Embrace",
            name_pt="Abrace Psiquico",
            effect_en="As often as you like during your turn, you may attach a Basic Psychic Energy card from your discard pile to 1 of your Psychic Pokemon. If you attached Energy to a Pokemon in this way, put 2 damage counters on that Pokemon.",
            effect_pt="Quantas vezes quiser durante seu turno, voce pode anexar uma carta de Energia Psiquica Basica da sua pilha de descarte a 1 dos seus Pokemon Psiquicos. Se anexou Energia a um Pokemon dessa forma, coloque 2 contadores de dano nesse Pokemon.",
            category=AbilityCategory.ENERGY_ACCEL
        )
    ],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="Metal",
    resistance="Fighting",
    retreat_cost=2,
    regulation_mark="H",
    is_ex=True
)

POKEMON_DATABASE["ogerpon_teal_twm_25"] = PokemonCard(
    name_en="Ogerpon ex (Teal Mask)",
    name_pt="Ogerpon ex (Mascara Turquesa)",
    set_code="TWM",
    set_number="25",
    hp=210,
    energy_type="Grass",
    stage="Basic ex",
    abilities=[
        PokemonAbility(
            name="Teal Dance",
            name_pt="Danca Turquesa",
            effect_en="Once during your turn, you may attach a Basic Grass Energy card from your hand to this Pokemon. If you do, draw a card.",
            effect_pt="Uma vez durante seu turno, voce pode anexar uma carta de Energia Planta Basica da sua mao a este Pokemon. Se fizer isso, compre uma carta.",
            category=AbilityCategory.ENERGY_ACCEL
        )
    ],
    weakness="Fire",
    retreat_cost=1,
    regulation_mark="H",
    is_ex=True,
    is_tera=True
)

POKEMON_DATABASE["raging_bolt_ex_twm_123"] = PokemonCard(
    name_en="Raging Bolt ex",
    name_pt="Raging Bolt ex",
    set_code="TWM",
    set_number="123",
    hp=240,
    energy_type="Dragon",
    stage="Basic ex",
    abilities=[],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="None",
    retreat_cost=2,
    regulation_mark="H",
    is_ex=True
)

POKEMON_DATABASE["charizard_ex_obf_125"] = PokemonCard(
    name_en="Charizard ex",
    name_pt="Charizard ex",
    set_code="OBF",
    set_number="125",
    hp=330,
    energy_type="Fire",
    stage="Stage 2 ex",
    abilities=[
        PokemonAbility(
            name="Infernal Reign",
            name_pt="Reinado Infernal",
            effect_en="When you play this Pokemon from your hand to evolve 1 of your Pokemon during your turn, you may search your deck for up to 3 Basic Fire Energy cards and attach them to your Pokemon in any way you like. Then, shuffle your deck.",
            effect_pt="Quando voce joga este Pokemon da sua mao para evoluir 1 dos seus Pokemon durante seu turno, voce pode procurar no seu baralho por ate 3 cartas de Energia Fogo Basica e anexa-las aos seus Pokemon da forma que quiser. Depois, embaralhe seu baralho.",
            category=AbilityCategory.ENERGY_ACCEL
        )
    ],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="Water",
    retreat_cost=2,
    regulation_mark="H",
    is_ex=True
)

# -----------------------------------------------------------------------------
# SPREAD DAMAGE POKEMON
# -----------------------------------------------------------------------------

POKEMON_DATABASE["dragapult_ex_twm_130"] = PokemonCard(
    name_en="Dragapult ex",
    name_pt="Dragapult ex",
    set_code="TWM",
    set_number="130",
    hp=320,
    energy_type="Dragon",
    stage="Stage 2 ex",
    abilities=[],
    attack_categories=[AbilityCategory.SPREAD_DAMAGE],
    weakness="None",
    retreat_cost=1,
    regulation_mark="H",
    is_ex=True,
    is_tera=True
)

POKEMON_DATABASE["froslass_twm_53"] = PokemonCard(
    name_en="Froslass",
    name_pt="Froslass",
    set_code="TWM",
    set_number="53",
    hp=100,
    energy_type="Water",
    stage="Stage 1",
    abilities=[
        PokemonAbility(
            name="Chilling Mist",
            name_pt="Nevoa Gelada",
            effect_en="Once during your turn, if this Pokemon is in the Active Spot, you may put 2 damage counters on each of your opponent's Pokemon that has an Ability.",
            effect_pt="Uma vez durante seu turno, se este Pokemon estiver no Ponto Ativo, voce pode colocar 2 contadores de dano em cada Pokemon do oponente que tenha uma Habilidade.",
            category=AbilityCategory.SPREAD_DAMAGE
        )
    ],
    weakness="Metal",
    retreat_cost=1,
    regulation_mark="H"
)

POKEMON_DATABASE["munkidori_twm_95"] = PokemonCard(
    name_en="Munkidori",
    name_pt="Munkidori",
    set_code="TWM",
    set_number="95",
    hp=110,
    energy_type="Darkness",
    stage="Basic",
    abilities=[
        PokemonAbility(
            name="Adrena-Brain",
            name_pt="Cerebro-Adrena",
            effect_en="Once during your turn, you may move up to 3 damage counters from 1 of your Pokemon to 1 of your opponent's Pokemon.",
            effect_pt="Uma vez durante seu turno, voce pode mover ate 3 contadores de dano de 1 dos seus Pokemon para 1 dos Pokemon do oponente.",
            category=AbilityCategory.SPREAD_DAMAGE
        )
    ],
    weakness="Fighting",
    retreat_cost=1,
    regulation_mark="H"
)

# -----------------------------------------------------------------------------
# SWITCHING/PIVOTING POKEMON
# -----------------------------------------------------------------------------

POKEMON_DATABASE["pidgeot_ex_obf_164"] = PokemonCard(
    name_en="Pidgeot ex",
    name_pt="Pidgeot ex",
    set_code="OBF",
    set_number="164",
    hp=280,
    energy_type="Colorless",
    stage="Stage 2 ex",
    abilities=[
        PokemonAbility(
            name="Quick Search",
            name_pt="Busca Rapida",
            effect_en="Once during your turn, you may search your deck for a card and put it into your hand. Then, shuffle your deck.",
            effect_pt="Uma vez durante seu turno, voce pode procurar no seu baralho por uma carta e coloca-la na sua mao. Depois, embaralhe seu baralho.",
            category=AbilityCategory.SEARCH
        )
    ],
    weakness="Lightning",
    resistance="Fighting",
    retreat_cost=0,
    regulation_mark="H",
    is_ex=True
)

POKEMON_DATABASE["mega_dragonite_ex_asc_142"] = PokemonCard(
    name_en="Mega Dragonite ex",
    name_pt="Mega Dragonite ex",
    set_code="ASC",
    set_number="142",
    hp=350,
    energy_type="Dragon",
    stage="Mega ex",
    abilities=[
        PokemonAbility(
            name="Sky Transport",
            name_pt="Transporte Celeste",
            effect_en="Once during your turn, you may switch this Pokemon with 1 of your Benched Pokemon.",
            effect_pt="Uma vez durante seu turno, voce pode trocar este Pokemon com 1 dos seus Pokemon no Banco.",
            category=AbilityCategory.SWITCHING
        )
    ],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="Fairy",
    retreat_cost=2,
    regulation_mark="I",
    is_ex=True,
    is_mega=True
)

# -----------------------------------------------------------------------------
# MEGA POKEMON FROM ASCENDED HEROES
# -----------------------------------------------------------------------------

POKEMON_DATABASE["mega_charizard_y_ex_asc_22"] = PokemonCard(
    name_en="Mega Charizard Y ex",
    name_pt="Mega Charizard Y ex",
    set_code="ASC",
    set_number="22",
    hp=360,
    energy_type="Fire",
    stage="Mega ex",
    abilities=[],
    attack_categories=[AbilityCategory.DAMAGE_BOOST, AbilityCategory.SNIPE],
    weakness="Water",
    retreat_cost=2,
    regulation_mark="I",
    is_ex=True,
    is_mega=True
)

POKEMON_DATABASE["mega_gardevoir_ex_asc_79"] = PokemonCard(
    name_en="Mega Gardevoir ex",
    name_pt="Mega Gardevoir ex",
    set_code="ASC",
    set_number="79",
    hp=340,
    energy_type="Psychic",
    stage="Mega ex",
    abilities=[],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="Metal",
    resistance="Fighting",
    retreat_cost=2,
    regulation_mark="I",
    is_ex=True,
    is_mega=True
)

POKEMON_DATABASE["mega_froslass_ex_asc_52"] = PokemonCard(
    name_en="Mega Froslass ex",
    name_pt="Mega Froslass ex",
    set_code="ASC",
    set_number="52",
    hp=310,
    energy_type="Water",
    stage="Mega ex",
    abilities=[
        PokemonAbility(
            name="Frozen Veil",
            name_pt="Veu Congelado",
            effect_en="Once during your turn, you may put 1 damage counter on each of your opponent's Pokemon.",
            effect_pt="Uma vez durante seu turno, voce pode colocar 1 contador de dano em cada Pokemon do oponente.",
            category=AbilityCategory.SPREAD_DAMAGE
        )
    ],
    attack_categories=[AbilityCategory.SPREAD_DAMAGE],
    weakness="Metal",
    retreat_cost=1,
    regulation_mark="I",
    is_ex=True,
    is_mega=True
)

POKEMON_DATABASE["mega_lucario_ex_asc_108"] = PokemonCard(
    name_en="Mega Lucario ex",
    name_pt="Mega Lucario ex",
    set_code="ASC",
    set_number="108",
    hp=340,
    energy_type="Fighting",
    stage="Mega ex",
    abilities=[
        PokemonAbility(
            name="Aura Force",
            name_pt="Forca da Aura",
            effect_en="Attacks from this Pokemon do 30 more damage to your opponent's Active Pokemon.",
            effect_pt="Ataques deste Pokemon causam 30 de dano a mais ao Pokemon Ativo do oponente.",
            category=AbilityCategory.DAMAGE_BOOST
        )
    ],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="Psychic",
    retreat_cost=2,
    regulation_mark="I",
    is_ex=True,
    is_mega=True
)

POKEMON_DATABASE["mega_hawlucha_ex_asc_115"] = PokemonCard(
    name_en="Mega Hawlucha ex",
    name_pt="Mega Hawlucha ex",
    set_code="ASC",
    set_number="115",
    hp=300,
    energy_type="Fighting",
    stage="Mega ex",
    abilities=[
        PokemonAbility(
            name="Masked Protector",
            name_pt="Protetor Mascarado",
            effect_en="As long as this Pokemon has any Energy attached, it takes 30 less damage from attacks.",
            effect_pt="Enquanto este Pokemon tiver alguma Energia anexada, ele recebe 30 menos de dano de ataques.",
            category=AbilityCategory.DAMAGE_REDUCTION
        )
    ],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="Psychic",
    retreat_cost=1,
    regulation_mark="I",
    is_ex=True,
    is_mega=True
)

# -----------------------------------------------------------------------------
# GHOLDENGO LINE
# -----------------------------------------------------------------------------

POKEMON_DATABASE["gimmighoul_pre_86"] = PokemonCard(
    name_en="Gimmighoul",
    name_pt="Gimmighoul",
    set_code="PRE",
    set_number="86",
    hp=70,
    energy_type="Metal",
    stage="Basic",
    abilities=[],
    weakness="Fire",
    resistance="Grass",
    retreat_cost=2,
    regulation_mark="H"
)

POKEMON_DATABASE["gholdengo_ex_pre_164"] = PokemonCard(
    name_en="Gholdengo ex",
    name_pt="Gholdengo ex",
    set_code="PRE",
    set_number="164",
    hp=260,
    energy_type="Metal",
    stage="Stage 1 ex",
    abilities=[
        PokemonAbility(
            name="Coin Bonus",
            name_pt="Bonus de Moeda",
            effect_en="Once during your turn, when you play a Supporter card from your hand, you may draw 1 card.",
            effect_pt="Uma vez durante seu turno, quando voce joga uma carta Supporter da sua mao, voce pode comprar 1 carta.",
            category=AbilityCategory.DRAW_POWER
        )
    ],
    attack_categories=[AbilityCategory.DAMAGE_BOOST],
    weakness="Fire",
    resistance="Grass",
    retreat_cost=2,
    regulation_mark="H",
    is_ex=True
)

# -----------------------------------------------------------------------------
# ABILITY LOCK POKEMON
# -----------------------------------------------------------------------------

POKEMON_DATABASE["iron_thorns_ex_par_62"] = PokemonCard(
    name_en="Iron Thorns ex",
    name_pt="Iron Thorns ex",
    set_code="PAR",
    set_number="62",
    hp=250,
    energy_type="Lightning",
    stage="Basic ex",
    abilities=[
        PokemonAbility(
            name="Ability Shield",
            name_pt="Escudo de Habilidade",
            effect_en="Prevent all effects of Abilities of your opponent's Pokemon done to this Pokemon.",
            effect_pt="Previna todos os efeitos de Habilidades dos Pokemon do oponente feitos a este Pokemon.",
            category=AbilityCategory.EFFECT_BLOCK
        )
    ],
    weakness="Fighting",
    retreat_cost=3,
    regulation_mark="H",
    is_ex=True
)


# =============================================================================
# ABILITY CATEGORY DESCRIPTIONS
# =============================================================================

ABILITY_DESCRIPTIONS: dict[AbilityCategory, dict[str, str]] = {
    AbilityCategory.SAFEGUARD: {
        "en": "Prevents damage from Pokemon ex/V - great wall against big attackers",
        "pt": "Previne dano de Pokemon ex/V - otima parede contra atacantes fortes"
    },
    AbilityCategory.BENCH_BARRIER: {
        "en": "Protects benched Pokemon from snipe damage - essential vs spread decks",
        "pt": "Protege Pokemon no banco de snipe - essencial contra decks de spread"
    },
    AbilityCategory.DAMAGE_REDUCTION: {
        "en": "Reduces incoming damage - improves survivability",
        "pt": "Reduz dano recebido - melhora sobrevivencia"
    },
    AbilityCategory.ENERGY_ACCEL: {
        "en": "Accelerates energy attachment - speeds up attacks",
        "pt": "Acelera anexo de energia - acelera ataques"
    },
    AbilityCategory.DRAW_POWER: {
        "en": "Draws extra cards - improves consistency",
        "pt": "Compra cartas extras - melhora consistencia"
    },
    AbilityCategory.SEARCH: {
        "en": "Searches deck for specific cards - ultimate consistency",
        "pt": "Busca cartas especificas no deck - consistencia maxima"
    },
    AbilityCategory.SPREAD_DAMAGE: {
        "en": "Damages multiple Pokemon - chip damage strategy",
        "pt": "Causa dano a multiplos Pokemon - estrategia de dano acumulado"
    },
    AbilityCategory.SNIPE: {
        "en": "Targets benched Pokemon directly - bypasses walls",
        "pt": "Ataca Pokemon no banco diretamente - ignora paredes"
    },
    AbilityCategory.SWITCHING: {
        "en": "Switches Pokemon positions - enables pivoting",
        "pt": "Troca posicao de Pokemon - permite pivoteamento"
    },
    AbilityCategory.MEGA: {
        "en": "Mega Evolution Pokemon - powerful Stage 2 attackers",
        "pt": "Pokemon Mega Evolucao - atacantes Stage 2 poderosos"
    },
    AbilityCategory.TERA: {
        "en": "Tera Pokemon - modified type/weakness mechanics",
        "pt": "Pokemon Tera - mecanicas modificadas de tipo/fraqueza"
    },
}


# =============================================================================
# SEARCH AND FILTER FUNCTIONS
# =============================================================================

def get_pokemon_by_ability(category: AbilityCategory) -> list[PokemonCard]:
    """Get all Pokemon with a specific ability category."""
    results = []
    for pokemon in POKEMON_DATABASE.values():
        for ability in pokemon.abilities:
            if ability.category == category:
                results.append(pokemon)
                break
        # Also check attack categories
        if category in pokemon.attack_categories and pokemon not in results:
            results.append(pokemon)
    return results


def get_pokemon_by_type(energy_type: str) -> list[PokemonCard]:
    """Get all Pokemon of a specific energy type."""
    return [p for p in POKEMON_DATABASE.values() if p.energy_type.lower() == energy_type.lower()]


def get_pokemon_by_stage(stage: str) -> list[PokemonCard]:
    """Get all Pokemon of a specific stage."""
    return [p for p in POKEMON_DATABASE.values() if stage.lower() in p.stage.lower()]


def get_ex_pokemon() -> list[PokemonCard]:
    """Get all Pokemon ex."""
    return [p for p in POKEMON_DATABASE.values() if p.is_ex]


def get_mega_pokemon() -> list[PokemonCard]:
    """Get all Mega Pokemon."""
    return [p for p in POKEMON_DATABASE.values() if p.is_mega]


def get_tera_pokemon() -> list[PokemonCard]:
    """Get all Tera Pokemon."""
    return [p for p in POKEMON_DATABASE.values() if p.is_tera]


def get_legal_pokemon(regulation_marks: list[str] = None) -> list[PokemonCard]:
    """Get all legal Pokemon (H, I or later by default)."""
    if regulation_marks is None:
        regulation_marks = ["H", "I", "J"]
    return [p for p in POKEMON_DATABASE.values() if p.regulation_mark in regulation_marks]


def search_pokemon(
    name: str = None,
    energy_type: str = None,
    ability_category: AbilityCategory = None,
    stage: str = None,
    min_hp: int = None,
    max_hp: int = None,
    is_ex: bool = None,
    is_mega: bool = None,
    is_tera: bool = None,
    legal_only: bool = True
) -> list[PokemonCard]:
    """Search Pokemon with multiple filters."""
    results = list(POKEMON_DATABASE.values())

    if legal_only:
        results = [p for p in results if p.regulation_mark in ["H", "I", "J"]]

    if name:
        results = [p for p in results if name.lower() in p.name_en.lower() or name.lower() in p.name_pt.lower()]

    if energy_type:
        results = [p for p in results if p.energy_type.lower() == energy_type.lower()]

    if ability_category:
        filtered = []
        for p in results:
            has_ability = any(a.category == ability_category for a in p.abilities)
            has_attack = ability_category in p.attack_categories
            if has_ability or has_attack:
                filtered.append(p)
        results = filtered

    if stage:
        results = [p for p in results if stage.lower() in p.stage.lower()]

    if min_hp is not None:
        results = [p for p in results if p.hp >= min_hp]

    if max_hp is not None:
        results = [p for p in results if p.hp <= max_hp]

    if is_ex is not None:
        results = [p for p in results if p.is_ex == is_ex]

    if is_mega is not None:
        results = [p for p in results if p.is_mega == is_mega]

    if is_tera is not None:
        results = [p for p in results if p.is_tera == is_tera]

    return results


def get_all_ability_categories() -> list[tuple[AbilityCategory, str, str]]:
    """Get all ability categories with their descriptions."""
    return [
        (cat, desc.get("en", ""), desc.get("pt", ""))
        for cat, desc in ABILITY_DESCRIPTIONS.items()
    ]


def get_counters_for_ability(ability: AbilityCategory) -> list[PokemonCard]:
    """Get Pokemon that counter a specific ability category."""
    counters = {
        AbilityCategory.SPREAD_DAMAGE: [AbilityCategory.BENCH_BARRIER],
        AbilityCategory.SNIPE: [AbilityCategory.BENCH_BARRIER],
        AbilityCategory.DAMAGE_BOOST: [AbilityCategory.DAMAGE_REDUCTION, AbilityCategory.SAFEGUARD],
        AbilityCategory.ENERGY_ACCEL: [AbilityCategory.ENERGY_DENIAL],
        AbilityCategory.DRAW_POWER: [AbilityCategory.HAND_DISRUPTION],
        AbilityCategory.ABILITY_LOCK: [AbilityCategory.EFFECT_BLOCK],
    }

    counter_categories = counters.get(ability, [])
    results = []
    for cat in counter_categories:
        results.extend(get_pokemon_by_ability(cat))
    return list(set(results))


# =============================================================================
# DECK ARCHETYPE TEMPLATES
# =============================================================================

DECK_TEMPLATES: dict[str, dict] = {
    "control": {
        "name_en": "Control/Stall",
        "name_pt": "Controle/Stall",
        "recommended_abilities": [
            AbilityCategory.SAFEGUARD,
            AbilityCategory.DAMAGE_REDUCTION,
            AbilityCategory.HAND_DISRUPTION,
            AbilityCategory.ITEM_LOCK
        ],
        "description_en": "Focus on disrupting opponent while being hard to KO",
        "description_pt": "Foca em atrapalhar o oponente enquanto e dificil de nocautear"
    },
    "aggro": {
        "name_en": "Aggro/Rush",
        "name_pt": "Aggro/Rush",
        "recommended_abilities": [
            AbilityCategory.ENERGY_ACCEL,
            AbilityCategory.DAMAGE_BOOST,
            AbilityCategory.FREE_RETREAT
        ],
        "description_en": "Fast damage output to take prizes quickly",
        "description_pt": "Dano rapido para pegar premios rapidamente"
    },
    "spread": {
        "name_en": "Spread Damage",
        "name_pt": "Dano Espalhado",
        "recommended_abilities": [
            AbilityCategory.SPREAD_DAMAGE,
            AbilityCategory.SNIPE,
            AbilityCategory.DAMAGE_BOOST
        ],
        "description_en": "Chip damage across the board for multi-KOs",
        "description_pt": "Dano acumulado no campo para multiplos KOs"
    },
    "combo": {
        "name_en": "Combo/Engine",
        "name_pt": "Combo/Engine",
        "recommended_abilities": [
            AbilityCategory.DRAW_POWER,
            AbilityCategory.SEARCH,
            AbilityCategory.ENERGY_ACCEL
        ],
        "description_en": "Consistent setup with powerful engine cards",
        "description_pt": "Setup consistente com cartas de engine poderosas"
    },
}
