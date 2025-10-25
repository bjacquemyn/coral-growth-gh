"""
Test the coral growth algorithm without Grasshopper.

Run this script from the repository root:
    python scripts/test_growth.py

This validates that the algorithm works correctly and can be
imported successfully from the python/ folder.
"""

import sys
import os

# Add python/ folder to path (same as we do in GhPython)
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.join(repo_root, "python")
sys.path.insert(0, python_dir)

from coral.growth_models.simple_branching import grow_coral


def test_basic_growth():
    """Test basic coral growth with default parameters."""
    print("Testing basic coral growth...")
    
    segments = grow_coral(
        start=(0, 0, 0),
        iterations=3,
        branch_length=1.0,
        branch_angle=20,
        split_probability=0.8,
        seed=42  # Fixed seed for reproducibility
    )
    
    print("  Generated {} segments".format(len(segments)))
    assert len(segments) > 0, "Should generate at least one segment"
    
    # Check that segments are valid
    for i, seg in enumerate(segments):
        start_pt, end_pt = seg
        assert len(start_pt) == 3, "Start point should be 3D"
        assert len(end_pt) == 3, "End point should be 3D"
        
        # Check that segment has non-zero length
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        dz = end_pt[2] - start_pt[2]
        length_sq = dx*dx + dy*dy + dz*dz
        assert length_sq > 0.01, "Segment {} has near-zero length".format(i)
    
    print("  ✓ All segments valid")
    return segments


def test_parameter_variations():
    """Test growth with different parameters."""
    print("\nTesting parameter variations...")
    
    # Low branching probability
    result1 = grow_coral(iterations=4, split_probability=0.2, seed=1)
    print("  Low branching: {} segments".format(len(result1)))
    
    # High branching probability
    result2 = grow_coral(iterations=4, split_probability=0.9, seed=1)
    print("  High branching: {} segments".format(len(result2)))
    
    assert len(result2) > len(result1), "High branching should create more segments"
    print("  ✓ Branching probability affects complexity")


def test_reproducibility():
    """Test that same seed produces same results."""
    print("\nTesting reproducibility...")
    
    result1 = grow_coral(iterations=3, seed=99)
    result2 = grow_coral(iterations=3, seed=99)
    
    assert len(result1) == len(result2), "Same seed should produce same number of segments"
    
    # Check first few segments are identical
    for i in range(min(5, len(result1))):
        seg1, seg2 = result1[i], result2[i]
        for j in range(2):  # Start and end points
            for k in range(3):  # x, y, z
                diff = abs(seg1[j][k] - seg2[j][k])
                assert diff < 1e-9, "Segments should be identical"
    
    print("  ✓ Results are reproducible with fixed seed")


def print_sample_output(segments, max_lines=10):
    """Print sample segment data."""
    print("\nSample output (first {} segments):".format(max_lines))
    for i, seg in enumerate(segments[:max_lines]):
        start, end = seg
        print("  Segment {}: ({:.2f}, {:.2f}, {:.2f}) -> ({:.2f}, {:.2f}, {:.2f})".format(
            i, start[0], start[1], start[2], end[0], end[1], end[2]
        ))


if __name__ == "__main__":
    print("=" * 60)
    print("Coral Growth Algorithm Test")
    print("=" * 60)
    
    try:
        # Run tests
        segments = test_basic_growth()
        test_parameter_variations()
        test_reproducibility()
        
        # Show sample output
        print_sample_output(segments)
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nThe algorithm is working correctly.")
        print("You can now use it in Grasshopper with confidence.")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Test failed!")
        print("=" * 60)
        print("\nError: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
