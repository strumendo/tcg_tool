#!/usr/bin/env python3
"""
TCG Rotation Checker - Pokemon TCG Deck Rotation Analyzer

Analyzes your deck for March 2026 rotation (regulation mark G)
and suggests substitutions from Ascended Heroes (ASC).
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
from models import CardType


console = Console()


def print_header():
    """Print application header."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]TCG Rotation Checker[/bold cyan]\n"
        "[dim]Pokemon TCG Deck Analyzer for March 2026 Rotation[/dim]",
        border_style="cyan"
    ))
    console.print()


def print_deck_summary(deck):
    """Print deck summary."""
    table = Table(title="Deck Summary", box=box.ROUNDED)
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

    # Severity color
    severity_colors = {
        "NONE": "green",
        "LOW": "green",
        "MODERATE": "yellow",
        "HIGH": "orange1",
        "CRITICAL": "red"
    }
    severity_color = severity_colors.get(summary["severity"], "white")

    # Overview panel
    overview = Text()
    overview.append(f"Impact: ", style="bold")
    overview.append(f"{summary['problem_percentage']}%", style=f"bold {severity_color}")
    overview.append(f" ({summary['severity']})\n", style=severity_color)
    overview.append(f"Rotating (March 2026): {summary['rotating_cards']} cards\n")
    if summary['illegal_cards'] > 0:
        overview.append(f"Already Illegal: {summary['illegal_cards']} cards\n", style="magenta")
    overview.append(f"Safe: {summary['safe_cards']} cards", style="green")

    console.print(Panel(overview, title="[bold]Rotation Analysis[/bold]", border_style=severity_color))
    console.print()

    # Already illegal cards (F or earlier)
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

    # Rotating cards table (G regulation)
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

    # Safe cards table
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

    # Group by type
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


def get_deck_input() -> str:
    """Get deck input from user."""
    console.print("[bold]Enter your deck (PTCGO format):[/bold]")
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


def main():
    """Main entry point."""
    print_header()

    # Get deck input
    if len(sys.argv) > 1:
        # Read from file
        filepath = sys.argv[1]
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                deck_text = f.read()
            console.print(f"[green]Loaded deck from: {filepath}[/green]")
        except FileNotFoundError:
            console.print(f"[red]File not found: {filepath}[/red]")
            sys.exit(1)
    else:
        # Interactive input
        deck_text = get_deck_input()

    if not deck_text.strip():
        console.print("[red]No deck provided. Exiting.[/red]")
        sys.exit(1)

    console.print()

    # Parse deck
    with console.status("[bold cyan]Parsing deck...[/bold cyan]"):
        deck = parse_deck(deck_text)

    if not deck.cards:
        console.print("[red]Could not parse any cards from input.[/red]")
        console.print("[dim]Make sure you're using PTCGO format: 4 Card Name SET 123[/dim]")
        sys.exit(1)

    print_deck_summary(deck)

    # Analyze rotation
    with console.status("[bold cyan]Analyzing rotation impact...[/bold cyan]"):
        report = analyze_rotation(deck)

    print_rotation_report(report)

    # Find substitutions if there are rotating cards
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

    console.print()
    console.print("[dim]Thank you for using TCG Rotation Checker![/dim]")


if __name__ == "__main__":
    main()
