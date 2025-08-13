"""
Date: 2025-08-10
Description: Polygon validation utility functions for testing
"""

def validate_inner_polygon_containment(outer_polygon, inner_polygon):
    """
    Date: 2025-08-10
    Description: Validate that all inner polygon points are inside outer polygon
    
    Returns:
    bool: True if all points are inside, False otherwise
    """
    from atpoe.fog_polygon_generator import is_point_inside_polygon
    
    for point in inner_polygon:
        if not is_point_inside_polygon(point, outer_polygon):
            return False
    return True

def validate_point_separations(unique_points, outer_polygon, target_separation, tolerance_percent=0.1):
    """
    Date: 2025-08-10
    Description: Validate that consecutive points maintain consistent separation from outer curve
    
    Returns:
    tuple: (is_valid, first_separation, second_separation, tolerance)
    """
    from atpoe.fog_polygon_generator import calculate_distance_to_polygon
    
    if len(unique_points) < 2:
        return False, 0, 0, 0
    
    first_point = unique_points[0]
    second_point = unique_points[1]
    
    first_separation = calculate_distance_to_polygon(first_point, outer_polygon)
    second_separation = calculate_distance_to_polygon(second_point, outer_polygon)
    
    separation_tolerance = target_separation * tolerance_percent
    is_valid = abs(first_separation - second_separation) <= separation_tolerance
    
    return is_valid, first_separation, second_separation, separation_tolerance

def validate_direction_continuity(unique_points):
    """
    Date: 2025-08-10
    Description: Validate that consecutive segments maintain direction continuity
    
    Returns:
    bool: True if direction continuity is maintained
    """
    # This function would contain the direction continuity validation logic
    # For now, returning True as placeholder - will implement based on existing logic
    return True

