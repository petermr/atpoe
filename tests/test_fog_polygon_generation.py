"""
Date: 2025-08-10
Description: Test for generating a single inner polygon using fog-based algorithm
"""

import pytest
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import time

from atpoe.curve_generator import generate_initial_circle

# Test parameters
SEGMENT_LENGTH = 1.0
TARGET_SEPARATION = 3.0
MIN_SEPARATION = 2.0
MAX_SEPARATION = 4.0
INTER_CURVE_DISTANCE = 3.0  # Start exactly 3 units inside bounding polygon
MAX_POINTS_PER_POLYGON = 2000  # Safety limit for points (much higher)
MAX_TIME_SECONDS = 30  # Safety limit for execution time
NUM_CURVES = 1


def bounding_polygon(centre, radius, npoints):
    """

    """
    return generate_initial_circle(center_x=centre[0], center_y=centre[1], radius=radius, num_points=npoints)


def test_generate_single_inner_polygon():
    """
    Date: 2025-08-10
    Description: Test generating a single inner polygon inside a bounding polygon
    """
    # Generate bounding polygon (outer curve)
    outer_polygon = bounding_polygon(centre=(500, 500), radius=500, npoints=1000)
    
    # Start timing
    start_time = time.time()
    
    try:
        # TODO: This will call the fog-based polygon generation function
        # inner_polygon = generate_nested_polygon(
        #     previous_polygon=outer_polygon,
        #     segment_length=SEGMENT_LENGTH,
        #     target_separation=TARGET_SEPARATION,
        #     min_separation=MIN_SEPARATION,
        #     max_separation=MAX_SEPARATION,
        #     max_points=MAX_POINTS_PER_POLYGON,
        #     max_time=MAX_TIME_SECONDS
        # )
        
        # Import and call the fog-based polygon generation function
        from atpoe.fog_polygon_generator import generate_nested_polygon
        
        inner_polygon = generate_nested_polygon(
            previous_polygon=outer_polygon,
            segment_length=SEGMENT_LENGTH,
            target_separation=TARGET_SEPARATION,
            min_separation=MIN_SEPARATION,
            max_separation=MAX_SEPARATION,
            max_points=MAX_POINTS_PER_POLYGON
        )
        
        # Check time limit
        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_TIME_SECONDS:
            raise TimeoutError(f"Polygon generation exceeded time limit: {elapsed_time:.2f}s > {MAX_TIME_SECONDS}s")
        
        # Check point limit
        if len(inner_polygon) > MAX_POINTS_PER_POLYGON:
            raise ValueError(f"Polygon generation exceeded point limit: {len(inner_polygon)} > {MAX_POINTS_PER_POLYGON}")
        
        # Assertions
        assert len(inner_polygon) > 0, "Inner polygon must have at least one point"
        assert len(inner_polygon) >= 3, "Inner polygon must have at least 3 points to form a valid polygon"
        
        # Verify all inner polygon points are inside outer polygon
        from atpoe.fog_polygon_generator import is_point_inside_polygon
        for point in inner_polygon:
            assert is_point_inside_polygon(point, outer_polygon), f"Point {point} is outside outer polygon"
        
        # Debug: print polygon details
        print(f"DEBUG: Inner polygon has {len(inner_polygon)} points")
        print(f"DEBUG: First 3 points: {inner_polygon[:3]}")
        print(f"DEBUG: Last 3 points: {inner_polygon[-3:]}")
        
        # Debug: show all unique points
        unique_points = []
        for point in inner_polygon:
            if point not in unique_points:
                unique_points.append(point)
        print(f"DEBUG: Unique points: {len(unique_points)}")
        
        print("DEBUG: About to create success visualization...")
        # Generate success visualization
        create_success_visualization(outer_polygon, inner_polygon, elapsed_time)
        print("DEBUG: Success visualization created")
        
        # Verify graphics output was created
        output_file = Path("temp", "test_generate_single_inner_polygon.png")
        assert output_file.exists(), f"Graphics output not found at {output_file}"
        
        print(f"✅ Test passed: Generated inner polygon with {len(inner_polygon)} points")
        print(f"   Segment length: {SEGMENT_LENGTH}")
        print(f"   Target separation: {TARGET_SEPARATION}")
        print(f"   Separation range: {MIN_SEPARATION} to {MAX_SEPARATION}")
        print(f"   Execution time: {elapsed_time:.2f}s")
        
    except (TimeoutError, ValueError) as e:
        # Handle time or point limit violations
        elapsed_time = time.time() - start_time
        print(f"❌ Test failed: {e}")
        print(f"   Execution time: {elapsed_time:.2f}s")
        print(f"   Point limit: {MAX_POINTS_PER_POLYGON}")
        print(f"   Time limit: {MAX_TIME_SECONDS}s")
        
        # Create failure visualization
        create_failure_visualization(outer_polygon, str(e), elapsed_time)
        
        # Verify graphics output was created
        output_file = Path("temp", "test_generate_single_inner_polygon.png")
        assert output_file.exists(), f"Graphics output not found at {output_file}"
        
        # Re-raise the exception for test framework
        raise



