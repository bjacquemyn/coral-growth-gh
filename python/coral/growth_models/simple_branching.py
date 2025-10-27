"""
Simple branching coral growth algorithm.

This model generates coral-like structures through iterative branching.
Each branch can split into two child branches with some probability,
creating organic, tree-like forms.

The algorithm is deterministic when using a fixed random seed, making it
reproducible for parametric studies in Grasshopper.
"""

import math
import random


def grow_coral(start=(0, 0, 0), iterations=5, branch_length=2.0,
               branch_angle=25, split_probability=0.7, seed=None,
               stem_generations=0, stem_angle=None,
               length_jitter=0.0, angle_jitter=0.0, length_decay=0.0,
               angle_scale=1.0, avoid_radius=0.0, twist_rate=0.0,
               terminate_probability=0.0, age_based_prune=0):
    """
    Generate a branching coral structure.
    
    Parameters
    ----------
    start : tuple of float
        Starting point (x, y, z) for the coral base.
    iterations : int
        Number of growth iterations. More iterations = more complex structure.
    branch_length : float
        Length of each branch segment.
    branch_angle : float
        Maximum deviation angle (degrees) for new branches.
    split_probability : float
        Probability (0-1) that a branch tip will split into two branches.
    seed : int, optional
        Random seed for reproducible results.
    stem_generations : int, optional
        Number of initial generations that must grow as a single stem before 
        branching is allowed. Default is 0 (branching allowed immediately).
    stem_angle : float or None, optional
        Maximum deviation angle (degrees) used for the main stem. If None,
        the stem uses the same value as branch_angle. Use a small value
        (e.g., 0-10) for a straight-ish stem while allowing branches to
        use a wider angle via branch_angle.
    length_jitter : float, optional
        Random variation factor for branch length (0-1). At 0, no variation.
        At 1, length varies randomly between 0 and 2*branch_length.
    angle_jitter : float, optional
        Random variation factor for branch angle (0-1). At 0, no variation.
        At 1, angle varies randomly between 0 and 2*branch_angle.
    length_decay : float, optional
        Multiplicative decay factor for branch length per generation (0-1).
        At 0, no decay. At 0.1, length reduces by 10% per generation.
    angle_scale : float, optional
        Scaling factor for branch angles. Values < 1 reduce angles,
        values > 1 increase angles. Default is 1.0 (no scaling).
    avoid_radius : float, optional
        Minimum distance to maintain between branch endpoints. If > 0,
        prevents new branches from growing too close to existing endpoints.
    twist_rate : float, optional
        Rotational twist rate in degrees per iteration around the growth axis.
        Adds spiral/helical patterns to the growth.
    terminate_probability : float, optional
        Probability (0-1) that a branch tip terminates and stops growing
        instead of continuing.
    age_based_prune : int, optional
        If > 0, branches older than this many generations are removed/pruned.
        Simulates aging and loss of older growth.
    
    Returns
    -------
    list of tuples
        List of line segments, each as ((x0,y0,z0), (x1,y1,z1)).
    """
    if seed is not None:
        random.seed(seed)
    
    # Validate and clamp parameters
    length_jitter = max(0.0, min(1.0, float(length_jitter)))
    angle_jitter = max(0.0, min(1.0, float(angle_jitter)))
    length_decay = max(0.0, min(1.0, float(length_decay)))
    angle_scale = max(0.0, float(angle_scale))
    avoid_radius = max(0.0, float(avoid_radius))
    terminate_probability = max(0.0, min(1.0, float(terminate_probability)))
    age_based_prune = max(0, int(age_based_prune))
    
    # Store all line segments and endpoints for collision detection
    segments = []
    endpoints = []  # For avoid_radius checking
    
    # Active tips: each is (point, direction_vector, is_trunk, generation_born, twist_angle)
    # Direction vector is normalized (unit vector)
    # generation_born tracks when this tip was created for age-based pruning
    # twist_angle accumulates rotational twist
    initial_direction = (0, 0, 1)  # Start growing upward
    tips = [(start, initial_direction, True, 0, 0.0)]  # start as trunk at generation 0
    
    for iteration in range(iterations):
        new_tips = []
        
        # Age-based pruning: remove tips that are too old
        if age_based_prune > 0:
            tips = [(pt, dir, trunk, gen, twist) for (pt, dir, trunk, gen, twist) in tips
                    if iteration - gen < age_based_prune]
        
        for tip_point, tip_direction, is_trunk, generation_born, twist_angle in tips:
            # Termination check
            if random.random() < terminate_probability:
                continue
            
            # Decide if this tip should split
            # During stem generations, force single stem growth (no branching)
            if iteration < stem_generations:
                # Stem generation: no branching allowed
                num_children = 1
            elif random.random() < split_probability:
                # Create two child branches
                num_children = 2
            else:
                # Single branch continues
                num_children = 1

            # Calculate length for this iteration with jitter and decay
            current_length = branch_length
            
            # Apply length decay based on generation depth
            generations_elapsed = iteration - generation_born
            if length_decay > 0 and generations_elapsed > 0:
                current_length *= (1.0 - length_decay) ** generations_elapsed
            
            # Apply length jitter (random variation)
            if length_jitter > 0:
                jitter_factor = 1.0 + (random.random() * 2 - 1) * length_jitter
                current_length *= jitter_factor

            # Determine angles to use
            trunk_angle = branch_angle if stem_angle is None else stem_angle
            
            # Apply angle scaling
            trunk_angle *= angle_scale
            effective_branch_angle = branch_angle * angle_scale

            # Update twist angle for this iteration
            new_twist_angle = twist_angle + twist_rate
            # Decide if this tip should split
            # During stem generations, force single stem growth (no branching)
            if iteration < stem_generations:
                # Stem generation: no branching allowed
                num_children = 1
            elif random.random() < split_probability:
                # Create two child branches
                num_children = 2
            else:
                # Single branch continues
                num_children = 1

            # Determine angles to use
            trunk_angle = branch_angle if stem_angle is None else stem_angle

            if num_children == 2:
                # If this tip is part of the trunk, keep one child as trunk with smaller angle
                if is_trunk:
                    # Trunk child (continues upward-ish)
                    # Apply angle jitter
                    actual_trunk_angle = trunk_angle
                    if angle_jitter > 0:
                        jitter_factor = 1.0 + (random.random() * 2 - 1) * angle_jitter
                        actual_trunk_angle *= jitter_factor
                    
                    new_dir_trunk = perturb_direction(tip_direction, max_angle=actual_trunk_angle, 
                                                     enforce_upward=True, twist_angle=new_twist_angle)
                    end_trunk = (
                        tip_point[0] + new_dir_trunk[0] * current_length,
                        tip_point[1] + new_dir_trunk[1] * current_length,
                        tip_point[2] + new_dir_trunk[2] * current_length
                    )
                    
                    # Check avoid_radius constraint
                    if avoid_radius > 0 and _too_close_to_existing(end_trunk, endpoints, avoid_radius):
                        # Skip this branch but continue processing
                        pass
                    else:
                        segments.append((tip_point, end_trunk))
                        endpoints.append(end_trunk)
                        new_tips.append((end_trunk, new_dir_trunk, True, iteration, new_twist_angle))

                    # Branch child (wide angle)
                    actual_branch_angle = effective_branch_angle
                    if angle_jitter > 0:
                        jitter_factor = 1.0 + (random.random() * 2 - 1) * angle_jitter
                        actual_branch_angle *= jitter_factor
                    
                    new_dir_branch = perturb_direction(tip_direction, max_angle=actual_branch_angle, 
                                                      enforce_upward=True, twist_angle=new_twist_angle)
                    end_branch = (
                        tip_point[0] + new_dir_branch[0] * current_length,
                        tip_point[1] + new_dir_branch[1] * current_length,
                        tip_point[2] + new_dir_branch[2] * current_length
                    )
                    
                    if avoid_radius > 0 and _too_close_to_existing(end_branch, endpoints, avoid_radius):
                        pass
                    else:
                        segments.append((tip_point, end_branch))
                        endpoints.append(end_branch)
                        new_tips.append((end_branch, new_dir_branch, False, iteration, new_twist_angle))
                else:
                    # Non-trunk tip splits into two branches (both non-trunk)
                    for _ in range(2):
                        actual_branch_angle = effective_branch_angle
                        if angle_jitter > 0:
                            jitter_factor = 1.0 + (random.random() * 2 - 1) * angle_jitter
                            actual_branch_angle *= jitter_factor
                        
                        new_direction = perturb_direction(tip_direction, max_angle=actual_branch_angle, 
                                                         enforce_upward=True, twist_angle=new_twist_angle)
                        end_point = (
                            tip_point[0] + new_direction[0] * current_length,
                            tip_point[1] + new_direction[1] * current_length,
                            tip_point[2] + new_direction[2] * current_length
                        )
                        
                        if avoid_radius > 0 and _too_close_to_existing(end_point, endpoints, avoid_radius):
                            continue
                        
                        segments.append((tip_point, end_point))
                        endpoints.append(end_point)
                        new_tips.append((end_point, new_direction, False, iteration, new_twist_angle))
            else:
                # Single continuation: trunk stays trunk and uses trunk_angle; branches use branch_angle
                angle = trunk_angle if is_trunk else effective_branch_angle
                
                if angle_jitter > 0:
                    jitter_factor = 1.0 + (random.random() * 2 - 1) * angle_jitter
                    angle *= jitter_factor
                
                new_direction = perturb_direction(tip_direction, max_angle=angle, 
                                                 enforce_upward=True, twist_angle=new_twist_angle)
                end_point = (
                    tip_point[0] + new_direction[0] * current_length,
                    tip_point[1] + new_direction[1] * current_length,
                    tip_point[2] + new_direction[2] * current_length
                )
                
                if avoid_radius > 0 and _too_close_to_existing(end_point, endpoints, avoid_radius):
                    # Skip this branch
                    pass
                else:
                    segments.append((tip_point, end_point))
                    endpoints.append(end_point)
                    new_tips.append((end_point, new_direction, is_trunk, iteration, new_twist_angle))
        
        # Update tips for next iteration
        tips = new_tips
        
        # If no tips left, stop early
        if not tips:
            break
    
    return segments


