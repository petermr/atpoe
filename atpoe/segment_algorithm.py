"""
Segment length algorithm functions - 2024-12-19
Core function for finding next point at specified distance from current position.
"""

import math
from typing import List, Tuple, Optional

def calculate_tangent_at_point(curve: List[Tuple[float, float]], point_index: int) -> Tuple[float, float]:
    """
    Calculate tangent direction at a specific point on the curve.
    
    Date: 2024-12-19
    Description: Calculate tangent using 3-point average method for smooth direction.
    """
    if len(curve) < 3:
        return (1.0, 0.0)  # Default rightward direction
    
    # Use 3-point average for smoother tangent calculation
    n = len(curve)
    prev_idx = (point_index - 1) % n
    next_idx = (point_index + 1) % n
    
    # Calculate direction vectors
    dx1 = curve[point_index][0] - curve[prev_idx][0]
    dy1 = curve[point_index][1] - curve[prev_idx][1]
    
    dx2 = curve[next_idx][0] - curve[point_index][0]
    dy2 = curve[next_idx][1] - curve[point_index][1]
    
    # Average the directions
    dx = (dx1 + dx2) / 2.0
    dy = (dy1 + dy2) / 2.0
    
    # Normalize
    length = math.sqrt(dx*dx + dy*dy)
    if length > 0:
        dx /= length
        dy /= length
    else:
        dx, dy = 1.0, 0.0
    
    return (dx, dy)

def calculate_inward_normal(tangent: Tuple[float, float], curve: List[Tuple[float, float]], point: Tuple[float, float]) -> Tuple[float, float]:
    """
    Calculate inward normal (perpendicular to tangent, pointing inside).
    
    Date: 2024-12-19
    Description: Calculate perpendicular direction that points toward curve interior.
    """
    tx, ty = tangent
    
    # Two possible normals: (ty, -tx) and (-ty, tx)
    normal1 = (ty, -tx)
    normal2 = (-ty, tx)
    
    # Choose the one that points more toward curve center
    center_x = sum(p[0] for p in curve) / len(curve)
    center_y = sum(p[1] for p in curve) / len(curve)
    
    to_center_x = center_x - point[0]
    to_center_y = center_y - point[1]
    
    # Dot product to see which normal is more aligned with center direction
    dot1 = normal1[0] * to_center_x + normal1[1] * to_center_y
    dot2 = normal2[0] * to_center_x + normal2[1] * to_center_y
    
    return normal1 if dot1 > dot2 else normal2

def generate_curve_following_segments(
    outer_curve: List[Tuple[float, float]], 
    distance: float, 
    segment_length: float,
    num_segments: int = None
) -> List[Tuple[float, float]]:
    """
    Generate new segments that follow the curve contour at specified distance.
    
    Date: 2024-12-19
    Description: True curve-following algorithm using tangent direction and iterative forward movement.
    """
    if not outer_curve or len(outer_curve) < 3:
        return []
    
    if num_segments is None:
        # Estimate number of segments based on curve perimeter
        perimeter = sum(math.hypot(outer_curve[i+1][0] - outer_curve[i][0], 
                                 outer_curve[i+1][1] - outer_curve[i][1]) 
                       for i in range(len(outer_curve)-1))
        num_segments = max(3, int(perimeter / segment_length))
    
    new_segments = []
    
    # Start at first point of outer curve
    current_outer_index = 0
    current_outer_point = outer_curve[0]
    
    for segment_idx in range(num_segments):
        # Calculate tangent at current position on outer curve
        tangent = calculate_tangent_at_point(outer_curve, current_outer_index)
        
        # Calculate inward normal
        inward_normal = calculate_inward_normal(tangent, outer_curve, current_outer_point)
        
        # Use inward normal direction but with very small distance to avoid crossings
        # Reduce distance to prevent curve following from getting too close to itself
        safe_distance = min(distance, segment_length * 0.3)  # Use 30% of segment length max
        
        # Move by safe distance in inward normal direction
        new_x = current_outer_point[0] + inward_normal[0] * safe_distance
        new_y = current_outer_point[1] + inward_normal[1] * safe_distance
        candidate_point = (new_x, new_y)
        
        # RULE 4: Check for crossings and minimum separation before accepting point
        if validate_point_safety(candidate_point, outer_curve, new_segments, distance * 0.5):
            new_segments.append(candidate_point)
