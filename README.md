# Coral Growth in Grasshopper + Python

This repository lets you:
- Edit Python code in Visual Studio Code.
- Track changes with Git and GitHub.
- Call your Python modules from a GhPython component in Grasshopper using a stable, relative import path.
- Experiment with a simple coral-like growth algorithm, then swap in other models.

## Folder layout

```
coral-growth-gh/
├── gh/                          # Grasshopper (.gh, .ghx) files
├── python/                      # Python modules
│   └── coral/                   # Main package
│       ├── __init__.py
│       └── growth_models/       # Pluggable growth algorithms
│           ├── __init__.py
│           └── simple_branching.py
├── data/                        # Sample inputs, outputs, test data
├── scripts/                     # Helper scripts (optional)
├── .gitignore
└── README.md
```

## How to use in Grasshopper

### 1. Set up the Python path in GhPython

In your GhPython component, add this at the top to enable imports from the `python/` folder:

```python
import sys
import os

# Get the directory of this .gh file
gh_dir = ghenv.Component.OnPingDocument().FilePath
if gh_dir:
    repo_root = os.path.dirname(gh_dir)
    python_dir = os.path.join(repo_root, "python")
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)
```

**Important:** Save your `.gh` file inside the `gh/` folder so the relative path works correctly.

### 2. Import and run the coral growth algorithm

```python
from coral.growth_models.simple_branching import grow_coral

# Example: grow from a starting point
start_point = (0, 0, 0)
branches = grow_coral(
    start=start_point,
    iterations=5,
    branch_length=2.0,
    branch_angle=25,
    split_probability=0.7
)

# branches is a list of line segments (tuples of start/end points)
# You can convert these to Rhino geometry for display
```

### 3. Convert output to Rhino geometry

```python
import Rhino.Geometry as rg

lines = [rg.Line(rg.Point3d(*seg[0]), rg.Point3d(*seg[1])) for seg in branches]
# Assign 'lines' to an output parameter
```

## How to test without Grasshopper

Run the standalone test script from the repository root:

```bash
cd coral-growth-gh
python scripts/test_growth.py
```

This will:
- Import the coral growth algorithm
- Generate sample geometry
- Print the results to the console
- Verify the algorithm works outside of Grasshopper

## Editing and version control

1. **Clone or create this repo on GitHub** to track changes.
2. **Open the `coral-growth-gh` folder in VS Code** for editing Python files.
3. **Edit `.gh` files in Grasshopper** (Rhino 7/8), saved in the `gh/` folder.
4. **Commit Python changes** frequently. Grasshopper files can be committed less often (they're binary and harder to diff).

## Evolving the algorithm

Want to try a different growth model?

1. Create a new file in `python/coral/growth_models/`, e.g., `radial_symmetry.py`.
2. Implement your algorithm with a consistent interface (e.g., a `grow_coral()` function).
3. Update your GhPython component import:
   ```python
   from coral.growth_models.radial_symmetry import grow_coral
   ```
4. Test, iterate, commit!

## Dependencies

- **Rhino 7 or 8** with Grasshopper
- **Python 2.7** (GhPython default in Rhino 7) or **Python 3.x** (GhPython in Rhino 8, or via `rhinoinside`)
- No external packages required for the basic algorithm (uses only standard library: `math`, `random`)

## Tips

- Keep the `python/` folder clean and focused on reusable logic.
- Use `data/` for test inputs, exported geometry, or parameter sets.
- The `.gitignore` excludes Rhino/Grasshopper temp files and Python cache.
- For larger projects, consider adding a `requirements.txt` for external dependencies (numpy, scipy, etc.).

## License

Choose your own! MIT, Apache 2.0, or keep it private.

---

**Happy growing!** 🪸
