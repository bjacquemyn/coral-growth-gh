"""
Pluggable coral growth models.

Each module in this package should expose a growth function
with a consistent interface for easy swapping in Grasshopper.
"""

from . import simple_branching

__all__ = ['simple_branching']
