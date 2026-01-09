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
from deck_suggest import find_pokemon_cards, get_pokemon_collections, suggest_deck_for_pokemon, get_legal_status
from models import CardType


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
    console.print("[bold]Choose an option:[/bold]")
    console.print("  [cyan]1[/cyan] - Analyze rotation (March 2026)")
    console.print("  [cyan]2[/cyan] - Compare decks (matchup analysis)")
    console.print("  [cyan]3[/cyan] - Both (rotation + comparison)")
    console.print("  [cyan]4[/cyan] - Suggest deck for a Pokemon")
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


def run_deck_suggestion():
    """Run deck suggestion mode."""
    console.print()
    pokemon_name = Prompt.ask("[bold]Enter Pokemon name[/bold]")

    if not pokemon_name.strip():
        console.print("[yellow]No Pokemon name provided.[/yellow]")
        return

    # Search for Pokemon
    with console.status(f"[bold cyan]Searching for {pokemon_name}...[/bold cyan]"):
        collections = get_pokemon_collections(pokemon_name)

    if not collections:
        console.print(f"[red]No Pokemon found matching '{pokemon_name}'.[/red]")
        console.print("[dim]Try using the full name (e.g., 'Charizard' instead of 'Char').[/dim]")
        return

    # Show collections
    print_pokemon_collections(pokemon_name, collections)

    # Ask if user wants deck suggestions
    if Confirm.ask("[cyan]Would you like deck suggestions for this Pokemon?[/cyan]", default=True):
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


def main():
    """Main entry point."""
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
            return
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

    # Load main deck
    if deck_file:
        deck, deck_name = load_deck_from_file_or_input(deck_file)
        if deck is None or not deck.cards:
            console.print("[red]Could not parse deck from file.[/red]")
            sys.exit(1)
    else:
        # Interactive menu
        print_menu()
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "q"], default="1")

        if choice == "q":
            console.print("[dim]Goodbye![/dim]")
            return

        if choice == "1":
            mode = "rotation"
        elif choice == "2":
            mode = "compare"
        elif choice == "4":
            run_deck_suggestion()
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
