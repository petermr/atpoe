"""
Date: 2025-08-10
Description: Tests for the simple polygon generation algorithm
"""

import math
import matplotlib.pyplot as plt
import numpy as np
import pytest

def create_polygon(radius: float, npoints: int) -> list:
    """
    Date: 2025-08-10
    Description: Create a regular polygon with given radius and number of points
    """
    points = []
    for i in range(npoints):
        angle = 2 * math.pi * i / npoints
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))
    return points

def plot_polygon(polygon: list, title: str = "Polygon"):
    """
    Date: 2025-08-10
    Description: Plot a polygon for visualization
    """
    # Close the polygon by adding first point at end
    closed_polygon = polygon + [polygon[0]]
    
    x_coords = [p[0] for p in closed_polygon]
    y_coords = [p[1] for p in closed_polygon]
    
    plt.figure(figsize=(8, 8))
    plt.plot(x_coords, y_coords, 'b-', linewidth=2)
    plt.plot([p[0] for p in polygon], [p[1] for p in polygon], 'ro', markersize=6)
    plt.grid(True, alpha=0.3)
    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')
    plt.savefig('temp/step1_polygon.png', dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Plot saved to temp/step1_polygon.png")

def create_start_point(polygon: list, curve_separation: float) -> tuple:
    """
    Date: 2025-08-10
    Description: Create start point by moving inward from first boundary point
    """
    if len(polygon) < 3:
        return None
    
    # Use points [0, 1, 2] to create unit normal inwards
    pt_curr = polygon[0]  # First point
    pt_next = polygon[1]  # Second point
    
    # Calculate boundary direction
    boundary_dx = pt_next[0] - pt_curr[0]
    boundary_dy = pt_next[1] - pt_curr[1]
    
    # Perpendicular inward vector (rotate 90 degrees)
    inward_x = -boundary_dy
    inward_y = boundary_dx
    
    # Normalize to unit vector
    length = math.hypot(inward_x, inward_y)
    if length == 0:
        return None
    
    inward_x /= length
    inward_y /= length
    
    # Move inward by curve_separation
    start_x = pt_curr[0] + inward_x * curve_separation
    start_y = pt_curr[1] + inward_y * curve_separation
    
    return (round(start_x, 2), round(start_y, 2))

def plot_start_point(polygon: list, start_point: tuple, curve_separation: float, title: str = "Start Point"):
    """
    Date: 2025-08-10
    Description: Plot polygon with start point
    """
    # Close the polygon by adding first point at end
    closed_polygon = polygon + [polygon[0]]
    
    x_coords = [p[0] for p in closed_polygon]
    y_coords = [p[1] for p in closed_polygon]
    
    plt.figure(figsize=(8, 8))
    plt.plot(x_coords, y_coords, 'b-', linewidth=2, label='Outer Polygon')
    plt.plot([p[0] for p in polygon], [p[1] for p in polygon], 'ro', markersize=6, label='Polygon Points')
    
    # Plot start point
    if start_point:
        plt.plot(start_point[0], start_point[1], 'go', markersize=10, label='Start Point')
        
        # Draw arrow from first polygon point to start point
        plt.arrow(polygon[0][0], polygon[0][1], 
                 start_point[0] - polygon[0][0], start_point[1] - polygon[0][1],
                 head_width=0.5, head_length=0.5, fc='green', ec='green', alpha=0.7)
        
        # Draw circle showing curve_separation
        circle = plt.Circle(polygon[0], curve_separation, fill=False, color='green', 
                          linestyle='--', alpha=0.5, label=f'Curve Separation: {curve_separation}')
        plt.gca().add_patch(circle)
    
    plt.grid(True, alpha=0.3)
    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')
    plt.legend()
    plt.savefig('temp/step2_start_point.png', dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Plot saved to temp/step2_start_point.png")

if __name__ == "__main__":
    # Test create_polygon
    print("Testing create_polygon function...")
    
    # Create an octagon with radius 10
    radius = 10
    npoints = 8
    polygon = create_polygon(radius, npoints)
    
    print(f"Created polygon with {len(polygon)} points:")
    for i, point in enumerate(polygon):
        print(f"  Point {i}: {point}")
    
    # Plot the result
    plot_polygon(polygon, f"Regular {npoints}-gon (radius={radius})")
    
    print("\n" + "="*50)
    print("Testing create_start_point function...")
    
    # Test create_start_point
    curve_separation = 3.0
    start_point = create_start_point(polygon, curve_separation)
    
    if start_point:
        print(f"Created start point: {start_point}")
        print(f"Distance from first polygon point: {math.hypot(start_point[0] - polygon[0][0], start_point[1] - polygon[0][1]):.2f}")
        
        # Plot the result
        plot_start_point(polygon, start_point, curve_separation, f"Start Point (separation={curve_separation})")
    else:
        print("Failed to create start point")
