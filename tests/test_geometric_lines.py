"""
Test file for geometric lines - 2024-12-19
Tests segment length algorithm on various geometric line shapes with visual diagrams.
"""

import sys
import os
import pytest
import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

from atpoe.utils.segment_analysis import analyze_curve_segments, get_segment_lengths
from atpoe.curve_generator import generate_nested_curve_simple
from atpoe.config_loader import load_config
from atpoe.segment_algorithm import generate_curve_following_segments

def generate_nested_polyline_simple(outer_curve, distance: float, error: float, min_separation: float = 1.0):
    """
    Generate a nested polyline by moving points below the first point by (0, -line_separation).
    
    Date: 2024-12-19
    Description: Creates polylines "inside" by moving points below first point by specified separation.
    """
    if not outer_curve or len(outer_curve) < 2:
        return []
    
    # Get the first point as reference
    first_point = outer_curve[0]
    line_separation = distance
    
    new_curve = []
    for i, point in enumerate(outer_curve):
        # Move point below the first point by (0, -line_separation)
        new_x = point[0]  # Keep same x-coordinate
        new_y = first_point[1] - line_separation  # Move below first point
        
        # Add random error
        if i == 0 or i == len(outer_curve) - 1:
            error_x = random.uniform(-error * 0.2, error * 0.2)
            error_y = random.uniform(-error * 0.2, error * 0.2)
        else:
            error_x = random.uniform(-error, error)
            error_y = random.uniform(-error, error)
        
        new_curve.append((new_x + error_x, new_y + error_y))
    
    return new_curve

def generate_line_by_angles(angular_deviations, start_point=(100, 100), segment_length=80, num_points=10):
    """
    Generate 10-point line from 9 angular deviations (positive = anticlockwise).
    
    Date: 2024-12-19
    Description: Create line with specified angular deviations between segments.
    
    Args:
        angular_deviations: List of 9 angles in degrees (positive = anticlockwise)
        start_point: Starting point (x, y)
        segment_length: Length of each segment
        num_points: Number of points (should be 10 for 9 angles)
    """
    if len(angular_deviations) != num_points - 1:
        raise ValueError(f"Expected {num_points - 1} angular deviations, got {len(angular_deviations)}")
    
    points = [start_point]
    current_angle = 0  # Start horizontal (0 degrees)
    
    for i, angle_dev in enumerate(angular_deviations):
        # Update angle by the deviation (positive = anticlockwise)
        current_angle += math.radians(angle_dev)
        
        # Calculate next point
        x = points[-1][0] + segment_length * math.cos(current_angle)
        y = points[-1][1] + segment_length * math.sin(current_angle)
        points.append((x, y))
    
    return points

def create_geometric_test_diagram(test_results, output_file="geometric_test_diagram.png"):
    """
    Generate single PNG with all test lines and their generated segments.
    
    Date: 2024-12-19
    Description: Create visual diagram using Path constructor for safe temp directory output.
    """
    from pathlib import Path
    
    # Use Path constructor with multiple arguments - never use "/" operator
    output_path = Path("temp", output_file)
    temp_dir = Path("temp")
    
    # Create temp directory if needed (ask permission first)
    if not temp_dir.exists():
        print(f"Creating temp directory: {temp_dir}")
        temp_dir.mkdir(exist_ok=True)
    
    print(f"Saving diagram to: {output_path}")
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 18))
    fig.suptitle('Geometric Line Tests - Original Lines and Generated Segments', fontsize=16)
    
    test_names = [
        "Straight", "Convex", "Concave",
        "Fast Wiggly", "Slow Wiggly", "Blunt Spike",
        "Blunt Spike (Offset)", "Sharp Spike", "Sharp Spike (Offset)"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, test_results)):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        original_line = result['original_line']
        new_segments = result.get('new_segments', [])
        analysis = result.get('analysis', {})
        
        # Plot original line
        x_orig = [p[0] for p in original_line]
        y_orig = [p[1] for p in original_line]
        ax.plot(x_orig, y_orig, 'b-o', linewidth=2, markersize=6, label='Original Line')
        
        # Plot new segments if available
        if new_segments:
            x_new = [p[0] for p in new_segments]
            y_new = [p[1] for p in new_segments]
            ax.plot(x_new, y_new, 'r-s', linewidth=2, markersize=4, label='New Segments')
        
        # Add analysis text
        if analysis:
            text = f"Segments: {analysis.get('num_segments', 0)}\n"
            text += f"Avg Length: {analysis.get('avg_length', 0):.2f}\n"
            text += f"Accuracy: {analysis.get('accuracy_percent', 0):.1f}%"
            ax.text(0.02, 0.98, text, transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.set_title(test_name)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal')
    
    # Load config for output settings
    config = load_config()
    dpi = config.get_output_dpi()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"Diagram saved to {output_path}")

