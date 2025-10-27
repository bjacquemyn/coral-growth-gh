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
               branch_angle=25, split_probability=0.7, seed=None, stem_generations=0):
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
    
    Returns
    -------
    list of tuples
        List of line segments, each as ((x0,y0,z0), (x1,y1,z1)).
    """
    if seed is not None:
        random.seed(seed)
    
    # Store all line segments
    segments = []
    
    # Active tips: each is (point, direction_vector)
    # Direction vector is normalized (unit vector)
    initial_direction = (0, 0, 1)  # Start growing upward
    tips = [(start, initial_direction)]
    
    for iteration in range(iterations):
        new_tips = []
        
        for tip_point, tip_direction in tips:
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
            
            for _ in range(num_children):
                # Randomize direction slightly
                new_direction = perturb_direction(
                    tip_direction, 
                    max_angle=branch_angle
                )
                
                # Calculate end point of new segment
                end_point = (
                    tip_point[0] + new_direction[0] * branch_length,
                    tip_point[1] + new_direction[1] * branch_length,
                    tip_point[2] + new_direction[2] * branch_length
                )
                
                # Store the segment
                segments.append((tip_point, end_point))
                
                # Add new tip for next iteration
                new_tips.append((end_point, new_direction))
        
        # Update tips for next iteration
        tips = new_tips
        
        # If no tips left, stop early
        if not tips:
            break
    
    return segments


def perturb_direction(direction, max_angle=25):
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
    
    # Random spherical coordinates for perturbation
    theta = random.uniform(0, 2 * math.pi)  # Azimuthal angle
    phi = random.uniform(0, max_rad)         # Polar angle from direction
    
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
    
    # Perturb in the cone
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)
    
    new_direction = (
        dx * cos_phi + u[0] * sin_phi * cos_theta + v[0] * sin_phi * sin_theta,
        dy * cos_phi + u[1] * sin_phi * cos_theta + v[1] * sin_phi * sin_theta,
        dz * cos_phi + u[2] * sin_phi * cos_theta + v[2] * sin_phi * sin_theta
    )
    
    return normalize(new_direction)


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
