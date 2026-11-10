"""Feature gate for the hidden MiniMax special workflow."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPECIAL_MODE_CONFIG_PATH = PROJECT_ROOT / "special-mode.cfg"


def is_special_mode_enabled() -> bool:
    """Return whether the hidden special mode is exposed for this checkout."""
    return SPECIAL_MODE_CONFIG_PATH.is_file()
