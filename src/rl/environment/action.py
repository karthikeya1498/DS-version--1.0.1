"""Discrete sequential control actions used by the Phase 4 environment."""
from __future__ import annotations

from enum import IntEnum


class Action(IntEnum):
    DEFER = 0
    SERVE = 1
    REROUTE = 2
    REPOSITION = 3

ACTION_NAMES = {action.value: action.name.lower() for action in Action}