# Debug output removed
        else:
            # Try alternative positions if candidate violates safety rules
            safe_point = find_safe_alternative_point(candidate_point, outer_curve, new_segments, distance, segment_length)
            if safe_point:
                new_segments.append(safe_point)
# Alternative point accepted
            else:
                # Skip this point to avoid violations, but still advance along curve
                print(f"Warning: Skipping point to avoid crossing violation at segment {segment_idx}")
                # Don't add point, but continue to advance along original curve
        
        # Move forward along the outer curve by segment_length
        remaining_distance = segment_length
        
        while remaining_distance > 0 and current_outer_index < len(outer_curve) - 1:
            next_idx = current_outer_index + 1
            segment_dist = math.hypot(
                outer_curve[next_idx][0] - current_outer_point[0],
                outer_curve[next_idx][1] - current_outer_point[1]
            )
            
            if segment_dist <= remaining_distance:
                # Move to next point
                remaining_distance -= segment_dist
                current_outer_index = next_idx
                current_outer_point = outer_curve[current_outer_index]
            else:
                # Interpolate within current segment
                ratio = remaining_distance / segment_dist
                current_outer_point = (
                    current_outer_point[0] + ratio * (outer_curve[next_idx][0] - current_outer_point[0]),
                    current_outer_point[1] + ratio * (outer_curve[next_idx][1] - current_outer_point[1])
                )
                remaining_distance = 0
    
    return new_segments

def find_next_point_at_distance(
    current_point: Tuple[float, float], 
    outer_curve: List[Tuple[float, float]], 
    segment_length: float, 
    distance: float,
    direction: float = 0.0
) -> Optional[Tuple[float, float]]:
    """
    Find the next point at specified segment length from current position.
    
    Date: 2024-12-19
    Description: Proceeds forward by segment length while maintaining distance from outer curve.
    
    Args:
        current_point: Current position (x, y)
        outer_curve: List of points defining the outer curve to follow
        segment_length: Target distance to the next point
        distance: Distance to maintain from outer curve
        direction: Initial direction in radians (0 = right, π/2 = up)
    
    Returns:
        Next point (x, y) or None if no valid point found
    """
    if not outer_curve or len(outer_curve) < 3:
        return None
    
    # Calculate center of outer curve for reference
    center_x = sum(p[0] for p in outer_curve) / len(outer_curve)
    center_y = sum(p[1] for p in outer_curve) / len(outer_curve)
    
    # Try multiple directions around the current point
    num_attempts = 16  # Try 16 different directions
    best_point = None
    best_score = float('inf')
    
    for i in range(num_attempts):
        # Calculate direction to try
        test_direction = direction + (2 * math.pi * i / num_attempts)
        
        # Calculate candidate point at segment_length distance
        candidate_x = current_point[0] + segment_length * math.cos(test_direction)
        candidate_y = current_point[1] + segment_length * math.sin(test_direction)
        candidate_point = (candidate_x, candidate_y)
        
        # Find closest point on outer curve
        min_dist_to_outer = float('inf')
        for outer_point in outer_curve:
            dist = math.hypot(candidate_x - outer_point[0], candidate_y - outer_point[1])
            min_dist_to_outer = min(min_dist_to_outer, dist)
        
        # Calculate score based on how close we are to target distance
        distance_error = abs(min_dist_to_outer - distance)
        
        # Prefer points that are inside the outer curve
        is_inside = is_point_inside_curve(candidate_point, outer_curve)
        
        # Score: lower is better
        score = distance_error
        if not is_inside:
            score += 1000  # Heavy penalty for being outside
        
        if score < best_score:
            best_score = score
            best_point = candidate_point
    
    return best_point

