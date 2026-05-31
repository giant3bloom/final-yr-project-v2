"""
SSM (System-Specific Model) — intermediate representation for NexAI entities.

Each entity describes structure and behavior without rendering logic.
The status shower interprets the nexai_status_shower SSM at runtime.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from config import STATUS_HOST, STATUS_PORT


def _nexai_status_shower() -> dict[str, Any]:
    return {
        "id": "nexai_status_shower_001",
        "type": "process_monitor",
        "role": "live_optimizer_dashboard",
        "geometry": {
            "layout": "vertical",
            "width": 520,
            "height": 640,
            "panels": ["header", "phase", "score", "log"],
        },
        "appearance": {
            "title": "NexAI Optimizer",
            "theme": "dark",
            "success_color": "#2ecc71",
            "failure_color": "#e74c3c",
            "idle_color": "#95a5a6",
            "font_family": "Segoe UI",
            "font_size": 10,
        },
        "dynamics": {
            "lifecycle": "child_process",
            "transport": "tcp",
            "host": STATUS_HOST,
            "port": STATUS_PORT,
            "message_format": "json",
            "fields": ["text", "status", "phase", "score", "error"],
        },
        "state": {
            "phase": "idle",
            "current_step": None,
            "score": None,
            "last_error": None,
            "history_limit": 200,
        },
    }


def _blue_ball() -> dict[str, Any]:
    return {
        "id": "blue_ball_001",
        "type": "agent",
        "geometry": {"shape": "sphere", "radius": 0.3},
        "position": {"row": 0, "col": 0, "z": 0},
        "appearance": {"color": "blue", "opacity": 1.0},
        "dynamics": {
            "moves": ["up", "down", "left", "right"],
            "speed": 1,
        },
        "state": {"discovered_map": None},
    }


_REGISTRY: dict[str, callable] = {
    "nexai_status_shower": _nexai_status_shower,
    "blue_ball": _blue_ball,
}


def get_ssm(entity: str) -> dict[str, Any]:
    """Return a deep copy of the SSM for the requested entity."""
    factory = _REGISTRY.get(entity)
    if factory is None:
        raise ValueError(f"No SSM available for entity '{entity}'")
    return deepcopy(factory())


def list_entities() -> list[str]:
    return sorted(_REGISTRY.keys())
