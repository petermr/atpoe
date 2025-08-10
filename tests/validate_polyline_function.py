"""
Validation test for polyline function - 2024-12-19
Test the generate_nested_polyline_simple function before using it in main tests.
"""

import sys
import os

import math
from tests.test_geometric_lines import generate_nested_polyline_simple, generate_line_by_angles

def validate_polyline_function():
    """
    Validate the polyline function with simple test cases.
    
    Date: 2024-12-19
    Description: Test polyline function with simple straight line before using in main tests.
    """
    print("=== Validating Polyline Function ===")
    
    # Test 1: Simple straight line
    print("Test 1: Simple straight line")
    straight_line = generate_line_by_angles([0, 0, 0, 0, 0, 0, 0, 0, 0], (100, 100))
    print(f"Original line: {len(straight_line)} points")
    
    # Generate polyline
    new_polyline = generate_nested_polyline_simple(straight_line, 15, 1.5, 1.0)
    print(f"Generated polyline: {len(new_polyline)} points")
    
    # Basic validation
    assert len(new_polyline) > 0, "Polyline should not be empty"
    assert len(new_polyline) == len(straight_line), "Should have same number of points"
    
    # Check that points are different (not just copied)
    assert new_polyline[0] != straight_line[0], "Points should be moved inward"
    
    print("✅ Polyline function validation passed!")
    return True

if __name__ == "__main__":
    validate_polyline_function()
