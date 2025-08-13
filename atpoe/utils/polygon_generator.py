"""
Date: 2025-08-10
Description: Polygon generation utility functions for testing
"""

import time
from pathlib import Path

def generate_inner_polygon_with_validation(
    outer_polygon, 
    segment_length, 
    target_separation, 
    min_separation, 
    max_separation, 
    max_points, 
    max_time_seconds,
    max_closure=10,
    start_time=0

):
    """
    Date: 2025-08-10
    Description: Generate inner polygon and perform validation checks
    
    Returns:
    tuple: (inner_polygon, unique_points, elapsed_time)
    """

    start_time = time.time()
    # Import and call the fog-based polygon generation function
    from atpoe.fog_polygon_generator import generate_nested_polygon
    
    inner_polygon = generate_nested_polygon(
        previous_polygon=outer_polygon,
        segment_length=segment_length,
        target_separation=target_separation,
        min_separation=min_separation,
        max_separation=max_separation,
        max_points=max_points,
        max_closure=max_closure
    )
    assert inner_polygon is not None, "inner polygon should not be None"
    lenpoly = len(inner_polygon)
    assert lenpoly > 3, f"Not enough points for polygon {lenpoly}"

    # Check time limit
    # elapsed_time = time.time() - start_time
    # if elapsed_time > max_time_seconds:
    #     raise TimeoutError(f"Polygon generation exceeded time limit: {elapsed_time:.2f}s > {max_time_seconds}s")
    
    # Check point limit
    if lenpoly > max_points:
        raise ValueError(f"Polygon generation exceeded point limit: {lenpoly} > {max_points}")
    
    # Get unique points
    unique_points = []
    for point in inner_polygon:
        if point not in unique_points:
            unique_points.append(point)
    
    assert len(unique_points) > 3, f"not enough unique points {len(unique_points)}"
    
    return inner_polygon, unique_points, time.time() - start_time

