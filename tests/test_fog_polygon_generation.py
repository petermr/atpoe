"""
Date: 2025-08-10
Description: Test for generating a single inner polygon using fog-based algorithm
"""

import pytest
import numpy as np
from pathlib import Path
import time

from atpoe.curve_generator import generate_initial_circle

# Test parameters
SEGMENT_LENGTH = 2.0
TARGET_SEPARATION = 3.0
MIN_SEPARATION = 2.0
MAX_SEPARATION = 4.0
INTER_CURVE_DISTANCE = 3.0  # Start exactly 3 units inside bounding polygon
MAX_POINTS_PER_POLYGON = 4000  # Dynamic limit based on circumference (increased for smaller segment length)
MAX_TIME_SECONDS = 30  # Safety limit for execution time
NUM_CURVES = 1



def test_generate_single_inner_polygon():
    """
    Date: 2025-08-10
    Description: Test generating a single inner polygon inside a bounding polygon
    """
    # Generate bounding polygon (outer curve)
    R = 500
    npoints = 1000 
    outer_polygon = generate_initial_circle(center_x=R, center_y=R, radius=R, 
                                            num_points=npoints)
    
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
        
        # Test: Ensure first and second points have approximately equal separation from outer curve
        if len(unique_points) >= 2:
            from atpoe.fog_polygon_generator import calculate_distance_to_polygon
            first_point = unique_points[0]
            second_point = unique_points[1]
            
            first_separation = calculate_distance_to_polygon(first_point, outer_polygon)
            second_separation = calculate_distance_to_polygon(second_point, outer_polygon)
            
            print(f"DEBUG: First point separation: {first_separation:.2f}")
            print(f"DEBUG: Second point separation: {second_separation:.2f}")
            
            # Assert that separations are approximately equal (within 10% of target separation)
            separation_tolerance = TARGET_SEPARATION * 0.1
            assert abs(first_separation - second_separation) <= separation_tolerance, \
                f"First and second points have significantly different separations: " \
                f"first={first_separation:.2f}, second={second_separation:.2f}, " \
                f"difference={abs(first_separation - second_separation):.2f}, " \
                f"tolerance={separation_tolerance:.2f}"
        
        # Test: Ensure all consecutive segments maintain direction continuity using DEGREES
        if len(unique_points) >= 3:
            print("DEBUG: Checking direction continuity for all segments (using degrees):")
            
            for i in range(1, len(unique_points) - 1):
                prev_point = unique_points[i-1]
                curr_point = unique_points[i]
                next_point = unique_points[i+1]
                
                # Calculate direction vectors
                import math
                vec_prev_x = curr_point[0] - prev_point[0]
                vec_prev_y = curr_point[1] - prev_point[1]
                vec_curr_x = next_point[0] - curr_point[0]
                vec_curr_y = next_point[1] - curr_point[1]
                
                # Calculate angles
                prev_angle = math.degrees(math.atan2(vec_prev_y, vec_prev_x))
                curr_angle = math.degrees(math.atan2(vec_curr_y, vec_curr_x))
                
                # Calculate turn angle (handle angle wrapping)
                turn_angle = abs(curr_angle - prev_angle)
                if turn_angle > 180:
                    turn_angle = 360 - turn_angle
                
                print(f"  Segment {i}: {prev_point} -> {curr_point} -> {next_point}, turn_angle = {turn_angle:.1f}°")
                
                # Assert that turn angle is reasonable (should be < 30 degrees for very smooth curves)
                # Allow some flexibility for pathological cases
                assert turn_angle < 30.0, \
                    f"Segment {i} has too sharp a turn: " \
                    f"turn_angle = {turn_angle:.1f}° (should be < 30°)"
        
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
    Description: Create visualization for successful polygon generation using direct SVG
    """
    # Create SVG with proper viewBox and styling
    svg_file = Path("temp", "test_generate_single_inner_polygon.svg")
    
    # Calculate bounding box for proper viewBox
    all_points = outer_polygon + inner_polygon
    min_x = min(p[0] for p in all_points) - 50
    max_x = max(p[0] for p in all_points) + 50
    min_y = min(p[1] for p in all_points) - 50
    max_y = max(p[1] for p in all_points) + 50
    width = max_x - min_x
    height = max_y - min_y
    
    with open(svg_file, 'w') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {width} {height}">\n')
        
        # Add grid (optional, for reference)
        grid_size = 100
        for x in range(int(min_x), int(max_x) + grid_size, grid_size):
            f.write(f'    <line x1="{x}" y1="{min_y}" x2="{x}" y2="{max_y}" stroke="#f0f0f0" stroke-width="0.5"/>\n')
        for y in range(int(min_y), int(max_y) + grid_size, grid_size):
            f.write(f'    <line x1="{min_x}" y1="{y}" x2="{max_x}" y2="{y}" stroke="#f0f0f0" stroke-width="0.5"/>\n')
        
        # Outer polygon (blue, thin line)
        outer_coords = ' '.join([f"{x},{y}" for x, y in outer_polygon])
        f.write(f'    <polygon points="{outer_coords}" fill="none" stroke="blue" stroke-width="2" opacity="0.7"/>\n')
        
        # Inner polygon (red, very thin line)
        inner_coords = ' '.join([f"{x},{y}" for x, y in inner_polygon[:-1]])  # Exclude duplicate start point
        f.write(f'    <polygon points="{inner_coords}" fill="none" stroke="red" stroke-width="0.5"/>\n')
        
        # Add title and labels
        f.write(f'    <text x="{min_x + 20}" y="{min_y + 30}" font-family="Arial" font-size="16" fill="black">')
        f.write(f'✅ SUCCESS: Fog-Based Polygon Generation</text>\n')
        f.write(f'    <text x="{min_x + 20}" y="{min_y + 50}" font-family="Arial" font-size="12" fill="black">')
        f.write(f'Segment Length: {SEGMENT_LENGTH}, Target Separation: {TARGET_SEPARATION}</text>\n')
        f.write(f'    <text x="{min_x + 20}" y="{min_y + 70}" font-family="Arial" font-size="12" fill="black">')
        f.write(f'Execution Time: {elapsed_time:.2f}s, Points: {len(inner_polygon)}</text>\n')
        
        f.write('</svg>\n')
    
    # Convert SVG to PNG using a simple approach (if available)
    png_file = Path("temp", "test_generate_single_inner_polygon.png")
    try:
        # Try to use cairosvg if available for high-quality conversion
        import cairosvg
        cairosvg.svg2png(url=str(svg_file), write_to=str(png_file), output_width=1200, output_height=1000)
        print(f"📊 PNG visualization saved to: {png_file} (using cairosvg)")
    except ImportError:
        # Fallback: just save SVG and inform user
        print(f"📊 SVG visualization saved to: {svg_file}")
        print("💡 To convert to PNG, install cairosvg: pip install cairosvg")
        print("   Or open the SVG in a browser and save as PNG")
    
    print(f"📊 SVG visualization saved to: {svg_file}")

def create_failure_visualization(outer_polygon, error_message, elapsed_time):
    """
    Date: 2025-08-10
    Description: Create visualization for failed polygon generation using direct SVG
    """
    # Create SVG with proper viewBox and styling
    svg_file = Path("temp", "test_generate_single_inner_polygon.svg")
    
    # Calculate bounding box for proper viewBox
    min_x = min(p[0] for p in outer_polygon) - 50
    max_x = max(p[0] for p in outer_polygon) + 50
    min_y = min(p[1] for p in outer_polygon) - 50
    max_y = max(p[1] for p in outer_polygon) + 50
    width = max_x - min_x
    height = max_y - min_y
    
    with open(svg_file, 'w') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {width} {height}">\n')
        
        # Add grid (optional, for reference)
        grid_size = 100
        for x in range(int(min_x), int(max_x) + grid_size, grid_size):
            f.write(f'    <line x1="{x}" y1="{min_y}" x2="{x}" y2="{max_y}" stroke="#f0f0f0" stroke-width="0.5"/>\n')
        for y in range(int(min_y), int(max_y) + grid_size, grid_size):
            f.write(f'    <line x1="{min_x}" y1="{y}" x2="{max_x}" y2="{y}" stroke="#f0f0f0" stroke-width="0.5"/>\n')
        
        # Outer polygon (blue, thin line)
        outer_coords = ' '.join([f"{x},{y}" for x, y in outer_polygon])
        f.write(f'    <polygon points="{outer_coords}" fill="none" stroke="blue" stroke-width="2" opacity="0.7"/>\n')
        
        # Add error message box
        f.write(f'    <rect x="{min_x + 20}" y="{min_y + 20}" width="400" height="120" fill="red" opacity="0.1" stroke="red" stroke-width="1"/>\n')
        f.write(f'    <text x="{min_x + 30}" y="{min_y + 45}" font-family="Arial" font-size="16" fill="red">❌ FAILURE: {error_message}</text>\n')
        f.write(f'    <text x="{min_x + 30}" y="{min_y + 65}" font-family="Arial" font-size="12" fill="red">Execution Time: {elapsed_time:.2f}s</text>\n')
        f.write(f'    <text x="{min_x + 30}" y="{min_y + 85}" font-family="Arial" font-size="12" fill="red">Point Limit: {MAX_POINTS_PER_POLYGON}</text>\n')
        f.write(f'    <text x="{min_x + 30}" y="{min_y + 105}" font-family="Arial" font-size="12" fill="red">Time Limit: {MAX_TIME_SECONDS}s</text>\n')
        
        # Add title
        f.write(f'    <text x="{min_x + 20}" y="{min_y + 150}" font-family="Arial" font-size="14" fill="black">❌ FAILURE: Fog-Based Polygon Generation</text>\n')
        f.write(f'    <text x="{min_x + 20}" y="{min_y + 170}" font-family="Arial" font-size="12" fill="black">Segment Length: {SEGMENT_LENGTH}, Target Separation: {TARGET_SEPARATION}</text>\n')
        
        f.write('</svg>\n')
    
    # Convert SVG to PNG using a simple approach (if available)
    png_file = Path("temp", "test_generate_single_inner_polygon.png")
    try:
        # Try to use cairosvg if available for high-quality conversion
        import cairosvg
        cairosvg.svg2png(url=str(svg_file), write_to=str(png_file), output_width=1200, output_height=1000)
        print(f"📊 PNG visualization saved to: {png_file} (using cairosvg)")
    except ImportError:
        # Fallback: just save SVG and inform user
        print(f"📊 SVG visualization saved to: {svg_file}")
        print("💡 To convert to PNG, install cairosvg: pip install cairosvg")
        print("   Or open the SVG in a browser and save as PNG")
    
    print(f"📊 SVG visualization saved to: {svg_file}")

if __name__ == "__main__":
    # Run the test
    test_generate_single_inner_polygon()
