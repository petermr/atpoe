"""
Test file for segment length algorithm - 2024-12-19
Tests the find_next_point_at_distance strategy with pathological cases.
"""

import math
import random
from typing import List, Tuple
from atpoe.segment_algorithm import find_next_point_at_distance
from atpoe.fog_polygon_generator import is_point_inside_polygon

def test_find_next_point_pathologies():
    """Test find_next_point_at_distance with pathological curve shapes."""
    
    print("=== PATHOLOGICAL TESTS FOR find_next_point_at_distance ===")
    
    # Test 1: Very pointed curve (sharp spike)
    print("\n--- Test 1: Sharp Spike ---")
    spike_curve = generate_spike_curve(center=(500, 500), radius=100, spike_length=200)
    test_single_point_placement(spike_curve, start_point=(450, 500), segment_length=20, distance=15, test_name="Sharp Spike")
    
    # Test 2: Deep concave curve (potential for islands)
    print("\n--- Test 2: Deep Concave ---")
    deep_concave = generate_deep_concave_curve(center=(500, 500), radius=100, depth=150)
    test_single_point_placement(deep_concave, start_point=(450, 500), segment_length=20, distance=15, test_name="Deep Concave")
    
    # Test 3: Star with very sharp points
    print("\n--- Test 3: Sharp Star ---")
    sharp_star = generate_sharp_star_curve(center=(500, 500), radius=100, num_points=5)
    test_single_point_placement(sharp_star, start_point=(450, 500), segment_length=20, distance=15, test_name="Sharp Star")
    
    # Test 4: Irregular curve with extreme variations
    print("\n--- Test 4: Extreme Irregular ---")
    extreme_irregular = generate_extreme_irregular_curve(center=(500, 500), radius=100)
    test_single_point_placement(extreme_irregular, start_point=(450, 500), segment_length=20, distance=15, test_name="Extreme Irregular")
    
    # Test 5: Curve with narrow passages
    print("\n--- Test 5: Narrow Passages ---")
    narrow_passages = generate_narrow_passages_curve(center=(500, 500), radius=100)
    test_single_point_placement(narrow_passages, start_point=(450, 500), segment_length=20, distance=15, test_name="Narrow Passages")

def generate_spike_curve(center: Tuple[float, float], radius: float, spike_length: float) -> List[Tuple[float, float]]:
    """Generate curve with a very sharp spike that could cause issues."""
    points = []
    for i in range(10):
        angle = 2 * math.pi * i / 10
        if i == 0:  # Create sharp spike
            r = spike_length
        else:
            r = radius
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_deep_concave_curve(center: Tuple[float, float], radius: float, depth: float) -> List[Tuple[float, float]]:
    """Generate curve with deep concave sections that might create islands."""
    points = []
    for i in range(10):
        angle = 2 * math.pi * i / 10
        # Create deep concave in middle section
        if 0.3 <= (i / 10) <= 0.7:
            r = depth  # Very deep concave
        else:
            r = radius
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_sharp_star_curve(center: Tuple[float, float], radius: float, num_points: int) -> List[Tuple[float, float]]:
    """Generate star with very sharp, long points."""
    points = []
    for i in range(num_points * 2):
        angle = 2 * math.pi * i / (num_points * 2)
        if i % 2 == 0:
            r = radius * 2.5  # Very long sharp points
        else:
            r = radius * 0.3  # Very deep valleys
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_extreme_irregular_curve(center: Tuple[float, float], radius: float) -> List[Tuple[float, float]]:
    """Generate curve with extreme random variations."""
    points = []
    random.seed(123)  # For reproducible tests
    for i in range(10):
        angle = 2 * math.pi * i / 10
        # Extreme variations
        r = radius * (0.2 + 2.0 * random.random())  # 0.2x to 2.2x radius
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_narrow_passages_curve(center: Tuple[float, float], radius: float) -> List[Tuple[float, float]]:
    """Generate curve with very narrow passages that might trap the algorithm."""
    points = []
    for i in range(12):
        angle = 2 * math.pi * i / 12
        # Create narrow passages
        if i % 3 == 0:
            r = radius * 1.5  # Wide sections
        elif i % 3 == 1:
            r = radius * 0.8  # Medium sections
        else:
            r = radius * 0.4  # Very narrow passages
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def test_single_point_placement(outer_curve: List[Tuple[float, float]], start_point: Tuple[float, float], 
                               segment_length: float, distance: float, test_name: str):
    """Test single point placement for pathological cases."""
    print(f"Testing {test_name}")
    print(f"Start point: {start_point}")
    print(f"Outer curve has {len(outer_curve)} points")
    
    # Test multiple directions
    for direction in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]:
        next_point = find_next_point_at_distance(
            start_point, outer_curve, segment_length, distance, direction
        )
        
        if next_point:
            actual_distance = math.hypot(next_point[0] - start_point[0], next_point[1] - start_point[1])
            print(f"  Direction {direction:.2f}: Next point {next_point}, actual distance {actual_distance:.2f}")
            
            # Check if point is inside curve
            # from segment_length_algorithm import is_point_inside_curve
            inside = is_point_inside_polygon(next_point, outer_curve)
            print(f"    Inside curve: {inside}")
        else:
            print(f"  Direction {direction:.2f}: No valid point found")

