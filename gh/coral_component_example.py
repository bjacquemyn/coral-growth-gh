"""
Example GhPython component script for coral growth.

This shows the recommended pattern for using the coral growth algorithm
in Grasshopper, with proper Point3d to tuple conversion.

INPUTS:
  start: Point3d - Starting point for coral growth (as a Grasshopper Point)
  iterations: int - Number of growth iterations (default: 5)
  branch_length: float - Length of each branch segment (default: 2.0)
  branch_angle: float - Maximum deviation angle in degrees (default: 25)
  split_probability: float - Probability of branching (0-1, default: 0.7)
  seed: int - Random seed for reproducibility (optional)

OUTPUTS:
  lines: List of Curve objects (LineCurve) for visualization
  segments: Alias of 'lines' for convenience (Curve list)
  segments_raw: List of raw segment data (tuples)
"""

import sys
import os

# Ensure the repo's python/ folder is on sys.path so we can import coral.*
def _ensure_repo_python_on_path():
    attempted = []

    def _add(p):
        if p and os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)

    # 1) Explicit override via environment variable
    env_path = os.getenv('CORAL_GH_PYTHON_PATH')
    if env_path:
        attempted.append(env_path)
        _add(env_path)

    # 2) Based on the Grasshopper document location
    gh_doc = ghenv.Component.OnPingDocument()
    if gh_doc:
        gh_file = getattr(gh_doc, 'FilePath', None)
        if gh_file:
            gh_dir = os.path.dirname(gh_file)

            # Common layout: repo_root/gh/<file>.gh -> repo_root/python
            if os.path.basename(gh_dir).lower() == 'gh':
                repo_root = os.path.dirname(gh_dir)
            else:
                # If the .gh is not inside a 'gh' folder, try its parent as root
                repo_root = gh_dir

            candidates = [
                os.path.join(repo_root, 'python'),   # preferred
                os.path.join(gh_dir, 'python'),      # legacy sibling layout
            ]

            # Upward search (max 5 levels) for a python/coral folder
            cur = gh_dir
            for _ in range(5):
                candidates.append(os.path.join(cur, 'python'))
                cur = os.path.dirname(cur)

            for c in candidates:
                c = os.path.normpath(c)
                if c not in attempted:
                    attempted.append(c)
                if os.path.isdir(os.path.join(c, 'coral')):
                    _add(c)

    return attempted

_attempted_paths = _ensure_repo_python_on_path()

# Import coral growth algorithm
try:
    from coral.growth_models.simple_branching import grow_coral
except ImportError as _e:
    msg = (
        "Could not import 'coral.growth_models.simple_branching'.\n"
        "Check that your Grasshopper file is saved inside the repo (e.g., ...\\coral-growth-gh\\gh\\yourfile.gh),\n"
        "or set the environment variable CORAL_GH_PYTHON_PATH to the absolute path of the repo's 'python' folder.\n\n"
        "Attempted locations:\n  - " + "\n  - ".join(_attempted_paths)
    )
    raise ImportError(msg)
import Rhino.Geometry as rg

# Convert Grasshopper input to a plain (x, y, z) tuple at the boundary
# Accepts Rhino.Geometry.Point3d or an (x, y, z) iterable
def _as_tuple3(value):
    try:
        # Support tuple/list-like
        x, y, z = value
        return (float(x), float(y), float(z))
    except Exception:
        pass
    # Support Rhino Point3d
    if hasattr(value, "X") and hasattr(value, "Y") and hasattr(value, "Z"):
        return (float(value.X), float(value.Y), float(value.Z))
    # Fallback default
    return (0.0, 0.0, 0.0)

start_tuple = _as_tuple3(start)

# Call the growth algorithm with plain tuple
# Robustly coerce GH inputs to valid Python types with sensible defaults
def _as_int(value, default):
    try:
        if value is None:
            return default
        return int(round(float(value)))
    except Exception:
        return default

def _as_float(value, default):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

def _as_prob(value, default):
    v = _as_float(value, default)
    # clamp to [0, 1]
    return max(0.0, min(1.0, v))

def _as_seed(value):
    if value in (None, "", False):
        return None
    try:
        return int(value)
    except Exception:
        return None

iterations_val = _as_int(globals().get('iterations', None), 5)
branch_length_val = _as_float(globals().get('branch_length', None), 2.0)
branch_angle_val = _as_float(globals().get('branch_angle', None), 25)
split_prob_val = _as_prob(globals().get('split_probability', None), 0.7)
seed_val = _as_seed(globals().get('seed', None))

segments_raw = grow_coral(
    start=start_tuple,
    iterations=iterations_val,
    branch_length=branch_length_val,
    branch_angle=branch_angle_val,
    split_probability=split_prob_val,
    seed=seed_val,
)

# Convert output tuples back to Rhino geometry for Grasshopper display
# Use LineCurve to ensure the output is a Curve type, which plugs into Crv params.
lines = []
for seg in segments_raw:
    start_pt = rg.Point3d(*seg[0])  # Tuple -> Point3d
    end_pt = rg.Point3d(*seg[1])    # Tuple -> Point3d
    lines.append(rg.LineCurve(start_pt, end_pt))

# Backward/compat outputs:
# - 'segments' outputs curves as well (for users already wiring this output into a Curve param)
# - 'segments_raw' exposes the tuple data for debugging/analysis
segments = lines
segments_raw = segments_raw
