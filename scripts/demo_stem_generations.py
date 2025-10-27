"""
Demonstrate the effect of stem_generations parameter.

This script generates coral structures with and without stem_generations
to show the visual difference in the growth pattern.
"""

import sys
import os

# Add python/ folder to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.join(repo_root, "python")
sys.path.insert(0, python_dir)

from coral.growth_models.simple_branching import grow_coral


def demonstrate_stem_effect():
    """Show the effect of stem_generations on coral structure."""
    print("=" * 70)
    print("Stem Generations Demonstration")
    print("=" * 70)
    
    # Configuration
    config = {
        'iterations': 5,
        'branch_length': 1.0,
        'branch_angle': 25,
        'split_probability': 0.8,
        'seed': 42
    }
    
    print("\nConfiguration:")
    for key, value in config.items():
        print("  {}: {}".format(key, value))
    
    # Test without stem_generations (old behavior)
    print("\n" + "-" * 70)
    print("WITHOUT stem_generations (immediate branching):")
    print("-" * 70)
    
    segments_no_stem = grow_coral(**config, stem_generations=0)
    origin_segments_no_stem = [s for s in segments_no_stem if s[0] == (0, 0, 0)]
    
    print("Total segments: {}".format(len(segments_no_stem)))
    print("Segments from origin: {} (indicates immediate branching)".format(
        len(origin_segments_no_stem)))
    print("\nFirst 5 segments:")
    for i, seg in enumerate(segments_no_stem[:5]):
        start, end = seg
        print("  {}: ({:.3f}, {:.3f}, {:.3f}) -> ({:.3f}, {:.3f}, {:.3f})".format(
            i, start[0], start[1], start[2], end[0], end[1], end[2]))
    
    # Test with stem_generations=3
    print("\n" + "-" * 70)
    print("WITH stem_generations=3 (main stem before branching):")
    print("-" * 70)
    
    segments_with_stem = grow_coral(**config, stem_generations=3)
    origin_segments_with_stem = [s for s in segments_with_stem if s[0] == (0, 0, 0)]
    
    print("Total segments: {}".format(len(segments_with_stem)))
    print("Segments from origin: {} (single main stem)".format(
        len(origin_segments_with_stem)))
    print("\nFirst 5 segments (showing main stem structure):")
    for i, seg in enumerate(segments_with_stem[:5]):
        start, end = seg
        print("  {}: ({:.3f}, {:.3f}, {:.3f}) -> ({:.3f}, {:.3f}, {:.3f})".format(
            i, start[0], start[1], start[2], end[0], end[1], end[2]))
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print("\nWithout stem_generations:")
    print("  - Multiple segments start from origin (immediate branching)")
    print("  - Creates a bushy structure from the base")
    print("  - Total segments: {}".format(len(segments_no_stem)))
    
    print("\nWith stem_generations=3:")
    print("  - Single segment from origin (forced main stem)")
    print("  - Creates a trunk before branching")
    print("  - Total segments: {}".format(len(segments_with_stem)))
    print("  - More tree-like appearance with clear main stem")
    
    print("\n" + "=" * 70)
    print("Use stem_generations=3 in Grasshopper to create coral structures")
    print("with a clear main stem before branching begins!")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_stem_effect()
