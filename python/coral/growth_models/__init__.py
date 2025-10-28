"""Dynamic registry for the available coral growth models.

Historically this package eagerly imported a hard-coded list of modules.
That meant missing optional modules (e.g., experimental algorithms that are
not shipped with the repository) triggered an ``ImportError`` during package
import.  In Grasshopper this surfaced as a misleading
``Could not import 'coral.growth_models.simple_branching'`` runtime error even
though :mod:`simple_branching` was present and valid.  The eager import of the
non-existent :mod:`fungal_surface` module was the culprit.

To make the package robust we now discover modules dynamically at import time.
Any ``*.py`` module in this directory is imported and re-exported through
``__all__``.  Missing optional modules are simply skipped, eliminating spurious
errors while still keeping the original plug-and-play behaviour.
"""

import importlib
import pkgutil


__all__ = []
AVAILABLE_MODELS = {}


def _load_available_models():
    """Import all non-package modules in this namespace.

    Modules whose filenames start with an underscore are treated as internal
    helpers and ignored.  Successfully imported modules are exposed via the
    module globals and recorded in :data:`AVAILABLE_MODELS` for convenience.
    """

    package_name = __name__

    for module_info in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
        if module_info.ispkg:
            continue

        module_name = module_info.name
        if module_name.startswith("_"):
            continue

        qualified_name = ".{0}".format(module_name)
        module = importlib.import_module(qualified_name, package_name)

        globals()[module_name] = module
        __all__.append(module_name)
        AVAILABLE_MODELS[module_name] = module


_load_available_models()

