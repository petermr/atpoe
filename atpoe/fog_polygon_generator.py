"""
Date: 2025-08-10
Description: Fog-based polygon generation system for creating nested polygons
"""

import math
import time
from typing import List, Tuple, Optional
from pathlib import Path

try:
    from shapely.geometry import Point, Polygon, LineString
    from shapely.ops import unary_union
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("Warning: Shapely not available, using fallback geometry")


def is_point_inside_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Date: 2025-08-10
    Description: Check if a point is inside a polygon using ray casting algorithm
    """
    if not SHAPELY_AVAILABLE:
        # Fallback ray casting implementation
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    else:
        # Use Shapely for better performance
        shapely_polygon = Polygon(polygon)
        shapely_point = Point(point)
        return shapely_polygon.contains(shapely_point)


def calculate_distance_to_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> float:
    """
    Date: 2025-08-10
    Description: Calculate minimum distance from point to polygon boundary
    """
    if not SHAPELY_AVAILABLE:
        # Fallback distance calculation
        min_distance = float('inf')
        n = len(polygon)
        
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]
            
            # Distance to line segment
            dist = distance_to_line_segment(point, p1, p2)
            min_distance = min(min_distance, dist)
        
        return min_distance
    else:
        # Use Shapely for better performance
        shapely_polygon = Polygon(polygon)
        shapely_point = Point(point)
        return shapely_point.distance(shapely_polygon)


def distance_to_line_segment(point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> float:
    """
    Date: 2025-08-10
    Description: Calculate distance from point to line segment
    """
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Vector from line_start to line_end
    dx = x2 - x1
    dy = y2 - y1
    
    # Vector from line_start to point
    px1 = px - x1
    py1 = py - y1
    
    # Projection parameter
    t = max(0, min(1, (px1 * dx + py1 * dy) / (dx * dx + dy * dy)))
    
    # Closest point on line segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    # Distance to closest point
    return math.hypot(px - closest_x, py - closest_y)


def would_segment_cross_polygon(start_point: Tuple[float, float], end_point: Tuple[float, float], 
                               polygon: List[Tuple[float, float]]) -> bool:
    """
    Date: 2025-08-10
    Description: Check if line segment would cross polygon boundary
    """
    if not SHAPELY_AVAILABLE:
        # Fallback intersection check
        n = len(polygon)
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]
            
            if segments_intersect(start_point, end_point, p1, p2):
                return True
        
        return False
    else:
        # Use Shapely for better performance
        shapely_polygon = Polygon(polygon)
        shapely_line = LineString([start_point, end_point])
        return shapely_line.intersects(shapely_polygon)


def segments_intersect(p1: Tuple[float, float], p2: Tuple[float, float], 
                      p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """
    Date: 2025-08-10
    Description: Check if two line segments intersect
    """
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    # Check if line segments intersect
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def find_next_point(current_point: Tuple[float, float], previous_polygon: List[Tuple[float, float]], 
                   segment_length: float, target_separation: float, min_separation: float, 
                   max_separation: float, previous_direction: Optional[Tuple[float, float]] = None, 
                   max_turn_angle: float = 15.0) -> Optional[Tuple[float, float]]:
    """
    Date: 2025-08-10
    Description: Simple algorithm: keep straight on, adjust angle slightly if needed
    """
    # First try: keep straight on (angle change = 0)
    if previous_direction:
        # Try to continue in the same direction
        candidate_x = round(current_point[0] + previous_direction[0] * segment_length, 2)
        candidate_y = round(current_point[1] + previous_direction[1] * segment_length, 2)
        candidate_point = (candidate_x, candidate_y)
        
        # Check constraints
        if (is_point_inside_polygon(candidate_point, previous_polygon) and
            not would_segment_cross_polygon(current_point, candidate_point, previous_polygon)):
            
            separation = calculate_distance_to_polygon(candidate_point, previous_polygon)
            if min_separation <= separation <= max_separation:
                print(f"DEBUG: Found straight point: {candidate_point}, separation={separation:.2f}")
                return candidate_point
    
    # If straight on fails, try small angle adjustments
    if previous_direction:
        # Calculate current direction angle
        current_angle = math.degrees(math.atan2(previous_direction[1], previous_direction[0]))
        
        # Try small angle adjustments: ±5°, ±10°, ±15°
        for angle_adjustment in [0, 5, -5, 10, -10, 15, -15]:
            if abs(angle_adjustment) > max_turn_angle:
                continue
                
            new_angle = math.radians(current_angle + angle_adjustment)
            direction_x = math.cos(new_angle)
            direction_y = math.sin(new_angle)
            
            candidate_x = round(current_point[0] + direction_x * segment_length, 2)
            candidate_y = round(current_point[1] + direction_y * segment_length, 2)
            candidate_point = (candidate_x, candidate_y)
            
            # Check constraints
            if (is_point_inside_polygon(candidate_point, previous_polygon) and
                not would_segment_cross_polygon(current_point, candidate_point, previous_polygon)):
                
                separation = calculate_distance_to_polygon(candidate_point, previous_polygon)
                if min_separation <= separation <= max_separation:
                    print(f"DEBUG: Found adjusted point: {candidate_point}, angle={angle_adjustment}°, separation={separation:.2f}")
                    return candidate_point
    
    # If no point found with small adjustments, try larger angles
    for angle_offset in range(0, 360, 30):  # Try every 30 degrees
        angle_rad = math.radians(angle_offset)
        direction_x = math.cos(angle_rad)
        direction_y = math.sin(angle_rad)
        
        candidate_x = round(current_point[0] + direction_x * segment_length, 2)
        candidate_y = round(current_point[1] + direction_y * segment_length, 2)
        candidate_point = (candidate_x, candidate_y)
        
        # Check constraints
        if (is_point_inside_polygon(candidate_point, previous_polygon) and
            not would_segment_cross_polygon(current_point, candidate_point, previous_polygon)):
            
            separation = calculate_distance_to_polygon(candidate_point, previous_polygon)
            if min_separation <= separation <= max_separation:
                print(f"DEBUG: Found fallback point: {candidate_point}, angle={angle_offset}°, separation={separation:.2f}")
                return candidate_point
    
    return None


def find_next_point_with_preferred_direction(current_point: Tuple[float, float], previous_polygon: List[Tuple[float, float]], 
                                           segment_length: float, target_separation: float, min_separation: float, 
                                           max_separation: float, previous_direction: Tuple[float, float], 
                                           preferred_direction: Tuple[float, float]) -> Optional[Tuple[float, float]]:
    """
    Date: 2025-08-10
    Description: Find next point with a preferred direction to force gradual turns
    """
    best_point = None
    best_score = float('-inf')
    
    # Try different directions around the current point
    for angle_offset in range(0, 360, 15):  # Try every 15 degrees
        angle_rad = math.radians(angle_offset)
        
        # Calculate direction vector
        direction_x = math.cos(angle_rad)
        direction_y = math.sin(angle_rad)
        
        # Try different distances around the target segment length
        for distance_factor in [0.9, 1.0, 1.1]:  # Smaller variation for more consistent segments
            candidate_x = round(current_point[0] + segment_length * distance_factor * direction_x, 2)
            candidate_y = round(current_point[1] + segment_length * distance_factor * direction_y, 2)
            candidate_point = (candidate_x, candidate_y)
            
            # Check if candidate is valid
            if not is_point_inside_polygon(candidate_point, previous_polygon):
                continue
            
            # Check minimum segment length - ensure points are not too close
            segment_distance = math.hypot(candidate_point[0] - current_point[0], 
                                        candidate_point[1] - current_point[1])
            if segment_distance < segment_length * 0.8:  # Must be at least 80% of target length
                continue
            
            # Calculate separation from previous polygon
            separation = calculate_distance_to_polygon(candidate_point, previous_polygon)
            
            # Check if segment would cross polygon
            if would_segment_cross_polygon(current_point, candidate_point, previous_polygon):
                continue
            
            # Score based on separation - prefer points closer to target but allow flexibility
            if separation < min_separation * 0.5:  # Too close to boundary
                continue
            if separation > max_separation * 2.0:  # Too far from boundary
                continue
                
            # Base score: prefer target separation but allow reasonable alternatives
            separation_penalty = abs(separation - target_separation)
            score = -separation_penalty
            
            # Add direction continuity bonus/penalty
            if previous_direction:
                # Calculate current direction vector
                current_direction_x = candidate_point[0] - current_point[0]
                current_direction_y = candidate_point[1] - current_point[1]
                
                # Normalize both vectors
                prev_len = math.hypot(previous_direction[0], previous_direction[1])
                curr_len = math.hypot(current_direction_x, current_direction_y)
                
                if prev_len > 0 and curr_len > 0:
                    # Calculate dot product of normalized vectors
                    dot_product = (previous_direction[0] * current_direction_x + 
                                 previous_direction[1] * current_direction_y) / (prev_len * curr_len)
                    
                    # Direction continuity bonus: prefer similar directions
                    direction_bonus = dot_product * 1.0
                    score += direction_bonus
            
            # Add preferred direction bonus to force gradual turns
            if preferred_direction:
                # Calculate current direction vector
                current_direction_x = candidate_point[0] - current_point[0]
                current_direction_y = candidate_point[1] - current_point[1]
                
                # Normalize both vectors
                pref_len = math.hypot(preferred_direction[0], preferred_direction[1])
                curr_len = math.hypot(current_direction_x, current_direction_y)
                
                if pref_len > 0 and curr_len > 0:
                    # Calculate dot product with preferred direction
                    pref_dot_product = (preferred_direction[0] * current_direction_x + 
                                      preferred_direction[1] * current_direction_y) / (pref_len * curr_len)
                    
                    # Bonus for following preferred direction (encourages gradual turns)
                    preferred_bonus = pref_dot_product * 0.5  # Smaller weight than continuity
                    score += preferred_bonus
            
            if score > best_score:
                best_score = score
                best_point = candidate_point
    
    return best_point


def find_next_point_along_boundary(current_point: Tuple[float, float], previous_polygon: List[Tuple[float, float]], 
                                  segment_length: float, target_separation: float) -> Optional[Tuple[float, float]]:
    """
    Date: 2025-08-10
    Description: Find next point by following the boundary at target_separation distance
    """
    # Find the closest point on the boundary
    min_distance = float('inf')
    closest_boundary_idx = 0
    
    for i, boundary_point in enumerate(previous_polygon):
        distance = math.hypot(current_point[0] - boundary_point[0], 
                             current_point[1] - boundary_point[1])
        if distance < min_distance:
            min_distance = distance
            closest_boundary_idx = i
    
    # Look ahead along the boundary to find next point
    n = len(previous_polygon)
    for offset in range(1, min(20, n)):  # Look ahead up to 20 points
        next_boundary_idx = (closest_boundary_idx + offset) % n
        next_boundary_point = previous_polygon[next_boundary_idx]
        
        # Calculate direction from current to next boundary point
        dx = next_boundary_point[0] - previous_polygon[closest_boundary_idx][0]
        dy = next_boundary_point[1] - previous_polygon[closest_boundary_idx][1]
        
        # Normalize
        length = math.hypot(dx, dy)
        if length == 0:
            continue
            
        dx /= length
        dy /= length
        
        # Calculate perpendicular inward direction
        inward_x = -dy
        inward_y = dx
        
        # Calculate candidate point at target_separation from boundary
        candidate_x = round(next_boundary_point[0] + inward_x * target_separation, 2)
        candidate_y = round(next_boundary_point[1] + inward_y * target_separation, 2)
        
        # Check if candidate is valid
        if is_point_inside_polygon((candidate_x, candidate_y), previous_polygon):
            # Check if segment length is reasonable
            segment_distance = math.hypot(candidate_x - current_point[0], 
                                        candidate_y - current_point[1])
            if segment_distance <= segment_length * 1.5:  # Allow some flexibility
                return (candidate_x, candidate_y)
    
    return None


def should_close_polygon(current_points: List[Tuple[float, float]], start_point: Tuple[float, float], 
                        segment_length: float) -> bool:
    """
    Date: 2025-08-10
    Description: Check if polygon should be closed
    """
    if len(current_points) < 20:  # Require at least 20 points before considering closure
        return False
    
    # Check if we can close to start point
    last_point = current_points[-1]
    distance_to_start = math.hypot(last_point[0] - start_point[0], last_point[1] - start_point[1])
    
    # Only close if we're very close to the start point (within 0.2 * segment_length)
    # This ensures the polygon actually reaches back to the start point
    return distance_to_start <= segment_length * 0.2


def generate_nested_polygon(previous_polygon: List[Tuple[float, float]], segment_length: float, 
                           target_separation: float, min_separation: float, max_separation: float, 
                           max_points: int = 100) -> List[Tuple[float, float]]:
    """
    Date: 2025-08-10
    Description: Generate a single nested polygon using fog-based algorithm
    """
    if not previous_polygon or len(previous_polygon) < 3:
        return []
    
    # Start with a point inside the previous polygon at target_separation distance
    # Find a good starting point by sampling the boundary
    n = len(previous_polygon)
    start_point = None
    
    # Try to find a starting point by sampling boundary points
    for i in range(0, n, max(1, n // 20)):  # Sample every ~20th point
        boundary_point = previous_polygon[i]
        next_idx = (i + 1) % n
        next_boundary = previous_polygon[next_idx]
        
        # Calculate inward direction (perpendicular to boundary)
        boundary_dx = next_boundary[0] - boundary_point[0]
        boundary_dy = next_boundary[1] - boundary_point[1]
        
        # Perpendicular inward vector (rotate 90 degrees)
        inward_x = -boundary_dy
        inward_y = boundary_dx
        
        # Normalize
        length = math.hypot(inward_x, inward_y)
        if length == 0:
            continue
            
        inward_x /= length
        inward_y /= length
        
        # Move inward by target_separation
        candidate_start = (round(boundary_point[0] + inward_x * target_separation, 2), 
                          round(boundary_point[1] + inward_y * target_separation, 2))
        
        if is_point_inside_polygon(candidate_start, previous_polygon):
            start_point = candidate_start
            break
    
    if not start_point:
        return []
    
    # Generate points with proper segment lengths
    inner_points = [start_point]
    current_point = start_point
    previous_direction = None  # Track the direction from previous to current point
    
    # Calculate dynamic iteration limit based on polygon circumference
    circumference = sum(math.hypot(previous_polygon[i][0] - previous_polygon[(i+1) % len(previous_polygon)][0],
                                  previous_polygon[i][1] - previous_polygon[(i+1) % len(previous_polygon)][1])
                        for i in range(len(previous_polygon)))
    dynamic_max_points = int((circumference / segment_length) * 2)  # Limit to 2x circumference
    actual_max_points = min(max_points, dynamic_max_points)
    
    print(f"DEBUG: Polygon circumference: {circumference:.1f}, segment_length: {segment_length}")
    print(f"DEBUG: Dynamic max points: {dynamic_max_points}, using: {actual_max_points}")
    
    # Adaptive angle system: start with very small turns, increase smoothly when stuck
    current_max_turn_angle = 15.0  # Start with 15° max turn for very smooth curves
    stuck_counter = 0
    progress_tracker = []
    
    for i in range(actual_max_points):
        print(f"DEBUG: Iteration {i+1}, current_point: {current_point}, max_turn: {current_max_turn_angle:.1f}°")
        
        # Check for infinite loop: if we're stuck in a small area
        if len(progress_tracker) >= 30:  # Check progress over 30 iterations for smoother detection
            recent_points = progress_tracker[-30:]
            min_x, max_x = min(p[0] for p in recent_points), max(p[0] for p in recent_points)
            min_y, max_y = min(p[1] for p in recent_points), max(p[1] for p in recent_points)
            
            area_size = (max_x - min_x) * (max_y - min_y)
            if area_size < 800:  # If stuck in area smaller than 800 square units
                stuck_counter += 1
                print(f"DEBUG: Detected stuck (iteration {stuck_counter}) - area size: {area_size:.1f}")
                
                # Smooth adaptive angle increase: 15° → 20° → 25° → 30° → 35° → 40°
                if stuck_counter == 1:
                    current_max_turn_angle = 20.0
                    print(f"DEBUG: Smoothly increasing max turn angle to {current_max_turn_angle}°")
                elif stuck_counter == 2:
                    current_max_turn_angle = 25.0
                    print(f"DEBUG: Smoothly increasing max turn angle to {current_max_turn_angle}°")
                elif stuck_counter == 3:
                    current_max_turn_angle = 30.0
                    print(f"DEBUG: Smoothly increasing max turn angle to {current_max_turn_angle}°")
                elif stuck_counter == 4:
                    current_max_turn_angle = 35.0
                    print(f"DEBUG: Smoothly increasing max turn angle to {current_max_turn_angle}°")
                elif stuck_counter == 5:
                    current_max_turn_angle = 40.0
                    print(f"DEBUG: Smoothly increasing max turn angle to {current_max_turn_angle}°")
                elif stuck_counter >= 6:
                    print(f"DEBUG: Maximum stuck iterations reached, allowing moderate turns")
                    current_max_turn_angle = 60.0  # Allow moderate turns but not extreme ones
            else:
                # Reset stuck counter if making progress
                stuck_counter = 0
                current_max_turn_angle = 15.0  # Reset to initial smooth angle
        
        # Simple approach: try to keep straight on, adjust angle slightly if needed
        next_point = find_next_point(current_point, previous_polygon, segment_length,
                                   target_separation, min_separation, max_separation, 
                                   previous_direction, current_max_turn_angle)
        
        if not next_point:
            print(f"DEBUG: No next point found, stopping")
            break
            
        print(f"DEBUG: Found next_point: {next_point}")
        inner_points.append(next_point)
        
        # Track progress
        progress_tracker.append(current_point)
        
        # Calculate direction for next iteration
        previous_direction = (next_point[0] - current_point[0], next_point[1] - current_point[1])
        current_point = next_point
        
        # Check if we should close the polygon
        if should_close_polygon(inner_points, start_point, segment_length):
            print(f"DEBUG: Closing polygon after {len(inner_points)} points")
            inner_points.append(start_point)
            break
    
    return inner_points


def generate_nested_polygons(initial_polygon: List[Tuple[float, float]], num_polygons: int, 
                            segment_length: float, target_separation: float, min_separation: float, 
                            max_separation: float, inter_curve_distance: float) -> List[List[Tuple[float, float]]]:
    """
    Date: 2025-08-10
    Description: Generate multiple nested polygons
    """
    polygons = [initial_polygon]
    
    for i in range(num_polygons):
        previous_polygon = polygons[-1]
        
        # Adjust separation for this level
        current_target = target_separation + i * inter_curve_distance
        current_min = min_separation + i * inter_curve_distance
        current_max = max_separation + i * inter_curve_distance
        
        new_polygon = generate_nested_polygon(previous_polygon, segment_length, 
                                            current_target, current_min, current_max)
        
        if new_polygon:
            polygons.append(new_polygon)
        else:
            break
    
    return polygons