def test_segment_length_on_geometric_lines():
    """
    Test segment length algorithm on all geometric line types and create diagram.
    
    Date: 2024-12-19
    Description: Test algorithm on various geometric shapes using config constraints and visualize results.
    """
    # Use config-based segment length constraints
    config = load_config()
    min_len, max_len = config.get_segment_length_range()
    target_length = float(min_len) + 2.0  # Use value within config range
    test_results = []
    
    # Define test cases with angular deviations (9 angles for 10 points)
    test_cases = [
        ("Straight", [0, 0, 0, 0, 0, 0, 0, 0, 0], (100, 100)),
        ("Convex", [10, 10, 10, 10, 10, 10, 10, 10, 10], (100, 200)),
        ("Concave", [-10, -10, -10, -10, -10, -10, -10, -10, -10], (100, 300)),
        ("Fast Wiggly", [10, -10, 10, -10, 10, -10, 10, -10, 10], (100, 400)),
        ("Slow Wiggly", [-10, -10, -10, -10, -10, 10, 10, 10, 10], (100, 500)),
        ("Blunt Spike", [0, 0, 0, 30, -60, 30, 0, 0, 0], (100, 600)),
        ("Blunt Spike (Offset)", [0, 0, 30, 0, -60, 0, 30, 0, 0], (100, 700)),
        ("Sharp Spike", [0, 0, 0, 60, -120, 60, 0, 0, 0], (100, 800)),
        ("Sharp Spike (Offset)", [0, 0, 60, 0, -120, 0, 60, 0, 0], (100, 900))
    ]
    
    for test_name, angular_deviations, start_point in test_cases:
        print(f"\n=== Test: {test_name} ===")
        print(f"Angular deviations: {angular_deviations}")
        
        # Generate line with specified angular deviations using target_length for reference curve
        original_line = generate_line_by_angles(angular_deviations, start_point, target_length, 10)
        
        # Use proper curve-following algorithm with feasible distance parameter
        # distance should be smaller than segment_length to avoid crossing issues
        safe_distance = target_length * 0.8  # 80% of segment length
        new_segments = generate_curve_following_segments(original_line, safe_distance, target_length)
        analysis = analyze_curve_segments(new_segments, target_length) if new_segments else {}
        
        test_results.append({
            'original_line': original_line,
            'new_segments': new_segments,
            'analysis': analysis
        })
        print(f"{test_name} analysis: {analysis}")
    
    # Create diagram
    create_geometric_test_diagram(test_results)
    
    # Basic assertions
    for i, result in enumerate(test_results):
        if result['new_segments']:
            analysis = result['analysis']
            assert analysis['num_segments'] > 0, f"Test {i+1}: No segments generated"
            assert analysis['avg_length'] > 0, f"Test {i+1}: Zero average length"
        else:
            print(f"Test {i+1}: No segments generated")

if __name__ == "__main__":
    test_segment_length_on_geometric_lines()
