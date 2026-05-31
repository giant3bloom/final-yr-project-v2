# render/projection.py

def project(point, width, height, scale, camera_z=5.0):
    """
    Simple perspective projection (engine utility).

    Role in rendering pipeline:
    - Converts 3D world-space Vec3 → 2D screen coordinates
    - Stateless and renderer-agnostic
    - Safe for data-driven scenes

    Args:
        point: Vec3 in world space
        width (int): Screen width in pixels
        height (int): Screen height in pixels
        scale (float): Projection scale factor (zoom)
        camera_z (float): Camera distance from origin along +Z axis

    Returns:
        Tuple[int, int]: (x, y) screen coordinates
    """

    # Defensive: minimal validation for engine safety
    if width <= 0 or height <= 0:
        return 0, 0

    # Depth relative to camera (simple camera model)
    z = point.z + camera_z

    # Prevent division by zero / near-plane distortion
    if z < 1e-4:
        z = 1e-4

    # Perspective scaling factor
    factor = scale / z

    # Convert to screen space (centered projection)
    x = int(width * 0.5 + point.x * factor)
    y = int(height * 0.5 - point.y * factor)

    return x, y
