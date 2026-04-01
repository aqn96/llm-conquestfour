class NarrativeDirector:
    """Controls a simple narrative arc for move-by-move LLM commentary."""

    def __init__(self, *, theme, personality, bot_name, player_name):
        self.theme = (theme or "Default").strip()
        self.personality = (personality or "Neutral").strip()
        self.bot_name = (bot_name or "Narrator").strip()
        self.player_name = (player_name or "Player").strip()
        self.turn_count = 0
        self.quality_counts = {"good": 0, "mediocre": 0, "bad": 0}
        self._premise = self._build_premise()

    def _build_premise(self):
        return (
            f"Story premise: {self.bot_name} and {self.player_name} are in a {self.theme} setting. "
            f"The narrator voice is {self.personality}. Keep continuity with this premise."
        )

    def opening_prompt(self):
        return (
            f"{self._premise} Start the opening beat before the first move. "
            "Write one short paragraph (2-4 sentences, under 80 words) with complete sentences."
        )

    def build_move_prompt(self, move_quality):
        quality = (move_quality or "").strip().lower()
        if quality not in self.quality_counts:
            quality = "mediocre"

        self.turn_count += 1
        self.quality_counts[quality] += 1

        phase = "opening"
        if self.turn_count >= 10:
            phase = "endgame"
        elif self.turn_count >= 5:
            phase = "midgame"

        phase_cue = {
            "opening": "Establish tone and early stakes.",
            "midgame": "Escalate tension and track momentum shifts.",
            "endgame": "Focus on payoff, pressure, and near-term consequences.",
        }[phase]

        quality_cue = {
            "good": "The player made a strong move. Show respect and rising tension.",
            "mediocre": "The player made a workable move. Mention one missed opportunity.",
            "bad": "The player made a weak move. Highlight the opening this creates.",
        }[quality]

        return (
            f"{self._premise} Current phase: {phase}. {phase_cue} "
            f"Move quality: {quality}. {quality_cue} "
            f"State so far: good={self.quality_counts['good']}, "
            f"mediocre={self.quality_counts['mediocre']}, bad={self.quality_counts['bad']}. "
            "Write one short paragraph (2-4 sentences, under 80 words) with complete sentences."
        )

    def ending_prompt(self, result):
        return (
            f"{self._premise} The game has ended: {result}. "
            f"Total move-quality summary: good={self.quality_counts['good']}, "
            f"mediocre={self.quality_counts['mediocre']}, bad={self.quality_counts['bad']}. "
            "Write a closing beat in one short paragraph (2-4 sentences, under 80 words) "
            "that feels conclusive and consistent with prior tone."
        )
