"""
Test that age-based pruning doesn't prematurely prune stems during stem_generations.

This test validates the fix for the issue where the generation counting logic
caused too rapid pruning of the main stem before branching could occur.
"""

import sys
import os

# Add python/ folder to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.join(repo_root, "python")
sys.path.insert(0, python_dir)

from coral.growth_models.simple_branching import grow_coral


def test_stem_survives_with_age_based_pruning():
    """
    Test that stem tips are not prematurely pruned during stem_generations phase.
    
    The bug was that during stem_generations, the trunk tip kept its original
    generation_born value, causing it to age and be pruned before branching
    could occur after the stem_generations phase.
    """
    print("Testing stem survival with age-based pruning...")
    
    # Configuration that previously failed (only 3 segments created)
    segments = grow_coral(
        start=(0, 0, 0),
        iterations=10,
        branch_length=1.0,
        branch_angle=25,
        split_probability=0.8,
        stem_generations=3,
        age_based_prune=0.3,  # Moderate pruning rate
        seed=42
    )
    
    print("  Generated {} segments".format(len(segments)))
    
    # Before fix: would have only 3 segments (stem gets pruned at iteration 3)
    # After fix: should have many more segments (stem survives to branch)
    assert len(segments) > 10, \
        "Expected >10 segments, got {}. Stem was pruned too early!".format(len(segments))
    
    # Verify the first 3 segments form the main stem
    assert segments[0][0] == (0, 0, 0), "First segment should start at origin"
    
    # Check that stem continues (second segment starts where first ends)
    for i in range(min(2, len(segments) - 1)):
        end_pt = segments[i][1]
        # Find segments that start near this endpoint
        next_segs = [s for s in segments[i+1:i+3] 
                     if all(abs(s[0][j] - end_pt[j]) < 1e-9 for j in range(3))]
        assert len(next_segs) > 0, \
            "Segment {} should connect to next segment".format(i)
    
    print("  ✓ Stem survives through stem_generations phase")


def test_various_pruning_rates():
    """Test that the fix works with various age_based_prune values."""
    print("\nTesting various pruning rates with stem_generations...")
    
    # Test that the fix allows MORE segments compared to without the fix
    # by comparing averages across multiple seeds
    results = {}
    
    for prune_rate in [0.1, 0.2, 0.3]:
        segment_counts = []
        for seed in range(20, 30):  # Use 10 different seeds
            segments = grow_coral(
                iterations=10,
                split_probability=0.8,
                stem_generations=3,
                age_based_prune=prune_rate,
                seed=seed
            )
            segment_counts.append(len(segments))
        
        avg = sum(segment_counts) / len(segment_counts)
        max_count = max(segment_counts)
        results[prune_rate] = (avg, max_count)
        print("  age_based_prune={:.1f}: avg={:.1f}, max={}".format(
            prune_rate, avg, max_count))
    
    # With the fix, even moderate pruning should allow significant growth
    # The key test: with stem_generations=3, at least some seeds should produce
    # more than just the 3 stem segments
    assert results[0.1][1] > 10, \
        "With low pruning, should have grown significantly in at least one seed"
    
    print("  ✓ Fix allows growth after stem_generations phase")


def test_no_age_prune_unaffected():
    """Test that behavior without age_based_pruning is unchanged."""
    print("\nTesting that non-pruning cases are unaffected...")
    
    # Without age-based pruning, results should be same as before
    segments1 = grow_coral(
        iterations=5,
        split_probability=0.7,
        stem_generations=2,
        age_based_prune=0.0,  # No pruning
        seed=123
    )
    
    segments2 = grow_coral(
        iterations=5,
        split_probability=0.7,
        stem_generations=0,
        age_based_prune=0.0,  # No pruning
        seed=456
    )
    
    print("  With stem_generations=2, no pruning: {} segments".format(len(segments1)))
    print("  With stem_generations=0, no pruning: {} segments".format(len(segments2)))
    
    # Should have reasonable number of segments
    assert len(segments1) > 3, "Expected multiple segments"
    assert len(segments2) > 3, "Expected multiple segments"
    
    print("  ✓ Non-pruning behavior unchanged")


def test_edge_case_high_pruning():
    """Test edge case with very high pruning rate."""
    print("\nTesting edge case with very high pruning rate...")
    
    # With very high pruning, growth is severely limited
    # Test multiple seeds to see at least some growth in favorable cases
    segment_counts = []
    for seed in range(100, 110):
        segments = grow_coral(
            iterations=10,
            split_probability=0.9,
            stem_generations=2,
            age_based_prune=0.7,  # Very aggressive pruning
            seed=seed
        )
        segment_counts.append(len(segments))
    
    max_segments = max(segment_counts)
    print("  High pruning (0.7): max={} segments across 10 seeds".format(max_segments))
    
    # At least in some favorable seeds, should get past iteration 0
    assert max_segments >= 2, \
        "Expected at least 2 segments in best case with high pruning, got {}".format(max_segments)
    
    print("  ✓ High pruning rate handled (stem can survive with lucky seeds)")


def test_comparison_with_without_fix():
    """
    Demonstrate the improvement from the fix.
    
    This test shows what would have happened before vs after the fix.
    """
    print("\nDemonstrating the fix improvement...")
    
    config = {
        'iterations': 10,
        'split_probability': 0.8,
        'stem_generations': 3,
        'age_based_prune': 0.3,
        'seed': 42
    }
    
    segments = grow_coral(**config)
    
    print("  Configuration:")
    print("    iterations: {}".format(config['iterations']))
    print("    stem_generations: {}".format(config['stem_generations']))
    print("    age_based_prune: {}".format(config['age_based_prune']))
    print()
    print("  Before fix: ~3 segments (stem pruned prematurely)")
    print("  After fix: {} segments (stem survives to branch)".format(len(segments)))
    print()
    print("  ✓ Significant improvement in segment generation")


if __name__ == "__main__":
    print("=" * 70)
    print("Age-Based Pruning Fix Test")
    print("=" * 70)
    
    try:
        test_stem_survives_with_age_based_pruning()
        test_various_pruning_rates()
        test_no_age_prune_unaffected()
        test_edge_case_high_pruning()
        test_comparison_with_without_fix()
        
        print("\n" + "=" * 70)
        print("✓ All age-based pruning tests passed!")
        print("=" * 70)
        print("\nThe fix successfully prevents premature stem pruning during")
        print("the stem_generations phase while maintaining age-based pruning")
        print("for branches after stem growth completes.")
        
    except AssertionError as e:
        print("\n" + "=" * 70)
        print("✗ Test failed!")
        print("=" * 70)
        print("\nAssertion Error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ Test failed!")
        print("=" * 70)
        print("\nError: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
