# Grasshopper Files

Place your `.gh` or `.ghx` (XML format) Grasshopper definition files here.

## Tips

- **Save your definition in this folder** so the Python import path works correctly.
- When setting up the GhPython component, the code will look for `python/` relative to this folder.
- Consider using `.ghx` (XML) format for better Git diffs if collaborating with others.
- Add descriptive names like `coral_basic.gh` or `coral_parametric_v2.gh`.

## Example GhPython Setup

Add this boilerplate to the top of your GhPython component:

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

# Now you can import
from coral.growth_models.simple_branching import grow_coral
```
