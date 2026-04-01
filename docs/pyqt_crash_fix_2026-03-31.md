# PyQt Crash Fix (2026-03-31)

## Summary

Running `python main.py` could terminate with macOS `SIGABRT` (`Abort trap: 6`) in a Qt/PyQt6 event path.

The crash occurred during mouse release handling and signal/slot execution in the UI, not during ONNX conversion.

## Root Cause

Two issues combined:

1. PyQt6 coordinate type mismatch in board input handling:
   - `event.globalPosition()` returns `QPointF`.
   - `mapFromGlobal(...)` expects `QPoint`.
   - This can throw a Python exception from inside a Qt callback.

2. Unhandled exceptions in UI slot methods calling the LLM:
   - Bot calls in `update_event` and `send_message` were unguarded.
   - Exceptions raised in these callbacks can escalate through PyQt and terminate the process.

## Fixes Applied

### `ui/connect4board.py`

- Converted release position to `QPoint`:
  - `event.globalPosition().toPoint()`
- Added safe bounds checks before using computed release column.
- Wrapped mouse event callback handling in a `try/except` to prevent hard abort and reset UI state safely.
- Guarded `reset_top_button` against invalid/`None` columns.

### `ui/connect4_game_window.py`

- Wrapped bot calls in `update_event` and `send_message` with `try/except`.
- On failure, append an error message to chat instead of allowing exception propagation through Qt slots.

## Validation

Compilation sanity check:

```bash
python3 -m py_compile ui/connect4board.py ui/connect4_game_window.py main.py
```

Passed with no syntax errors.

## Clarification: ONNX/CoreML vs This Crash

This crash is separate from the ONNX/CoreML limitation documented elsewhere in this repository.

- ONNX/CoreML limitation: model/runtime compatibility and operator support constraints.
- This crash: UI event handling + unhandled exceptions in PyQt callback paths.