def test_find_next_point_at_distance():
    """Test the find_next_point_at_distance function with various curve shapes."""
    
    # Test 1: Simple circle (baseline)
    print("=== Test 1: Simple Circle ===")
    circle_curve = generate_test_circle(center=(500, 500), radius=100, num_points=10)
    test_segment_placement(circle_curve, segment_length=20, distance=15, test_name="Circle")
    
    # Test 2: Pointed curve (sharp angles)
    print("\n=== Test 2: Pointed Curve ===")
    pointed_curve = generate_test_pointed_curve(center=(500, 500), radius=100, num_points=10)
    test_segment_placement(pointed_curve, segment_length=20, distance=15, test_name="Pointed")
    
    # Test 3: Very concave curve (potential for islands/lakes)
    print("\n=== Test 3: Concave Curve ===")
    concave_curve = generate_test_concave_curve(center=(500, 500), radius=100, num_points=10)
    test_segment_placement(concave_curve, segment_length=20, distance=15, test_name="Concave")
    
    # Test 4: Star-shaped curve (multiple sharp points)
    print("\n=== Test 4: Star Curve ===")
    star_curve = generate_test_star_curve(center=(500, 500), radius=100, num_points=10)
    test_segment_placement(star_curve, segment_length=20, distance=15, test_name="Star")
    
    # Test 5: Irregular curve (random perturbations)
    print("\n=== Test 5: Irregular Curve ===")
    irregular_curve = generate_test_irregular_curve(center=(500, 500), radius=100, num_points=10)
    test_segment_placement(irregular_curve, segment_length=20, distance=15, test_name="Irregular")

def generate_test_circle(center: Tuple[float, float], radius: float, num_points: int) -> List[Tuple[float, float]]:
    """Generate a simple circular test curve."""
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    return points

def generate_test_pointed_curve(center: Tuple[float, float], radius: float, num_points: int) -> List[Tuple[float, float]]:
    """Generate a pointed curve with sharp angles."""
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Add sharp points every 3rd point
        if i % 3 == 0:
            r = radius * 1.5  # Sharp outward point
        else:
            r = radius * 0.7  # Sharp inward point
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_test_concave_curve(center: Tuple[float, float], radius: float, num_points: int) -> List[Tuple[float, float]]:
    """Generate a very concave curve that might create islands/lakes."""
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Create deep concave sections
        if 0.2 <= (i / num_points) <= 0.4 or 0.6 <= (i / num_points) <= 0.8:
            r = radius * 0.3  # Deep concave
        else:
            r = radius * 1.2  # Convex sections
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_test_star_curve(center: Tuple[float, float], radius: float, num_points: int) -> List[Tuple[float, float]]:
    """Generate a star-shaped curve with multiple sharp points."""
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Create star pattern
        if i % 2 == 0:
            r = radius * 1.3  # Star points
        else:
            r = radius * 0.5  # Star valleys
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def generate_test_irregular_curve(center: Tuple[float, float], radius: float, num_points: int) -> List[Tuple[float, float]]:
    """Generate an irregular curve with random perturbations."""
    points = []
    random.seed(42)  # For reproducible tests
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Add random perturbations
        r = radius * (0.8 + 0.4 * random.random())
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    return points

def test_segment_placement(outer_curve: List[Tuple[float, float]], segment_length: float, distance: float, test_name: str):
    """Test segment placement for a given curve shape."""
    print(f"Testing {test_name} curve with {len(outer_curve)} points")
    print(f"Segment length: {segment_length}, Distance: {distance}")
    
    # Generate new curve using the algorithm
    new_curve = generate_curve_by_segment_length(outer_curve, segment_length, distance)
    
    if new_curve:
        print(f"Generated curve with {len(new_curve)} points")
        
        # Calculate actual segment lengths
        segment_lengths = []
        for i in range(len(new_curve) - 1):
            p1 = new_curve[i]
            p2 = new_curve[i + 1]
            seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            segment_lengths.append(seg_len)
        
        # Calculate statistics
        avg_length = sum(segment_lengths) / len(segment_lengths)
        min_length = min(segment_lengths)
        max_length = max(segment_lengths)
        
        print(f"Segment length stats - Avg: {avg_length:.2f}, Min: {min_length:.2f}, Max: {max_length:.2f}")
        print(f"Target segment length: {segment_length}")
        print(f"Accuracy: {abs(avg_length - segment_length) / segment_length * 100:.1f}%")
        
        # Check for closure
        first_point = new_curve[0]
        last_point = new_curve[-1]
        closure_distance = math.hypot(last_point[0] - first_point[0], last_point[1] - first_point[1])
        print(f"Closure distance: {closure_distance:.2f} (should be < {segment_length})")
        
        # Visual representation (simple ASCII)
        print("Curve shape (simplified):")
        for i, point in enumerate(new_curve[::max(1, len(new_curve)//10)]):  # Show every 10th point
            print(f"  Point {i}: ({point[0]:.1f}, {point[1]:.1f})")
    else:
        print("Failed to generate curve")

def generate_curve_by_segment_length(outer_curve: List[Tuple[float, float]], segment_length: float, distance: float) -> List[Tuple[float, float]]:
    """
    Generate a new curve by proceeding forward by segment length.
    
    Args:
        outer_curve: The previous curve to follow
        segment_length: Target length between consecutive points
        distance: Distance to maintain from outer curve
    
    Returns:
        List of points forming the new curve
    """
    # This will be implemented in the main algorithm
    # For now, return a placeholder
    return []

if __name__ == "__main__":
    test_find_next_point_pathologies()
    print("\n" + "="*50)
    test_find_next_point_at_distance()
