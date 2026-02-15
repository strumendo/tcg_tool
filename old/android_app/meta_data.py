"""
Meta Database for Pokemon TCG Mobile App
Simplified version with all data included
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Language(str, Enum):
    EN = "en"
    PT = "pt"


@dataclass
class CardEntry:
    """A card entry in a deck list."""
    quantity: int
    name_en: str
    name_pt: str
    set_code: str
    set_number: str
    card_type: str

    def get_name(self, lang: Language = Language.EN) -> str:
        return self.name_pt if lang == Language.PT else self.name_en


@dataclass
class MetaDeck:
    """A meta deck with complete card list."""
    id: str
    name_en: str
    name_pt: str
    tier: int
    description_en: str
    description_pt: str
    strategy_en: str
    strategy_pt: str
    difficulty: str
    cards: list = field(default_factory=list)
    strengths_en: list = field(default_factory=list)
    strengths_pt: list = field(default_factory=list)
    weaknesses_en: list = field(default_factory=list)
    weaknesses_pt: list = field(default_factory=list)
    key_pokemon: list = field(default_factory=list)
    energy_types: list = field(default_factory=list)
    meta_share: float = 0.0

    def get_name(self, lang: Language = Language.EN) -> str:
        return self.name_pt if lang == Language.PT else self.name_en

    def get_description(self, lang: Language = Language.EN) -> str:
        return self.description_pt if lang == Language.PT else self.description_en

    def get_strategy(self, lang: Language = Language.EN) -> str:
        return self.strategy_pt if lang == Language.PT else self.strategy_en

    def get_strengths(self, lang: Language = Language.EN) -> list:
        return self.strengths_pt if lang == Language.PT else self.strengths_en

    def get_weaknesses(self, lang: Language = Language.EN) -> list:
        return self.weaknesses_pt if lang == Language.PT else self.weaknesses_en

    def get_pokemon(self) -> list:
        return [c for c in self.cards if c.card_type == "pokemon"]

    def get_trainers(self) -> list:
        return [c for c in self.cards if c.card_type == "trainer"]

    def get_energy(self) -> list:
        return [c for c in self.cards if c.card_type == "energy"]

    def total_cards(self) -> int:
        return sum(c.quantity for c in self.cards)


@dataclass
class MatchupData:
    """Matchup data between two decks."""
    deck_a_id: str
    deck_b_id: str
    win_rate_a: float
    notes_en: str = ""
    notes_pt: str = ""

    @property
    def win_rate_b(self) -> float:
        return 100 - self.win_rate_a

    def get_notes(self, lang: Language = Language.EN) -> str:
        return self.notes_pt if lang == Language.PT else self.notes_en


# =============================================================================
# TOP 8 META DECKS
# =============================================================================

META_DECKS = {}

# 1. GHOLDENGO EX
META_DECKS["gholdengo"] = MetaDeck(
    id="gholdengo",
    name_en="Gholdengo ex",
    name_pt="Gholdengo ex",
    tier=1,
    description_en="The #1 deck with incredible draw power and infinite damage potential",
    description_pt="O deck #1 com poder de compra incrivel e potencial de dano infinito",
    strategy_en="Use Gholdengo ex's Coin Bonus ability to draw cards. Accumulate Basic Energy, then use Make It Rain for 50 damage per energy discarded.",
    strategy_pt="Use a habilidade Coin Bonus do Gholdengo ex para comprar cartas. Acumule Energias Basicas e use Make It Rain para 50 de dano por energia descartada.",
    difficulty="Intermediate",
    meta_share=26.49,
    key_pokemon=["Gholdengo ex", "Genesect ex", "Gimmighoul"],
    energy_types=["Metal", "Basic"],
    strengths_en=["Highest damage ceiling", "Excellent draw power", "Can OHKO any Pokemon", "Consistent setup"],
    strengths_pt=["Maior teto de dano", "Excelente poder de compra", "Pode nocautear qualquer Pokemon", "Setup consistente"],
    weaknesses_en=["Weak to Fire", "Needs many energy", "Struggles vs disruption"],
    weaknesses_pt=["Fraco contra Fogo", "Precisa de muitas energias", "Dificuldade contra disrupcao"],
    cards=[
        CardEntry(4, "Gimmighoul", "Gimmighoul", "PRE", "86", "pokemon"),
        CardEntry(3, "Gholdengo ex", "Gholdengo ex", "PRE", "164", "pokemon"),
        CardEntry(2, "Genesect ex", "Genesect ex", "JTG", "51", "pokemon"),
        CardEntry(2, "Solrock", "Solrock", "MEV", "45", "pokemon"),
        CardEntry(2, "Lunatone", "Lunatone", "MEV", "46", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        CardEntry(4, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(1, "Ciphermaniac's Codebreaking", "Decifracao do Ciphermaniac", "TEF", "145", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(4, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(3, "Earthen Vessel", "Vaso de Barro", "PAR", "163", "trainer"),
        CardEntry(2, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "Superior Energy Retrieval", "Recuperacao de Energia Superior", "PAL", "189", "trainer"),
        CardEntry(1, "Precious Trolley", "Carrinho Precioso", "JTG", "69", "trainer"),
        CardEntry(1, "TM: Devolution", "MT: Devolucao", "PAR", "177", "trainer"),
        CardEntry(2, "Jamming Tower", "Torre de Interferencia", "TWM", "153", "trainer"),
        CardEntry(4, "Basic Metal Energy", "Energia Metal Basica", "SVE", "8", "energy"),
        CardEntry(4, "Basic Fighting Energy", "Energia Lutador Basica", "SVE", "6", "energy"),
        CardEntry(4, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
        CardEntry(3, "Basic Fire Energy", "Energia Fogo Basica", "SVE", "2", "energy"),
    ]
)

# 2. DRAGAPULT EX
META_DECKS["dragapult"] = MetaDeck(
    id="dragapult",
    name_en="Dragapult ex",
    name_pt="Dragapult ex",
    tier=1,
    description_en="Powerful spread damage deck with bench sniping and devolution",
    description_pt="Deck poderoso de dano espalhado com snipe de banco e devolucao",
    strategy_en="Use Phantom Dive for 200 damage + 6 spread counters. Munkidori redirects damage. TM Devolution KOs evolved Pokemon.",
    strategy_pt="Use Phantom Dive para 200 de dano + 6 contadores espalhados. Munkidori redireciona dano. MT Devolucao nocauteia evoluidos.",
    difficulty="Intermediate",
    meta_share=19.95,
    key_pokemon=["Dragapult ex", "Dreepy", "Munkidori"],
    energy_types=["Psychic", "Darkness"],
    strengths_en=["Excellent spread damage", "Multi-prize turns", "Strong vs evolution", "Good draw options"],
    strengths_pt=["Excelente dano espalhado", "Turnos de multiplos premios", "Forte vs evolucao", "Boas opcoes de compra"],
    weaknesses_en=["Weak to Darkness", "Setup can be disrupted", "Struggles vs single-prize"],
    weaknesses_pt=["Fraco contra Escuridao", "Setup pode ser interrompido", "Dificuldade vs premio unico"],
    cards=[
        CardEntry(4, "Dreepy", "Dreepy", "TWM", "88", "pokemon"),
        CardEntry(1, "Drakloak", "Drakloak", "TWM", "89", "pokemon"),
        CardEntry(3, "Dragapult ex", "Dragapult ex", "TWM", "130", "pokemon"),
        CardEntry(3, "Munkidori", "Munkidori", "TWM", "95", "pokemon"),
        CardEntry(1, "Latias ex", "Latias ex", "SSP", "76", "pokemon"),
        CardEntry(1, "Bloodmoon Ursaluna ex", "Ursaluna Lua Sangrenta ex", "TWM", "141", "pokemon"),
        CardEntry(1, "Maractus", "Maractus", "JTG", "8", "pokemon"),
        CardEntry(1, "Hawlucha", "Hawlucha", "PAR", "88", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(4, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(3, "Hilda", "Hilda", "JTG", "76", "trainer"),
        CardEntry(2, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(1, "Brock's Scouting", "Exploracao do Brock", "MEV", "56", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(4, "Buddy-Buddy Poffin", "Poffin Amigo-Amigo", "TEF", "144", "trainer"),
        CardEntry(3, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(2, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(2, "TM: Devolution", "MT: Devolucao", "PAR", "177", "trainer"),
        CardEntry(1, "Secret Box", "Caixa Secreta", "JTG", "71", "trainer"),
        CardEntry(6, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
        CardEntry(3, "Luminous Energy", "Energia Luminosa", "PAL", "191", "energy"),
    ]
)

# 3. GARDEVOIR EX
META_DECKS["gardevoir"] = MetaDeck(
    id="gardevoir",
    name_en="Gardevoir ex",
    name_pt="Gardevoir ex",
    tier=1,
    description_en="Long-running top deck with infinite energy acceleration and flexible attackers",
    description_pt="Deck de topo duradouro com aceleracao de energia infinita e atacantes flexiveis",
    strategy_en="Use Psychic Embrace to attach energy from discard. Multiple attackers like Mega Diancie ex, Clefairy ex provide coverage.",
    strategy_pt="Use Psychic Embrace para anexar energia do descarte. Atacantes como Mega Diancie ex, Clefairy ex fornecem cobertura.",
    difficulty="Advanced",
    meta_share=16.61,
    key_pokemon=["Gardevoir ex", "Ralts", "Kirlia", "Mega Diancie ex"],
    energy_types=["Psychic"],
    strengths_en=["Infinite energy acceleration", "Flexible attackers", "Strong vs Dragon", "Excellent recovery"],
    strengths_pt=["Aceleracao de energia infinita", "Atacantes flexiveis", "Forte vs Dragao", "Excelente recuperacao"],
    weaknesses_en=["Weak to Darkness", "Complex to pilot", "Self-damage from ability"],
    weaknesses_pt=["Fraco contra Escuridao", "Complexo de pilotar", "Auto-dano da habilidade"],
    cards=[
        CardEntry(4, "Ralts", "Ralts", "SVI", "67", "pokemon"),
        CardEntry(3, "Kirlia", "Kirlia", "SVI", "68", "pokemon"),
        CardEntry(2, "Gardevoir ex", "Gardevoir ex", "SVI", "86", "pokemon"),
        CardEntry(1, "Mega Gardevoir ex", "Mega Gardevoir ex", "MEV", "38", "pokemon"),
        CardEntry(1, "Mega Diancie ex", "Mega Diancie ex", "MEV", "40", "pokemon"),
        CardEntry(1, "Lillie's Clefairy ex", "Clefairy da Lillie ex", "JTG", "56", "pokemon"),
        CardEntry(1, "Scream Tail", "Cauda Gritante", "PAR", "86", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Munkidori", "Munkidori", "TWM", "95", "pokemon"),
        CardEntry(3, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(3, "Lillie's Determination", "Determinacao da Lillie", "JTG", "77", "trainer"),
        CardEntry(2, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(2, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(1, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(3, "Earthen Vessel", "Vaso de Barro", "PAR", "163", "trainer"),
        CardEntry(3, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(2, "TM: Evolution", "MT: Evolucao", "PAR", "178", "trainer"),
        CardEntry(1, "Buddy-Buddy Poffin", "Poffin Amigo-Amigo", "TEF", "144", "trainer"),
        CardEntry(1, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(1, "Secret Box", "Caixa Secreta", "JTG", "71", "trainer"),
        CardEntry(2, "Mystery Garden", "Jardim Misterioso", "MEV", "71", "trainer"),
        CardEntry(7, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
        CardEntry(4, "Basic Darkness Energy", "Energia Escuridao Basica", "SVE", "7", "energy"),
    ]
)

# 4. CHARIZARD EX
META_DECKS["charizard"] = MetaDeck(
    id="charizard",
    name_en="Charizard ex / Pidgeot ex",
    name_pt="Charizard ex / Pidgeot ex",
    tier=1,
    description_en="Classic powerhouse with excellent consistency and comeback potential",
    description_pt="Deck classico poderoso com excelente consistencia e potencial de virada",
    strategy_en="Set up Pidgeot ex for Quick Search. Charizard ex's Infernal Reign accelerates energy, Burning Darkness deals more damage as opponent takes prizes.",
    strategy_pt="Monte Pidgeot ex para Quick Search. Infernal Reign do Charizard ex acelera energia, Burning Darkness causa mais dano conforme o oponente pega premios.",
    difficulty="Beginner",
    meta_share=13.86,
    key_pokemon=["Charizard ex", "Charmander", "Pidgeot ex", "Pidgey"],
    energy_types=["Fire"],
    strengths_en=["Very consistent", "Strong comeback", "High damage", "Beginner-friendly"],
    strengths_pt=["Muito consistente", "Forte virada", "Alto dano", "Amigavel para iniciantes"],
    weaknesses_en=["Weak to Water", "Path shuts abilities", "Slow setup"],
    weaknesses_pt=["Fraco contra Agua", "Path desliga habilidades", "Setup lento"],
    cards=[
        CardEntry(4, "Charmander", "Charmander", "MEW", "4", "pokemon"),
        CardEntry(1, "Charmeleon", "Charmeleon", "OBF", "27", "pokemon"),
        CardEntry(3, "Charizard ex", "Charizard ex", "OBF", "125", "pokemon"),
        CardEntry(2, "Pidgey", "Pidgey", "OBF", "162", "pokemon"),
        CardEntry(2, "Pidgeot ex", "Pidgeot ex", "OBF", "164", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Rotom V", "Rotom V", "CRZ", "45", "pokemon"),
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(3, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(1, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(4, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(3, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(2, "Super Rod", "Super Vara", "PAL", "188", "trainer"),
        CardEntry(2, "Escape Rope", "Corda de Fuga", "BST", "125", "trainer"),
        CardEntry(1, "Pal Pad", "Bloco de Amigo", "SVI", "182", "trainer"),
        CardEntry(1, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(1, "Forest Seal Stone", "Pedra do Selo", "SIT", "156", "trainer"),
        CardEntry(2, "Artazon", "Artazon", "PAL", "171", "trainer"),
        CardEntry(8, "Basic Fire Energy", "Energia Fogo Basica", "SVE", "2", "energy"),
        CardEntry(2, "Luminous Energy", "Energia Luminosa", "PAL", "191", "energy"),
    ]
)

# 5. RAGING BOLT EX
META_DECKS["raging_bolt"] = MetaDeck(
    id="raging_bolt",
    name_en="Raging Bolt ex / Ogerpon ex",
    name_pt="Raging Bolt ex / Ogerpon ex",
    tier=1,
    description_en="Aggressive Ancient deck with turn-one knockout potential",
    description_pt="Deck Antigo agressivo com potencial de nocaute no primeiro turno",
    strategy_en="Teal Mask Ogerpon ex's Teal Dance attaches energy and draws. Professor Sada accelerates to Ancient. Bellowing Thunder deals 70 per energy discarded.",
    strategy_pt="Teal Dance do Ogerpon ex Mascara Turquesa anexa energia e compra. Professora Sada acelera para Antigos. Bellowing Thunder causa 70 por energia descartada.",
    difficulty="Beginner",
    meta_share=8.50,
    key_pokemon=["Raging Bolt ex", "Teal Mask Ogerpon ex", "Squawkabilly ex"],
    energy_types=["Grass", "Lightning", "Fighting"],
    strengths_en=["Turn-one KO potential", "Fast energy acceleration", "Can snipe bench", "Very aggressive"],
    strengths_pt=["Potencial de KO no turno 1", "Aceleracao rapida", "Pode acertar banco", "Muito agressivo"],
    weaknesses_en=["Weak to Fighting", "Relies on Ogerpon", "Vulnerable to disruption"],
    weaknesses_pt=["Fraco contra Lutador", "Depende do Ogerpon", "Vulneravel a disrupcao"],
    cards=[
        CardEntry(4, "Raging Bolt ex", "Raging Bolt ex", "TEF", "123", "pokemon"),
        CardEntry(4, "Teal Mask Ogerpon ex", "Ogerpon ex Mascara Turquesa", "TWM", "25", "pokemon"),
        CardEntry(2, "Squawkabilly ex", "Squawkabilly ex", "PAL", "169", "pokemon"),
        CardEntry(1, "Slither Wing", "Slither Wing", "PAR", "107", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        CardEntry(4, "Professor Sada's Vitality", "Vitalidade da Professora Sada", "PAR", "170", "trainer"),
        CardEntry(2, "Crispin", "Crispin", "SCR", "133", "trainer"),
        CardEntry(1, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(1, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(4, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(4, "Earthen Vessel", "Vaso de Barro", "PAR", "163", "trainer"),
        CardEntry(3, "Pokegear 3.0", "Pokegear 3.0", "SVI", "186", "trainer"),
        CardEntry(3, "Pokemon Catcher", "Pokemon Catcher", "SVI", "187", "trainer"),
        CardEntry(2, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "Energy Retrieval", "Recuperacao de Energia", "SVI", "171", "trainer"),
        CardEntry(1, "Prime Catcher", "Prime Catcher", "TEF", "157", "trainer"),
        CardEntry(2, "Jamming Tower", "Torre de Interferencia", "TWM", "153", "trainer"),
        CardEntry(6, "Basic Grass Energy", "Energia Planta Basica", "SVE", "9", "energy"),
        CardEntry(3, "Basic Lightning Energy", "Energia Eletrica Basica", "SVE", "4", "energy"),
        CardEntry(3, "Basic Fighting Energy", "Energia Lutador Basica", "SVE", "6", "energy"),
    ]
)

# 6. GRIMMSNARL EX
META_DECKS["grimmsnarl"] = MetaDeck(
    id="grimmsnarl",
    name_en="Marnie's Grimmsnarl ex / Froslass",
    name_pt="Grimmsnarl da Marnie ex / Froslass",
    tier=1,
    description_en="Control deck with spread damage and ability disruption",
    description_pt="Deck de controle com dano espalhado e disrupcao de habilidades",
    strategy_en="Froslass places damage counters on ability Pokemon. Munkidori moves damage. Grimmsnarl ex deals 180 + bench damage. Wear down systematically.",
    strategy_pt="Froslass coloca contadores em Pokemon com habilidade. Munkidori move dano. Grimmsnarl ex causa 180 + dano no banco. Desgaste sistematico.",
    difficulty="Advanced",
    meta_share=6.50,
    key_pokemon=["Marnie's Grimmsnarl ex", "Froslass", "Snorunt", "Munkidori"],
    energy_types=["Darkness"],
    strengths_en=["Punishes abilities", "Excellent spread", "Type advantage vs Garde", "Strong late game"],
    strengths_pt=["Pune habilidades", "Excelente spread", "Vantagem vs Garde", "Final de jogo forte"],
    weaknesses_en=["Weak to Grass", "Setup can be slow", "Struggles vs basics"],
    weaknesses_pt=["Fraco contra Planta", "Setup pode ser lento", "Dificuldade vs basicos"],
    cards=[
        CardEntry(3, "Marnie's Impidimp", "Impidimp da Marnie", "DRI", "134", "pokemon"),
        CardEntry(2, "Marnie's Morgrem", "Morgrem da Marnie", "DRI", "135", "pokemon"),
        CardEntry(2, "Marnie's Grimmsnarl ex", "Grimmsnarl da Marnie ex", "DRI", "136", "pokemon"),
        CardEntry(3, "Munkidori", "Munkidori", "TWM", "95", "pokemon"),
        CardEntry(2, "Snorunt", "Snorunt", "TWM", "51", "pokemon"),
        CardEntry(2, "Froslass", "Froslass", "TWM", "53", "pokemon"),
        CardEntry(1, "Budew", "Budew", "PRE", "4", "pokemon"),
        CardEntry(1, "Shaymin", "Shaymin", "DRI", "10", "pokemon"),
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(4, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(3, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(2, "Buddy-Buddy Poffin", "Poffin Amigo-Amigo", "TEF", "144", "trainer"),
        CardEntry(2, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(2, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(2, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(2, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "TM: Evolution", "MT: Evolucao", "PAR", "178", "trainer"),
        CardEntry(1, "TM: Devolution", "MT: Devolucao", "PAR", "177", "trainer"),
        CardEntry(3, "Spikemuth Gym", "Ginasio Spikemuth", "DRI", "152", "trainer"),
        CardEntry(8, "Basic Darkness Energy", "Energia Escuridao Basica", "SVE", "7", "energy"),
    ]
)

# 7. JOLTIK BOX
META_DECKS["joltik_box"] = MetaDeck(
    id="joltik_box",
    name_en="Joltik Box",
    name_pt="Joltik Box",
    tier=2,
    description_en="Flexible toolbox deck with multiple attackers for different matchups",
    description_pt="Deck toolbox flexivel com multiplos atacantes para diferentes matchups",
    strategy_en="Joltik's Jolting Charge attaches 2 energy to bench. Miraidon finds Lightning Pokemon. Choose attacker based on matchup: Iron Hands, Pikachu ex, Miraidon ex.",
    strategy_pt="Jolting Charge do Joltik anexa 2 energias ao banco. Miraidon encontra Pokemon Eletrico. Escolha atacante baseado no matchup: Iron Hands, Pikachu ex, Miraidon ex.",
    difficulty="Intermediate",
    meta_share=4.80,
    key_pokemon=["Joltik", "Miraidon ex", "Iron Hands ex", "Pikachu ex"],
    energy_types=["Lightning", "Grass", "Metal", "Psychic"],
    strengths_en=["Flexible attackers", "Good vs variety", "Iron Hands extra prize", "Fast energy"],
    strengths_pt=["Atacantes flexiveis", "Bom vs variedade", "Iron Hands premio extra", "Energia rapida"],
    weaknesses_en=["Weak to Fighting", "Needs matchup knowledge", "Can brick without Joltik"],
    weaknesses_pt=["Fraco contra Lutador", "Requer conhecimento", "Pode travar sem Joltik"],
    cards=[
        CardEntry(2, "Joltik", "Joltik", "SCR", "50", "pokemon"),
        CardEntry(1, "Galvantula", "Galvantula", "SFA", "2", "pokemon"),
        CardEntry(2, "Miraidon ex", "Miraidon ex", "SVI", "81", "pokemon"),
        CardEntry(2, "Iron Hands ex", "Iron Hands ex", "PAR", "70", "pokemon"),
        CardEntry(2, "Pikachu ex", "Pikachu ex", "SSP", "57", "pokemon"),
        CardEntry(1, "Iron Leaves ex", "Iron Leaves ex", "TEF", "25", "pokemon"),
        CardEntry(1, "Bloodmoon Ursaluna ex", "Ursaluna ex", "TWM", "141", "pokemon"),
        CardEntry(1, "Lillie's Clefairy ex", "Clefairy da Lillie ex", "JTG", "56", "pokemon"),
        CardEntry(1, "Latias ex", "Latias ex", "SSP", "76", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        CardEntry(1, "Maractus", "Maractus", "JTG", "8", "pokemon"),
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(4, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(4, "Crispin", "Crispin", "SCR", "133", "trainer"),
        CardEntry(1, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(4, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(3, "Pokegear 3.0", "Pokegear 3.0", "SVI", "186", "trainer"),
        CardEntry(1, "Earthen Vessel", "Vaso de Barro", "PAR", "163", "trainer"),
        CardEntry(1, "Prime Catcher", "Prime Catcher", "TEF", "157", "trainer"),
        CardEntry(2, "Bravery Charm", "Amuleto da Bravura", "PAL", "173", "trainer"),
        CardEntry(5, "Basic Lightning Energy", "Energia Eletrica Basica", "SVE", "4", "energy"),
        CardEntry(5, "Basic Grass Energy", "Energia Planta Basica", "SVE", "9", "energy"),
        CardEntry(2, "Basic Metal Energy", "Energia Metal Basica", "SVE", "8", "energy"),
        CardEntry(2, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
    ]
)

# 8. FLAREON EX
META_DECKS["flareon"] = MetaDeck(
    id="flareon",
    name_en="Flareon ex",
    name_pt="Flareon ex",
    tier=2,
    description_en="Anti-meta deck that counters Metal-type decks like Gholdengo ex",
    description_pt="Deck anti-meta que countrea decks Metal como Gholdengo ex",
    strategy_en="Flareon ex deals double damage to Metal Pokemon. Perfect counter to Gholdengo ex. Use Eevee for evolution support. Ditto copies Flareon.",
    strategy_pt="Flareon ex causa dano dobrado a Pokemon Metal. Counter perfeito para Gholdengo ex. Use Eevee para suporte. Ditto copia Flareon.",
    difficulty="Beginner",
    meta_share=3.20,
    key_pokemon=["Flareon ex", "Eevee", "Ditto"],
    energy_types=["Fire"],
    strengths_en=["Destroys Gholdengo", "Type advantage vs Metal", "Simple to play", "Good energy efficiency"],
    strengths_pt=["Destroi Gholdengo", "Vantagem vs Metal", "Simples de jogar", "Boa eficiencia"],
    weaknesses_en=["Weak to Water", "Matchup dependent", "Limited versatility"],
    weaknesses_pt=["Fraco contra Agua", "Depende do matchup", "Versatilidade limitada"],
    cards=[
        CardEntry(4, "Eevee", "Eevee", "MEV", "69", "pokemon"),
        CardEntry(3, "Flareon ex", "Flareon ex", "MEV", "10", "pokemon"),
        CardEntry(2, "Ditto", "Ditto", "SVI", "132", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        CardEntry(1, "Entei V", "Entei V", "BRS", "22", "pokemon"),
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(4, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(2, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "PAL", "172", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(4, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(4, "Buddy-Buddy Poffin", "Poffin Amigo-Amigo", "TEF", "144", "trainer"),
        CardEntry(2, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "Switch", "Trocar", "SVI", "194", "trainer"),
        CardEntry(1, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(1, "TM: Evolution", "MT: Evolucao", "PAR", "178", "trainer"),
        CardEntry(2, "Artazon", "Artazon", "PAL", "171", "trainer"),
        CardEntry(10, "Basic Fire Energy", "Energia Fogo Basica", "SVE", "2", "energy"),
        CardEntry(2, "Luminous Energy", "Energia Luminosa", "PAL", "191", "energy"),
    ]
)


# =============================================================================
# MATCHUPS
# =============================================================================

MATCHUPS = [
    MatchupData("gholdengo", "dragapult", 55, "Gholdengo slightly favored due to OHKO potential", "Gholdengo levemente favorecido devido ao potencial de OHKO"),
    MatchupData("gholdengo", "gardevoir", 48, "Slightly unfavored but playable", "Levemente desfavorecido mas jogavel"),
    MatchupData("gholdengo", "charizard", 60, "Favored - can OHKO before setup", "Favorecido - pode nocautear antes de montar"),
    MatchupData("gholdengo", "raging_bolt", 50, "Even - depends on who goes first", "Equilibrado - depende de quem comeca"),
    MatchupData("gholdengo", "grimmsnarl", 55, "Slightly favored - Grimmsnarl lacks OHKOs", "Levemente favorecido - Grimmsnarl nao tem OHKOs"),
    MatchupData("gholdengo", "joltik_box", 52, "Slightly favored - higher damage ceiling", "Levemente favorecido - maior teto de dano"),
    MatchupData("gholdengo", "flareon", 25, "Very unfavored - Flareon deals double damage", "Muito desfavorecido - Flareon causa dano dobrado"),
    MatchupData("dragapult", "gardevoir", 40, "Unfavored - Gardevoir sets up too fast", "Desfavorecido - Gardevoir monta muito rapido"),
    MatchupData("dragapult", "charizard", 55, "Favored - spread disrupts Charizard setup", "Favorecido - spread atrapalha setup do Charizard"),
    MatchupData("dragapult", "raging_bolt", 45, "Slightly unfavored - Raging Bolt is too fast", "Levemente desfavorecido - Raging Bolt e muito rapido"),
    MatchupData("dragapult", "grimmsnarl", 50, "Even - both spread damage", "Equilibrado - ambos espalham dano"),
    MatchupData("dragapult", "joltik_box", 48, "Slightly unfavored - Iron Hands can snipe back", "Levemente desfavorecido - Iron Hands pode dar snipe"),
    MatchupData("dragapult", "flareon", 55, "Slightly favored - Flareon lacks bench protection", "Levemente favorecido - Flareon nao protege banco"),
    MatchupData("gardevoir", "charizard", 45, "Slightly unfavored - Charizard has raw power", "Levemente desfavorecido - Charizard tem poder bruto"),
    MatchupData("gardevoir", "raging_bolt", 60, "Favored - Clefairy hits Dragon weakness", "Favorecido - Clefairy acerta fraqueza de Dragao"),
    MatchupData("gardevoir", "grimmsnarl", 35, "Very unfavored - Darkness weakness is brutal", "Muito desfavorecido - fraqueza Escuridao e brutal"),
    MatchupData("gardevoir", "joltik_box", 52, "Slightly favored - better late game", "Levemente favorecido - melhor final de jogo"),
    MatchupData("gardevoir", "flareon", 50, "Even - neither has advantage", "Equilibrado - nenhum tem vantagem"),
    MatchupData("charizard", "raging_bolt", 45, "Slightly unfavored - Raging Bolt is faster", "Levemente desfavorecido - Raging Bolt e mais rapido"),
    MatchupData("charizard", "grimmsnarl", 55, "Slightly favored - high HP survives spread", "Levemente favorecido - HP alto sobrevive ao spread"),
    MatchupData("charizard", "joltik_box", 50, "Even - depends on setup speed", "Equilibrado - depende da velocidade de setup"),
    MatchupData("charizard", "flareon", 65, "Favored - Flareon can't OHKO Charizard ex", "Favorecido - Flareon nao pode nocautear em um golpe"),
    MatchupData("raging_bolt", "grimmsnarl", 60, "Favored - Ogerpon has type advantage", "Favorecido - Ogerpon tem vantagem de tipo"),
    MatchupData("raging_bolt", "joltik_box", 52, "Slightly favored - faster aggression", "Levemente favorecido - agressao mais rapida"),
    MatchupData("raging_bolt", "flareon", 55, "Slightly favored - can OHKO before setup", "Levemente favorecido - pode nocautear antes de montar"),
    MatchupData("grimmsnarl", "joltik_box", 48, "Slightly unfavored - Joltik is too flexible", "Levemente desfavorecido - Joltik e muito flexivel"),
    MatchupData("grimmsnarl", "flareon", 60, "Favored - Froslass wears down Flareon", "Favorecido - Froslass desgasta Flareon"),
    MatchupData("joltik_box", "flareon", 55, "Slightly favored - more versatile attackers", "Levemente favorecido - atacantes mais versateis"),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_matchup(deck_a_id: str, deck_b_id: str) -> Optional[MatchupData]:
    """Get matchup data between two decks."""
    for matchup in MATCHUPS:
        if matchup.deck_a_id == deck_a_id and matchup.deck_b_id == deck_b_id:
            return matchup
        elif matchup.deck_a_id == deck_b_id and matchup.deck_b_id == deck_a_id:
            return MatchupData(
                deck_a_id=deck_b_id,
                deck_b_id=deck_a_id,
                win_rate_a=matchup.win_rate_b,
                notes_en=matchup.notes_en,
                notes_pt=matchup.notes_pt
            )
    return None


def get_deck_matchups(deck_id: str) -> list:
    """Get all matchups for a deck."""
    matchups = []
    for other_id in META_DECKS.keys():
        if other_id == deck_id:
            continue
        matchup = get_matchup(deck_id, other_id)
        if matchup:
            matchups.append((other_id, matchup.win_rate_a, matchup.notes_en))
    return sorted(matchups, key=lambda x: -x[1])


def get_all_decks() -> list:
    """Get all decks sorted by meta share."""
    return sorted(META_DECKS.values(), key=lambda d: -d.meta_share)


def get_translation(key: str, lang: Language = Language.EN) -> str:
    """Get UI translation."""
    translations = {
        "en": {
            "tier": "Tier", "meta_share": "Meta Share", "difficulty": "Difficulty",
            "strategy": "Strategy", "strengths": "Strengths", "weaknesses": "Weaknesses",
            "matchups": "Matchups", "win_rate": "Win Rate", "favored": "Favored",
            "unfavored": "Unfavored", "even": "Even", "notes": "Notes",
            "pokemon": "Pokemon", "trainer": "Trainer", "energy": "Energy",
            "key_pokemon": "Key Pokemon", "description": "Description",
        },
        "pt": {
            "tier": "Tier", "meta_share": "Participacao no Meta", "difficulty": "Dificuldade",
            "strategy": "Estrategia", "strengths": "Pontos Fortes", "weaknesses": "Pontos Fracos",
            "matchups": "Confrontos", "win_rate": "Taxa de Vitoria", "favored": "Favorecido",
            "unfavored": "Desfavorecido", "even": "Equilibrado", "notes": "Observacoes",
            "pokemon": "Pokemon", "trainer": "Treinador", "energy": "Energia",
            "key_pokemon": "Pokemon Chave", "description": "Descricao",
        }
    }
    lang_key = lang.value if isinstance(lang, Language) else lang
    return translations.get(lang_key, translations["en"]).get(key, key)


def get_difficulty_translation(difficulty: str, lang: Language = Language.EN) -> str:
    """Translate difficulty level."""
    diff_map = {
        "Beginner": {"en": "Beginner", "pt": "Iniciante"},
        "Intermediate": {"en": "Intermediate", "pt": "Intermediario"},
        "Advanced": {"en": "Advanced", "pt": "Avancado"},
    }
    lang_key = lang.value if isinstance(lang, Language) else lang
    return diff_map.get(difficulty, {}).get(lang_key, difficulty)