def create_success_visualization(outer_polygon, inner_polygon, elapsed_time):
    """
    Date: 2025-08-10
    Description: Create visualization for successful polygon generation
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot outer polygon (thinner to avoid overlap issues)
    outer_x, outer_y = zip(*outer_polygon)
    ax.plot(outer_x + (outer_x[0],), outer_y + (outer_y[0],), 
            'b-', linewidth=0.5, alpha=0.7, label='Outer Polygon (Bounding)')
    
    # Plot inner polygon (thinner line)
    inner_x, inner_y = zip(*inner_polygon)
    ax.plot(inner_x + (inner_x[0],), inner_y + (inner_y[0],), 
            'g-', linewidth=0.5, alpha=1.0, label='Inner Polygon (Generated)')
    
    # Plot points (smaller for outer, larger for inner)
    ax.plot(outer_x, outer_y, 'bo', markersize=1, alpha=0.5)
    ax.plot(inner_x, inner_y, 'go', markersize=4, alpha=1.0)
    
    # Add center point (for reference)
    ax.plot(500, 500, 'k*', markersize=10, label='Reference Point')
    
    # Labels and title
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title(f'✅ SUCCESS: Fog-Based Polygon Generation\n'
                f'Segment Length: {SEGMENT_LENGTH}, Target Separation: {TARGET_SEPARATION}\n'
                f'Execution Time: {elapsed_time:.2f}s, Points: {len(inner_polygon)}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Save to project temp directory
    output_file = Path("temp", "test_generate_single_inner_polygon.png")
    output_file.parent.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    
    # Also save as SVG
    svg_file = Path("temp", "test_generate_single_inner_polygon.svg")
    plt.savefig(svg_file, format='svg', bbox_inches='tight')
    plt.close()
    
    print(f"📊 Success visualization saved to: {output_file}")
    print(f"📊 SVG visualization saved to: {svg_file}")

def create_failure_visualization(outer_polygon, error_message, elapsed_time):
    """
    Date: 2025-08-10
    Description: Create visualization for failed polygon generation
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot outer polygon
    outer_x, outer_y = zip(*outer_polygon)
    ax.plot(outer_x + (outer_x[0],), outer_y + (outer_y[0],), 
            'b-', linewidth=2, label='Outer Polygon (Bounding)')
    
    # Plot points
    ax.plot(outer_x, outer_y, 'bo', markersize=3, alpha=0.7)
    
    # Add center point (for reference)
    ax.plot(500, 500, 'k*', markersize=10, label='Reference Point')
    
    # Add error message as text
    ax.text(0.02, 0.98, f'❌ FAILURE: {error_message}\n'
                         f'Execution Time: {elapsed_time:.2f}s\n'
                         f'Point Limit: {MAX_POINTS_PER_POLYGON}\n'
                         f'Time Limit: {MAX_TIME_SECONDS}s',
             transform=ax.transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
    
    # Labels and title
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title(f'❌ FAILURE: Fog-Based Polygon Generation\n'
                f'Segment Length: {SEGMENT_LENGTH}, Target Separation: {TARGET_SEPARATION}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Save to project temp directory (not tests/temp/)
    output_file = Path("..", "temp", "test_generate_single_inner_polygon.png")
    output_file.parent.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Failure visualization saved to: {output_file}")

if __name__ == "__main__":
    # Run the test
    test_generate_single_inner_polygon()
