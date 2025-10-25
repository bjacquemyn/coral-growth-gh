# Data Folder

Use this folder for:

- **Sample input data** (point clouds, curves, surfaces to guide growth)
- **Exported geometry** (OBJ, STL, JSON with coordinates)
- **Parameter sets** (JSON files with different growth configurations)
- **Test data** for validating algorithms

## Structure suggestions

You can organize subdirectories like:

```
data/
├── inputs/          # Source geometry, seed points
├── exports/         # Generated models (ignored by git if large)
└── parameters/      # JSON files with parameter presets
```

## Example parameter JSON

```json
{
  "name": "dense_coral",
  "iterations": 6,
  "branch_length": 1.2,
  "branch_angle": 20,
  "split_probability": 0.85,
  "seed": 42
}
```

Load in Python:
```python
import json
with open("data/parameters/dense_coral.json", "r") as f:
    params = json.load(f)
segments = grow_coral(**params)
```
