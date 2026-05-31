# scene/loader.py
import json
from pathlib import Path

from nexai_sim.physics.ball import Ball
from nexai_sim.math3d.vec3 import Vec3


def load_scene(path: str) -> Ball:
    """
    Scene loader (engine front-end / data bridge).

    Converts:
        scene.json (data definition)
            ↓
        Ball object (runtime simulation entity)

    Design principles:
    - Data-driven (no hardcoded entities)
    - Engine-safe path resolution
    - Backward compatible with existing App + Renderer
    """

    # -------------------------------------------------
    # Resolve path safely (works regardless of cwd)
    # -------------------------------------------------
    scene_path = Path(path)

    if not scene_path.is_absolute():
        # Resolve relative to project package directory
        base_dir = Path(__file__).resolve().parent.parent
        scene_path = base_dir / path

    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_path}")

    # -------------------------------------------------
    # Load JSON scene data
    # -------------------------------------------------
    with open(scene_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    objects = data.get("objects", [])
    if not objects:
        raise ValueError("Scene contains no objects")

    # -------------------------------------------------
    # Current engine: single Ball entity
    # (future: multi-entity scene graph)
    # -------------------------------------------------
    obj = objects[0]

    if obj.get("type") != "ball":
        raise ValueError("Only 'ball' type is supported currently")

    ball = Ball()

    # -------- Position (render anchor) --------
    pos = obj.get("position", [0.0, 0.0, 0.0])
    if len(pos) != 3:
        raise ValueError("Position must be a 3-element array [x, y, z]")

    ball.position = Vec3(pos[0], pos[1], pos[2])

    # -------- Velocity (simulation vector) --------
    vel = obj.get("velocity", [1.2, 0.8, 0.5])
    if len(vel) != 3:
        raise ValueError("Velocity must be a 3-element array [x, y, z]")

    ball.velocity = Vec3(vel[0], vel[1], vel[2])

    # -------- Drag (simulation parameter) --------
    drag = obj.get("drag", 0.25)
    ball.drag = float(drag)

    return ball
