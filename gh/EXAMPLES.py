"""
COMPREHENSIVE EXAMPLE: Using All Coral Growth Parameters in Grasshopper

This example demonstrates how to use all available parameters to create
different types of coral structures. Copy any of these examples into your
GhPython component in Grasshopper.

All examples assume you have the standard component setup from 
coral_component_example.py with the path configuration.
"""

# ============================================================================
# EXAMPLE 1: Simple Bushy Coral
# ============================================================================
# Good for: Dense, compact coral forms
#
# Grasshopper Inputs:
#   start: Point (e.g., origin)
#   iterations: 6
#   branch_length: 1.5
#   branch_angle: 30
#   split_probability: 0.8
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=6,
    branch_length=1.5,
    branch_angle=30,
    split_probability=0.8,
    seed=42
)


# ============================================================================
# EXAMPLE 2: Tree-like Coral with Main Trunk
# ============================================================================
# Good for: Tall coral with clear main structure
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 8
#   branch_length: 2.0
#   branch_angle: 25
#   split_probability: 0.7
#   stem_generations: 3
#   stem_angle: 5
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=8,
    branch_length=2.0,
    branch_angle=25,
    split_probability=0.7,
    stem_generations=3,
    stem_angle=5,  # Straight stem
    seed=42
)


# ============================================================================
# EXAMPLE 3: Organic Coral with Variation
# ============================================================================
# Good for: Natural-looking, irregular growth
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 7
#   branch_length: 1.8
#   branch_angle: 28
#   split_probability: 0.75
#   length_jitter: 0.25
#   angle_jitter: 0.3
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=7,
    branch_length=1.8,
    branch_angle=28,
    split_probability=0.75,
    length_jitter=0.25,   # 25% length variation
    angle_jitter=0.3,      # 30% angle variation
    seed=42
)


# ============================================================================
# EXAMPLE 4: Tapering Coral (Young to Old)
# ============================================================================
# Good for: Realistic growth with thinner tips
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 8
#   branch_length: 2.5
#   branch_angle: 25
#   split_probability: 0.7
#   length_decay: 0.12
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=8,
    branch_length=2.5,
    branch_angle=25,
    split_probability=0.7,
    length_decay=0.12,  # 12% reduction per generation
    seed=42
)


# ============================================================================
# EXAMPLE 5: Spiral Coral
# ============================================================================
# Good for: Twisted, helical forms
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 10
#   branch_length: 1.5
#   branch_angle: 20
#   split_probability: 0.6
#   twist_rate: 15.0
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=10,
    branch_length=1.5,
    branch_angle=20,
    split_probability=0.6,
    twist_rate=15.0,  # 15° twist per iteration
    seed=42
)


# ============================================================================
# EXAMPLE 6: Sparse Coral with Space Constraints
# ============================================================================
# Good for: Controlled density, avoiding self-intersection
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 8
#   branch_length: 2.0
#   branch_angle: 30
#   split_probability: 0.85
#   avoid_radius: 1.2
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=8,
    branch_length=2.0,
    branch_angle=30,
    split_probability=0.85,  # High split probability
    avoid_radius=1.2,         # But avoid crowding
    seed=42
)


# ============================================================================
# EXAMPLE 7: Dying/Pruning Coral
# ============================================================================
# Good for: Simulating natural death and regeneration
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 10
#   branch_length: 1.8
#   branch_angle: 25
#   split_probability: 0.75
#   terminate_probability: 0.15
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=10,
    branch_length=1.8,
    branch_angle=25,
    split_probability=0.75,
    terminate_probability=0.15,  # 15% chance to stop growing
    seed=42
)


# ============================================================================
# EXAMPLE 8: Young Coral (Only Recent Growth)
# ============================================================================
# Good for: Showing only active growth zones
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 10
#   branch_length: 2.0
#   branch_angle: 30
#   split_probability: 0.8
#   age_based_prune: 3
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=10,
    branch_length=2.0,
    branch_angle=30,
    split_probability=0.8,
    age_based_prune=3,  # Keep only last 3 generations
    seed=42
)