def is_point_inside_curve(point: Tuple[float, float], curve: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a closed curve using ray casting.
    
    Date: 2024-12-19
    Description: Simple ray casting algorithm to determine if point is inside curve.
    """
    if len(curve) < 3:
        return False
    
    x, y = point
    inside = False
    
    for i in range(len(curve)):
        j = (i + 1) % len(curve)
        xi, yi = curve[i]
        xj, yj = curve[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
    
    return inside

def validate_point_safety(candidate_point: Tuple[float, float], 
                         outer_curve: List[Tuple[float, float]], 
                         existing_segments: List[Tuple[float, float]], 
                         min_separation: float) -> bool:
    """
    Validate that a candidate point doesn't violate crossing or separation rules.
    
    Date: 2024-12-19
    Description: Enforce RULE 4 - No crossings and minimum separation.
    """
    # Check minimum separation from nearby points on outer curve only
    # Only check points within a reasonable radius to avoid false positives from distant curve parts
    max_check_distance = min_separation * 3  # Check within 3x the minimum separation
    for i, outer_point in enumerate(outer_curve):
        distance = math.hypot(candidate_point[0] - outer_point[0], candidate_point[1] - outer_point[1])
        if distance < max_check_distance and distance < min_separation:
# Minimum separation violation detected
            return False
    
    # Check minimum separation from existing generated segments
    for i, existing_point in enumerate(existing_segments):
        distance = math.hypot(candidate_point[0] - existing_point[0], candidate_point[1] - existing_point[1])
        if distance < min_separation:
# Too close to existing segment
            return False
    
    # Check for line segment crossings if we have enough points
    if len(existing_segments) >= 2:
        # Check if line from last segment to candidate crosses any existing segments
        last_point = existing_segments[-1]
        for i in range(len(existing_segments) - 1):
            if segments_intersect(last_point, candidate_point, existing_segments[i], existing_segments[i + 1]):
                return False
        
        # Check if line crosses outer curve segments
        for i in range(len(outer_curve) - 1):
            if segments_intersect(last_point, candidate_point, outer_curve[i], outer_curve[i + 1]):
                return False
    
    return True

def segments_intersect(p1: Tuple[float, float], p2: Tuple[float, float], 
                      p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """
    Check if two line segments intersect.
    
    Date: 2024-12-19
    Description: Line segment intersection detection for crossing prevention.
    """
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    # Check if segments p1p2 and p3p4 intersect
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

def find_safe_alternative_point(candidate_point: Tuple[float, float], 
                               outer_curve: List[Tuple[float, float]], 
                               existing_segments: List[Tuple[float, float]], 
                               distance: float, 
                               segment_length: float) -> Optional[Tuple[float, float]]:
    """
    Find a safe alternative point that maintains distance and segment length.
    
    Date: 2024-12-19
    Description: Try different positions to avoid crossings while maintaining constraints.
    """
    if not existing_segments:
        return candidate_point
    
    last_point = existing_segments[-1]
    min_separation = distance * 0.5
    
    # Try different angles around the desired position
    for angle_offset in [0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3]:
        # Adjust direction slightly
        dx = candidate_point[0] - last_point[0]
        dy = candidate_point[1] - last_point[1]
        
        # Rotate by angle_offset
        cos_offset = math.cos(angle_offset)
        sin_offset = math.sin(angle_offset)
        
        new_dx = dx * cos_offset - dy * sin_offset
        new_dy = dx * sin_offset + dy * cos_offset
        
        # Normalize to segment_length
        length = math.hypot(new_dx, new_dy)
        if length > 0:
            new_dx = new_dx * segment_length / length
            new_dy = new_dy * segment_length / length
        
        alternative_point = (last_point[0] + new_dx, last_point[1] + new_dy)
        
        if validate_point_safety(alternative_point, outer_curve, existing_segments, min_separation):
            return alternative_point
    
    return None

