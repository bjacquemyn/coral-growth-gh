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
  lines: List of Line objects for visualization in Grasshopper
  segments: List of raw segment data (tuples)
"""

import sys
import os

# Add python/ to path
gh_doc = ghenv.Component.OnPingDocument()
if gh_doc:
    gh_path = gh_doc.FilePath
    if gh_path:
        repo_root = os.path.dirname(gh_path)
        python_dir = os.path.join(repo_root, "python")
        if python_dir not in sys.path:
            sys.path.insert(0, python_dir)

# Import coral growth algorithm
from coral.growth_models.simple_branching import grow_coral
import Rhino.Geometry as rg

# Convert Point3d to tuple at the component boundary
# This keeps the core function library-agnostic while staying
# friendly to normal Grasshopper wires
if start:
    start_tuple = (start.X, start.Y, start.Z)  # Point3d -> tuple
else:
    start_tuple = (0, 0, 0)  # Default starting point

# Call the growth algorithm with plain tuple
# Use try/except to provide defaults for optional parameters
try:
    iter_val = iterations
except NameError:
    iter_val = 5

try:
    length_val = branch_length
except NameError:
    length_val = 2.0

try:
    angle_val = branch_angle
except NameError:
    angle_val = 25

try:
    prob_val = split_probability
except NameError:
    prob_val = 0.7

try:
    seed_val = seed
except NameError:
    seed_val = None

segments = grow_coral(
    start=start_tuple,
    iterations=iter_val,
    branch_length=length_val,
    branch_angle=angle_val,
    split_probability=prob_val,
    seed=seed_val
)

# Convert output tuples back to Rhino geometry for Grasshopper display
lines = []
for seg in segments:
    start_pt = rg.Point3d(*seg[0])  # Tuple -> Point3d
    end_pt = rg.Point3d(*seg[1])    # Tuple -> Point3d
    lines.append(rg.Line(start_pt, end_pt))
