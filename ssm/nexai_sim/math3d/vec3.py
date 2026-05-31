# math3d/vec3.py
import math


class Vec3:
    """
    Minimal 3D vector class.

    Used for:
    - Positions
    - Velocities
    - Directions
    - Display-only state

    Design goals:
    - Lightweight (no matrices, no heavy ops)
    - Deterministic behavior for simulation
    - Safe scalar math for engine usage
    """

    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # -------------------------------------------------
    # Basic arithmetic
    # -------------------------------------------------
    def __add__(self, other):
        if not isinstance(other, Vec3):
            return NotImplemented
        return Vec3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other):
        if not isinstance(other, Vec3):
            return NotImplemented
        return Vec3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def __mul__(self, scalar: float):
        # Defensive: ensure scalar math only
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vec3(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar
        )

    def __rmul__(self, scalar: float):
        return self.__mul__(scalar)

    # -------------------------------------------------
    # Vector math
    # -------------------------------------------------
    def magnitude(self):
        """Return Euclidean magnitude of the vector."""
        return math.sqrt(
            self.x * self.x +
            self.y * self.y +
            self.z * self.z
        )

    def normalized(self):
        """Return a normalized copy of the vector."""
        mag = self.magnitude()
        if mag == 0.0:
            return Vec3(0.0, 0.0, 0.0)
        return self * (1.0 / mag)

    # -------------------------------------------------
    # Utilities
    # -------------------------------------------------
    def copy(self):
        """Return a shallow copy of the vector."""
        return Vec3(self.x, self.y, self.z)

    def to_tuple(self):
        """Convert vector to tuple (x, y, z)."""
        return (self.x, self.y, self.z)

    # -------------------------------------------------
    # Debug / Representation
    # -------------------------------------------------
    def __repr__(self):
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
