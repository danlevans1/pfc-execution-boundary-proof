"""Helpers for loading example scenarios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ActionProposal, PolicySnapshot


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_action_document(path: str | Path) -> ActionProposal:
    data = load_json(path)
    return ActionProposal.from_dict(data.get("action", data))


def load_policy_document(path: str | Path) -> PolicySnapshot:
    data = load_json(path)
    return PolicySnapshot.from_dict(data.get("policy", data))


def load_scenario(path: str | Path) -> tuple[ActionProposal, PolicySnapshot]:
    data = load_json(path)
    return ActionProposal.from_dict(data["action"]), PolicySnapshot.from_dict(data["policy"])
