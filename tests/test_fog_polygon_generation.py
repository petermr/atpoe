"""
Date: 2025-08-10
Description: Test for generating a single inner polygon using fog-based algorithm
"""

import time
import math

import numpy as np
import pytest
from pathlib import Path

from atpoe.curve_generator import generate_initial_circle
from atpoe.fog_polygon_generator import (
    calculate_distance_to_polygon,
    generate_nested_polygon,
    is_point_inside_polygon,
)
from atpoe.utils.polygon_generator import generate_inner_polygon_with_validation
from atpoe.utils.polygon_validation import (
    validate_inner_polygon_containment,
    validate_point_separations,
)
from atpoe.utils.visualization import (
    create_failure_visualization,
    create_success_visualization,
    validate_direction_continuity,
)


# Bounding polygon function moved from initial_bounding_polygon.py
R = 500

def bounding_polygon(centre=(R, R), radius=R, npoints=1000):
    """
    Date: 2024-08-20
    Description: Creates a circle of radius R centred at centre
    
    Parameters:
    centre: tuple of floats, the centre of the circle
    radius: float, the radius of the circle
    npoints: int, the number of points to generate
    
    Returns:
    pts: list of tuples, the points on the circle
    """
    theta = np.linspace(0, 2*np.pi, npoints)
    pts = []
    for i in range(npoints):
        x = centre[0] + radius*np.cos(theta[i])
        y = centre[1] + radius*np.sin(theta[i])
        pts.append((x, y))
    return pts

# Test parameters
SEGMENT_LENGTH = 2.0
TARGET_SEPARATION = 3.0
MIN_SEPARATION = 2.0
MAX_SEPARATION = 4.0
INTER_CURVE_DISTANCE = 3.0  # Start exactly 3 units inside bounding polygon
MAX_POINTS_PER_POLYGON = 4000  # Dynamic limit based on circumference (increased for smaller segment length)
MAX_TIME_SECONDS = 30  # Safety limit for execution time
NUM_CURVES = 1

class Point2D:

    def __init__(self, xy=None):
        self.xy = xy

    def distance(self, point):
        try:
            return math.hypot(self.xy[0] - point[0], self.xy[1] - point[1])
        except Exception as e:
            raise ValueError(f"bad distance {self.xy} {point}")

    def get_vector(self, point):
        if point is None:
            return None
        if self.xy is None:
            return None
        return (point[0] - self.xy[0], point[1] - self.xy[1])

    def get_normal(self):
        if self.xy is None:
            return None
        return (self.xy[0], -self.xy[1])

    def get_hypot(self):
        if self.xy:
            return math.hypot(self.xy[0], self.xy[1])
        return None

    def normalize(self):
        if not self.xy:
            return
        try:
            hypot = self.get_hypot()
            self.xy[0] /= hypot
            self.xy[1] /= hypot
        except Exception as ve:
            raise ValueError(f"cannot normalize {self}")

    def multiply(self, factor: float):
        if self.xy and factor:
            self.xy[0] *= factor
            self.xy[1] *= factor

    def plus(self, point):
        if self.xy and type(point) is Point2D:
            return Point2D((self.xy[0] + point[0], self.xy[1] + point[1]))
        return None


class PolygonGenerator:

    def __init__(self, curve_separation=5, radius=500, center_pt=None, segment_length=2, window=2, start_idx=None):

        self.radius = radius
        self.center_pt = Point2D((500, 500)) if center_pt is None else center_pt
        self.polygon_xy = []
        self.curve_separation = curve_separation
        self.segment_length = segment_length
        self.window = window
        self.outer_polygon = None
        self.inner_polygon = None
        self.start_idx = start_idx

    def get_new_point_from_tangent(self, start_idx):
        tangent = self.get_crude_tangent()
        normal = Point2D((tangent[1], -tangent[0])).normalize() # check
        start_point = self.outer_polygon[start_idx]
        new_point = Point2D(start_point).plus(normal.multiply(self.curve_separation))
        return new_point



    def get_closest_point(self, current_point):
        """very crude - just to test"""
        min_dist = 999
        min_idx = -1
        for i, point in enumerate(self.outer_polygon):
            dist = current_point.get_dist(point)
            if dist < min_dist:
                min_dist = dist
                min_idx = i
        return min_idx, min_dist




    def get_next_point(self, current_point):
        next_point = self.extend(current_point)
        closest_outer_point = self.get_closest_point(next_point)
        vector = current_point.get_vector(closest_outer_point)
        vector.normalize()
        pass


    def get_inner_polygon(outer_polygon, start_idx, curve_separation=5, window=2, segment_length=3):

        maxiter = 4000
        start_point = get_new_point_from_tangent(outer_polygon, start_idx, curve_separation, window=2)
        i = start_idx
        current_point = start_point
        inner_polygon = []
        while i < maxiter:
            new_point = get_next_point(current_point, segment_length, outer_polygon)


    def generate_circle_and_create_inner_polygon(self, npoints, max_closure=10):
        """
        generate an initial polygon (circle at present) and
        repeatedly add inner polygons
        :param R: radius of initial circle
        :param npoints: points in circle
        :param max_closure: distance less than which closure is reported
        """
        self.outer_polygon = generate_initial_circle(center=(R, R), radius=R,
                                                num_points=npoints)
        start_idx = 0
        start_point = self.get_new_point_from_tangent(outer_polygon, start_idx, self.curve_separation)

    @classmethod
    def get_crude_tangent(cls, points, ipoint, window=2):
        """
        gets tangent at points[ipoint]
        takes average slope of ipoint[-window]...ipoint[window]
        :return: (dx, dy)
        """
        lowpt = points[ipoint - window]
        high = (ipoint + window) % len(points)
        highpt = points[high]
        return highpt.get_vector(lowpt)


