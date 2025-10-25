# -*- coding: utf-8 -*-
"""
Fungal hyphae network growth over a surface.

Library-agnostic core algorithm that relies on a minimal surface adapter
interface provided by the caller (e.g., Grasshopper/Rhino wrapper).

Adapter protocol (duck-typed):
    - closest_uv_of_point(pt3: (x,y,z)) -> (u, v)
    - point_at(u: float, v: float) -> (x, y, z)
    - frame_at(u: float, v: float) -> (t1, t2, n)
        where t1, t2, n are orthonormal 3D vectors (tuples), with n normal,
        and t1/t2 spanning the tangent plane.
    - Optional: step(u, v, dir_world, step_length) -> (u2, v2, p2)
        If not present, a fallback will: p + dir*L then project to surface.

The algorithm maintains active hyphal tips on the surface, represented by
surface params (u, v) and a world-space tangent direction vector. Each
iteration extends each tip by a step along the surface, possibly branching
probabilistically, and records edges as world-space segments.
"""

import math
import random


def grow_fungal_network(
    surface_adapter,
    spores,
    iterations=200,
    step_length=1.0,
    branch_probability=0.2,
    angle_spread=30.0,
    terminate_probability=0.0,
    min_spacing=0.0,
    nutrient_fn=None,
    seed=None,
):
    """
    Grow a fungal-like network over a surface.

    Parameters
    ----------
    surface_adapter : object
        Object implementing the adapter protocol (closest_uv_of_point, point_at,
        frame_at, optional step). See module docstring.
    spores : sequence of (x, y, z)
        Initial world-space starting points; they will be projected to the surface.
    iterations : int
        Number of growth iterations.
    step_length : float
        Length of a single hyphal extension per iteration.
    branch_probability : float
        Probability that a tip branches into two children (else one).
    angle_spread : float
        Max angular deviation (degrees) in the tangent plane for child directions.
    terminate_probability : float
        Probability that a tip terminates (dies) instead of continuing.
    min_spacing : float
        If > 0, prevents new tips forming within this distance of existing
        nodes (simple crowding control).
    nutrient_fn : (u, v) -> scalar, optional
        If provided, modulates local step length (scaled by 0.5..1.5) and
        branching probability (+/-25%) based on returned value in [0,1]. Values
        outside are clamped.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    list of ((x,y,z), (x,y,z))
        World-space line segments representing hyphae edges.
    """
    if seed is not None:
        random.seed(seed)

    angle_rad = math.radians(angle_spread)
    min_spacing_sq = max(0.0, float(min_spacing)) ** 2

    # Active tips: (u, v, dir_world_vec)
    tips = []  # (u, v, dir_world_vec)
    nodes = []  # for crowding checks, world-space points
    segments = []

    # Initialize tips from spores
    for sp in spores:
        u, v = surface_adapter.closest_uv_of_point(sp)
        # Choose an arbitrary tangent direction at (u, v)
        t1, t2, n = surface_adapter.frame_at(u, v)
        # Random direction in tangent plane
        theta = random.uniform(0, 2 * math.pi)
        dir_world = normalize(
            (
                t1[0] * math.cos(theta) + t2[0] * math.sin(theta),
                t1[1] * math.cos(theta) + t2[1] * math.sin(theta),
                t1[2] * math.cos(theta) + t2[2] * math.sin(theta),
            )
        )
        tips.append((u, v, dir_world))
        nodes.append(surface_adapter.point_at(u, v))

    for _ in range(max(0, int(iterations))):
        new_tips = []

        for u, v, d in tips:
            # Termination?
            if random.random() < terminate_probability:
                continue

            # Nutrient modulation
            branch_p = branch_probability
            step_len = step_length
            if nutrient_fn is not None:
                val = clamp01(nutrient_fn(u, v))
                # Scale branching prob by +/- 25%
                branch_p = clamp01(branch_probability * (0.75 + 0.5 * val))
                # Scale step length by 0.5..1.5x
                step_len = step_length * (0.5 + val)

            num_children = 2 if random.random() < branch_p else 1
            # Optionally occasionally zero children if terminate_probability > 0

            for _child in range(num_children):
                # Perturb direction within tangent plane
                t1, t2, n = surface_adapter.frame_at(u, v)
                d_tangent = project_onto_plane(d, n)
                d_tangent = normalize(d_tangent)
                # Random rotation in plane: choose random angle within +/- angle_spread
                phi = random.uniform(-angle_rad, angle_rad)
                # Represent d in (t1, t2) basis, rotate, then go back to world
                a = dot(d_tangent, t1)
                b = dot(d_tangent, t2)
                # Rotate (a, b)
                cos_p = math.cos(phi)
                sin_p = math.sin(phi)
                a2 = a * cos_p - b * sin_p
                b2 = a * sin_p + b * cos_p
                new_dir = normalize(
                    (
                        t1[0] * a2 + t2[0] * b2,
                        t1[1] * a2 + t2[1] * b2,
                        t1[2] * a2 + t2[2] * b2,
                    )
                )

                # Step along the surface
                p_cur = surface_adapter.point_at(u, v)
                if hasattr(surface_adapter, "step"):
                    u2, v2, p_next = surface_adapter.step(u, v, new_dir, step_len)
                else:
                    # Fallback: move in world, project to surface
                    p_guess = (
                        p_cur[0] + new_dir[0] * step_len,
                        p_cur[1] + new_dir[1] * step_len,
                        p_cur[2] + new_dir[2] * step_len,
                    )
                    u2, v2 = surface_adapter.closest_uv_of_point(p_guess)
                    p_next = surface_adapter.point_at(u2, v2)

                # Crowding: reject if too close to existing nodes
                if min_spacing_sq > 0.0 and nodes:
                    if any(dist_sq(p_next, q) < min_spacing_sq for q in nodes):
                        continue

                # Accept segment and new tip
                segments.append((p_cur, p_next))
                nodes.append(p_next)
                new_tips.append((u2, v2, new_dir))

        tips = new_tips
        if not tips:
            break

    return segments


# -----------------------------
# Vector helpers (pure Python)
# -----------------------------

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def length_sq(v):
    return dot(v, v)


def length(v):
    return math.sqrt(length_sq(v))


def normalize(v):
    m = length(v)
    if m <= 1e-12:
        return (1.0, 0.0, 0.0)
    return (v[0] / m, v[1] / m, v[2] / m)


def project_onto_plane(v, n):
    # Remove normal component from v
    k = dot(v, n)
    return (v[0] - k * n[0], v[1] - k * n[1], v[2] - k * n[2])


def dist_sq(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return dx * dx + dy * dy + dz * dz


def clamp01(x):
    return max(0.0, min(1.0, float(x)))


# -----------------------------
# Optional: simple plane adapter
# -----------------------------

class XYPlaneAdapter(object):
    """
    Simple surface adapter for the XY plane (z = 0) for quick testing
    without Rhino. Uses (u, v) = (x, y).
    """

    def closest_uv_of_point(self, p):
        return (float(p[0]), float(p[1]))

    def point_at(self, u, v):
        return (float(u), float(v), 0.0)

    def frame_at(self, u, v):
        t1 = (1.0, 0.0, 0.0)
        t2 = (0.0, 1.0, 0.0)
        n = (0.0, 0.0, 1.0)
        return (t1, t2, n)

    def step(self, u, v, d, L):
        # Already planar; just move in XY then clamp z=0
        p = self.point_at(u, v)
        p2 = (p[0] + d[0] * L, p[1] + d[1] * L, 0.0)
        u2, v2 = self.closest_uv_of_point(p2)
        return (u2, v2, p2)



