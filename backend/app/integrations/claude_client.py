"""Anthropic Claude API integration for AI-powered TCG analysis."""

import anthropic

from app.config import settings


class ClaudeClient:
    """Anthropic Claude API integration for AI-powered TCG analysis."""

    def __init__(self) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def chat(
        self,
        message: str,
        system_context: str = "",
        history: list[dict] | None = None,
    ) -> str:
        """Send a chat message with optional system context and history."""
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system_context or self._default_system_prompt(),
            messages=messages,
        )
        return response.content[0].text

    async def chat_stream(
        self,
        message: str,
        system_context: str = "",
        history: list[dict] | None = None,
    ):
        """Stream a chat response. Yields text chunks."""
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        async with self.client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system_context or self._default_system_prompt(),
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def suggest_swaps(self, deck_info: dict, meta_context: dict) -> str:
        """AI-powered card swap suggestions."""
        prompt = self._build_swap_prompt(deck_info, meta_context)
        return await self.chat(prompt, self._swap_system_prompt())

    async def analyze_battle(self, battle_data: dict) -> str:
        """Generate insights from battle data."""
        prompt = self._build_battle_prompt(battle_data)
        return await self.chat(prompt, self._battle_system_prompt())

    async def simulate_plays(
        self, deck_info: dict, opponent_info: dict, turns: int = 6
    ) -> str:
        """Simulate optimal play sequence."""
        prompt = self._build_simulation_prompt(deck_info, opponent_info, turns)
        return await self.chat(prompt, self._simulation_system_prompt())

    # ------------------------------------------------------------------
    # System prompts
    # ------------------------------------------------------------------

    def _default_system_prompt(self) -> str:
        return (
            "You are a Pokemon TCG expert assistant. You help players with deck building, "
            "strategy analysis, card substitutions, and competitive play advice. "
            "You are knowledgeable about the current Standard format (March 2026 rotation), "
            "meta decks, matchups, and card interactions. "
            "Respond in the same language as the user's message."
        )

    def _swap_system_prompt(self) -> str:
        return (
            "You are a Pokemon TCG deck optimization expert. Analyze the deck and suggest "
            "card swaps that improve the deck's performance. Consider rotation legality, "
            "meta matchups, consistency, and synergy. Return structured JSON with suggestions."
        )

    def _battle_system_prompt(self) -> str:
        return (
            "You are a Pokemon TCG battle analyst. Analyze the battle record and provide "
            "insights on play decisions, missed opportunities, and strategic improvements."
        )

    def _simulation_system_prompt(self) -> str:
        return (
            "You are a Pokemon TCG play sequence simulator. Given two deck lists, "
            "simulate optimal play sequences turn by turn. Consider common opening hands, "
            "setup sequences, and win conditions."
        )

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def _build_swap_prompt(self, deck_info: dict, meta_context: dict) -> str:
        return (
            "Analyze this deck and suggest optimal card swaps:\n\n"
            f"Deck: {deck_info}\n\n"
            f"Meta Context: {meta_context}"
        )

    def _build_battle_prompt(self, battle_data: dict) -> str:
        return (
            "Analyze this battle record and provide strategic insights:\n\n"
            f"{battle_data}"
        )

    def _build_simulation_prompt(
        self, deck_info: dict, opponent_info: dict, turns: int
    ) -> str:
        return (
            f"Simulate {turns} turns of play:\n\n"
            f"Your deck: {deck_info}\n\n"
            f"Opponent: {opponent_info}"
        )