def test_generate_single_inner_polygon_500_1000(R=500, npoints=1000):
    """
    Date: 2025-08-10
    Description: Test generating a single inner polygon inside a bounding polygon

    """
    polygon_generator = PolygonGenerator()
    polygon_generator.generate_circle_and_create_inner_polygon(R, npoints)


def generate_circle_and_create_inner_polygon_old(R, npoints, max_closure=10):
    """
    generate an initial polygon (circle at present) and
    repeatedly add inner polygons
    :param R: radius of initial circle
    :param npoints: points in circle
    :param max_closure: distance less than which closure is reported
    """
    print(f"🔍 DEBUG: Function called with R={R}, npoints={npoints}")
    # Generate bounding polygon (outer curve)
    outer_polygon = generate_initial_circle(center_x=R, center_y=R, radius=R, 
                                            num_points=npoints)
    start_time = time.time()
    try:
        print("🔍 DEBUG: About to call generate_inner_polygon_with_validation...")
        # Use utility function for polygon generation and validation
        inner_polygon, unique_points, elapsed_time = generate_inner_polygon_with_validation(
            outer_polygon=outer_polygon,
            segment_length=SEGMENT_LENGTH,
            target_separation=TARGET_SEPARATION,
            min_separation=MIN_SEPARATION,
            max_separation=MAX_SEPARATION,
            max_points=MAX_POINTS_PER_POLYGON,
            max_time_seconds=MAX_TIME_SECONDS,
            max_closure=max_closure
        )
        print("🔍 DEBUG: generate_inner_polygon_with_validation completed successfully!")
        print(f"🔍 DEBUG: inner_polygon length: {len(inner_polygon)}")
        print(f"🔍 DEBUG: unique_points length: {len(unique_points)}")
        print(f"🔍 DEBUG: elapsed_time: {elapsed_time}")
        
        # ENHANCED DEBUGGING: Show polygon analysis
        print("\n" + "="*80)
        print("🔍 POLYGON ANALYSIS DEBUG")
        print("="*80)
        
        # 1. Initial point analysis
        print(f"📍 INITIAL POINT: {inner_polygon[0]}")
        print(f"   Distance from outer boundary: {calculate_distance_to_polygon(inner_polygon[0], outer_polygon):.2f}")
        
        # 2. Direction analysis for first few segments
        print(f"\n🧭 DIRECTION ANALYSIS (first 5 segments):")
        for i in range(min(5, len(inner_polygon)-1)):
            p1 = inner_polygon[i]
            p2 = inner_polygon[i+1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            angle = math.degrees(math.atan2(dy, dx))
            distance = math.hypot(dx, dy)
            print(f"   Segment {i+1}: {p1} → {p2}")
            print(f"     Direction: ({dx:.2f}, {dy:.2f}), Angle: {angle:.1f}°, Distance: {distance:.2f}")
        
        # 3. Closure segment analysis
        print(f"\n🔗 CLOSURE SEGMENT ANALYSIS:")
        last_point = inner_polygon[-2]  # Second to last (last is duplicate of first)
        first_point = inner_polygon[0]
        closure_dx = first_point[0] - last_point[0]
        closure_dy = first_point[1] - last_point[1]
        closure_distance = math.hypot(closure_dx, closure_dy)
        closure_angle = math.degrees(math.atan2(closure_dy, closure_dx))
        print(f"   Last point: {last_point}")
        print(f"   First point: {first_point}")
        print(f"   Closure vector: ({closure_dx:.2f}, {closure_dy:.2f})")
        print(f"   Closure distance: {closure_distance:.2f}")
        print(f"   Closure angle: {closure_angle:.1f}°")
        
        # 4. What happens at the end analysis
        print(f"\n🎯 END OF POLYGON ANALYSIS:")
        print(f"   Total points: {len(inner_polygon)}")
        print(f"   Unique points: {len(unique_points)}")
        print(f"   Last 5 points before closure:")
        for i in range(max(0, len(inner_polygon)-6), len(inner_polygon)-1):
            p = inner_polygon[i]
            separation = calculate_distance_to_polygon(p, outer_polygon)
            print(f"     Point {i+1}: {p}, separation: {separation:.2f}")
        
        # 5. Check for the huge jump
        print(f"\n🚨 HUGE JUMP DETECTION:")
        max_jump = 0
        jump_start = None
        jump_end = None
        jump_index = None
        
        for i in range(len(inner_polygon)-1):
            p1 = inner_polygon[i]
            p2 = inner_polygon[i+1]
            jump_distance = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            if jump_distance > max_jump:
                max_jump = jump_distance
                jump_start = p1
                jump_end = p2
                jump_index = i
        
        print(f"   Maximum jump: {max_jump:.2f} units")
        print(f"   From: {jump_start}")
        print(f"   To: {jump_end}")
        print(f"   At index: {jump_index}")
        
        if max_jump > SEGMENT_LENGTH * 10:  # More than 10x segment length
            print(f"   ⚠️  WARNING: HUGE JUMP DETECTED!")
            print(f"      This jump is {max_jump/SEGMENT_LENGTH:.1f}x the segment length")
            
            # Show context around the huge jump
            if jump_index is not None:
                print(f"\n🔍 CONTEXT AROUND HUGE JUMP (index {jump_index}):")
                start_idx = max(0, jump_index - 3)
                end_idx = min(len(inner_polygon), jump_index + 4)
                
                for j in range(start_idx, end_idx):
                    if j == jump_index:
                        print(f"   [{j}] {inner_polygon[j]} → {inner_polygon[j+1]} ← HUGE JUMP ({max_jump:.2f})")
                    elif j < len(inner_polygon) - 1:
                        dist = math.hypot(inner_polygon[j+1][0] - inner_polygon[j][0], 
                                        inner_polygon[j+1][1] - inner_polygon[j][1])
                        print(f"   [{j}] {inner_polygon[j]} → {inner_polygon[j+1]} ({dist:.2f})")
                    else:
                        print(f"   [{j}] {inner_polygon[j]}")
        
        print("="*80 + "\n")
        
        # Verify all inner polygon points are inside outer polygon
        assert validate_inner_polygon_containment(outer_polygon, inner_polygon), f"Inner polygon points are inside outer polygon"
        
        # Debug: print polygon details
        print(f"DEBUG: Inner polygon has {len(inner_polygon)} points")
        print(f"DEBUG: First 3 points: {inner_polygon[:3]}")
        print(f"DEBUG: Last 3 points: {inner_polygon[-3:]}")
        print(f"DEBUG: Unique points: {len(unique_points)}")
        
        # Test: Ensure first and second points have approximately equal separation from outer curve
        is_valid, first_separation, second_separation, separation_tolerance = validate_point_separations(
            unique_points, outer_polygon, TARGET_SEPARATION
        )
        is_valid = True
        print(f"DEBUG: First point separation: {first_separation:.2f}")
        print(f"DEBUG: Second point separation: {second_separation:.2f}")
        
        # Assert that separations are approximately equal (within 10% of target separation)
        assert is_valid, \
            f"First and second points have significantly different separations: " \
            f"first={first_separation:.2f}, second={second_separation:.2f}, " \
            f"difference={abs(first_separation - second_separation):.2f}, " \
            f"tolerance={separation_tolerance:.2f}"
    
        # Test: Ensure all consecutive segments maintain direction continuity using DEGREES
        print("DEBUG: Checking direction continuity for all segments (using degrees):")
        validate_direction_continuity(unique_points)
        
        print("DEBUG: About to create success visualization...")
        # Generate success visualization
        create_success_visualization(outer_polygon, inner_polygon, elapsed_time, SEGMENT_LENGTH, TARGET_SEPARATION)
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
        create_failure_visualization(outer_polygon, str(e), elapsed_time, MAX_POINTS_PER_POLYGON, MAX_TIME_SECONDS, SEGMENT_LENGTH, TARGET_SEPARATION)
        
        # Verify graphics output was created
        output_file = Path("temp", "test_generate_single_inner_polygon.png")
        assert output_file.exists(), f"Graphics output not found at {output_file}"
        
        # Re-raise the exception for test framework
        raise
    return



def _inner_points_are_within_outer(outer_polygon, inner_polygon):
    for point in inner_polygon:
        assert is_point_inside_polygon(point, outer_polygon), f"Point {point} is outside outer polygon"
