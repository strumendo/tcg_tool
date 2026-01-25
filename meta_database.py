"""
Meta Database for Pokemon TCG - Top Competitive Decks with Matchups

This module contains:
- Complete deck lists for top 9 meta decks (January 2026)
- Updated with Ascended Heroes (ASC) cards
- Matchup win rate calculations
- Bilingual support (English/Portuguese)
- Card translations and deck descriptions
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Language(str, Enum):
    """Supported languages."""
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
    card_type: str  # "pokemon", "trainer", "energy"

    def get_name(self, lang: Language = Language.EN) -> str:
        """Get card name in specified language."""
        return self.name_pt if lang == Language.PT else self.name_en

    def __str__(self) -> str:
        return f"{self.quantity} {self.name_en} {self.set_code} {self.set_number}"


@dataclass
class MetaDeck:
    """A meta deck with complete card list and information."""
    id: str
    name_en: str
    name_pt: str
    tier: int  # 1, 2, or 3
    description_en: str
    description_pt: str
    strategy_en: str
    strategy_pt: str
    difficulty: str  # "Beginner", "Intermediate", "Advanced"
    cards: list[CardEntry] = field(default_factory=list)
    strengths_en: list[str] = field(default_factory=list)
    strengths_pt: list[str] = field(default_factory=list)
    weaknesses_en: list[str] = field(default_factory=list)
    weaknesses_pt: list[str] = field(default_factory=list)
    key_pokemon: list[str] = field(default_factory=list)
    energy_types: list[str] = field(default_factory=list)
    meta_share: float = 0.0  # Percentage of meta share

    def get_name(self, lang: Language = Language.EN) -> str:
        return self.name_pt if lang == Language.PT else self.name_en

    def get_description(self, lang: Language = Language.EN) -> str:
        return self.description_pt if lang == Language.PT else self.description_en

    def get_strategy(self, lang: Language = Language.EN) -> str:
        return self.strategy_pt if lang == Language.PT else self.strategy_en

    def get_strengths(self, lang: Language = Language.EN) -> list[str]:
        return self.strengths_pt if lang == Language.PT else self.strengths_en

    def get_weaknesses(self, lang: Language = Language.EN) -> list[str]:
        return self.weaknesses_pt if lang == Language.PT else self.weaknesses_en

    def get_pokemon(self) -> list[CardEntry]:
        return [c for c in self.cards if c.card_type == "pokemon"]

    def get_trainers(self) -> list[CardEntry]:
        return [c for c in self.cards if c.card_type == "trainer"]

    def get_energy(self) -> list[CardEntry]:
        return [c for c in self.cards if c.card_type == "energy"]

    def total_cards(self) -> int:
        return sum(c.quantity for c in self.cards)

    def get_deck_list(self, lang: Language = Language.EN) -> str:
        """Get formatted deck list in specified language."""
        pokemon_label = "Pokemon" if lang == Language.EN else "Pokemon"
        trainer_label = "Trainer" if lang == Language.EN else "Treinador"
        energy_label = "Energy" if lang == Language.EN else "Energia"

        lines = []

        pokemon = self.get_pokemon()
        if pokemon:
            lines.append(f"{pokemon_label}:")
            for card in pokemon:
                lines.append(f"  {card.quantity} {card.get_name(lang)} {card.set_code} {card.set_number}")

        trainers = self.get_trainers()
        if trainers:
            lines.append(f"\n{trainer_label}:")
            for card in trainers:
                lines.append(f"  {card.quantity} {card.get_name(lang)} {card.set_code} {card.set_number}")

        energy = self.get_energy()
        if energy:
            lines.append(f"\n{energy_label}:")
            for card in energy:
                lines.append(f"  {card.quantity} {card.get_name(lang)} {card.set_code} {card.set_number}")

        return "\n".join(lines)


@dataclass
class MatchupData:
    """Matchup data between two decks."""
    deck_a_id: str
    deck_b_id: str
    win_rate_a: float  # Win rate for deck A against deck B (0-100)
    notes_en: str = ""
    notes_pt: str = ""

    @property
    def win_rate_b(self) -> float:
        """Win rate for deck B against deck A."""
        return 100 - self.win_rate_a

    def get_notes(self, lang: Language = Language.EN) -> str:
        return self.notes_pt if lang == Language.PT else self.notes_en


# =============================================================================
# TOP 8 META DECKS - JANUARY 2026
# =============================================================================

META_DECKS: dict[str, MetaDeck] = {}

# -----------------------------------------------------------------------------
# 1. GHOLDENGO EX
# -----------------------------------------------------------------------------
META_DECKS["gholdengo"] = MetaDeck(
    id="gholdengo",
    name_en="Gholdengo ex",
    name_pt="Gholdengo ex",
    tier=1,
    description_en="The #1 deck in the meta with incredible draw power and infinite damage potential",
    description_pt="O deck #1 do meta com poder de compra incrivel e potencial de dano infinito",
    strategy_en="Use Gholdengo ex's Coin Bonus ability to draw cards each turn. Accumulate Basic Energy in hand, then use Make It Rain to deal 50 damage per energy discarded. Genesect ex provides additional draw power.",
    strategy_pt="Use a habilidade Coin Bonus do Gholdengo ex para comprar cartas a cada turno. Acumule Energias Basicas na mao e use Make It Rain para causar 50 de dano por energia descartada. Genesect ex fornece poder de compra adicional.",
    difficulty="Intermediate",
    meta_share=26.49,
    key_pokemon=["Gholdengo ex", "Genesect ex", "Gimmighoul"],
    energy_types=["Metal", "Basic"],
    strengths_en=[
        "Highest damage ceiling in format",
        "Excellent draw power with Coin Bonus",
        "Can OHKO any Pokemon",
        "Consistent setup with Precious Trolley"
    ],
    strengths_pt=[
        "Maior teto de dano do formato",
        "Excelente poder de compra com Coin Bonus",
        "Pode nocautear qualquer Pokemon em um golpe",
        "Setup consistente com Precious Trolley"
    ],
    weaknesses_en=[
        "Weak to Fire (Flareon ex)",
        "Needs many energy in hand",
        "Struggles against disruption"
    ],
    weaknesses_pt=[
        "Fraco contra Fogo (Flareon ex)",
        "Precisa de muitas energias na mao",
        "Dificuldade contra disrupcao"
    ],
    cards=[
        # Pokemon
        CardEntry(4, "Gimmighoul", "Gimmighoul", "PRE", "86", "pokemon"),
        CardEntry(3, "Gholdengo ex", "Gholdengo ex", "PRE", "164", "pokemon"),
        CardEntry(2, "Genesect ex", "Genesect ex", "JTG", "51", "pokemon"),
        CardEntry(2, "Solrock", "Solrock", "MEV", "45", "pokemon"),
        CardEntry(2, "Lunatone", "Lunatone", "MEV", "46", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        # Trainers
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
        CardEntry(1, "Technical Machine: Devolution", "Maquina Tecnica: Devolucao", "PAR", "177", "trainer"),
        CardEntry(2, "Jamming Tower", "Torre de Interferencia", "TWM", "153", "trainer"),
        # Energy
        CardEntry(4, "Basic Metal Energy", "Energia Metal Basica", "SVE", "8", "energy"),
        CardEntry(4, "Basic Fighting Energy", "Energia Lutador Basica", "SVE", "6", "energy"),
        CardEntry(4, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
        CardEntry(3, "Basic Fire Energy", "Energia Fogo Basica", "SVE", "2", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 2. DRAGAPULT EX
# -----------------------------------------------------------------------------
META_DECKS["dragapult"] = MetaDeck(
    id="dragapult",
    name_en="Dragapult ex",
    name_pt="Dragapult ex",
    tier=1,
    description_en="Powerful spread damage deck with bench sniping and devolution tech",
    description_pt="Deck poderoso de dano espalhado com snipe de banco e tecnologia de devolucao",
    strategy_en="Use Phantom Dive to deal 200 damage and spread 6 damage counters. Munkidori redirects damage to opponent's bench. Technical Machine: Devolution knocks out evolved Pokemon with spread damage.",
    strategy_pt="Use Phantom Dive para causar 200 de dano e espalhar 6 contadores de dano. Munkidori redireciona dano para o banco adversario. Maquina Tecnica: Devolucao nocauteia Pokemon evoluidos com dano espalhado.",
    difficulty="Intermediate",
    meta_share=19.95,
    key_pokemon=["Dragapult ex", "Dreepy", "Drakloak", "Munkidori"],
    energy_types=["Psychic", "Darkness"],
    strengths_en=[
        "Excellent spread damage",
        "Can take multiple prizes per turn",
        "Strong against evolution decks",
        "Good draw support options"
    ],
    strengths_pt=[
        "Excelente dano espalhado",
        "Pode pegar multiplos premios por turno",
        "Forte contra decks de evolucao",
        "Boas opcoes de suporte de compra"
    ],
    weaknesses_en=[
        "Weak to Darkness",
        "Setup can be disrupted",
        "Struggles against single-prize decks"
    ],
    weaknesses_pt=[
        "Fraco contra Escuridao",
        "Setup pode ser interrompido",
        "Dificuldade contra decks de premio unico"
    ],
    cards=[
        # Pokemon
        CardEntry(4, "Dreepy", "Dreepy", "TWM", "88", "pokemon"),
        CardEntry(1, "Drakloak", "Drakloak", "TWM", "89", "pokemon"),
        CardEntry(3, "Dragapult ex", "Dragapult ex", "TWM", "130", "pokemon"),
        CardEntry(3, "Munkidori", "Munkidori", "TWM", "95", "pokemon"),
        CardEntry(1, "Latias ex", "Latias ex", "SSP", "76", "pokemon"),
        CardEntry(1, "Bloodmoon Ursaluna ex", "Ursaluna Lua Sangrenta ex", "TWM", "141", "pokemon"),
        CardEntry(1, "Maractus", "Maractus", "JTG", "8", "pokemon"),
        CardEntry(1, "Hawlucha", "Hawlucha", "PAR", "88", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        # Trainers
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
        CardEntry(2, "Technical Machine: Devolution", "Maquina Tecnica: Devolucao", "PAR", "177", "trainer"),
        CardEntry(1, "Secret Box", "Caixa Secreta", "JTG", "71", "trainer"),
        # Energy
        CardEntry(6, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
        CardEntry(3, "Luminous Energy", "Energia Luminosa", "PAL", "191", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 3. GARDEVOIR EX
# -----------------------------------------------------------------------------
META_DECKS["gardevoir"] = MetaDeck(
    id="gardevoir",
    name_en="Gardevoir ex / Mega Gardevoir ex",
    name_pt="Gardevoir ex / Mega Gardevoir ex",
    tier=1,
    description_en="The longest-running top deck with infinite energy acceleration, now with Mega Gardevoir ex options from MEV and Ascended Heroes",
    description_pt="O deck de topo mais duradouro com aceleracao de energia infinita, agora com opcoes de Mega Gardevoir ex de MEV e Ascended Heroes",
    strategy_en="Use Gardevoir ex's Psychic Embrace to attach energy from discard pile. Mega Gardevoir ex provides a powerful finisher. Multiple attackers like Mega Diancie ex and Lillie's Clefairy ex provide coverage. Earthen Vessel helps discard energy for later use.",
    strategy_pt="Use Psychic Embrace do Gardevoir ex para anexar energia da pilha de descarte. Mega Gardevoir ex fornece um finalizador poderoso. Multiplos atacantes como Mega Diancie ex e Clefairy da Lillie ex fornecem cobertura. Earthen Vessel ajuda a descartar energia para uso posterior.",
    difficulty="Advanced",
    meta_share=15.80,
    key_pokemon=["Gardevoir ex", "Mega Gardevoir ex", "Ralts", "Kirlia", "Mega Diancie ex", "Lillie's Clefairy ex"],
    energy_types=["Psychic"],
    strengths_en=[
        "Infinite energy acceleration",
        "Flexible attacker options with Mega evolutions",
        "Strong against Dragon types",
        "Excellent recovery options"
    ],
    strengths_pt=[
        "Aceleracao de energia infinita",
        "Opcoes flexiveis de atacante com Mega evolucoes",
        "Forte contra tipos Dragao",
        "Excelentes opcoes de recuperacao"
    ],
    weaknesses_en=[
        "Weak to Darkness",
        "Complex to pilot optimally",
        "Self-damage from ability"
    ],
    weaknesses_pt=[
        "Fraco contra Escuridao",
        "Complexo de pilotar de forma otima",
        "Auto-dano da habilidade"
    ],
    cards=[
        # Pokemon
        CardEntry(4, "Ralts", "Ralts", "SVI", "67", "pokemon"),
        CardEntry(3, "Kirlia", "Kirlia", "SVI", "68", "pokemon"),
        CardEntry(2, "Gardevoir ex", "Gardevoir ex", "SVI", "86", "pokemon"),
        CardEntry(1, "Mega Gardevoir ex", "Mega Gardevoir ex", "ASC", "79", "pokemon"),
        CardEntry(1, "Mega Diancie ex", "Mega Diancie ex", "MEV", "40", "pokemon"),
        CardEntry(1, "Lillie's Clefairy ex", "Clefairy da Lillie ex", "JTG", "56", "pokemon"),
        CardEntry(1, "Scream Tail", "Cauda Gritante", "PAR", "86", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Munkidori", "Munkidori", "TWM", "95", "pokemon"),
        # Trainers
        CardEntry(3, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(3, "Lillie's Determination", "Determinacao da Lillie", "JTG", "77", "trainer"),
        CardEntry(2, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(2, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(1, "Boss's Orders", "Ordens do Chefe", "ASC", "189", "trainer"),
        CardEntry(1, "Anthea & Concordia", "Anthea & Concordia", "ASC", "187", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(3, "Earthen Vessel", "Vaso de Barro", "PAR", "163", "trainer"),
        CardEntry(3, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(2, "Technical Machine: Evolution", "Maquina Tecnica: Evolucao", "PAR", "178", "trainer"),
        CardEntry(1, "Buddy-Buddy Poffin", "Poffin Amigo-Amigo", "TEF", "144", "trainer"),
        CardEntry(1, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(1, "Secret Box", "Caixa Secreta", "JTG", "71", "trainer"),
        CardEntry(2, "Mystery Garden", "Jardim Misterioso", "MEV", "71", "trainer"),
        # Energy
        CardEntry(7, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
        CardEntry(4, "Basic Darkness Energy", "Energia Escuridao Basica", "SVE", "7", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 4. CHARIZARD EX
# -----------------------------------------------------------------------------
META_DECKS["charizard"] = MetaDeck(
    id="charizard",
    name_en="Charizard ex / Mega Charizard Y ex",
    name_pt="Charizard ex / Mega Charizard Y ex",
    tier=1,
    description_en="Classic powerhouse deck updated with Mega Charizard Y ex from Ascended Heroes for devastating bench snipes",
    description_pt="Deck classico poderoso atualizado com Mega Charizard Y ex do Ascended Heroes para snipes devastadores no banco",
    strategy_en="Set up Pidgeot ex for Quick Search consistency. Charizard ex's Infernal Reign accelerates energy on evolution, and Burning Darkness deals more damage as opponent takes prizes. Mega Charizard Y ex adds 280 damage with bench snipe for finishing games. Survive early, then sweep late game.",
    strategy_pt="Monte Pidgeot ex para consistencia com Quick Search. Infernal Reign do Charizard ex acelera energia na evolucao, e Burning Darkness causa mais dano conforme o oponente pega premios. Mega Charizard Y ex adiciona 280 de dano com snipe no banco para finalizar jogos. Sobreviva no inicio, depois varra no final do jogo.",
    difficulty="Beginner",
    meta_share=14.50,
    key_pokemon=["Charizard ex", "Mega Charizard Y ex", "Charmander", "Pidgeot ex", "Pidgey"],
    energy_types=["Fire"],
    strengths_en=[
        "Very consistent with Pidgeot ex",
        "Strong comeback mechanic",
        "High damage output with bench snipe",
        "Mega Charizard Y ex threatens KOs on benched Pokemon"
    ],
    strengths_pt=[
        "Muito consistente com Pidgeot ex",
        "Forte mecanica de virada",
        "Alto dano com snipe no banco",
        "Mega Charizard Y ex ameaca KOs em Pokemon no banco"
    ],
    weaknesses_en=[
        "Weak to Water",
        "Path to the Peak shuts down abilities",
        "Slow setup"
    ],
    weaknesses_pt=[
        "Fraco contra Agua",
        "Path to the Peak desliga habilidades",
        "Setup lento"
    ],
    cards=[
        # Pokemon
        CardEntry(4, "Charmander", "Charmander", "ASC", "20", "pokemon"),
        CardEntry(1, "Charmeleon", "Charmeleon", "OBF", "27", "pokemon"),
        CardEntry(2, "Charizard ex", "Charizard ex", "OBF", "125", "pokemon"),
        CardEntry(1, "Mega Charizard Y ex", "Mega Charizard Y ex", "ASC", "22", "pokemon"),
        CardEntry(2, "Pidgey", "Pidgey", "OBF", "162", "pokemon"),
        CardEntry(2, "Pidgeot ex", "Pidgeot ex", "OBF", "164", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Entei", "Entei", "ASC", "25", "pokemon"),
        # Trainers
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(3, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "ASC", "189", "trainer"),
        CardEntry(1, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(4, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(3, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(2, "Super Rod", "Super Vara", "PAL", "188", "trainer"),
        CardEntry(2, "Escape Rope", "Corda de Fuga", "BST", "125", "trainer"),
        CardEntry(1, "Pal Pad", "Bloco de Amigo", "SVI", "182", "trainer"),
        CardEntry(1, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(2, "Artazon", "Artazon", "PAL", "171", "trainer"),
        # Energy
        CardEntry(8, "Basic Fire Energy", "Energia Fogo Basica", "SVE", "2", "energy"),
        CardEntry(2, "Luminous Energy", "Energia Luminosa", "PAL", "191", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 5. RAGING BOLT EX
# -----------------------------------------------------------------------------
META_DECKS["raging_bolt"] = MetaDeck(
    id="raging_bolt",
    name_en="Raging Bolt ex / Ogerpon ex",
    name_pt="Raging Bolt ex / Ogerpon ex",
    tier=1,
    description_en="Aggressive Ancient deck with turn-one knockout potential",
    description_pt="Deck Antigo agressivo com potencial de nocaute no primeiro turno",
    strategy_en="Use Teal Mask Ogerpon ex's Teal Dance to attach energy and draw cards. Professor Sada's Vitality accelerates energy to Ancient Pokemon. Raging Bolt's Bellowing Thunder deals 70 damage per energy discarded.",
    strategy_pt="Use Teal Dance do Ogerpon ex Mascara Turquesa para anexar energia e comprar cartas. Vitalidade da Professora Sada acelera energia para Pokemon Antigos. Bellowing Thunder do Raging Bolt causa 70 de dano por energia descartada.",
    difficulty="Beginner",
    meta_share=8.50,
    key_pokemon=["Raging Bolt ex", "Teal Mask Ogerpon ex", "Squawkabilly ex"],
    energy_types=["Grass", "Lightning", "Fighting"],
    strengths_en=[
        "Turn-one knockout potential",
        "Excellent energy acceleration",
        "Can snipe benched Pokemon",
        "Fast and aggressive"
    ],
    strengths_pt=[
        "Potencial de nocaute no primeiro turno",
        "Excelente aceleracao de energia",
        "Pode acertar Pokemon no banco",
        "Rapido e agressivo"
    ],
    weaknesses_en=[
        "Weak to Fighting",
        "Relies heavily on Ogerpon",
        "Vulnerable to disruption"
    ],
    weaknesses_pt=[
        "Fraco contra Lutador",
        "Depende muito do Ogerpon",
        "Vulneravel a disrupcao"
    ],
    cards=[
        # Pokemon
        CardEntry(4, "Raging Bolt ex", "Raging Bolt ex", "TEF", "123", "pokemon"),
        CardEntry(4, "Teal Mask Ogerpon ex", "Ogerpon ex Mascara Turquesa", "TWM", "25", "pokemon"),
        CardEntry(2, "Squawkabilly ex", "Squawkabilly ex", "PAL", "169", "pokemon"),
        CardEntry(1, "Slither Wing", "Slither Wing", "PAR", "107", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        # Trainers
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
        CardEntry(1, "Superior Energy Retrieval", "Recuperacao de Energia Superior", "PAL", "189", "trainer"),
        CardEntry(1, "Pal Pad", "Bloco de Amigo", "SVI", "182", "trainer"),
        CardEntry(1, "Prime Catcher", "Prime Catcher", "TEF", "157", "trainer"),
        CardEntry(1, "Switch", "Trocar", "SVI", "194", "trainer"),
        CardEntry(2, "Jamming Tower", "Torre de Interferencia", "TWM", "153", "trainer"),
        # Energy
        CardEntry(6, "Basic Grass Energy", "Energia Planta Basica", "SVE", "9", "energy"),
        CardEntry(3, "Basic Lightning Energy", "Energia Eletrica Basica", "SVE", "4", "energy"),
        CardEntry(3, "Basic Fighting Energy", "Energia Lutador Basica", "SVE", "6", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 6. MARNIE'S GRIMMSNARL EX
# -----------------------------------------------------------------------------
META_DECKS["grimmsnarl"] = MetaDeck(
    id="grimmsnarl",
    name_en="Marnie's Grimmsnarl ex / Mega Froslass ex",
    name_pt="Grimmsnarl da Marnie ex / Mega Froslass ex",
    tier=1,
    description_en="Control deck with spread damage and ability disruption, now enhanced with Mega Froslass ex from Ascended Heroes",
    description_pt="Deck de controle com dano espalhado e disrupcao de habilidades, agora aprimorado com Mega Froslass ex do Ascended Heroes",
    strategy_en="Froslass places damage counters on Pokemon with abilities each turn. Mega Froslass ex from Ascended Heroes provides a powerful finisher with spread synergy. Munkidori moves damage to key targets. Marnie's Grimmsnarl ex deals 180 damage with Shadow Bullet while also hitting bench.",
    strategy_pt="Froslass coloca contadores de dano em Pokemon com habilidades a cada turno. Mega Froslass ex do Ascended Heroes fornece um finalizador poderoso com sinergia de spread. Munkidori move dano para alvos importantes. Grimmsnarl da Marnie ex causa 180 de dano com Shadow Bullet enquanto tambem acerta o banco.",
    difficulty="Advanced",
    meta_share=7.20,
    key_pokemon=["Marnie's Grimmsnarl ex", "Mega Froslass ex", "Froslass", "Snorunt", "Munkidori"],
    energy_types=["Darkness", "Water"],
    strengths_en=[
        "Punishes ability-heavy decks",
        "Excellent spread damage",
        "Mega Froslass ex adds burst damage potential",
        "Type advantage vs Gardevoir"
    ],
    strengths_pt=[
        "Pune decks com muitas habilidades",
        "Excelente dano espalhado",
        "Mega Froslass ex adiciona potencial de burst",
        "Vantagem de tipo contra Gardevoir"
    ],
    weaknesses_en=[
        "Weak to Grass (Ogerpon)",
        "Setup can be slow",
        "Struggles against basic Pokemon decks"
    ],
    weaknesses_pt=[
        "Fraco contra Planta (Ogerpon)",
        "Setup pode ser lento",
        "Dificuldade contra decks de Pokemon basicos"
    ],
    cards=[
        # Pokemon
        CardEntry(3, "Marnie's Impidimp", "Impidimp da Marnie", "DRI", "134", "pokemon"),
        CardEntry(2, "Marnie's Morgrem", "Morgrem da Marnie", "DRI", "135", "pokemon"),
        CardEntry(2, "Marnie's Grimmsnarl ex", "Grimmsnarl da Marnie ex", "DRI", "136", "pokemon"),
        CardEntry(3, "Munkidori", "Munkidori", "TWM", "95", "pokemon"),
        CardEntry(2, "Snorunt", "Snorunt", "TWM", "51", "pokemon"),
        CardEntry(1, "Froslass", "Froslass", "TWM", "53", "pokemon"),
        CardEntry(1, "Mega Froslass ex", "Mega Froslass ex", "ASC", "52", "pokemon"),
        CardEntry(1, "Budew", "Budew", "PRE", "4", "pokemon"),
        CardEntry(1, "Shaymin", "Shaymin", "DRI", "10", "pokemon"),
        # Trainers
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(4, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(3, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "ASC", "189", "trainer"),
        CardEntry(2, "Buddy-Buddy Poffin", "Poffin Amigo-Amigo", "TEF", "144", "trainer"),
        CardEntry(2, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(2, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(2, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(2, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(1, "Super Rod", "Super Vara", "PAL", "188", "trainer"),
        CardEntry(1, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(1, "Pokegear 3.0", "Pokegear 3.0", "SVI", "186", "trainer"),
        CardEntry(1, "Secret Box", "Caixa Secreta", "JTG", "71", "trainer"),
        CardEntry(2, "Technical Machine: Evolution", "Maquina Tecnica: Evolucao", "PAR", "178", "trainer"),
        CardEntry(1, "Technical Machine: Devolution", "Maquina Tecnica: Devolucao", "PAR", "177", "trainer"),
        CardEntry(1, "Rescue Board", "Prancha de Resgate", "TEF", "159", "trainer"),
        CardEntry(2, "Spikemuth Gym", "Ginasio Spikemuth", "DRI", "152", "trainer"),
        CardEntry(1, "Nighttime Mine", "Mina Noturna", "ASC", "195", "trainer"),
        # Energy
        CardEntry(6, "Basic Darkness Energy", "Energia Escuridao Basica", "SVE", "7", "energy"),
        CardEntry(2, "Basic Water Energy", "Energia Agua Basica", "SVE", "3", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 7. JOLTIK BOX
# -----------------------------------------------------------------------------
META_DECKS["joltik_box"] = MetaDeck(
    id="joltik_box",
    name_en="Joltik Box",
    name_pt="Joltik Box",
    tier=2,
    description_en="Flexible toolbox deck with multiple attackers for different matchups",
    description_pt="Deck toolbox flexivel com multiplos atacantes para diferentes matchups",
    strategy_en="Use Joltik's Jolting Charge to attach 2 energy to benched Pokemon. Miraidon ex finds Lightning Pokemon with Tandem Unit. Choose the right attacker: Iron Hands ex for extra prizes, Pikachu ex for big damage, Miraidon ex for basics.",
    strategy_pt="Use Jolting Charge do Joltik para anexar 2 energias a Pokemon no banco. Miraidon ex encontra Pokemon Eletrico com Tandem Unit. Escolha o atacante certo: Iron Hands ex para premios extras, Pikachu ex para grande dano, Miraidon ex para basicos.",
    difficulty="Intermediate",
    meta_share=4.80,
    key_pokemon=["Joltik", "Miraidon ex", "Iron Hands ex", "Pikachu ex"],
    energy_types=["Lightning", "Grass", "Metal", "Psychic"],
    strengths_en=[
        "Flexible attacker selection",
        "Good against variety of decks",
        "Iron Hands gets extra prize",
        "Fast energy acceleration"
    ],
    strengths_pt=[
        "Selecao flexivel de atacante",
        "Bom contra variedade de decks",
        "Iron Hands pega premio extra",
        "Aceleracao rapida de energia"
    ],
    weaknesses_en=[
        "Weak to Fighting",
        "Requires good matchup knowledge",
        "Can brick without Joltik"
    ],
    weaknesses_pt=[
        "Fraco contra Lutador",
        "Requer bom conhecimento de matchups",
        "Pode travar sem Joltik"
    ],
    cards=[
        # Pokemon
        CardEntry(2, "Joltik", "Joltik", "SCR", "50", "pokemon"),
        CardEntry(1, "Galvantula", "Galvantula", "SFA", "2", "pokemon"),
        CardEntry(2, "Miraidon ex", "Miraidon ex", "SVI", "81", "pokemon"),
        CardEntry(2, "Iron Hands ex", "Iron Hands ex", "PAR", "70", "pokemon"),
        CardEntry(2, "Pikachu ex", "Pikachu ex", "SSP", "57", "pokemon"),
        CardEntry(1, "Iron Leaves ex", "Iron Leaves ex", "TEF", "25", "pokemon"),
        CardEntry(1, "Bloodmoon Ursaluna ex", "Ursaluna Lua Sangrenta ex", "TWM", "141", "pokemon"),
        CardEntry(1, "Lillie's Clefairy ex", "Clefairy da Lillie ex", "JTG", "56", "pokemon"),
        CardEntry(1, "Latias ex", "Latias ex", "SSP", "76", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        CardEntry(1, "Maractus", "Maractus", "JTG", "8", "pokemon"),
        # Trainers
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
        CardEntry(1, "Rescue Board", "Prancha de Resgate", "TEF", "159", "trainer"),
        CardEntry(1, "Future Booster Energy Capsule", "Capsula de Energia Potenciadora do Futuro", "TEF", "149", "trainer"),
        # Energy
        CardEntry(5, "Basic Lightning Energy", "Energia Eletrica Basica", "SVE", "4", "energy"),
        CardEntry(5, "Basic Grass Energy", "Energia Planta Basica", "SVE", "9", "energy"),
        CardEntry(2, "Basic Metal Energy", "Energia Metal Basica", "SVE", "8", "energy"),
        CardEntry(2, "Basic Psychic Energy", "Energia Psiquica Basica", "SVE", "5", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 8. FLAREON EX
# -----------------------------------------------------------------------------
META_DECKS["flareon"] = MetaDeck(
    id="flareon",
    name_en="Flareon ex",
    name_pt="Flareon ex",
    tier=2,
    description_en="Anti-meta deck that counters Metal-type decks like Gholdengo ex",
    description_pt="Deck anti-meta que countrea decks de tipo Metal como Gholdengo ex",
    strategy_en="Flareon ex deals double damage to Metal Pokemon, making it a perfect counter to Gholdengo ex. Use Eevee's energy acceleration and evolution support. Ditto can copy Flareon ex for additional attackers.",
    strategy_pt="Flareon ex causa dano dobrado a Pokemon Metal, tornando-o um counter perfeito para Gholdengo ex. Use a aceleracao de energia e suporte de evolucao do Eevee. Ditto pode copiar Flareon ex para atacantes adicionais.",
    difficulty="Beginner",
    meta_share=3.20,
    key_pokemon=["Flareon ex", "Eevee", "Ditto"],
    energy_types=["Fire"],
    strengths_en=[
        "Destroys Gholdengo ex",
        "Type advantage vs Metal",
        "Simple to play",
        "Good energy efficiency"
    ],
    strengths_pt=[
        "Destroi Gholdengo ex",
        "Vantagem de tipo contra Metal",
        "Simples de jogar",
        "Boa eficiencia de energia"
    ],
    weaknesses_en=[
        "Weak to Water",
        "Relies on matchup",
        "Limited versatility"
    ],
    weaknesses_pt=[
        "Fraco contra Agua",
        "Depende do matchup",
        "Versatilidade limitada"
    ],
    cards=[
        # Pokemon
        CardEntry(4, "Eevee", "Eevee", "MEV", "69", "pokemon"),
        CardEntry(3, "Flareon ex", "Flareon ex", "MEV", "10", "pokemon"),
        CardEntry(2, "Ditto", "Ditto", "SVI", "132", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        CardEntry(1, "Entei V", "Entei V", "BRS", "22", "pokemon"),
        # Trainers
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
        CardEntry(1, "Technical Machine: Evolution", "Maquina Tecnica: Evolucao", "PAR", "178", "trainer"),
        CardEntry(2, "Artazon", "Artazon", "PAL", "171", "trainer"),
        CardEntry(1, "Magma Basin", "Bacia de Magma", "BRS", "144", "trainer"),
        # Energy
        CardEntry(10, "Basic Fire Energy", "Energia Fogo Basica", "SVE", "2", "energy"),
        CardEntry(2, "Luminous Energy", "Energia Luminosa", "PAL", "191", "energy"),
    ]
)

# -----------------------------------------------------------------------------
# 9. MEGA DRAGONITE EX (NEW - ASCENDED HEROES)
# -----------------------------------------------------------------------------
META_DECKS["mega_dragonite"] = MetaDeck(
    id="mega_dragonite",
    name_en="Mega Dragonite ex",
    name_pt="Mega Dragonite ex",
    tier=1,
    description_en="New powerhouse from Ascended Heroes with Sky Transport ability for pivoting and massive 330 damage attacks",
    description_pt="Novo powerhouse do Ascended Heroes com habilidade Sky Transport para pivoteamento e ataques massivos de 330 de dano",
    strategy_en="Use Mega Dragonite ex's Sky Transport ability to pivot between attackers while building up energy. Ryuno Glide deals a devastating 330 damage. Dragonite V provides early game pressure while you set up. Use Rare Candy to evolve quickly.",
    strategy_pt="Use a habilidade Sky Transport do Mega Dragonite ex para pivotar entre atacantes enquanto acumula energia. Ryuno Glide causa devastadores 330 de dano. Dragonite V fornece pressao no inicio do jogo enquanto voce monta. Use Doce Raro para evoluir rapidamente.",
    difficulty="Intermediate",
    meta_share=5.50,
    key_pokemon=["Mega Dragonite ex", "Dragonite V", "Dratini", "Dragonair"],
    energy_types=["Lightning", "Water"],
    strengths_en=[
        "Massive 330 damage output",
        "Sky Transport enables flexible switching",
        "Strong against most meta decks",
        "New archetype with surprise factor"
    ],
    strengths_pt=[
        "Dano massivo de 330",
        "Sky Transport permite troca flexivel",
        "Forte contra maioria dos decks do meta",
        "Arquetipo novo com fator surpresa"
    ],
    weaknesses_en=[
        "Weak to Fairy/Dragon types",
        "Requires setup time",
        "Energy-intensive attacks"
    ],
    weaknesses_pt=[
        "Fraco contra tipos Fada/Dragao",
        "Requer tempo de setup",
        "Ataques intensivos em energia"
    ],
    cards=[
        # Pokemon
        CardEntry(3, "Dratini", "Dratini", "ASC", "140", "pokemon"),
        CardEntry(2, "Dragonair", "Dragonair", "ASC", "141", "pokemon"),
        CardEntry(3, "Mega Dragonite ex", "Mega Dragonite ex", "ASC", "142", "pokemon"),
        CardEntry(2, "Dragonite V", "Dragonite V", "SIT", "118", "pokemon"),
        CardEntry(1, "Latias ex", "Latias ex", "SSP", "76", "pokemon"),
        CardEntry(1, "Mew ex", "Mew ex", "MEW", "151", "pokemon"),
        CardEntry(1, "Fezandipiti ex", "Fezandipiti ex", "SFA", "38", "pokemon"),
        # Trainers
        CardEntry(4, "Iono", "Iono", "PAL", "185", "trainer"),
        CardEntry(4, "Arven", "Arven", "OBF", "186", "trainer"),
        CardEntry(2, "Boss's Orders", "Ordens do Chefe", "ASC", "189", "trainer"),
        CardEntry(1, "Professor's Research", "Pesquisa do Professor", "SVI", "189", "trainer"),
        CardEntry(4, "Ultra Ball", "Ultra Ball", "SVI", "196", "trainer"),
        CardEntry(4, "Rare Candy", "Doce Raro", "SVI", "191", "trainer"),
        CardEntry(3, "Nest Ball", "Nest Ball", "SVI", "181", "trainer"),
        CardEntry(2, "Night Stretcher", "Maca Noturna", "SFA", "61", "trainer"),
        CardEntry(2, "Earthen Vessel", "Vaso de Barro", "PAR", "163", "trainer"),
        CardEntry(1, "Counter Catcher", "Coletor Contador", "PAR", "160", "trainer"),
        CardEntry(1, "Switch", "Trocar", "SVI", "194", "trainer"),
        CardEntry(1, "Poke Pad", "Poke Pad", "ASC", "192", "trainer"),
        CardEntry(2, "Artazon", "Artazon", "PAL", "171", "trainer"),
        # Energy
        CardEntry(5, "Basic Lightning Energy", "Energia Eletrica Basica", "SVE", "4", "energy"),
        CardEntry(5, "Basic Water Energy", "Energia Agua Basica", "SVE", "3", "energy"),
        CardEntry(2, "Double Turbo Energy", "Energia Dupla Turbo", "BRS", "151", "energy"),
    ]
)


# =============================================================================
# MATCHUP MATRIX
# =============================================================================

# Matchup data based on tournament results and community analysis
# Win rate is from perspective of first deck (deck_a)
MATCHUPS: list[MatchupData] = [
    # Gholdengo matchups
    MatchupData("gholdengo", "dragapult", 55,
                "Gholdengo slightly favored due to OHKO potential",
                "Gholdengo levemente favorecido devido ao potencial de OHKO"),
    MatchupData("gholdengo", "gardevoir", 48,
                "Slightly unfavored but playable with good execution",
                "Levemente desfavorecido mas jogavel com boa execucao"),
    MatchupData("gholdengo", "charizard", 60,
                "Favored - can OHKO Charizard before it sets up",
                "Favorecido - pode nocautear Charizard antes de montar"),
    MatchupData("gholdengo", "raging_bolt", 50,
                "Even matchup - depends on who goes first",
                "Matchup equilibrado - depende de quem comeca"),
    MatchupData("gholdengo", "grimmsnarl", 55,
                "Slightly favored - Grimmsnarl lacks OHKOs",
                "Levemente favorecido - Grimmsnarl nao tem OHKOs"),
    MatchupData("gholdengo", "joltik_box", 52,
                "Slightly favored due to higher damage ceiling",
                "Levemente favorecido por maior teto de dano"),
    MatchupData("gholdengo", "flareon", 25,
                "Very unfavored - Flareon deals double damage",
                "Muito desfavorecido - Flareon causa dano dobrado"),

    # Dragapult matchups
    MatchupData("dragapult", "gardevoir", 40,
                "Unfavored - Gardevoir sets up too fast",
                "Desfavorecido - Gardevoir monta muito rapido"),
    MatchupData("dragapult", "charizard", 55,
                "Favored - spread damage disrupts Charizard setup",
                "Favorecido - dano espalhado atrapalha setup do Charizard"),
    MatchupData("dragapult", "raging_bolt", 45,
                "Slightly unfavored - Raging Bolt is too fast",
                "Levemente desfavorecido - Raging Bolt e muito rapido"),
    MatchupData("dragapult", "grimmsnarl", 50,
                "Even matchup - both spread damage",
                "Matchup equilibrado - ambos espalham dano"),
    MatchupData("dragapult", "joltik_box", 48,
                "Slightly unfavored - Iron Hands can snipe back",
                "Levemente desfavorecido - Iron Hands pode dar snipe de volta"),
    MatchupData("dragapult", "flareon", 55,
                "Slightly favored - Flareon lacks bench protection",
                "Levemente favorecido - Flareon nao protege banco"),

    # Gardevoir matchups
    MatchupData("gardevoir", "charizard", 45,
                "Slightly unfavored - Charizard has raw power",
                "Levemente desfavorecido - Charizard tem poder bruto"),
    MatchupData("gardevoir", "raging_bolt", 60,
                "Favored - Clefairy hits Dragon weakness",
                "Favorecido - Clefairy acerta fraqueza de Dragao"),
    MatchupData("gardevoir", "grimmsnarl", 35,
                "Very unfavored - Darkness weakness is brutal",
                "Muito desfavorecido - fraqueza Escuridao e brutal"),
    MatchupData("gardevoir", "joltik_box", 52,
                "Slightly favored - better late game",
                "Levemente favorecido - melhor final de jogo"),
    MatchupData("gardevoir", "flareon", 50,
                "Even matchup - neither has advantage",
                "Matchup equilibrado - nenhum tem vantagem"),

    # Charizard matchups
    MatchupData("charizard", "raging_bolt", 45,
                "Slightly unfavored - Raging Bolt is faster",
                "Levemente desfavorecido - Raging Bolt e mais rapido"),
    MatchupData("charizard", "grimmsnarl", 55,
                "Slightly favored - high HP survives spread",
                "Levemente favorecido - HP alto sobrevive ao spread"),
    MatchupData("charizard", "joltik_box", 50,
                "Even matchup - depends on setup speed",
                "Matchup equilibrado - depende da velocidade de setup"),
    MatchupData("charizard", "flareon", 65,
                "Favored - Flareon can't OHKO Charizard ex",
                "Favorecido - Flareon nao pode nocautear Charizard ex em um golpe"),

    # Raging Bolt matchups
    MatchupData("raging_bolt", "grimmsnarl", 60,
                "Favored - Ogerpon has type advantage",
                "Favorecido - Ogerpon tem vantagem de tipo"),
    MatchupData("raging_bolt", "joltik_box", 52,
                "Slightly favored - faster aggression",
                "Levemente favorecido - agressao mais rapida"),
    MatchupData("raging_bolt", "flareon", 55,
                "Slightly favored - can OHKO before Flareon sets up",
                "Levemente favorecido - pode nocautear antes do Flareon montar"),

    # Grimmsnarl matchups
    MatchupData("grimmsnarl", "joltik_box", 48,
                "Slightly unfavored - Joltik is too flexible",
                "Levemente desfavorecido - Joltik e muito flexivel"),
    MatchupData("grimmsnarl", "flareon", 60,
                "Favored - Froslass wears down Flareon",
                "Favorecido - Froslass desgasta Flareon"),

    # Joltik Box matchups
    MatchupData("joltik_box", "flareon", 55,
                "Slightly favored - more versatile attackers",
                "Levemente favorecido - atacantes mais versateis"),
    MatchupData("joltik_box", "mega_dragonite", 45,
                "Slightly unfavored - Dragonite's raw power is hard to handle",
                "Levemente desfavorecido - poder bruto do Dragonite e dificil de lidar"),

    # Mega Dragonite ex matchups (NEW - Ascended Heroes)
    MatchupData("mega_dragonite", "gholdengo", 48,
                "Slightly unfavored - Gholdengo's OHKO potential is problematic",
                "Levemente desfavorecido - potencial de OHKO do Gholdengo e problematico"),
    MatchupData("mega_dragonite", "dragapult", 55,
                "Favored - 330 damage OHKOs Dragapult easily",
                "Favorecido - 330 de dano nocauteia Dragapult facilmente"),
    MatchupData("mega_dragonite", "gardevoir", 35,
                "Unfavored - Gardevoir's Clefairy hits Dragon weakness",
                "Desfavorecido - Clefairy do Gardevoir acerta fraqueza de Dragao"),
    MatchupData("mega_dragonite", "charizard", 50,
                "Even matchup - both are slow setup decks",
                "Matchup equilibrado - ambos sao decks de setup lento"),
    MatchupData("mega_dragonite", "raging_bolt", 55,
                "Slightly favored - can trade efficiently with high HP",
                "Levemente favorecido - pode trocar eficientemente com HP alto"),
    MatchupData("mega_dragonite", "grimmsnarl", 52,
                "Slightly favored - Sky Transport dodges spread damage",
                "Levemente favorecido - Sky Transport evita dano espalhado"),
    MatchupData("mega_dragonite", "flareon", 60,
                "Favored - Flareon can't OHKO Mega Dragonite",
                "Favorecido - Flareon nao pode nocautear Mega Dragonite em um golpe"),
]


def get_matchup(deck_a_id: str, deck_b_id: str) -> Optional[MatchupData]:
    """Get matchup data between two decks."""
    for matchup in MATCHUPS:
        if matchup.deck_a_id == deck_a_id and matchup.deck_b_id == deck_b_id:
            return matchup
        elif matchup.deck_a_id == deck_b_id and matchup.deck_b_id == deck_a_id:
            # Return inverted matchup
            return MatchupData(
                deck_a_id=deck_b_id,
                deck_b_id=deck_a_id,
                win_rate_a=matchup.win_rate_b,
                notes_en=matchup.notes_en,
                notes_pt=matchup.notes_pt
            )
    return None


def get_deck_matchups(deck_id: str) -> list[tuple[str, float, str]]:
    """Get all matchups for a deck. Returns list of (opponent_id, win_rate, notes)."""
    matchups = []
    for other_id in META_DECKS.keys():
        if other_id == deck_id:
            continue
        matchup = get_matchup(deck_id, other_id)
        if matchup:
            matchups.append((other_id, matchup.win_rate_a, matchup.notes_en))
    return sorted(matchups, key=lambda x: -x[1])  # Sort by win rate descending


def calculate_meta_score(deck_id: str) -> float:
    """
    Calculate overall meta score for a deck based on:
    - Matchup win rates weighted by opponent's meta share
    """
    if deck_id not in META_DECKS:
        return 0.0

    total_weighted_winrate = 0.0
    total_weight = 0.0

    for other_id, other_deck in META_DECKS.items():
        if other_id == deck_id:
            continue

        matchup = get_matchup(deck_id, other_id)
        if matchup:
            weight = other_deck.meta_share
            total_weighted_winrate += matchup.win_rate_a * weight
            total_weight += weight

    if total_weight == 0:
        return 50.0

    return total_weighted_winrate / total_weight


def get_best_deck_against(opponent_ids: list[str]) -> Optional[str]:
    """Find the best deck to play against a list of opponents."""
    best_deck = None
    best_avg_winrate = 0

    for deck_id in META_DECKS.keys():
        total_winrate = 0
        count = 0

        for opp_id in opponent_ids:
            matchup = get_matchup(deck_id, opp_id)
            if matchup:
                total_winrate += matchup.win_rate_a
                count += 1

        if count > 0:
            avg_winrate = total_winrate / count
            if avg_winrate > best_avg_winrate:
                best_avg_winrate = avg_winrate
                best_deck = deck_id

    return best_deck


def get_tier_list(lang: Language = Language.EN) -> dict[int, list[MetaDeck]]:
    """Get decks organized by tier."""
    tiers: dict[int, list[MetaDeck]] = {1: [], 2: [], 3: []}

    for deck in META_DECKS.values():
        if deck.tier in tiers:
            tiers[deck.tier].append(deck)

    # Sort each tier by meta share
    for tier in tiers:
        tiers[tier].sort(key=lambda d: -d.meta_share)

    return tiers


def search_deck_by_pokemon(pokemon_name: str) -> list[MetaDeck]:
    """Find meta decks that contain a specific Pokemon."""
    pokemon_lower = pokemon_name.lower()
    results = []

    for deck in META_DECKS.values():
        # Check key pokemon
        for key_mon in deck.key_pokemon:
            if pokemon_lower in key_mon.lower():
                results.append(deck)
                break
        else:
            # Check all cards
            for card in deck.cards:
                if card.card_type == "pokemon" and pokemon_lower in card.name_en.lower():
                    results.append(deck)
                    break

    return results


def get_deck_by_id(deck_id: str) -> Optional[MetaDeck]:
    """Get a meta deck by its ID."""
    return META_DECKS.get(deck_id)


def get_all_decks() -> list[MetaDeck]:
    """Get all meta decks sorted by meta share."""
    return sorted(META_DECKS.values(), key=lambda d: -d.meta_share)


# =============================================================================
# BILINGUAL TRANSLATIONS FOR UI ELEMENTS
# =============================================================================

UI_TRANSLATIONS = {
    "en": {
        "tier": "Tier",
        "meta_share": "Meta Share",
        "difficulty": "Difficulty",
        "strategy": "Strategy",
        "strengths": "Strengths",
        "weaknesses": "Weaknesses",
        "key_pokemon": "Key Pokemon",
        "matchups": "Matchups",
        "win_rate": "Win Rate",
        "favored": "Favored",
        "unfavored": "Unfavored",
        "even": "Even",
        "deck_list": "Deck List",
        "pokemon": "Pokemon",
        "trainer": "Trainer",
        "energy": "Energy",
        "total": "Total",
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
        "vs": "vs",
        "notes": "Notes",
    },
    "pt": {
        "tier": "Tier",
        "meta_share": "Participacao no Meta",
        "difficulty": "Dificuldade",
        "strategy": "Estrategia",
        "strengths": "Pontos Fortes",
        "weaknesses": "Pontos Fracos",
        "key_pokemon": "Pokemon Chave",
        "matchups": "Confrontos",
        "win_rate": "Taxa de Vitoria",
        "favored": "Favorecido",
        "unfavored": "Desfavorecido",
        "even": "Equilibrado",
        "deck_list": "Lista do Deck",
        "pokemon": "Pokemon",
        "trainer": "Treinador",
        "energy": "Energia",
        "total": "Total",
        "beginner": "Iniciante",
        "intermediate": "Intermediario",
        "advanced": "Avancado",
        "vs": "vs",
        "notes": "Observacoes",
    }
}


def get_translation(key: str, lang: Language = Language.EN) -> str:
    """Get UI translation for a key."""
    lang_key = lang.value if isinstance(lang, Language) else lang
    return UI_TRANSLATIONS.get(lang_key, UI_TRANSLATIONS["en"]).get(key, key)


def get_difficulty_translation(difficulty: str, lang: Language = Language.EN) -> str:
    """Translate difficulty level."""
    difficulty_map = {
        "Beginner": {"en": "Beginner", "pt": "Iniciante"},
        "Intermediate": {"en": "Intermediate", "pt": "Intermediario"},
        "Advanced": {"en": "Advanced", "pt": "Avancado"},
    }
    lang_key = lang.value if isinstance(lang, Language) else lang
    return difficulty_map.get(difficulty, {}).get(lang_key, difficulty)
