# Grasshopper Files

Place your `.gh` or `.ghx` (XML format) Grasshopper definition files here.

## Tips

- **Save your definition in this folder** so the Python import path works correctly.
- When setting up the GhPython component, the code will look for `python/` relative to this folder.
- Consider using `.ghx` (XML) format for better Git diffs if collaborating with others.
- Add descriptive names like `coral_basic.gh` or `coral_parametric_v2.gh`.

## Example GhPython Setup

See `coral_component_example.py` for a complete working example.

### Key Pattern: Point3d to Tuple Conversion

In Grasshopper, points are `Point3d` objects. The coral growth algorithm uses plain Python tuples `(x, y, z)` to stay library-agnostic. **Convert at the component boundary:**

```python
import sys
import os

# Add python/ to path
gh_path = ghenv.Component.OnPingDocument().FilePath
if gh_path:
    repo_root = os.path.dirname(gh_path)
    python_dir = os.path.join(repo_root, "python")
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)

# Import the algorithm and Rhino geometry
from coral.growth_models.simple_branching import grow_coral
import Rhino.Geometry as rg

# IMPORTANT: Convert Point3d to tuple before calling the function
start_tuple = (start.X, start.Y, start.Z)  # Point3d -> tuple

# Call the growth algorithm with the tuple
segments = grow_coral(
    start=start_tuple,
    iterations=5,
    branch_length=2.0,
    branch_angle=25,
    split_probability=0.7
)

# Convert output back to Rhino geometry for display
lines = [rg.Line(rg.Point3d(*seg[0]), rg.Point3d(*seg[1])) for seg in segments]
```

This pattern keeps the core function library-agnostic while staying friendly to normal Grasshopper wires (Point inputs).
