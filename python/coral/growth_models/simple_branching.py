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
               stem_generations=0, stem_angle=None):
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
    
    Returns
    -------
    list of tuples
        List of line segments, each as ((x0,y0,z0), (x1,y1,z1)).
    """
    if seed is not None:
        random.seed(seed)
    
    # Store all line segments
    segments = []
    
    # Active tips: each is (point, direction_vector, is_trunk)
    # Direction vector is normalized (unit vector)
    initial_direction = (0, 0, 1)  # Start growing upward
    tips = [(start, initial_direction, True)]  # start as trunk
    
    for iteration in range(iterations):
        new_tips = []
        
        for tip_point, tip_direction, is_trunk in tips:
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
                    new_dir_trunk = perturb_direction(tip_direction, max_angle=trunk_angle, enforce_upward=True)
                    end_trunk = (
                        tip_point[0] + new_dir_trunk[0] * branch_length,
                        tip_point[1] + new_dir_trunk[1] * branch_length,
                        tip_point[2] + new_dir_trunk[2] * branch_length
                    )
                    segments.append((tip_point, end_trunk))
                    new_tips.append((end_trunk, new_dir_trunk, True))

                    # Branch child (wide angle)
                    new_dir_branch = perturb_direction(tip_direction, max_angle=branch_angle, enforce_upward=True)
                    end_branch = (
                        tip_point[0] + new_dir_branch[0] * branch_length,
                        tip_point[1] + new_dir_branch[1] * branch_length,
                        tip_point[2] + new_dir_branch[2] * branch_length
                    )
                    segments.append((tip_point, end_branch))
                    new_tips.append((end_branch, new_dir_branch, False))
                else:
                    # Non-trunk tip splits into two branches (both non-trunk)
                    for _ in range(2):
                        new_direction = perturb_direction(tip_direction, max_angle=branch_angle, enforce_upward=True)
                        end_point = (
                            tip_point[0] + new_direction[0] * branch_length,
                            tip_point[1] + new_direction[1] * branch_length,
                            tip_point[2] + new_direction[2] * branch_length
                        )
                        segments.append((tip_point, end_point))
                        new_tips.append((end_point, new_direction, False))
            else:
                # Single continuation: trunk stays trunk and uses trunk_angle; branches use branch_angle
                angle = trunk_angle if is_trunk else branch_angle
                new_direction = perturb_direction(tip_direction, max_angle=angle, enforce_upward=True)
                end_point = (
                    tip_point[0] + new_direction[0] * branch_length,
                    tip_point[1] + new_direction[1] * branch_length,
                    tip_point[2] + new_direction[2] * branch_length
                )
                segments.append((tip_point, end_point))
                new_tips.append((end_point, new_direction, is_trunk))
        
        # Update tips for next iteration
        tips = new_tips
        
        # If no tips left, stop early
        if not tips:
            break
    
    return segments


def perturb_direction(direction, max_angle=25, enforce_upward=False, _max_attempts=12):
    """
    Randomly perturb a direction vector within a cone of max_angle degrees.
    
    Parameters
    ----------
    direction : tuple of float
        Input direction vector (dx, dy, dz), should be normalized.
    max_angle : float
        Maximum perturbation angle in degrees.
    
    Returns
    -------
    tuple of float
        New normalized direction vector.
    """
    # Convert angle to radians
    max_rad = math.radians(max_angle)
    
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
