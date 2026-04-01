# Narrative Coherence Controls

## Problem

During longer games, responses became less natural:
- repetitive tone loops,
- occasional chopped endings,
- weak correlation to move quality.

## Root Causes

1. Prompts did not enforce a stable story arc.
2. Generation style allowed long, drifting outputs.
3. Raw model output occasionally contained partial or duplicated speaker labels.

## Implemented Fixes

### 1) Narrative Director

Added `game/narrative_director.py` to control:
- opening premise,
- mid-game progression by move quality (`good` / `mediocre` / `bad`),
- ending beat when game result is known.

### 2) Move-Quality Prompt Steering

`ui/connect4_game_window.py` now uses narrative-director prompts instead of generic move text.
Each move includes:
- current phase (`opening`, `midgame`, `endgame`),
- quality cue,
- rolling quality counts for continuity.

### 3) Response Normalization

`ai/ollama/llama_bot.py` now normalizes output to:
- remove accidental `Gemma:` / `assistant:` prefixes,
- collapse whitespace,
- trim to last complete sentence when possible,
- ensure sentence-ending punctuation.

### 4) Ending Signal

`ui/connect4board.py` now emits `gameEnded` signal (`winner=YOU`, `winner=Computer`, or `draw`)
so the narrator can produce a closing paragraph.

## Performance Notes

Instrumentation shows minimax is not the latency bottleneck:
- move eval and AI move selection are typically sub-150ms.
- LLM generation (`llm_chat_ms`) dominates end-to-end delay.

## Practical Guidance

- Keep responses short (2-4 sentences) for lower latency and better consistency.
- Use move-quality guidance to make reactions feel grounded in gameplay.
- Keep history bounded to avoid prompt bloat and style drift.

## Player-Reaction Design Choice

Question: should the human side also auto-generate a response every move?

Recommended default:
- Keep Gemma as the only per-move LLM narrator.
- Use template/rule-based player reactions (optional) keyed on move quality.

Why:
- A second per-move LLM call usually doubles generation cost and pushes latency up.
- It accelerates chat-history growth, increasing memory use and context drift.
- It can reduce narrative coherence by introducing competing generated voices.

When to use LLM player text:
- Only when the user explicitly types or speaks a message.
- Optionally in "cinematic mode" behind a feature flag with tighter token limits.