# ============================================================================
# EXAMPLE 9: Complex Realistic Coral
# ============================================================================
# Good for: Most natural-looking result combining multiple effects
#
# Grasshopper Inputs:
#   start: Point
#   iterations: 10
#   branch_length: 2.0
#   branch_angle: 28
#   split_probability: 0.75
#   stem_generations: 2
#   stem_angle: 8
#   length_jitter: 0.2
#   angle_jitter: 0.25
#   length_decay: 0.08
#   angle_scale: 1.1
#   twist_rate: 5.0
#   terminate_probability: 0.05
#   seed: 42

segments = grow_coral(
    start=start_tuple,
    iterations=10,
    branch_length=2.0,
    branch_angle=28,
    split_probability=0.75,
    stem_generations=2,
    stem_angle=8,
    length_jitter=0.2,
    angle_jitter=0.25,
    length_decay=0.08,
    angle_scale=1.1,
    twist_rate=5.0,
    terminate_probability=0.05,
    seed=42
)


# ============================================================================
# EXAMPLE 10: Parametric Study Setup
# ============================================================================
# Good for: Exploring parameter space in Grasshopper
# Use number sliders for each parameter
#
# Grasshopper Inputs (with suggested slider ranges):
#   start: Point
#   iterations: int slider (3-15)
#   branch_length: float slider (0.5-5.0)
#   branch_angle: float slider (5-60)
#   split_probability: float slider (0.0-1.0)
#   stem_generations: int slider (0-5)
#   stem_angle: float slider (0-45)
#   length_jitter: float slider (0.0-0.5)
#   angle_jitter: float slider (0.0-0.5)
#   length_decay: float slider (0.0-0.3)
#   angle_scale: float slider (0.5-2.0)
#   avoid_radius: float slider (0.0-3.0)
#   twist_rate: float slider (0-30)
#   terminate_probability: float slider (0.0-0.3)
#   age_based_prune: int slider (0-5)
#   seed: int slider (0-1000)

segments = grow_coral(
    start=start_tuple,
    iterations=iterations,
    branch_length=branch_length,
    branch_angle=branch_angle,
    split_probability=split_probability,
    stem_generations=stem_generations,
    stem_angle=stem_angle if stem_angle > 0 else None,
    length_jitter=length_jitter,
    angle_jitter=angle_jitter,
    length_decay=length_decay,
    angle_scale=angle_scale,
    avoid_radius=avoid_radius,
    twist_rate=twist_rate,
    terminate_probability=terminate_probability,
    age_based_prune=age_based_prune,
    seed=seed if seed > 0 else None
)


# ============================================================================
# TIPS FOR GRASSHOPPER USAGE
# ============================================================================

"""
1. Start Simple:
   - Begin with just iterations, branch_length, and split_probability
   - Add parameters gradually to understand their effects

2. Use Number Sliders:
   - Connect sliders to each input parameter
   - This allows real-time exploration of the parameter space

3. Seed Values:
   - Use a fixed seed (e.g., 42) for reproducible results
   - Change seed to generate variations with the same parameters

4. Performance:
   - Higher iterations and split_probability = more segments = slower
   - Use avoid_radius sparingly (it checks all existing endpoints)
   - age_based_prune can limit segment count for high iterations

5. Natural-Looking Results:
   - Combine length_jitter + angle_jitter for organic variation
   - Use length_decay for realistic tapering
   - Add small twist_rate (3-10°) for subtle helical patterns

6. Experiment!
   - These parameters interact in complex ways
   - Try extreme values to understand boundaries
   - Save interesting parameter combinations

7. Outputs:
   - 'out' or 'segments' → Connect to pipeline or display
   - 'end_points' → Use for further geometry operations
   - 'segments_raw' → Access raw data for analysis
"""
