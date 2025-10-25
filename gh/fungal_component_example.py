"""
GhPython component example: Fungal network growth over a surface.

INPUTS:
  S: Surface or Brep (the surface to colonize)
  spores: List of Point3d start locations (world-space)
  iterations: int - growth iterations (default 200)
  step_length: float - extension length per step (default 1.0)
  branch_probability: float - probability of branching (0..1, default 0.2)
  angle_spread: float - max in-plane deviation angle in degrees (default 30)
  terminate_probability: float - probability of tip termination (default 0)
  min_spacing: float - crowding distance; <=0 disables (default 0)
  seed: int - random seed (optional)

OUTPUTS:
  curves: Curve list (LineCurve) lying on the surface
  edges_raw: List of ((x,y,z),(x,y,z)) tuples for analysis/debug
"""

import sys
import os
import Rhino.Geometry as rg


# Add repo python/ dir to path
def _add_repo_python():
    gh_doc = ghenv.Component.OnPingDocument()
    if not gh_doc:
        return
    gh_file = gh_doc.FilePath
    if not gh_file:
        return
    gh_dir = os.path.dirname(gh_file)
    repo_root = os.path.dirname(gh_dir) if os.path.basename(gh_dir).lower() == 'gh' else gh_dir
    py_dir = os.path.join(repo_root, 'python')
    if os.path.isdir(py_dir) and py_dir not in sys.path:
        sys.path.insert(0, py_dir)


_add_repo_python()

from coral.growth_models.fungal_surface import grow_fungal_network


def _as_float(v, d):
    try:
        return float(v) if v is not None else d
    except Exception:
        return d


def _as_int(v, d):
    try:
        return int(round(float(v))) if v is not None else d
    except Exception:
        return d


def _as_prob(v, d):
    try:
        x = float(v)
    except Exception:
        x = d
    return max(0.0, min(1.0, x))


class RhinoSurfaceAdapter(object):
    def __init__(self, surface_like):
        # Accept Surface, Brep, or BrepFace
        if isinstance(surface_like, rg.Brep):
            # Use first face
            if surface_like.Faces.Count == 0:
                raise ValueError("Brep has no faces")
            self.srf = surface_like.Faces[0]
            self.srf = self.srf.ToNurbsSurface()
        elif isinstance(surface_like, rg.BrepFace):
            self.srf = surface_like.ToNurbsSurface()
        elif isinstance(surface_like, rg.Surface):
            self.srf = surface_like
        else:
            raise TypeError("S must be a Surface, Brep, or BrepFace")

    def closest_uv_of_point(self, pt):
        if not isinstance(pt, rg.Point3d):
            pt = rg.Point3d(float(pt[0]), float(pt[1]), float(pt[2]))
        ok, u, v = self.srf.ClosestPoint(pt)
        if not ok:
            # As fallback, clamp to domain mid
            dom_u = self.srf.Domain(0)
            dom_v = self.srf.Domain(1)
            u = 0.5 * (dom_u.T0 + dom_u.T1)
            v = 0.5 * (dom_v.T0 + dom_v.T1)
        return (float(u), float(v))

    def point_at(self, u, v):
        p = self.srf.PointAt(float(u), float(v))
        return (p.X, p.Y, p.Z)

    def frame_at(self, u, v):
        ok, plane = self.srf.FrameAt(float(u), float(v))
        if not ok:
            # Fallback using Evaluate derivatives
            pt, du, dv = self.srf.Evaluate(float(u), float(v), 1)
            t1 = du
            t2 = dv
            n = rg.Vector3d.CrossProduct(t1, t2)
        else:
            t1 = plane.XAxis
            t2 = plane.YAxis
            n = plane.ZAxis
        t1.Unitize(); t2.Unitize(); n.Unitize()
        return ((t1.X, t1.Y, t1.Z), (t2.X, t2.Y, t2.Z), (n.X, n.Y, n.Z))

    def step(self, u, v, d_world, L):
        # Approximate geodesic step: move in world, then project back
        p = self.srf.PointAt(float(u), float(v))
        vec = rg.Vector3d(float(d_world[0]), float(d_world[1]), float(d_world[2]))
        vec.Unitize()
        p2 = rg.Point3d(p.X + vec.X * float(L), p.Y + vec.Y * float(L), p.Z + vec.Z * float(L))
        ok, u2, v2 = self.srf.ClosestPoint(p2)
        if not ok:
            u2, v2 = u, v
            p2 = p
        return (float(u2), float(v2), (p2.X, p2.Y, p2.Z))


# Coerce inputs
iterations_v = _as_int(globals().get('iterations', None), 200)
step_length_v = _as_float(globals().get('step_length', None), 1.0)
branch_prob_v = _as_prob(globals().get('branch_probability', None), 0.2)
angle_spread_v = _as_float(globals().get('angle_spread', None), 30.0)
terminate_prob_v = _as_prob(globals().get('terminate_probability', None), 0.0)
min_spacing_v = _as_float(globals().get('min_spacing', None), 0.0)
seed_v = globals().get('seed', None)
try:
    seed_v = int(seed_v) if seed_v not in (None, "", False) else None
except Exception:
    seed_v = None


curves = []
edges_raw = []

def _as_point_list(sp_input):
    if sp_input is None:
        return []
    try:
        # Try list-like
        pts = []
        for s in sp_input:
            pts.append(rg.Point3d(s.X, s.Y, s.Z))
        return pts
    except Exception:
        # Single item
        try:
            return [rg.Point3d(sp_input.X, sp_input.Y, sp_input.Z)]
        except Exception:
            return []

if S:
    adapter = RhinoSurfaceAdapter(S)
    spores_pts = _as_point_list(spores)
    if not spores_pts:
        # Provide a sensible default: surface mid-point as a single spore
        dom_u = adapter.srf.Domain(0)
        dom_v = adapter.srf.Domain(1)
        u_mid = 0.5 * (dom_u.T0 + dom_u.T1)
        v_mid = 0.5 * (dom_v.T0 + dom_v.T1)
        p_mid = adapter.srf.PointAt(u_mid, v_mid)
        spores_pts = [p_mid]
        print("No spores provided; using surface midpoint as default seed.")

    edges_raw = grow_fungal_network(
        adapter,
        spores=spores_pts,
        iterations=iterations_v,
        step_length=step_length_v,
        branch_probability=branch_prob_v,
        angle_spread=angle_spread_v,
        terminate_probability=terminate_prob_v,
        min_spacing=min_spacing_v,
        seed=seed_v,
    )
    # Build curves
    for a, b in edges_raw:
        pa = rg.Point3d(*a)
        pb = rg.Point3d(*b)
        curves.append(rg.LineCurve(pa, pb))
