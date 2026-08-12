from __future__ import annotations

import json
import os
from pathlib import Path

from .domain import Household


def save_path() -> Path:
    configured = os.environ.get("CODEPET_SAVE")
    return Path(configured).expanduser() if configured else Path.home() / ".codepet" / "save.json"


def load(path: Path | None = None) -> Household | None:
    path = path or save_path()
    if not path.exists():
        return None
    try:
        household = Household.from_dict(json.loads(path.read_text(encoding="utf-8")))
        household.apply_time_decay()
        return household
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read save data: {exc}") from exc


def write(household: Household, path: Path | None = None) -> None:
    path = path or save_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(household.to_dict(), indent=2), encoding="utf-8")
    temporary.replace(path)
