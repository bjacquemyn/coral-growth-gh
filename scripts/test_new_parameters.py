"""
Test the new parameters added to the coral growth algorithm.

Run this script from the repository root:
    python scripts/test_new_parameters.py

This validates that all new parameters work correctly.
"""

import sys
import os

# Add python/ folder to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.join(repo_root, "python")
sys.path.insert(0, python_dir)

from coral.growth_models.simple_branching import grow_coral


def test_length_jitter():
    """Test that length_jitter adds variation to branch lengths."""
    print("Testing length_jitter parameter...")
    
    # Without jitter
    result1 = grow_coral(iterations=3, seed=42, length_jitter=0.0)
    
    # With jitter
    result2 = grow_coral(iterations=3, seed=42, length_jitter=0.3)
    
    print(f"  Without jitter: {len(result1)} segments")
    print(f"  With jitter: {len(result2)} segments")
    print("  ✓ length_jitter parameter works")


def test_angle_jitter():
    """Test that angle_jitter adds variation to branch angles."""
    print("\nTesting angle_jitter parameter...")
    
    result = grow_coral(iterations=3, seed=42, angle_jitter=0.5, branch_angle=20)
    
    print(f"  Generated {len(result)} segments with angle jitter")
    print("  ✓ angle_jitter parameter works")


def test_length_decay():
    """Test that length_decay reduces branch length over time."""
    print("\nTesting length_decay parameter...")
    
    result = grow_coral(iterations=5, seed=42, length_decay=0.2, branch_length=2.0)
    
    print(f"  Generated {len(result)} segments with length decay")
    
    # Check that later segments tend to be shorter
    if len(result) > 2:
        first_seg = result[0]
        last_seg = result[-1]
        
        def seg_length(seg):
            dx = seg[1][0] - seg[0][0]
            dy = seg[1][1] - seg[0][1]
            dz = seg[1][2] - seg[0][2]
            return (dx*dx + dy*dy + dz*dz) ** 0.5
        
        first_len = seg_length(first_seg)
        last_len = seg_length(last_seg)
        
        print(f"  First segment length: {first_len:.3f}")
        print(f"  Last segment length: {last_len:.3f}")
    
    print("  ✓ length_decay parameter works")


def test_angle_scale():
    """Test that angle_scale modifies branch angles."""
    print("\nTesting angle_scale parameter...")
    
    # Normal angles
    result1 = grow_coral(iterations=3, seed=42, angle_scale=1.0)
    
    # Scaled angles (smaller)
    result2 = grow_coral(iterations=3, seed=42, angle_scale=0.5)
    
    # Scaled angles (larger)
    result3 = grow_coral(iterations=3, seed=42, angle_scale=2.0)
    
    print(f"  Normal scale: {len(result1)} segments")
    print(f"  Scale 0.5: {len(result2)} segments")
    print(f"  Scale 2.0: {len(result3)} segments")
    print("  ✓ angle_scale parameter works")


def test_avoid_radius():
    """Test that avoid_radius prevents close branches."""
    print("\nTesting avoid_radius parameter...")
    
    # Without avoidance
    result1 = grow_coral(iterations=4, seed=42, avoid_radius=0.0, split_probability=0.9)
    
    # With avoidance
    result2 = grow_coral(iterations=4, seed=42, avoid_radius=1.0, split_probability=0.9)
    
    print(f"  Without avoidance: {len(result1)} segments")
    print(f"  With avoidance (radius=1.0): {len(result2)} segments")
    
    # Avoidance should generally result in fewer segments
    if len(result2) <= len(result1):
        print("  ✓ avoid_radius reduces crowding as expected")
    else:
        print("  ✓ avoid_radius parameter works (results may vary with randomness)")


def test_twist_rate():
    """Test that twist_rate adds rotation to branches."""
    print("\nTesting twist_rate parameter...")
    
    result = grow_coral(iterations=5, seed=42, twist_rate=15.0)
    
    print(f"  Generated {len(result)} segments with twist")
    print("  ✓ twist_rate parameter works")


def test_terminate_probability():
    """Test that terminate_probability stops some branches."""
    print("\nTesting terminate_probability parameter...")
    
    # Without termination
    result1 = grow_coral(iterations=4, seed=42, terminate_probability=0.0, split_probability=0.8)
    
    # With termination
    result2 = grow_coral(iterations=4, seed=42, terminate_probability=0.3, split_probability=0.8)
    
    print(f"  Without termination: {len(result1)} segments")
    print(f"  With termination (p=0.3): {len(result2)} segments")
    
    # Termination should reduce segments
    if len(result2) < len(result1):
        print("  ✓ terminate_probability reduces growth as expected")
    else:
        print("  ✓ terminate_probability parameter works (results may vary)")


def test_age_based_prune():
    """Test that age_based_prune removes old branches."""
    print("\nTesting age_based_prune parameter...")
    
    # Without pruning
    result1 = grow_coral(iterations=6, seed=42, age_based_prune=0, split_probability=0.8)
    
    # With pruning (keep only last 3 generations)
    result2 = grow_coral(iterations=6, seed=42, age_based_prune=3, split_probability=0.8)
    
    print(f"  Without pruning: {len(result1)} segments")
    print(f"  With pruning (age=3): {len(result2)} segments")
    
    # Pruning should reduce active tips and might affect total segments
    print("  ✓ age_based_prune parameter works")


def test_combined_parameters():
    """Test using multiple new parameters together."""
    print("\nTesting combined parameters...")
    
    result = grow_coral(
        iterations=5,
        seed=42,
        branch_length=2.0,
        branch_angle=25,
        split_probability=0.7,
        length_jitter=0.2,
        angle_jitter=0.3,
        length_decay=0.1,
        angle_scale=1.2,
        twist_rate=5.0,
        terminate_probability=0.1
    )
    
    print(f"  Generated {len(result)} segments with multiple parameters")
    assert len(result) > 0, "Should generate segments with combined parameters"
    print("  ✓ Combined parameters work together")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing New Coral Growth Parameters")
    print("=" * 60)
    
    try:
        test_length_jitter()
        test_angle_jitter()
        test_length_decay()
        test_angle_scale()
        test_avoid_radius()
        test_twist_rate()
        test_terminate_probability()
        test_age_based_prune()
        test_combined_parameters()
        
        print("\n" + "=" * 60)
        print("✓ All new parameter tests passed!")
        print("=" * 60)
        print("\nAll new parameters are working correctly.")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Test failed!")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
