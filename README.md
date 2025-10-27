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
import Rhino.Geometry as rg

# IMPORTANT: In Grasshopper, you'll receive a Point3d from input wires.
# Convert it to a tuple at the component boundary:
# Assuming 'start' is a GhPython input parameter connected to a Point
start_tuple = (start.X, start.Y, start.Z)  # Point3d -> tuple

# Now call the growth algorithm with the tuple
branches = grow_coral(
    start=start_tuple,
    iterations=5,
    branch_length=2.0,
    branch_angle=25,
    split_probability=0.7,
    stem_generations=3  # NEW: Force 3 generations of single stem before branching
)

# branches is a list of line segments (tuples of start/end points)
```

### 3. Convert output to Rhino geometry

```python
# Convert the tuple-based segments back to Rhino geometry for display
lines = [rg.Line(rg.Point3d(*seg[0]), rg.Point3d(*seg[1])) for seg in branches]
# Assign 'lines' to an output parameter
```

**Why this pattern?** The coral growth algorithm uses plain Python tuples to stay library-agnostic. By converting Point3d to tuple at the component boundary, the script stays friendly to normal Grasshopper wires (Point inputs) while keeping the core function reusable in other contexts.

## Available Parameters

The `grow_coral` function supports the following parameters:

### Basic Parameters
- **start** (tuple): Starting point (x, y, z) for the coral base
- **iterations** (int): Number of growth iterations (default: 5)
- **branch_length** (float): Length of each branch segment (default: 2.0)
- **branch_angle** (float): Maximum deviation angle in degrees (default: 25)
- **split_probability** (float): Probability (0-1) that a branch splits into two (default: 0.7)
- **seed** (int, optional): Random seed for reproducible results

### Stem Control
- **stem_generations** (int): Number of initial generations forced to grow as a single stem before branching (default: 0)
- **stem_angle** (float, optional): Maximum deviation angle for the main stem. If not specified, uses `branch_angle`

### Variation Parameters
- **length_jitter** (float): Random variation factor for branch length, 0-1 (default: 0.0)
- **angle_jitter** (float): Random variation factor for branch angle, 0-1 (default: 0.0)
- **length_decay** (float): Multiplicative decay factor for branch length per generation, 0-1 (default: 0.0)
- **angle_scale** (float): Scaling factor for all branch angles (default: 1.0)

### Advanced Control
- **twist_rate** (float): Rotational twist in degrees per iteration around growth axis (default: 0.0)
- **avoid_radius** (float): Minimum distance between branch endpoints to prevent crowding (default: 0.0)
- **terminate_probability** (float): Probability (0-1) that a branch tip terminates and stops growing (default: 0.0)

### Example with Advanced Parameters

```python
# Create a more complex coral with variation and constraints
branches = grow_coral(
    start=(0, 0, 0),
    iterations=10,
    branch_length=2.0,
    branch_angle=30,
    split_probability=0.7,
    stem_generations=3,
    stem_angle=5,          # Straight stem
    length_jitter=0.2,     # 20% length variation
    angle_jitter=0.3,      # 30% angle variation
    length_decay=0.1,      # 10% decay per generation
    twist_rate=5.0,        # 5° twist per iteration
    terminate_probability=0.05,  # 5% chance to terminate
    seed=42
)
```


### Understanding the stem_generations parameter

The `stem_generations` parameter controls how many initial generations must grow as a single main stem before branching is allowed:

- **`stem_generations=0` (default)**: Branching can occur from the very first generation, creating a bushy structure from the base
- **`stem_generations=3`**: Forces the first 3 generations to grow as a single stem, creating a trunk-like structure before branches form

**Example comparison:**
```python
# Without stem: branches immediately (bushy)
bushy = grow_coral(iterations=5, split_probability=0.8, stem_generations=0)

# With stem: creates main trunk first (tree-like)
trunk = grow_coral(iterations=5, split_probability=0.8, stem_generations=3)
```

Use `stem_generations` to create more realistic tree or coral forms with a clear main stem structure!

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
