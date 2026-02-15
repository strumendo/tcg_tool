"""Analysis API route handlers (rotation, comparison, matchup, substitution)."""

from fastapi import APIRouter

from app.core.deck_parser import ParsedCard, ParsedDeck
from app.core.matchup_engine import analyze_matchup, compare_decks
from app.core.rotation import analyze_rotation, get_rotation_summary
from app.core.substitution_engine import find_substitutions_from_pool
from app.dependencies import DBSession
from app.schemas.analysis import (
    CompareRequest,
    DeckComparisonOut,
    MatchupAnalysisOut,
    MatchupRequest,
    RotationAnalysisRequest,
    RotationBreakdownOut,
    RotationCardOut,
    RotationReportOut,
    SharedCardOut,
    SubstitutionRequest,
    SubstitutionSuggestionOut,
    UniqueCardOut,
)
from app.services import deck_service

router = APIRouter()


def _deck_to_parsed(deck) -> ParsedDeck:
    """Convert a DB Deck model into a ParsedDeck for core analysis functions."""
    parsed = ParsedDeck()
    for dc in deck.deck_cards:
        card = dc.card
        set_code = card.card_set.code if card.card_set else "UNK"
        set_number = card.set_number or "0"
        from app.core.deck_parser import detect_card_type, detect_trainer_subtype, CardType
        from app.core.set_codes import get_regulation_mark

        card_type = detect_card_type(card.name_en or "")
        subtype = None
        if card_type == CardType.TRAINER:
            subtype = card.trainer_subtype or detect_trainer_subtype(card.name_en or "")

        parsed.cards.append(
            ParsedCard(
                name=card.name_en or card.name_pt or "Unknown",
                card_type=card_type,
                set_code=set_code,
                set_number=set_number,
                quantity=dc.quantity,
                regulation_mark=card.regulation_mark or get_regulation_mark(set_code),
                subtype=subtype,
            )
        )
    return parsed


def _parsed_card_to_out(card: ParsedCard) -> RotationCardOut:
    """Convert a ParsedCard to a RotationCardOut schema."""
    return RotationCardOut(
        name=card.name,
        set_code=card.set_code,
        set_number=card.set_number,
        quantity=card.quantity,
        regulation_mark=card.regulation_mark,
        card_type=card.card_type.value,
    )


@router.post("/rotation", response_model=RotationReportOut)
async def analyze_deck_rotation(
    db: DBSession, request: RotationAnalysisRequest
) -> RotationReportOut:
    """Perform rotation analysis on a deck."""
    deck = await deck_service.get_deck(db, request.deck_id)
    parsed = _deck_to_parsed(deck)
    report = analyze_rotation(parsed)
    summary = get_rotation_summary(report)

    rotating_cards = (
        report.rotating_pokemon + report.rotating_trainers + report.rotating_energy
    )
    safe_cards = report.safe_pokemon + report.safe_trainers + report.safe_energy

    return RotationReportOut(
        total_cards=summary["total_cards"],
        rotating_cards=summary["rotating_cards"],
        illegal_cards=summary["illegal_cards"],
        safe_cards=summary["safe_cards"],
        rotation_percentage=summary["rotation_percentage"],
        problem_percentage=summary["problem_percentage"],
        severity=summary["severity"],
        breakdown=RotationBreakdownOut(**summary["breakdown"]),
        rotating_card_list=[_parsed_card_to_out(c) for c in rotating_cards],
        safe_card_list=[_parsed_card_to_out(c) for c in safe_cards],
    )


@router.post("/compare", response_model=DeckComparisonOut)
async def compare_two_decks(
    db: DBSession, request: CompareRequest
) -> DeckComparisonOut:
    """Compare two decks and identify shared/unique cards."""
    deck_a = await deck_service.get_deck(db, request.deck_a_id)
    deck_b = await deck_service.get_deck(db, request.deck_b_id)

    parsed_a = _deck_to_parsed(deck_a)
    parsed_b = _deck_to_parsed(deck_b)

    comparison = compare_decks(
        parsed_a,
        parsed_b,
        name_a=request.deck_a_name or deck_a.name,
        name_b=request.deck_b_name or deck_b.name,
    )

    return DeckComparisonOut(
        deck_a_name=comparison.deck_a_name,
        deck_b_name=comparison.deck_b_name,
        shared_count=comparison.shared_count,
        similarity_percentage=round(comparison.similarity_percentage, 1),
        shared_cards=[
            SharedCardOut(
                name=a.name,
                quantity_a=a.quantity,
                quantity_b=b.quantity,
            )
            for a, b in comparison.shared_cards
        ],
        unique_to_a=[
            UniqueCardOut(
                name=c.name,
                quantity=c.quantity,
                card_type=c.card_type.value,
            )
            for c in comparison.unique_to_a
        ],
        unique_to_b=[
            UniqueCardOut(
                name=c.name,
                quantity=c.quantity,
                card_type=c.card_type.value,
            )
            for c in comparison.unique_to_b
        ],
    )


@router.post("/matchup", response_model=MatchupAnalysisOut)
async def analyze_deck_matchup(
    db: DBSession, request: MatchupRequest
) -> MatchupAnalysisOut:
    """Perform matchup analysis between two decks."""
    deck_a = await deck_service.get_deck(db, request.deck_a_id)
    deck_b = await deck_service.get_deck(db, request.deck_b_id)

    parsed_a = _deck_to_parsed(deck_a)
    parsed_b = _deck_to_parsed(deck_b)

    analysis = analyze_matchup(
        parsed_a,
        parsed_b,
        name_a=request.deck_a_name or deck_a.name,
        name_b=request.deck_b_name or deck_b.name,
    )

    return MatchupAnalysisOut(
        deck_a_name=analysis.deck_a_name,
        deck_b_name=analysis.deck_b_name,
        matchup_favor=analysis.matchup_favor,
        a_advantages=analysis.a_advantages,
        b_advantages=analysis.b_advantages,
        key_differences=analysis.key_differences,
        speed_score_a=analysis.speed_score_a,
        speed_score_b=analysis.speed_score_b,
        consistency_score_a=analysis.consistency_score_a,
        consistency_score_b=analysis.consistency_score_b,
        power_score_a=analysis.power_score_a,
        power_score_b=analysis.power_score_b,
    )


@router.post("/substitutions", response_model=list[SubstitutionSuggestionOut])
async def find_substitutions(
    db: DBSession, request: SubstitutionRequest
) -> list[SubstitutionSuggestionOut]:
    """Find substitution suggestions for rotating cards in a deck."""
    deck = await deck_service.get_deck(db, request.deck_id)
    parsed = _deck_to_parsed(deck)

    rotating_cards = [c for c in parsed.cards if c.is_rotating]
    safe_cards = [c for c in parsed.cards if not c.is_rotating]

    if not rotating_cards:
        return []

    substitutions = find_substitutions_from_pool(
        rotating_cards=rotating_cards,
        available_cards=safe_cards,
        min_score=request.min_score,
        max_per_card=request.max_per_card,
    )

    return [
        SubstitutionSuggestionOut(
            original_name=sub.original_card.name,
            original_set_code=sub.original_card.set_code,
            original_set_number=sub.original_card.set_number,
            suggested_name=sub.suggested_card.name,
            suggested_set_code=sub.suggested_card.set_code,
            suggested_set_number=sub.suggested_card.set_number,
            match_score=round(sub.match_score, 1),
            reasons=sub.reasons,
        )
        for sub in substitutions
    ]