def perturb_direction(direction, max_angle=25, enforce_upward=False, twist_angle=0.0, _max_attempts=12):
    """
    Randomly perturb a direction vector within a cone of max_angle degrees.
    
    Parameters
    ----------
    direction : tuple of float
        Input direction vector (dx, dy, dz), should be normalized.
    max_angle : float
        Maximum perturbation angle in degrees.
    enforce_upward : bool
        If True, ensures the Z component is non-negative.
    twist_angle : float
        Additional twist rotation in degrees around the direction axis.
    
    Returns
    -------
    tuple of float
        New normalized direction vector.
    """
    # Convert angle to radians
    max_rad = math.radians(max_angle)
    twist_rad = math.radians(twist_angle)
    
    # Create a local coordinate system aligned with the input direction
    dx, dy, dz = direction

    # Find an arbitrary perpendicular vector
    if abs(dz) < 0.9:
        perpendicular = (0, 0, 1)
    else:
        perpendicular = (1, 0, 0)

    # Cross product to get first basis vector
    u = cross_product(direction, perpendicular)
    u = normalize(u)

    # Cross product to get second basis vector
    v = cross_product(direction, u)
    v = normalize(v)

    # Sample directions; enforce positive Z if requested
    cand = None
    for _ in range(max(1, int(_max_attempts))):
        theta = random.uniform(0, 2 * math.pi)  # Azimuthal angle
        phi = random.uniform(0, max_rad)        # Polar angle from direction

        # Apply twist rotation to the azimuthal angle
        theta += twist_rad

        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        cand = (
            dx * cos_phi + u[0] * sin_phi * cos_theta + v[0] * sin_phi * sin_theta,
            dy * cos_phi + u[1] * sin_phi * cos_theta + v[1] * sin_phi * sin_theta,
            dz * cos_phi + u[2] * sin_phi * cos_theta + v[2] * sin_phi * sin_theta
        )
        if not enforce_upward or cand[2] >= 0:
            return normalize(cand)

    # Fallback: reflect across XY plane to ensure non-negative Z
    cand = (cand[0], cand[1], abs(cand[2]))
    return normalize(cand)


