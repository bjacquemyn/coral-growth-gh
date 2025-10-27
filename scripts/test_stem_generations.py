"""
Test the stem_generations parameter for coral growth.

This test validates that the stem_generations parameter correctly
prevents branching during the initial generations, creating a main
stem before allowing branches to form.
"""

import sys
import os

# Add python/ folder to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.join(repo_root, "python")
sys.path.insert(0, python_dir)

from coral.growth_models.simple_branching import grow_coral

# Floating point comparison tolerance
FLOAT_TOLERANCE = 1e-9


def test_default_behavior():
    """Test that default behavior (stem_generations=0) allows immediate branching."""
    print("Testing default behavior (stem_generations=0)...")
    
    segments = grow_coral(
        iterations=3,
        split_probability=1.0,  # Force branching when allowed
        seed=42,
        stem_generations=0  # Default: branching allowed immediately
    )
    
    # With split_probability=1.0, should branch immediately
    # Count segments starting from origin
    origin_segments = [seg for seg in segments if seg[0] == (0, 0, 0)]
    
    print("  Generated {} total segments".format(len(segments)))
    print("  Segments starting from origin: {}".format(len(origin_segments)))
    
    # Should have 2 segments from origin (immediate branching)
    assert len(origin_segments) == 2, "Expected 2 segments from origin with immediate branching"
    print("  ✓ Default behavior allows immediate branching")


def test_stem_generations_basic():
    """Test that stem_generations prevents early branching."""
    print("\nTesting stem_generations=2...")
    
    segments = grow_coral(
        iterations=4,
        split_probability=1.0,  # Force branching when allowed
        seed=42,
        stem_generations=2  # First 2 generations must be single stem
    )
    
    # Count segments starting from origin
    origin_segments = [seg for seg in segments if seg[0] == (0, 0, 0)]
    
    print("  Generated {} total segments".format(len(segments)))
    print("  Segments starting from origin: {}".format(len(origin_segments)))
    
    # Should have only 1 segment from origin (stem growth)
    assert len(origin_segments) == 1, "Expected only 1 segment from origin with stem_generations=2"
    
    # Verify the stem structure: first 2 segments should form a single line
    # Segment 0 starts at origin, segment 1 should start at segment 0's endpoint
    assert len(segments) >= 2, "Should have at least 2 segments"
    
    first_seg_end = segments[0][1]
    second_seg_start = segments[1][0]
    
    # Check that second segment starts where first segment ends
    for i in range(3):
        diff = abs(first_seg_end[i] - second_seg_start[i])
        assert diff < FLOAT_TOLERANCE, "Second segment should start where first segment ends"
    
    print("  ✓ stem_generations=2 creates a main stem before branching")


def test_stem_generations_various():
    """Test various stem_generations values."""
    print("\nTesting various stem_generations values...")
    
    for stem_gens in [0, 1, 2, 3]:
        segments = grow_coral(
            iterations=5,
            split_probability=1.0,
            seed=99,
            stem_generations=stem_gens
        )
        
        origin_segments = [seg for seg in segments if seg[0] == (0, 0, 0)]
        
        if stem_gens == 0:
            # Should branch immediately
            assert len(origin_segments) == 2
        else:
            # Should have single stem
            assert len(origin_segments) == 1
        
        print("  stem_generations={}: {} segments total, {} from origin".format(
            stem_gens, len(segments), len(origin_segments)))
    
    print("  ✓ All stem_generations values work correctly")


def test_stem_with_low_split_probability():
    """Test stem_generations with realistic split_probability."""
    print("\nTesting stem_generations with split_probability=0.7...")
    
    # Without stem_generations
    segments1 = grow_coral(
        iterations=5,
        split_probability=0.7,
        seed=123,
        stem_generations=0
    )
    
    # With stem_generations
    segments2 = grow_coral(
        iterations=5,
        split_probability=0.7,
        seed=123,
        stem_generations=3
    )
    
    origin_segs1 = [seg for seg in segments1 if seg[0] == (0, 0, 0)]
    origin_segs2 = [seg for seg in segments2 if seg[0] == (0, 0, 0)]
    
    print("  Without stem_generations: {} from origin".format(len(origin_segs1)))
    print("  With stem_generations=3: {} from origin".format(len(origin_segs2)))
    
    # With stem_generations=3, should always have exactly 1 from origin
    assert len(origin_segs2) == 1, "Expected single stem with stem_generations=3"
    print("  ✓ stem_generations works with realistic split probabilities")


def test_stem_equals_iterations():
    """Test edge case where stem_generations equals iterations."""
    print("\nTesting edge case: stem_generations == iterations...")
    
    segments = grow_coral(
        iterations=3,
        split_probability=1.0,
        seed=42,
        stem_generations=3  # No branching allowed at all
    )
    
    print("  Generated {} segments".format(len(segments)))
    
    # Should have exactly iterations number of segments, forming a single line
    assert len(segments) == 3, "Expected exactly 3 segments with stem_generations=iterations"
    
    # Verify it's a single line: each segment's end should be the next segment's start
    for i in range(len(segments) - 1):
        end_pt = segments[i][1]
        start_pt = segments[i + 1][0]
        for j in range(3):
            diff = abs(end_pt[j] - start_pt[j])
            assert diff < FLOAT_TOLERANCE, "Segments should form continuous line"
    
    print("  ✓ Edge case handled correctly")


if __name__ == "__main__":
    print("=" * 60)
    print("Stem Generations Test")
    print("=" * 60)
    
    try:
        test_default_behavior()
        test_stem_generations_basic()
        test_stem_generations_various()
        test_stem_with_low_split_probability()
        test_stem_equals_iterations()
        
        print("\n" + "=" * 60)
        print("✓ All stem generation tests passed!")
        print("=" * 60)
        print("\nThe stem_generations parameter is working correctly.")
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print("✗ Test failed!")
        print("=" * 60)
        print("\nAssertion Error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Test failed!")
        print("=" * 60)
        print("\nError: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
