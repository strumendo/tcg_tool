#!/usr/bin/env python3
"""
TCG Rotation Checker - Pokemon TCG Deck Analyzer

Analyzes your deck for March 2026 rotation (regulation mark G)
and compares against other decks for matchup analysis.
"""
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

from deck_parser import parse_deck
from rotation_checker import analyze_rotation, get_rotation_summary
from substitution import find_substitutions, generate_updated_deck
from deck_compare import compare_decks, analyze_matchup, get_main_attackers
from deck_suggest import (
    find_pokemon_cards, get_pokemon_collections, suggest_deck_for_pokemon, get_legal_status,
    suggest_meta_deck_for_pokemon, get_top_meta_decks, get_deck_counter,
    format_deck_suggestion_bilingual, MetaDeckSuggestion
)
from meta_database import (
    META_DECKS, Language, get_matchup, get_deck_matchups,
    get_tier_list, get_translation, get_difficulty_translation
)
from models import CardType
from deck_builder import (
    DeckBuilderState, DeckBuilderCard, AbilityCategory,
    add_pokemon_to_deck, add_trainer_to_deck, add_energy_to_deck,
    remove_card_from_deck, analyze_all_matchups, generate_all_guides,
    calculate_overall_meta_score, get_deck_summary, get_matchup_display,
    get_guide_display, suggest_cards_for_deck, POKEMON_DATABASE,
    search_pokemon, get_all_ability_categories, ABILITY_DESCRIPTIONS
)


# Current language setting
CURRENT_LANGUAGE = Language.EN


console = Console()


