# render/mesh.py
import math
from nexai_sim.math3d.vec3 import Vec3


def generate_sphere(radius=1.0, lat_steps=16, lon_steps=16):
    """
    Generate a UV sphere mesh.

    Engine role:
    - Procedural mesh generation
    - Renderer-agnostic geometry provider
    - Reusable for multiple render backends

    Coordinate system:
    - Y axis: up/down
    - XZ plane: horizontal
    - Winding order: counter-clockwise (outward-facing)

    Args:
        radius (float): Sphere radius
        lat_steps (int): Latitude subdivisions (>= 2)
        lon_steps (int): Longitude subdivisions (>= 3)

    Returns:
        Tuple[List[Vec3], List[Tuple[int, int, int]]]
        - vertices: List of Vec3 positions
        - faces: Triangle indices (CCW winding)
    """

    # -------- Defensive validation (engine safety) --------
    if radius <= 0:
        raise ValueError("radius must be > 0")

    if lat_steps < 2 or lon_steps < 3:
        raise ValueError("lat_steps >= 2 and lon_steps >= 3 required")

    vertices = []
    faces = []

    # -------------------------------------------------
    # Generate vertices (UV sphere parameterization)
    # -------------------------------------------------
    for lat in range(lat_steps + 1):
        theta = math.pi * lat / lat_steps  # 0 -> pi
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)

        for lon in range(lon_steps):
            phi = 2.0 * math.pi * lon / lon_steps  # 0 -> 2pi
            sin_p = math.sin(phi)
            cos_p = math.cos(phi)

            x = radius * sin_t * cos_p
            y = radius * cos_t
            z = radius * sin_t * sin_p

            vertices.append(Vec3(x, y, z))

    # -------------------------------------------------
    # Generate faces (two triangles per quad)
    # -------------------------------------------------
    for lat in range(lat_steps):
        for lon in range(lon_steps):
            current = lat * lon_steps + lon
            next_lon = lat * lon_steps + (lon + 1) % lon_steps
            below = (lat + 1) * lon_steps + lon
            below_next = (lat + 1) * lon_steps + (lon + 1) % lon_steps

            # Triangle 1 (CCW)
            faces.append((current, below, next_lon))

            # Triangle 2 (CCW)
            faces.append((next_lon, below, below_next))

    # -------------------------------------------------
    # Sanity check (engine integrity guard)
    # -------------------------------------------------
    max_index = len(vertices) - 1
    for tri in faces:
        if any(i < 0 or i > max_index for i in tri):
            raise RuntimeError("Generated invalid face index")

    return vertices, faces