def cross_product(a, b):
    """Compute cross product of two 3D vectors."""
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    )


def normalize(vector):
    """Normalize a 3D vector to unit length."""
    magnitude = math.sqrt(sum(c ** 2 for c in vector))
    if magnitude < 1e-10:
        return (0, 0, 1)  # Default fallback
    return tuple(c / magnitude for c in vector)


def _too_close_to_existing(point, existing_points, min_distance):
    """
    Check if a point is too close to any existing points.
    
    Parameters
    ----------
    point : tuple of float
        The point to check (x, y, z).
    existing_points : list of tuples
        List of existing points to check against.
    min_distance : float
        Minimum allowed distance.
    
    Returns
    -------
    bool
        True if point is too close to any existing point.
    """
    min_dist_sq = min_distance * min_distance
    px, py, pz = point
    
    for ex, ey, ez in existing_points:
        dx = px - ex
        dy = py - ey
        dz = pz - ez
        dist_sq = dx*dx + dy*dy + dz*dz
        
        if dist_sq < min_dist_sq:
            return True
    
    return False


# Example usage for quick testing
if __name__ == "__main__":
    # Generate a small coral structure without stem (default)
    print("Example 1: Default behavior (immediate branching)")
    result1 = grow_coral(
        start=(0, 0, 0),
        iterations=4,
        branch_length=1.5,
        branch_angle=30,
        split_probability=0.6,
        seed=42
    )
    print("Generated {} branch segments".format(len(result1)))
    
    # Generate with stem
    print("\nExample 2: With stem_generations=2 (main stem first)")
    result2 = grow_coral(
        start=(0, 0, 0),
        iterations=4,
        branch_length=1.5,
        branch_angle=30,
        split_probability=0.6,
        seed=42,
        stem_generations=2
    )
    print("Generated {} branch segments".format(len(result2)))
    
    print("\nFirst 3 segments of example 2:")
    for i, seg in enumerate(result2[:3]):
        print("  {}: {} -> {}".format(i, seg[0], seg[1]))