def print_header():
    """Print application header."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]TCG Rotation Checker[/bold cyan]\n"
        "[dim]Pokemon TCG Deck Analyzer & Matchup Tool[/dim]",
        border_style="cyan"
    ))
    console.print()


def print_menu():
    """Print main menu options."""
    global CURRENT_LANGUAGE
    lang_label = "PT" if CURRENT_LANGUAGE == Language.PT else "EN"

    console.print("[bold]Choose an option:[/bold]")
    console.print("  [cyan]1[/cyan] - Analyze rotation (March 2026)")
    console.print("  [cyan]2[/cyan] - Compare decks (matchup analysis)")
    console.print("  [cyan]3[/cyan] - Both (rotation + comparison)")
    console.print("  [cyan]4[/cyan] - Suggest deck for a Pokemon")
    console.print("  [cyan]5[/cyan] - Browse Meta Decks (Top 8)")
    console.print("  [cyan]6[/cyan] - View Meta Matchups")
    console.print("  [cyan]7[/cyan] - [bold green]Deck Builder[/bold green] (Build + Matchups + Guides)")
    console.print(f"  [cyan]L[/cyan] - Toggle Language (Current: [yellow]{lang_label}[/yellow])")
    console.print("  [cyan]q[/cyan] - Quit")
    console.print()


def print_deck_summary(deck, title="Deck Summary"):
    """Print deck summary."""
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right", style="green")

    table.add_row("Pokemon", str(deck.pokemon_count))
    table.add_row("Trainers", str(deck.trainer_count))
    table.add_row("Energy", str(deck.energy_count))
    table.add_row("[bold]Total[/bold]", f"[bold]{deck.total_cards}[/bold]")

    console.print(table)
    console.print()


def print_rotation_report(report):
    """Print rotation analysis report."""
    summary = get_rotation_summary(report)

    severity_colors = {
        "NONE": "green",
        "LOW": "green",
        "MODERATE": "yellow",
        "HIGH": "orange1",
        "CRITICAL": "red"
    }
    severity_color = severity_colors.get(summary["severity"], "white")

    overview = Text()
    overview.append("Impact: ", style="bold")
    overview.append(f"{summary['problem_percentage']}%", style=f"bold {severity_color}")
    overview.append(f" ({summary['severity']})\n", style=severity_color)
    overview.append(f"Rotating (March 2026): {summary['rotating_cards']} cards\n")
    if summary['illegal_cards'] > 0:
        overview.append(f"Already Illegal: {summary['illegal_cards']} cards\n", style="magenta")
    overview.append(f"Safe: {summary['safe_cards']} cards", style="green")

    console.print(Panel(overview, title="[bold]Rotation Analysis[/bold]", border_style=severity_color))
    console.print()

    if report.illegal_pokemon or report.illegal_trainers or report.illegal_energy:
        table = Table(title="[magenta]Already Illegal (Regulation F or earlier)[/magenta]", box=box.ROUNDED)
        table.add_column("Qty", justify="right", style="magenta")
        table.add_column("Card Name", style="white")
        table.add_column("Set", style="dim")
        table.add_column("Reg", style="magenta")

        for card in report.illegal_pokemon + report.illegal_trainers + report.illegal_energy:
            table.add_row(
                str(card.quantity),
                card.name,
                f"{card.set_code} {card.set_number}",
                card.regulation_mark or "?"
            )

        console.print(table)
        console.print("[dim]These cards are already rotated out of Standard format.[/dim]")
        console.print()

    if report.rotating_pokemon or report.rotating_trainers or report.rotating_energy:
        table = Table(title="[red]Rotating March 2026 (Regulation G)[/red]", box=box.ROUNDED)
        table.add_column("Qty", justify="right", style="red")
        table.add_column("Card Name", style="white")
        table.add_column("Set", style="dim")
        table.add_column("Type", style="cyan")

        for card in report.rotating_pokemon:
            table.add_row(str(card.quantity), card.name, f"{card.set_code} {card.set_number}", "Pokemon")

        for card in report.rotating_trainers:
            subtype = f"({card.subtype})" if card.subtype else ""
            table.add_row(str(card.quantity), card.name, f"{card.set_code} {card.set_number}", f"Trainer {subtype}")

        for card in report.rotating_energy:
            table.add_row(str(card.quantity), card.name, f"{card.set_code} {card.set_number}", "Energy")

        console.print(table)
        console.print()

    if report.safe_pokemon or report.safe_trainers or report.safe_energy:
        table = Table(title="[green]Safe (Regulation H, I or later)[/green]", box=box.ROUNDED)
        table.add_column("Qty", justify="right", style="green")
        table.add_column("Card Name", style="white")
        table.add_column("Set", style="dim")
        table.add_column("Reg", style="cyan")

        for card in report.safe_pokemon + report.safe_trainers + report.safe_energy:
            table.add_row(
                str(card.quantity),
                card.name,
                f"{card.set_code} {card.set_number}",
                card.regulation_mark or "basic"
            )

        console.print(table)
        console.print()


def print_comparison(comparison):
    """Print deck comparison results."""
    console.print(Panel.fit(
        f"[bold cyan]Deck Comparison[/bold cyan]\n"
        f"[dim]Similarity: {comparison.similarity_percentage:.1f}%[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Shared cards
    if comparison.shared_cards:
        table = Table(title=f"[yellow]Shared Cards ({len(comparison.shared_cards)})[/yellow]", box=box.ROUNDED)
        table.add_column("Card Name", style="yellow")
        table.add_column(comparison.deck_a_name, justify="right", style="cyan")
        table.add_column(comparison.deck_b_name, justify="right", style="magenta")

        for card_a, card_b in sorted(comparison.shared_cards, key=lambda x: x[0].name):
            table.add_row(card_a.name, str(card_a.quantity), str(card_b.quantity))

        console.print(table)
        console.print()

    # Unique cards side by side
    table = Table(title="[bold]Unique Cards[/bold]", box=box.ROUNDED)
    table.add_column(f"{comparison.deck_a_name} Only", style="cyan")
    table.add_column(f"{comparison.deck_b_name} Only", style="magenta")

    unique_a = sorted(comparison.unique_to_a, key=lambda x: x.name)
    unique_b = sorted(comparison.unique_to_b, key=lambda x: x.name)

    max_len = max(len(unique_a), len(unique_b))
    for i in range(max_len):
        card_a = f"{unique_a[i].quantity}x {unique_a[i].name}" if i < len(unique_a) else ""
        card_b = f"{unique_b[i].quantity}x {unique_b[i].name}" if i < len(unique_b) else ""
        table.add_row(card_a, card_b)

    console.print(table)
    console.print()


def print_matchup_analysis(analysis):
    """Print matchup analysis results."""
    # Determine who's favored
    favor = analysis.matchup_favor
    if favor == analysis.deck_a_name:
        favor_color = "green"
        favor_text = f"[green]{favor}[/green] is favored"
    elif favor == analysis.deck_b_name:
        favor_color = "red"
        favor_text = f"[red]{favor}[/red] is favored"
    else:
        favor_color = "yellow"
        favor_text = "[yellow]Even matchup[/yellow]"

    console.print(Panel.fit(
        f"[bold]Matchup Analysis[/bold]\n{favor_text}",
        border_style=favor_color
    ))
    console.print()

    # Advantages table
    table = Table(title="[bold]Advantages[/bold]", box=box.ROUNDED)
    table.add_column(analysis.deck_a_name, style="green")
    table.add_column(analysis.deck_b_name, style="red")

    max_adv = max(len(analysis.a_advantages), len(analysis.b_advantages))
    if max_adv == 0:
        table.add_row("[dim]No clear advantages[/dim]", "[dim]No clear advantages[/dim]")
    else:
        for i in range(max_adv):
            adv_a = analysis.a_advantages[i] if i < len(analysis.a_advantages) else ""
            adv_b = analysis.b_advantages[i] if i < len(analysis.b_advantages) else ""
            table.add_row(adv_a, adv_b)

    console.print(table)
    console.print()

    # Key differences
    if analysis.key_differences:
        console.print("[bold]Key Differences:[/bold]")
        for diff in analysis.key_differences:
            console.print(f"  • {diff}")
        console.print()


def print_substitutions(substitutions):
    """Print substitution suggestions."""
    if not substitutions:
        console.print("[yellow]No substitutions found from Ascended Heroes (ASC).[/yellow]")
        console.print("[dim]The set may not be available in the API yet, or no suitable replacements were found.[/dim]")
        return

    table = Table(title="[cyan]Suggested Substitutions from Ascended Heroes[/cyan]", box=box.ROUNDED)
    table.add_column("Original Card", style="red")
    table.add_column("→", justify="center", style="dim")
    table.add_column("Suggested Replacement", style="green")
    table.add_column("Match %", justify="right", style="cyan")
    table.add_column("Reasons", style="dim")

    seen = set()
    for sub in substitutions:
        key = (sub.original_card.name, sub.suggested_card.name)
        if key in seen:
            continue
        seen.add(key)

        table.add_row(
            sub.original_card.name,
            "→",
            sub.suggested_card.name,
            f"{sub.match_score:.0f}%",
            ", ".join(sub.reasons[:2])
        )

    console.print(table)
    console.print()


def print_updated_deck(updated_cards):
    """Print updated deck list."""
    if not updated_cards:
        console.print("[yellow]No cards remaining after rotation.[/yellow]")
        return

    console.print(Panel.fit(
        "[bold green]Updated Deck (Post-Rotation)[/bold green]",
        border_style="green"
    ))
    console.print()

    pokemon = [c for c in updated_cards if c.card_type == CardType.POKEMON]
    trainers = [c for c in updated_cards if c.card_type == CardType.TRAINER]
    energy = [c for c in updated_cards if c.card_type == CardType.ENERGY]

    total = sum(c.quantity for c in updated_cards)

    if pokemon:
        console.print("[bold cyan]Pokemon:[/bold cyan]")
        for card in pokemon:
            console.print(f"  {card.quantity} {card.name} {card.set_code} {card.set_number}")
        console.print()

    if trainers:
        console.print("[bold cyan]Trainers:[/bold cyan]")
        for card in trainers:
            console.print(f"  {card.quantity} {card.name} {card.set_code} {card.set_number}")
        console.print()

    if energy:
        console.print("[bold cyan]Energy:[/bold cyan]")
        for card in energy:
            console.print(f"  {card.quantity} {card.name} {card.set_code} {card.set_number}")
        console.print()

    console.print(f"[bold]Total: {total} cards[/bold]")

    if total < 60:
        missing = 60 - total
        console.print(f"[yellow]Warning: Deck has {missing} cards missing. Consider adding more cards.[/yellow]")


def print_pokemon_collections(pokemon_name: str, collections: list[dict]):
    """Print collections where a Pokemon appears."""
    if not collections:
        console.print(f"[yellow]No cards found for '{pokemon_name}'.[/yellow]")
        return

    console.print(Panel.fit(
        f"[bold cyan]Collections for {pokemon_name}[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    table = Table(title="Available Sets", box=box.ROUNDED)
    table.add_column("Set Code", style="cyan")
    table.add_column("Set Name", style="white")
    table.add_column("Cards", justify="right", style="green")
    table.add_column("Regulation", style="yellow")
    table.add_column("Status", style="dim")

    for collection in collections:
        reg_mark = collection.get("regulation_mark", "")
        status = get_legal_status(reg_mark)

        # Color status
        if "Illegal" in status:
            status = f"[red]{status}[/red]"
        elif "Rotating" in status:
            status = f"[yellow]{status}[/yellow]"
        elif "Legal" in status:
            status = f"[green]{status}[/green]"

        table.add_row(
            collection.get("set_code", "?"),
            collection.get("set_name", "Unknown"),
            str(len(collection.get("cards", []))),
            reg_mark or "?",
            status,
        )

    console.print(table)
    console.print()

    # Show card variants
    console.print("[bold]Card Variants:[/bold]")
    for collection in collections:
        for card in collection.get("cards", []):
            variant_tags = []
            if card.get("is_ex"):
                variant_tags.append("[magenta]ex[/magenta]")
            if card.get("is_v"):
                variant_tags.append("[cyan]V[/cyan]")
            if card.get("is_vstar"):
                variant_tags.append("[yellow]VSTAR[/yellow]")
            if card.get("is_vmax"):
                variant_tags.append("[red]VMAX[/red]")

            hp_str = f"HP {card.get('hp')}" if card.get('hp') else ""
            types_str = "/".join(card.get("types", [])) if card.get("types") else ""
            tags_str = " ".join(variant_tags) if variant_tags else ""

            console.print(f"  • {card.get('name')} ({collection.get('set_code')} {card.get('number')}) {tags_str} {types_str} {hp_str}")
    console.print()


def print_deck_suggestions(pokemon_name: str, suggestions):
    """Print deck suggestions for a Pokemon."""
    if not suggestions:
        console.print(f"[yellow]No deck suggestions available for '{pokemon_name}'.[/yellow]")
        return

    console.print(Panel.fit(
        f"[bold green]Deck Suggestions for {pokemon_name}[/bold green]",
        border_style="green"
    ))
    console.print()

    for i, suggestion in enumerate(suggestions, 1):
        # Difficulty color
        diff_colors = {
            "Beginner": "green",
            "Intermediate": "yellow",
            "Advanced": "red",
        }
        diff_color = diff_colors.get(suggestion.difficulty, "white")

        console.print(Panel(
            f"[bold]{suggestion.archetype_name}[/bold]\n"
            f"[dim]{suggestion.description}[/dim]\n\n"
            f"[cyan]Difficulty:[/cyan] [{diff_color}]{suggestion.difficulty}[/{diff_color}]",
            title=f"[bold]Suggestion #{i}[/bold]",
            border_style="cyan"
        ))

        # Pokemon info
        pokemon = suggestion.pokemon
        console.print(f"[bold]Main Attacker:[/bold] {pokemon.name}")
        console.print(f"  Set: {pokemon.set_code} {pokemon.number}")
        console.print(f"  Regulation: {pokemon.regulation_mark} ({get_legal_status(pokemon.regulation_mark)})")
        if pokemon.hp:
            console.print(f"  HP: {pokemon.hp}")
        if pokemon.types:
            console.print(f"  Type: {'/'.join(pokemon.types)}")
        console.print()

        # Strategy
        console.print(f"[bold cyan]Strategy:[/bold cyan] {suggestion.strategy}")
        console.print()

        # Key cards table
        table = Table(title="[bold]Key Cards[/bold]", box=box.ROUNDED, show_header=False)
        table.add_column("Card", style="white")

        for card in suggestion.key_cards[:12]:  # Limit display
            table.add_row(card)

        console.print(table)
        console.print()

        # Energy
        console.print("[bold cyan]Energy:[/bold cyan]")
        for energy in suggestion.energy_types:
            console.print(f"  • {energy}")
        console.print()

        # Strengths and Weaknesses side by side
        str_weak_table = Table(box=box.ROUNDED, show_header=True)
        str_weak_table.add_column("Strengths", style="green")
        str_weak_table.add_column("Weaknesses", style="red")

        max_len = max(len(suggestion.strengths), len(suggestion.weaknesses))
        for j in range(max_len):
            strength = suggestion.strengths[j] if j < len(suggestion.strengths) else ""
            weakness = suggestion.weaknesses[j] if j < len(suggestion.weaknesses) else ""
            str_weak_table.add_row(strength, weakness)

        console.print(str_weak_table)
        console.print()


def print_meta_deck_detail(suggestion: MetaDeckSuggestion, lang: Language = Language.EN):
    """Print detailed meta deck information."""
    deck = suggestion.deck
    formatted = format_deck_suggestion_bilingual(suggestion, lang)

    # Difficulty color
    diff_colors = {
        "Beginner": "green", "Iniciante": "green",
        "Intermediate": "yellow", "Intermediario": "yellow",
        "Advanced": "red", "Avancado": "red",
    }
    diff_color = diff_colors.get(formatted["difficulty"], "white")

    # Header
    tier_label = get_translation("tier", lang)
    meta_label = get_translation("meta_share", lang)

    console.print(Panel(
        f"[bold]{formatted['name']}[/bold]\n"
        f"[dim]{formatted['description']}[/dim]\n\n"
        f"[cyan]{tier_label}:[/cyan] {deck.tier}  |  "
        f"[cyan]{meta_label}:[/cyan] {formatted['meta_share']}  |  "
        f"[cyan]{get_translation('difficulty', lang)}:[/cyan] [{diff_color}]{formatted['difficulty']}[/{diff_color}]",
        border_style="cyan"
    ))

    # Strategy
    console.print(f"\n[bold cyan]{get_translation('strategy', lang)}:[/bold cyan]")
    console.print(f"  {formatted['strategy']}")
    console.print()

    # Key Pokemon
    console.print(f"[bold cyan]{get_translation('key_pokemon', lang)}:[/bold cyan] {', '.join(deck.key_pokemon)}")
    console.print(f"[bold cyan]Energy:[/bold cyan] {', '.join(deck.energy_types)}")
    console.print()

    # Strengths and Weaknesses
    str_weak_table = Table(box=box.ROUNDED, show_header=True)
    str_weak_table.add_column(get_translation("strengths", lang), style="green")
    str_weak_table.add_column(get_translation("weaknesses", lang), style="red")

    max_len = max(len(formatted["strengths"]), len(formatted["weaknesses"]))
    for j in range(max_len):
        strength = formatted["strengths"][j] if j < len(formatted["strengths"]) else ""
        weakness = formatted["weaknesses"][j] if j < len(formatted["weaknesses"]) else ""
        str_weak_table.add_row(strength, weakness)

    console.print(str_weak_table)
    console.print()

    # Matchups
    if formatted["matchups"]:
        console.print(f"[bold cyan]{get_translation('matchups', lang)}:[/bold cyan]")
        matchup_table = Table(box=box.ROUNDED)
        matchup_table.add_column("vs", style="white")
        matchup_table.add_column(get_translation("win_rate", lang), justify="right", style="cyan")
        matchup_table.add_column("", style="dim")
        matchup_table.add_column(get_translation("notes", lang), style="dim")

        for opp_name, win_rate, notes in formatted["matchups"]:
            if win_rate >= 55:
                rate_color = "green"
                status = f"[green]{get_translation('favored', lang)}[/green]"
            elif win_rate <= 45:
                rate_color = "red"
                status = f"[red]{get_translation('unfavored', lang)}[/red]"
            else:
                rate_color = "yellow"
                status = f"[yellow]{get_translation('even', lang)}[/yellow]"

            matchup_table.add_row(opp_name, f"[{rate_color}]{win_rate:.0f}%[/{rate_color}]", status, notes[:50])

        console.print(matchup_table)
        console.print()


def print_meta_deck_list(suggestion: MetaDeckSuggestion, lang: Language = Language.EN):
    """Print the complete deck list for a meta deck."""
    deck = suggestion.deck

    console.print(Panel.fit(
        f"[bold green]{get_translation('deck_list', lang)} - {deck.get_name(lang)}[/bold green]",
        border_style="green"
    ))
    console.print()

    # Pokemon
    pokemon = deck.get_pokemon()
    if pokemon:
        console.print(f"[bold cyan]{get_translation('pokemon', lang)} ({sum(c.quantity for c in pokemon)}):[/bold cyan]")
        for card in pokemon:
            console.print(f"  {card.quantity} {card.get_name(lang)} {card.set_code} {card.set_number}")
        console.print()

    # Trainers
    trainers = deck.get_trainers()
    if trainers:
        console.print(f"[bold cyan]{get_translation('trainer', lang)} ({sum(c.quantity for c in trainers)}):[/bold cyan]")
        for card in trainers:
            console.print(f"  {card.quantity} {card.get_name(lang)} {card.set_code} {card.set_number}")
        console.print()

    # Energy
    energy = deck.get_energy()
    if energy:
        console.print(f"[bold cyan]{get_translation('energy', lang)} ({sum(c.quantity for c in energy)}):[/bold cyan]")
        for card in energy:
            console.print(f"  {card.quantity} {card.get_name(lang)} {card.set_code} {card.set_number}")
        console.print()

    console.print(f"[bold]{get_translation('total', lang)}: {deck.total_cards()}[/bold]")
    console.print()


def run_browse_meta_decks():
    """Browse the top 8 meta decks."""
    global CURRENT_LANGUAGE

    console.print()
    console.print(Panel.fit(
        "[bold cyan]Top 8 Meta Decks - January 2026[/bold cyan]" if CURRENT_LANGUAGE == Language.EN
        else "[bold cyan]Top 8 Decks do Meta - Janeiro 2026[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # Get top decks
    top_decks = get_top_meta_decks(8, CURRENT_LANGUAGE)

    # Display tier list
    table = Table(title="Meta Tier List", box=box.ROUNDED)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Deck", style="cyan")
    table.add_column(get_translation("tier", CURRENT_LANGUAGE), justify="center", style="yellow")
    table.add_column(get_translation("meta_share", CURRENT_LANGUAGE), justify="right", style="green")
    table.add_column(get_translation("difficulty", CURRENT_LANGUAGE), style="white")

    for i, suggestion in enumerate(top_decks, 1):
        deck = suggestion.deck
        tier_style = "green" if deck.tier == 1 else "yellow" if deck.tier == 2 else "white"

        diff = get_difficulty_translation(deck.difficulty, CURRENT_LANGUAGE)
        diff_color = "green" if "Beginner" in deck.difficulty else "yellow" if "Intermediate" in deck.difficulty else "red"

        table.add_row(
            str(i),
            deck.get_name(CURRENT_LANGUAGE),
            f"[{tier_style}]{deck.tier}[/{tier_style}]",
            f"{deck.meta_share:.1f}%",
            f"[{diff_color}]{diff}[/{diff_color}]"
        )

    console.print(table)
    console.print()

    # Ask which deck to view
    prompt_text = "Enter deck number to view details (or 'q' to go back)" if CURRENT_LANGUAGE == Language.EN else "Digite o numero do deck para ver detalhes (ou 'q' para voltar)"
    choice = Prompt.ask(prompt_text, default="q")

    if choice.lower() == "q":
        return

    try:
        deck_idx = int(choice) - 1
        if 0 <= deck_idx < len(top_decks):
            suggestion = top_decks[deck_idx]
            console.print()
            print_meta_deck_detail(suggestion, CURRENT_LANGUAGE)

            # Ask to show full deck list
            show_list_prompt = "Show complete deck list?" if CURRENT_LANGUAGE == Language.EN else "Mostrar lista completa do deck?"
            if Confirm.ask(f"[cyan]{show_list_prompt}[/cyan]", default=True):
                print_meta_deck_list(suggestion, CURRENT_LANGUAGE)

            # Ask about counter
            counter_prompt = "Find best counter deck?" if CURRENT_LANGUAGE == Language.EN else "Encontrar melhor deck counter?"
            if Confirm.ask(f"[cyan]{counter_prompt}[/cyan]", default=False):
                counter = get_deck_counter(suggestion.deck.id, CURRENT_LANGUAGE)
                if counter:
                    console.print()
                    counter_label = "Best Counter" if CURRENT_LANGUAGE == Language.EN else "Melhor Counter"
                    console.print(f"[bold green]{counter_label}: {counter.deck.get_name(CURRENT_LANGUAGE)}[/bold green]")
                    print_meta_deck_detail(counter, CURRENT_LANGUAGE)
        else:
            console.print("[yellow]Invalid selection.[/yellow]")
    except ValueError:
        console.print("[yellow]Invalid input.[/yellow]")


def run_view_matchups():
    """View matchup chart between meta decks."""
    global CURRENT_LANGUAGE

    console.print()
    title = "Meta Matchup Chart" if CURRENT_LANGUAGE == Language.EN else "Tabela de Confrontos do Meta"
    console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
    console.print()

    # Create matchup matrix table
    decks = list(META_DECKS.values())[:8]  # Top 8

    # Header
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("", style="cyan")  # Row headers

    # Add column for each deck (abbreviated)
    for deck in decks:
        name = deck.get_name(CURRENT_LANGUAGE)
        short_name = name[:12] + ".." if len(name) > 14 else name
        table.add_column(short_name, justify="center", style="white")

    # Add rows
    for row_deck in decks:
        row_name = row_deck.get_name(CURRENT_LANGUAGE)
        short_row = row_name[:12] + ".." if len(row_name) > 14 else row_name

        row_values = [f"[cyan]{short_row}[/cyan]"]

        for col_deck in decks:
            if row_deck.id == col_deck.id:
                row_values.append("[dim]-[/dim]")
            else:
                matchup = get_matchup(row_deck.id, col_deck.id)
                if matchup:
                    win_rate = matchup.win_rate_a
                    if win_rate >= 55:
                        row_values.append(f"[green]{win_rate:.0f}[/green]")
                    elif win_rate <= 45:
                        row_values.append(f"[red]{win_rate:.0f}[/red]")
                    else:
                        row_values.append(f"[yellow]{win_rate:.0f}[/yellow]")
                else:
                    row_values.append("[dim]?[/dim]")

        table.add_row(*row_values)

    console.print(table)
    console.print()

    # Legend
    legend = "[green]Green[/green]=Favored (55%+)  [yellow]Yellow[/yellow]=Even (46-54%)  [red]Red[/red]=Unfavored (45%-)" if CURRENT_LANGUAGE == Language.EN else "[green]Verde[/green]=Favorecido (55%+)  [yellow]Amarelo[/yellow]=Equilibrado (46-54%)  [red]Vermelho[/red]=Desfavorecido (45%-)"
    console.print(f"[dim]{legend}[/dim]")
    console.print()

    # Ask to view specific matchup
    prompt_text = "Enter two deck numbers to see detailed matchup (e.g., '1 3') or 'q' to go back" if CURRENT_LANGUAGE == Language.EN else "Digite dois numeros de deck para ver confronto detalhado (ex: '1 3') ou 'q' para voltar"
    choice = Prompt.ask(prompt_text, default="q")

    if choice.lower() == "q":
        return

    try:
        parts = choice.split()
        if len(parts) == 2:
            idx_a, idx_b = int(parts[0]) - 1, int(parts[1]) - 1
            if 0 <= idx_a < len(decks) and 0 <= idx_b < len(decks) and idx_a != idx_b:
                deck_a = decks[idx_a]
                deck_b = decks[idx_b]
                matchup = get_matchup(deck_a.id, deck_b.id)

                if matchup:
                    console.print()
                    console.print(Panel(
                        f"[bold]{deck_a.get_name(CURRENT_LANGUAGE)}[/bold] vs [bold]{deck_b.get_name(CURRENT_LANGUAGE)}[/bold]\n\n"
                        f"[cyan]{deck_a.get_name(CURRENT_LANGUAGE)}[/cyan] {get_translation('win_rate', CURRENT_LANGUAGE)}: "
                        f"[bold]{matchup.win_rate_a:.0f}%[/bold]\n"
                        f"[magenta]{deck_b.get_name(CURRENT_LANGUAGE)}[/magenta] {get_translation('win_rate', CURRENT_LANGUAGE)}: "
                        f"[bold]{matchup.win_rate_b:.0f}%[/bold]\n\n"
                        f"[dim]{get_translation('notes', CURRENT_LANGUAGE)}: {matchup.get_notes(CURRENT_LANGUAGE)}[/dim]",
                        title="Matchup Analysis",
                        border_style="cyan"
                    ))
                else:
                    console.print("[yellow]Matchup data not available.[/yellow]")
    except (ValueError, IndexError):
        console.print("[yellow]Invalid input.[/yellow]")


def run_deck_suggestion():
    """Run deck suggestion mode with meta integration."""
    global CURRENT_LANGUAGE

    console.print()
    prompt_text = "Enter Pokemon name" if CURRENT_LANGUAGE == Language.EN else "Digite o nome do Pokemon"
    pokemon_name = Prompt.ask(f"[bold]{prompt_text}[/bold]")

    if not pokemon_name.strip():
        msg = "No Pokemon name provided." if CURRENT_LANGUAGE == Language.EN else "Nenhum nome de Pokemon fornecido."
        console.print(f"[yellow]{msg}[/yellow]")
        return

    # First check for meta decks
    with console.status(f"[bold cyan]Searching meta decks for {pokemon_name}...[/bold cyan]"):
        meta_suggestions = suggest_meta_deck_for_pokemon(pokemon_name, CURRENT_LANGUAGE)

    if meta_suggestions:
        title = f"Meta Decks featuring {pokemon_name}" if CURRENT_LANGUAGE == Language.EN else f"Decks do Meta com {pokemon_name}"
        console.print(Panel.fit(f"[bold green]{title}[/bold green]", border_style="green"))
        console.print()

        for i, suggestion in enumerate(meta_suggestions, 1):
            deck = suggestion.deck
            console.print(f"[cyan]{i}.[/cyan] [bold]{deck.get_name(CURRENT_LANGUAGE)}[/bold] (Tier {deck.tier}, {deck.meta_share:.1f}% meta)")
            console.print(f"   {deck.get_description(CURRENT_LANGUAGE)}")
            console.print()

        prompt_text = "Enter number to view deck details (or 'c' to continue with generic suggestions)" if CURRENT_LANGUAGE == Language.EN else "Digite o numero para ver detalhes (ou 'c' para continuar com sugestoes genericas)"
        choice = Prompt.ask(prompt_text, default="1")

        if choice.lower() != "c":
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(meta_suggestions):
                    console.print()
                    print_meta_deck_detail(meta_suggestions[idx], CURRENT_LANGUAGE)

                    show_list_prompt = "Show complete deck list?" if CURRENT_LANGUAGE == Language.EN else "Mostrar lista completa do deck?"
                    if Confirm.ask(f"[cyan]{show_list_prompt}[/cyan]", default=True):
                        print_meta_deck_list(meta_suggestions[idx], CURRENT_LANGUAGE)
                    return
            except ValueError:
                pass

    # Fall back to generic suggestions
    with console.status(f"[bold cyan]Searching for {pokemon_name}...[/bold cyan]"):
        collections = get_pokemon_collections(pokemon_name)

    if not collections:
        msg = f"No Pokemon found matching '{pokemon_name}'." if CURRENT_LANGUAGE == Language.EN else f"Nenhum Pokemon encontrado para '{pokemon_name}'."
        console.print(f"[red]{msg}[/red]")
        tip = "Try using the full name (e.g., 'Charizard' instead of 'Char')." if CURRENT_LANGUAGE == Language.EN else "Tente usar o nome completo (ex: 'Charizard' em vez de 'Char')."
        console.print(f"[dim]{tip}[/dim]")
        return

    # Show collections
    print_pokemon_collections(pokemon_name, collections)

    # Ask if user wants deck suggestions
    prompt_text = "Would you like generic deck suggestions for this Pokemon?" if CURRENT_LANGUAGE == Language.EN else "Gostaria de sugestoes genericas de deck para este Pokemon?"
    if Confirm.ask(f"[cyan]{prompt_text}[/cyan]", default=True):
        with console.status("[bold cyan]Generating deck suggestions...[/bold cyan]"):
            suggestions = suggest_deck_for_pokemon(pokemon_name)

        print_deck_suggestions(pokemon_name, suggestions)


def get_deck_input(prompt_text: str = "Enter your deck") -> str:
    """Get deck input from user."""
    console.print(f"[bold]{prompt_text} (PTCGO format):[/bold]")
    console.print("[dim]Example: 4 Charizard ex OBF 125[/dim]")
    console.print("[dim]Press Enter twice when done.[/dim]")
    console.print()

    lines = []
    empty_count = 0

    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)


def load_deck_from_file_or_input(filepath: str = None, prompt: str = "Enter deck") -> tuple:
    """Load deck from file or interactive input. Returns (deck, name)."""
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                deck_text = f.read()
            console.print(f"[green]Loaded: {filepath}[/green]")
            deck = parse_deck(deck_text)
            # Use filename as deck name
            name = filepath.split("/")[-1].replace(".txt", "").replace("_", " ").title()
            return deck, name
        except FileNotFoundError:
            console.print(f"[red]File not found: {filepath}[/red]")
            return None, None
    else:
        deck_text = get_deck_input(prompt)
        if not deck_text.strip():
            return None, None
        deck = parse_deck(deck_text)
        # Try to detect deck name from main attacker
        attackers = get_main_attackers(deck)
        if attackers:
            name = attackers[0].name
        else:
            name = "Deck"
        return deck, name


def run_rotation_analysis(deck):
    """Run rotation analysis on a deck."""
    with console.status("[bold cyan]Analyzing rotation impact...[/bold cyan]"):
        report = analyze_rotation(deck)

    print_rotation_report(report)

    if report.rotating_pokemon or report.rotating_trainers:
        if Confirm.ask("[cyan]Search for substitutions from Ascended Heroes (ASC)?[/cyan]", default=True):
            with console.status("[bold cyan]Searching Ascended Heroes for substitutions...[/bold cyan]"):
                rotating_cards = report.rotating_pokemon + report.rotating_trainers
                substitutions = find_substitutions(rotating_cards, "ASC")

            print_substitutions(substitutions)

            if substitutions:
                if Confirm.ask("[cyan]Generate updated deck with substitutions?[/cyan]", default=True):
                    updated_cards = generate_updated_deck(deck.cards, substitutions)
                    print_updated_deck(updated_cards)
    else:
        console.print("[bold green]Your deck is already rotation-proof![/bold green]")


def run_deck_comparison(deck_a, name_a: str):
    """Run deck comparison mode."""
    console.print()
    console.print("[bold]Now enter the opponent/comparison deck(s).[/bold]")
    console.print("[dim]You can compare against multiple decks. Enter 'done' when finished.[/dim]")
    console.print()

    comparisons = []

    while True:
        console.print(f"[cyan]Comparison deck #{len(comparisons) + 1}[/cyan]")

        # Check if reading from file
        file_path = Prompt.ask(
            "Enter file path or 'paste' for manual input, 'done' to finish",
            default="paste"
        )

        if file_path.lower() == "done":
            break

        if file_path.lower() == "paste":
            deck_b, name_b = load_deck_from_file_or_input(None, "Enter comparison deck")
        else:
            deck_b, name_b = load_deck_from_file_or_input(file_path)

        if deck_b is None or not deck_b.cards:
            console.print("[yellow]Could not parse deck, skipping.[/yellow]")
            continue

        # Allow custom name
        custom_name = Prompt.ask(f"Deck name", default=name_b)
        name_b = custom_name

        # Run comparison
        comparison = compare_decks(deck_a, deck_b, name_a, name_b)
        analysis = analyze_matchup(deck_a, deck_b, name_a, name_b)

        comparisons.append((comparison, analysis))

        console.print()
        print_deck_summary(deck_b, f"{name_b} Summary")
        print_comparison(comparison)
        print_matchup_analysis(analysis)

        if not Confirm.ask("[cyan]Compare against another deck?[/cyan]", default=False):
            break

    # Summary if multiple comparisons
    if len(comparisons) > 1:
        console.print()
        console.print(Panel.fit("[bold]Matchup Summary[/bold]", border_style="cyan"))

        table = Table(box=box.ROUNDED)
        table.add_column("Opponent", style="white")
        table.add_column("Similarity", justify="right", style="yellow")
        table.add_column("Result", style="cyan")

        for comp, analysis in comparisons:
            favor = analysis.matchup_favor
            if favor == name_a:
                result = "[green]Favored[/green]"
            elif favor == comp.deck_b_name:
                result = "[red]Unfavored[/red]"
            else:
                result = "[yellow]Even[/yellow]"

            table.add_row(
                comp.deck_b_name,
                f"{comp.similarity_percentage:.0f}%",
                result
            )

        console.print(table)
        console.print()


def run_deck_builder():
    """Run the interactive deck builder with real-time matchup analysis."""
    global CURRENT_LANGUAGE

    console.print()
    title = "Deck Builder" if CURRENT_LANGUAGE == Language.EN else "Construtor de Deck"
    subtitle = "Build your deck and see real-time matchup analysis" if CURRENT_LANGUAGE == Language.EN else "Construa seu deck e veja analise de matchups em tempo real"
    console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]", border_style="cyan"))
    console.print()

    # Initialize deck builder state
    deck = DeckBuilderState()
    deck_name_prompt = "Enter deck name" if CURRENT_LANGUAGE == Language.EN else "Digite o nome do deck"
    deck.deck_name = Prompt.ask(deck_name_prompt, default="My Custom Deck")

    while True:
        # Show current deck status
        console.print(f"\n{'=' * 60}")
        console.print(f"[bold]{deck.deck_name}[/bold]")
        console.print(f"{'=' * 60}")

        total = deck.total_cards
        if total == 60:
            status = "[green]Valid (60 cards)[/green]"
        else:
            status = f"[yellow]{total}/60 cards[/yellow]"

        console.print(f"Status: {status}")
        console.print(f"Pokemon: {deck.pokemon_count} | Trainers: {deck.trainer_count} | Energy: {deck.energy_count}")

        if deck.deck_abilities:
            abilities_str = ", ".join([a.value for a in deck.deck_abilities[:5]])
            console.print(f"Abilities: [cyan]{abilities_str}[/cyan]")

        console.print()

        # Show deck builder menu
        menu_title = "Options" if CURRENT_LANGUAGE == Language.EN else "Opcoes"
        console.print(f"[bold]{menu_title}:[/bold]")
        console.print("  [cyan]1[/cyan] - Add Pokemon (with ability filters)")
        console.print("  [cyan]2[/cyan] - Add Trainer card")
        console.print("  [cyan]3[/cyan] - Add Energy")
        console.print("  [cyan]4[/cyan] - Remove card")
        console.print("  [cyan]5[/cyan] - View current deck")
        console.print("  [cyan]6[/cyan] - [bold green]Analyze Matchups[/bold green]")
        console.print("  [cyan]7[/cyan] - [bold green]Generate Gameplay Guides[/bold green]")
        console.print("  [cyan]8[/cyan] - Get card suggestions")
        console.print("  [cyan]9[/cyan] - Import from meta deck")
        console.print("  [cyan]q[/cyan] - Finish and exit")
        console.print()

        choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "q"], default="1")

        if choice == "q":
            break

        elif choice == "1":
            # Add Pokemon with filters
            run_add_pokemon(deck)

        elif choice == "2":
            # Add Trainer
            run_add_trainer(deck)

        elif choice == "3":
            # Add Energy
            run_add_energy(deck)

        elif choice == "4":
            # Remove card
            run_remove_card(deck)

        elif choice == "5":
            # View current deck
            run_view_deck(deck)

        elif choice == "6":
            # Analyze matchups
            run_analyze_matchups(deck)

        elif choice == "7":
            # Generate guides
            run_generate_guides(deck)

        elif choice == "8":
            # Get suggestions
            run_get_suggestions(deck)

        elif choice == "9":
            # Import from meta
            run_import_from_meta(deck)

    # Final summary
    if deck.total_cards > 0:
        console.print()
        console.print(Panel.fit("[bold green]Final Deck Summary[/bold green]", border_style="green"))
        run_view_deck(deck)
        if deck.total_cards >= 40:
            run_analyze_matchups(deck)


def run_add_pokemon(deck: DeckBuilderState):
    """Add Pokemon to deck with ability filters."""
    global CURRENT_LANGUAGE

    console.print()
    console.print("[bold]Add Pokemon[/bold]")
    console.print()

    # Show filter options
    console.print("[bold]Filter by:[/bold]")
    console.print("  [cyan]1[/cyan] - Search by name")
    console.print("  [cyan]2[/cyan] - Filter by ability category")
    console.print("  [cyan]3[/cyan] - Filter by type")
    console.print("  [cyan]4[/cyan] - Show all ex Pokemon")
    console.print("  [cyan]5[/cyan] - Show all Mega Pokemon (ASC)")
    console.print("  [cyan]6[/cyan] - Browse database")
    console.print()

    filter_choice = Prompt.ask("Select filter", choices=["1", "2", "3", "4", "5", "6"], default="1")

    results = []

    if filter_choice == "1":
        # Search by name
        name = Prompt.ask("Enter Pokemon name")
        results = search_pokemon(name=name, legal_only=True)

    elif filter_choice == "2":
        # Filter by ability
        console.print()
        console.print("[bold]Ability Categories:[/bold]")
        categories = get_all_ability_categories()
        for i, (cat, desc_en, desc_pt) in enumerate(categories, 1):
            desc = desc_en if CURRENT_LANGUAGE == Language.EN else desc_pt
            console.print(f"  [cyan]{i:2}[/cyan] - {cat.value}: {desc}")

        cat_choice = Prompt.ask("Select category number", default="1")
        try:
            idx = int(cat_choice) - 1
            if 0 <= idx < len(categories):
                selected_cat = categories[idx][0]
                results = search_pokemon(ability_category=selected_cat, legal_only=True)
        except ValueError:
            pass

    elif filter_choice == "3":
        # Filter by type
        types = ["Fire", "Water", "Grass", "Lightning", "Psychic", "Fighting", "Darkness", "Metal", "Dragon", "Colorless"]
        console.print()
        for i, t in enumerate(types, 1):
            console.print(f"  [cyan]{i:2}[/cyan] - {t}")

        type_choice = Prompt.ask("Select type number", default="1")
        try:
            idx = int(type_choice) - 1
            if 0 <= idx < len(types):
                results = search_pokemon(energy_type=types[idx], legal_only=True)
        except ValueError:
            pass

    elif filter_choice == "4":
        # Show ex Pokemon
        results = search_pokemon(is_ex=True, legal_only=True)

    elif filter_choice == "5":
        # Show Mega Pokemon
        results = search_pokemon(is_mega=True, legal_only=True)

    elif filter_choice == "6":
        # Browse all
        results = list(POKEMON_DATABASE.values())[:20]

    if not results:
        console.print("[yellow]No Pokemon found with those filters.[/yellow]")
        return

    # Display results
    console.print()
    console.print(f"[bold]Found {len(results)} Pokemon:[/bold]")

    table = Table(box=box.ROUNDED)
    table.add_column("#", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("HP", justify="right")
    table.add_column("Stage", style="white")
    table.add_column("Abilities", style="green")

    for i, pokemon in enumerate(results[:15], 1):
        abilities = [a.category.value for a in pokemon.abilities]
        abilities.extend([a.value for a in pokemon.attack_categories])
        abilities_str = ", ".join(abilities[:3]) if abilities else "-"

        stage_str = pokemon.stage
        if pokemon.is_ex:
            stage_str += " [magenta]ex[/magenta]"
        if pokemon.is_mega:
            stage_str += " [cyan]Mega[/cyan]"

        table.add_row(
            str(i),
            pokemon.name_en,
            pokemon.energy_type,
            str(pokemon.hp),
            stage_str,
            abilities_str
        )

    console.print(table)

    if len(results) > 15:
        console.print(f"[dim]Showing 15 of {len(results)} results[/dim]")

    # Select Pokemon to add
    console.print()
    select_prompt = "Enter number to add (or 'q' to cancel)" if CURRENT_LANGUAGE == Language.EN else "Digite o numero para adicionar (ou 'q' para cancelar)"
    selection = Prompt.ask(select_prompt, default="q")

    if selection.lower() == "q":
        return

    try:
        idx = int(selection) - 1
        if 0 <= idx < min(len(results), 15):
            pokemon = results[idx]
            qty = int(Prompt.ask("Quantity", default="1"))
            qty = min(4, max(1, qty))

            # Find the key in POKEMON_DATABASE
            pokemon_key = None
            for key, p in POKEMON_DATABASE.items():
                if p.name_en == pokemon.name_en and p.set_code == pokemon.set_code:
                    pokemon_key = key
                    break

            if pokemon_key and add_pokemon_to_deck(deck, pokemon_key, qty):
                console.print(f"[green]Added {qty}x {pokemon.name_en}![/green]")
            else:
                console.print("[yellow]Could not add Pokemon (maybe exceeds 4-card limit).[/yellow]")
    except ValueError:
        console.print("[yellow]Invalid selection.[/yellow]")


def run_add_trainer(deck: DeckBuilderState):
    """Add trainer card to deck."""
    global CURRENT_LANGUAGE

    console.print()
    console.print("[bold]Add Trainer Card[/bold]")
    console.print()

    # Common trainers quick-add
    console.print("[bold]Quick Add (Common Trainers):[/bold]")
    common_trainers = [
        ("Iono", "Iono", "PAL", "185", "Supporter - Shuffle and draw"),
        ("Professor's Research", "Pesquisa do Professor", "SVI", "189", "Supporter - Discard hand, draw 7"),
        ("Boss's Orders", "Ordens do Chefe", "ASC", "189", "Supporter - Gust effect"),
        ("Arven", "Arven", "OBF", "186", "Supporter - Search Item/Tool"),
        ("Ultra Ball", "Ultra Ball", "SVI", "196", "Item - Search any Pokemon"),
        ("Nest Ball", "Nest Ball", "SVI", "181", "Item - Search Basic"),
        ("Rare Candy", "Doce Raro", "SVI", "191", "Item - Skip Stage 1"),
        ("Night Stretcher", "Maca Noturna", "SFA", "61", "Item - Recover Pokemon/Energy"),
        ("Counter Catcher", "Coletor Contador", "PAR", "160", "Item - Gust when behind"),
        ("Switch", "Trocar", "SVI", "194", "Item - Switch active"),
    ]

    for i, (name_en, name_pt, set_code, num, desc) in enumerate(common_trainers, 1):
        console.print(f"  [cyan]{i:2}[/cyan] - {name_en}: [dim]{desc}[/dim]")

    console.print(f"  [cyan]{len(common_trainers) + 1:2}[/cyan] - Custom (enter manually)")
    console.print()

    choice = Prompt.ask("Select trainer", default="1")

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(common_trainers):
            name_en, name_pt, set_code, set_num, _ = common_trainers[idx]
            qty = int(Prompt.ask("Quantity", default="4"))
            qty = min(4, max(1, qty))

            if add_trainer_to_deck(deck, name_en, name_pt, set_code, set_num, qty):
                console.print(f"[green]Added {qty}x {name_en}![/green]")
            else:
                console.print("[yellow]Could not add (maybe exceeds 4-card limit).[/yellow]")
        elif idx == len(common_trainers):
            # Custom entry
            name_en = Prompt.ask("Card name (English)")
            name_pt = Prompt.ask("Card name (Portuguese)", default=name_en)
            set_code = Prompt.ask("Set code (e.g., SVI)")
            set_num = Prompt.ask("Card number")
            qty = int(Prompt.ask("Quantity", default="1"))
            qty = min(4, max(1, qty))

            if add_trainer_to_deck(deck, name_en, name_pt, set_code, set_num, qty):
                console.print(f"[green]Added {qty}x {name_en}![/green]")
    except ValueError:
        console.print("[yellow]Invalid selection.[/yellow]")


def run_add_energy(deck: DeckBuilderState):
    """Add energy to deck."""
    console.print()
    console.print("[bold]Add Energy[/bold]")
    console.print()

    energy_types = ["Fire", "Water", "Grass", "Lightning", "Psychic", "Fighting", "Darkness", "Metal", "Dragon", "Fairy"]

    for i, e in enumerate(energy_types, 1):
        console.print(f"  [cyan]{i:2}[/cyan] - Basic {e} Energy")

    console.print()
    choice = Prompt.ask("Select energy type", default="1")

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(energy_types):
            energy_type = energy_types[idx]
            qty = int(Prompt.ask("Quantity", default="8"))
            qty = max(1, qty)

            if add_energy_to_deck(deck, energy_type, qty, is_basic=True):
                console.print(f"[green]Added {qty}x Basic {energy_type} Energy![/green]")
    except ValueError:
        console.print("[yellow]Invalid selection.[/yellow]")


def run_remove_card(deck: DeckBuilderState):
    """Remove card from deck."""
    if not deck.cards:
        console.print("[yellow]Deck is empty.[/yellow]")
        return

    console.print()
    console.print("[bold]Current Cards:[/bold]")

    for i, card in enumerate(deck.cards, 1):
        console.print(f"  [cyan]{i:2}[/cyan] - {card.quantity}x {card.name_en} ({card.set_code})")

    console.print()
    choice = Prompt.ask("Enter number to remove (or 'q' to cancel)", default="q")

    if choice.lower() == "q":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(deck.cards):
            card = deck.cards[idx]
            qty = int(Prompt.ask(f"Quantity to remove (max {card.quantity})", default="1"))
            qty = min(card.quantity, max(1, qty))

            if remove_card_from_deck(deck, card.name_en, qty):
                console.print(f"[green]Removed {qty}x {card.name_en}![/green]")
    except ValueError:
        console.print("[yellow]Invalid selection.[/yellow]")


def run_view_deck(deck: DeckBuilderState):
    """View complete deck list."""
    global CURRENT_LANGUAGE
    lang = "en" if CURRENT_LANGUAGE == Language.EN else "pt"

    console.print()
    summary = get_deck_summary(deck, lang)
    console.print(summary)

    if deck.cards:
        console.print()
        console.print("[bold]Complete Card List:[/bold]")

        # Pokemon
        pokemon = [c for c in deck.cards if c.card_type == "pokemon"]
        if pokemon:
            console.print("\n[bold cyan]Pokemon:[/bold cyan]")
            for card in pokemon:
                abilities = ", ".join([a.value for a in card.abilities]) if card.abilities else ""
                console.print(f"  {card.quantity}x {card.name_en} ({card.set_code} {card.set_number}) [dim]{abilities}[/dim]")

        # Trainers
        trainers = [c for c in deck.cards if c.card_type == "trainer"]
        if trainers:
            console.print("\n[bold cyan]Trainers:[/bold cyan]")
            for card in trainers:
                console.print(f"  {card.quantity}x {card.name_en} ({card.set_code} {card.set_number})")

        # Energy
        energy = [c for c in deck.cards if c.card_type == "energy"]
        if energy:
            console.print("\n[bold cyan]Energy:[/bold cyan]")
            for card in energy:
                console.print(f"  {card.quantity}x {card.name_en}")


def run_analyze_matchups(deck: DeckBuilderState):
    """Analyze matchups against meta decks."""
    global CURRENT_LANGUAGE

    if deck.total_cards < 20:
        msg = "Add more cards to analyze matchups (minimum 20)." if CURRENT_LANGUAGE == Language.EN else "Adicione mais cartas para analisar matchups (minimo 20)."
        console.print(f"[yellow]{msg}[/yellow]")
        return

    lang = "en" if CURRENT_LANGUAGE == Language.EN else "pt"

    with console.status("[bold cyan]Analyzing matchups against meta decks...[/bold cyan]"):
        matchups = analyze_all_matchups(deck, lang)

    display = get_matchup_display(matchups, lang)
    console.print(display)

    # Show details for specific matchup
    console.print()
    prompt = "Enter opponent number for details (or 'q' to skip)" if CURRENT_LANGUAGE == Language.EN else "Digite numero do oponente para detalhes (ou 'q' para pular)"
    choice = Prompt.ask(prompt, default="q")

    if choice.lower() != "q":
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(matchups):
                matchup = matchups[idx]
                console.print()
                console.print(Panel(
                    f"[bold]vs {matchup.opponent_name}[/bold]\n"
                    f"Win Rate: {matchup.win_rate:.0f}%\n\n"
                    f"[bold]Key Factors:[/bold]\n" +
                    "\n".join([f"  - {f}" for f in matchup.key_factors]) +
                    ("\n\n[bold]Tips:[/bold]\n" + "\n".join([f"  - {t}" for t in matchup.tips_en]) if matchup.tips_en else ""),
                    border_style="cyan"
                ))
        except ValueError:
            pass


def run_generate_guides(deck: DeckBuilderState):
    """Generate gameplay guides against meta decks."""
    global CURRENT_LANGUAGE

    if deck.total_cards < 20:
        msg = "Add more cards to generate guides (minimum 20)." if CURRENT_LANGUAGE == Language.EN else "Adicione mais cartas para gerar guias (minimo 20)."
        console.print(f"[yellow]{msg}[/yellow]")
        return

    lang = "en" if CURRENT_LANGUAGE == Language.EN else "pt"

    with console.status("[bold cyan]Generating gameplay guides...[/bold cyan]"):
        matchups = analyze_all_matchups(deck, lang)
        guides = generate_all_guides(deck, matchups, lang)

    console.print()
    title = "Gameplay Guides" if CURRENT_LANGUAGE == Language.EN else "Guias de Jogo"
    console.print(Panel.fit(f"[bold green]{title}[/bold green]", border_style="green"))

    # List available guides
    console.print()
    for i, guide in enumerate(guides, 1):
        difficulty_color = "green" if guide.difficulty in ["Easy", "Facil"] else "yellow" if guide.difficulty in ["Medium", "Medio"] else "red"
        console.print(f"  [cyan]{i:2}[/cyan] - vs {guide.opponent_name} ({guide.win_rate:.0f}%) [{difficulty_color}]{guide.difficulty}[/{difficulty_color}]")

    console.print()
    prompt = "Enter number to view full guide (or 'a' for all, 'q' to skip)" if CURRENT_LANGUAGE == Language.EN else "Digite numero para ver guia completo (ou 'a' para todos, 'q' para pular)"
    choice = Prompt.ask(prompt, default="q")

    if choice.lower() == "q":
        return

    if choice.lower() == "a":
        for guide in guides:
            display = get_guide_display(guide, lang)
            console.print(display)
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(guides):
                display = get_guide_display(guides[idx], lang)
                console.print(display)
        except ValueError:
            pass


def run_get_suggestions(deck: DeckBuilderState):
    """Get card suggestions for the deck."""
    global CURRENT_LANGUAGE
    lang = "en" if CURRENT_LANGUAGE == Language.EN else "pt"

    suggestions = suggest_cards_for_deck(deck, lang)

    console.print()
    title = "Card Suggestions" if CURRENT_LANGUAGE == Language.EN else "Sugestoes de Cartas"
    console.print(Panel.fit(f"[bold green]{title}[/bold green]", border_style="green"))
    console.print()

    for category, cards in suggestions.items():
        if cards:
            cat_title = category.replace("_", " ").title()
            console.print(f"[bold cyan]{cat_title}:[/bold cyan]")
            for card_name, reason in cards:
                console.print(f"  - {card_name}: [dim]{reason}[/dim]")
            console.print()


def run_import_from_meta(deck: DeckBuilderState):
    """Import cards from a meta deck."""
    global CURRENT_LANGUAGE

    console.print()
    console.print("[bold]Import from Meta Deck[/bold]")
    console.print()

    # List meta decks
    for i, (deck_id, meta_deck) in enumerate(META_DECKS.items(), 1):
        name = meta_deck.get_name(CURRENT_LANGUAGE)
        console.print(f"  [cyan]{i:2}[/cyan] - {name} (Tier {meta_deck.tier})")

    console.print()
    choice = Prompt.ask("Select deck to import from", default="1")

    try:
        idx = int(choice) - 1
        deck_ids = list(META_DECKS.keys())
        if 0 <= idx < len(deck_ids):
            meta_deck = META_DECKS[deck_ids[idx]]

            # Import all cards
            for card_entry in meta_deck.cards:
                if card_entry.card_type == "pokemon":
                    # Try to find in database
                    pokemon_key = None
                    for key, p in POKEMON_DATABASE.items():
                        if card_entry.name_en.lower() in p.name_en.lower() and card_entry.set_code == p.set_code:
                            pokemon_key = key
                            break

                    if pokemon_key:
                        add_pokemon_to_deck(deck, pokemon_key, card_entry.quantity)
                    else:
                        # Add as generic card
                        card = DeckBuilderCard(
                            name_en=card_entry.name_en,
                            name_pt=card_entry.name_pt,
                            set_code=card_entry.set_code,
                            set_number=card_entry.set_number,
                            quantity=card_entry.quantity,
                            card_type="pokemon"
                        )
                        deck.cards.append(card)

                elif card_entry.card_type == "trainer":
                    add_trainer_to_deck(deck, card_entry.name_en, card_entry.name_pt,
                                       card_entry.set_code, card_entry.set_number, card_entry.quantity)

                elif card_entry.card_type == "energy":
                    # Parse energy type from name
                    for energy_type in ["Fire", "Water", "Grass", "Lightning", "Psychic", "Fighting", "Darkness", "Metal", "Dragon", "Fairy"]:
                        if energy_type.lower() in card_entry.name_en.lower():
                            add_energy_to_deck(deck, energy_type, card_entry.quantity)
                            break

            console.print(f"[green]Imported {meta_deck.get_name(CURRENT_LANGUAGE)}![/green]")
    except ValueError:
        console.print("[yellow]Invalid selection.[/yellow]")


def main():
    """Main entry point."""
    global CURRENT_LANGUAGE
    print_header()

    # Check for command line arguments
    deck_file = None
    compare_files = []
    mode = None
    pokemon_name = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["-r", "--rotation"]:
            mode = "rotation"
        elif arg in ["-c", "--compare"]:
            mode = "compare"
        elif arg in ["-s", "--suggest"]:
            mode = "suggest"
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                i += 1
                pokemon_name = args[i]
        elif arg in ["-h", "--help"]:
            console.print("[bold]Usage:[/bold]")
            console.print("  python main.py [deck.txt] [options]")
            console.print()
            console.print("[bold]Options:[/bold]")
            console.print("  -r, --rotation          Run rotation analysis only")
            console.print("  -c, --compare           Run deck comparison only")
            console.print("  -s, --suggest [name]    Suggest deck for a Pokemon")
            console.print("  -m, --meta              Browse top 8 meta decks")
            console.print("  --matchups              View meta matchup chart")
            console.print("  --lang [en|pt]          Set language (English/Portuguese)")
            console.print("  --vs <deck.txt>         Compare against specific deck(s)")
            console.print("  -h, --help              Show this help")
            console.print()
            console.print("[bold]Examples:[/bold]")
            console.print("  python main.py                              # Interactive mode")
            console.print("  python main.py my_deck.txt                  # Analyze deck from file")
            console.print("  python main.py my_deck.txt -c               # Compare mode")
            console.print("  python main.py my_deck.txt --vs opp.txt     # Compare against specific deck")
            console.print("  python main.py -s Charizard                 # Suggest deck for Charizard")
            console.print("  python main.py --suggest \"Pikachu ex\"       # Suggest deck for Pikachu ex")
            console.print("  python main.py -m                           # Browse meta decks")
            console.print("  python main.py --matchups                   # View matchup chart")
            console.print("  python main.py -m --lang pt                 # Meta decks in Portuguese")
            return
        elif arg in ["-m", "--meta"]:
            mode = "meta"
        elif arg == "--matchups":
            mode = "matchups"
        elif arg == "--lang":
            if i + 1 < len(args):
                i += 1
                if args[i].lower() == "pt":
                    CURRENT_LANGUAGE = Language.PT
                else:
                    CURRENT_LANGUAGE = Language.EN
        elif arg == "--vs":
            if i + 1 < len(args):
                i += 1
                compare_files.append(args[i])
        elif not arg.startswith("-"):
            if mode == "suggest" and not pokemon_name:
                pokemon_name = arg
            else:
                deck_file = arg
        i += 1

    # Handle suggest mode from command line
    if mode == "suggest":
        if pokemon_name:
            # First check for meta decks
            meta_suggestions = suggest_meta_deck_for_pokemon(pokemon_name, CURRENT_LANGUAGE)
            if meta_suggestions:
                title = f"Meta Decks featuring {pokemon_name}" if CURRENT_LANGUAGE == Language.EN else f"Decks do Meta com {pokemon_name}"
                console.print(Panel.fit(f"[bold green]{title}[/bold green]", border_style="green"))
                console.print()

                for i, suggestion in enumerate(meta_suggestions, 1):
                    deck = suggestion.deck
                    console.print(f"[cyan]{i}.[/cyan] [bold]{deck.get_name(CURRENT_LANGUAGE)}[/bold] (Tier {deck.tier}, {deck.meta_share:.1f}% meta)")
                    print_meta_deck_detail(suggestion, CURRENT_LANGUAGE)
                    print_meta_deck_list(suggestion, CURRENT_LANGUAGE)
            else:
                with console.status(f"[bold cyan]Searching for {pokemon_name}...[/bold cyan]"):
                    collections = get_pokemon_collections(pokemon_name)

                if not collections:
                    console.print(f"[red]No Pokemon found matching '{pokemon_name}'.[/red]")
                    sys.exit(1)

                print_pokemon_collections(pokemon_name, collections)

                with console.status("[bold cyan]Generating deck suggestions...[/bold cyan]"):
                    suggestions = suggest_deck_for_pokemon(pokemon_name)

                print_deck_suggestions(pokemon_name, suggestions)
        else:
            run_deck_suggestion()

        console.print()
        console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")
        return

    # Handle meta mode from command line
    if mode == "meta":
        run_browse_meta_decks()
        console.print()
        console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")
        return

    # Handle matchups mode from command line
    if mode == "matchups":
        run_view_matchups()
        console.print()
        console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")
        return

    # Load main deck
    if deck_file:
        deck, deck_name = load_deck_from_file_or_input(deck_file)
        if deck is None or not deck.cards:
            console.print("[red]Could not parse deck from file.[/red]")
            sys.exit(1)
    else:
        # Interactive menu
        print_menu()
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6", "7", "l", "L", "q"], default="1")

        if choice.lower() == "q":
            console.print("[dim]Goodbye![/dim]")
            return

        if choice.lower() == "l":
            # Toggle language
            CURRENT_LANGUAGE = Language.PT if CURRENT_LANGUAGE == Language.EN else Language.EN
            lang_msg = "Language changed to Portuguese" if CURRENT_LANGUAGE == Language.PT else "Language changed to English"
            console.print(f"[green]{lang_msg}[/green]")
            console.print()
            print_menu()
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6", "7", "l", "q"], default="1")

        if choice == "1":
            mode = "rotation"
        elif choice == "2":
            mode = "compare"
        elif choice == "4":
            run_deck_suggestion()
            console.print()
            console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")
            return
        elif choice == "5":
            run_browse_meta_decks()
            console.print()
            console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")
            return
        elif choice == "6":
            run_view_matchups()
            console.print()
            console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")
            return
        elif choice == "7":
            run_deck_builder()
            console.print()
            console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")
            return
        else:
            mode = "both"

        deck, deck_name = load_deck_from_file_or_input(None, "Enter your deck")
        if deck is None or not deck.cards:
            console.print("[red]Could not parse any cards from input.[/red]")
            console.print("[dim]Make sure you're using PTCGO format: 4 Card Name SET 123[/dim]")
            sys.exit(1)

    console.print()
    print_deck_summary(deck, f"{deck_name} Summary")

    # Determine mode if not set
    if mode is None:
        if compare_files:
            mode = "compare"
        else:
            mode = "both"

    # Run rotation analysis
    if mode in ["rotation", "both"]:
        run_rotation_analysis(deck)

    # Run comparison
    if mode in ["compare", "both"]:
        if compare_files:
            # Compare against specified files
            for comp_file in compare_files:
                comp_deck, comp_name = load_deck_from_file_or_input(comp_file)
                if comp_deck and comp_deck.cards:
                    console.print()
                    print_deck_summary(comp_deck, f"{comp_name} Summary")
                    comparison = compare_decks(deck, comp_deck, deck_name, comp_name)
                    analysis = analyze_matchup(deck, comp_deck, deck_name, comp_name)
                    print_comparison(comparison)
                    print_matchup_analysis(analysis)
        else:
            # Interactive comparison
            if Confirm.ask("[cyan]Compare against other decks?[/cyan]", default=True):
                run_deck_comparison(deck, deck_name)

    console.print()
    console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")


if __name__ == "__main__":
    main()
