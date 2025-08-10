"""
Test file for segment length pathologies - 2024-12-19
Tests for closure segments, consistency, and pathological curve issues.
"""

import sys
import os
import pytest
import math
import random

from atpoe.utils.segment_analysis import analyze_curve_segments, get_segment_lengths
from atpoe.curve_generator import generate_nested_curve_simple, generate_initial_circle
from atpoe.config_loader import load_config

def generate_spike_curve(center, radius, spike_height):
    """
    Generate a curve with a sharp spike.
    
    Date: 2024-12-19
    Description: Create curve with extreme spike for testing segment length handling.
    """
    points = []
    num_points = 20
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        if i == num_points // 2:  # Create spike at top
            r = radius + spike_height
        else:
            r = radius
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    
    return points

def generate_deep_concave_curve(center, radius, depth):
    """
    Generate a deeply concave curve.
    
    Date: 2024-12-19
    Description: Create curve with deep concave section for testing.
    """
    points = []
    num_points = 20
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        if 0.3 <= i / num_points <= 0.7:  # Create concave section
            r = radius - depth * math.sin(math.pi * (i / num_points - 0.3) / 0.4)
        else:
            r = radius
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    
    return points

def generate_sharp_star_curve(center, radius, num_spikes):
    """
    Generate a star-shaped curve with sharp spikes.
    
    Date: 2024-12-19
    Description: Create star curve with multiple sharp spikes.
    """
    points = []
    num_points = num_spikes * 10
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        spike_angle = 2 * math.pi / num_spikes
        spike_phase = (angle % spike_angle) / spike_angle
        
        if spike_phase < 0.5:  # Create spike
            r = radius * 1.5
        else:  # Create valley
            r = radius * 0.5
        
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    
    return points

def generate_extreme_irregular_curve(center, radius):
    """
    Generate an extremely irregular curve.
    
    Date: 2024-12-19
    Description: Create highly irregular curve with random variations.
    """
    points = []
    num_points = 30
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Add random variations
        r = radius + random.uniform(-radius * 0.3, radius * 0.3)
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    
    return points

def generate_narrow_passages_curve(center, radius):
    """
    Generate a curve with narrow passages.
    
    Date: 2024-12-19
    Description: Create curve with constricted sections.
    """
    points = []
    num_points = 24
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Create narrow passages at specific angles
        passage_angles = [0, math.pi/2, math.pi, 3*math.pi/2]
        is_passage = any(abs(angle - pa) < 0.3 for pa in passage_angles)
        
        if is_passage:
            r = radius * 0.3
        else:
            r = radius
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    
    return points

def test_closure_segment_length():
    """
    Test for abnormally long final segments when curves close.
    
    Date: 2024-12-19
    Description: Verify that the final segment (closure) is not abnormally long.
    """
    # Test with simple circle
    outer_curve = generate_initial_circle(500, 500, 100, 50)
    # Use config-validated target length
    config = load_config()
    min_len, max_len = config.get_segment_length_range()
    target_length = float(min_len)
    
    # Generate nested curve using current algorithm
    new_curve = generate_nested_curve_simple(outer_curve, 15, 1.5, 1.0, target_length)
    
    if new_curve and len(new_curve) > 1:
        segment_lengths = get_segment_lengths(new_curve)
        
        # Check if closure segment is abnormally long
        closure_length = segment_lengths[-1] if segment_lengths else 0
        avg_length = sum(segment_lengths[:-1]) / len(segment_lengths[:-1]) if len(segment_lengths) > 1 else 0
        
        print(f"Closure segment length: {closure_length}")
        print(f"Average segment length: {avg_length}")
        
        # Assert closure segment is not more than 2x the average
        assert closure_length <= 2 * avg_length, f"Closure segment {closure_length} is too long compared to average {avg_length}"
        
        # Assert closure segment is not more than 3x target length
        assert closure_length <= 3 * target_length, f"Closure segment {closure_length} is too long compared to target {target_length}"
    else:
        pytest.skip("No curve generated to test")

def test_segment_length_consistency():
    """
    Verify all segments are close to target length.
    
    Date: 2024-12-19
    Description: Check that segment lengths are consistent throughout the curve.
    """
    # Test with different curve shapes
    test_cases = [
        ("circle", generate_initial_circle(500, 500, 100, 50)),
        ("larger_circle", generate_initial_circle(500, 500, 150, 75)),
    ]
    
    # Use config-validated target length
    config = load_config()
    min_len, max_len = config.get_segment_length_range()
    target_length = float(min_len)
    
    for curve_name, outer_curve in test_cases:
        print(f"\nTesting {curve_name}")
        
        new_curve = generate_nested_curve_simple(outer_curve, 15, 1.5, 1.0, target_length)
        
        if new_curve and len(new_curve) > 1:
            analysis = analyze_curve_segments(new_curve, target_length)
            
            print(f"  Segments: {analysis['num_segments']}")
            print(f"  Avg length: {analysis['avg_length']}")
            print(f"  Std dev: {analysis['std_dev']}")
            print(f"  Accuracy: {analysis['accuracy_percent']}%")
            
            # Assert reasonable consistency (std dev not too high)
            assert analysis['std_dev'] <= target_length * 0.5, f"Standard deviation {analysis['std_dev']} too high for target {target_length}"
            
            # Assert reasonable accuracy
            assert analysis['accuracy_percent'] >= 50, f"Accuracy {analysis['accuracy_percent']}% too low"
            
            # Assert no extremely short or long segments
            min_length = analysis['min_length']
            max_length = analysis['max_length']
            assert min_length >= target_length * 0.3, f"Segment too short: {min_length}"
            assert max_length <= target_length * 3.0, f"Segment too long: {max_length}"
        else:
            pytest.skip(f"No curve generated for {curve_name}")

def test_pathological_curve_segments():
    """
    Test segment lengths with pathological curves.
    
    Date: 2024-12-19
    Description: Test segment consistency with sharp spikes, deep concaves, and irregular shapes.
    """
    # Use local pathological curve generators
    
    pathological_curves = [
        ("spike", generate_spike_curve((500, 500), 100, 200)),
        ("deep_concave", generate_deep_concave_curve((500, 500), 100, 150)),
        ("sharp_star", generate_sharp_star_curve((500, 500), 100, 5)),
        ("extreme_irregular", generate_extreme_irregular_curve((500, 500), 100)),
        ("narrow_passages", generate_narrow_passages_curve((500, 500), 100))
    ]
    
    # Use config-validated target length  
    config = load_config()
    min_len, max_len = config.get_segment_length_range()
    target_length = float(min_len)
    
    for curve_name, outer_curve in pathological_curves:
        print(f"\nTesting pathological curve: {curve_name}")
        
        new_curve = generate_nested_curve_simple(outer_curve, 15, 1.5, 1.0, target_length)
        
        if new_curve and len(new_curve) > 1:
            analysis = analyze_curve_segments(new_curve, target_length)
            
            print(f"  Segments: {analysis['num_segments']}")
            print(f"  Avg length: {analysis['avg_length']}")
            print(f"  Min/Max: {analysis['min_length']}/{analysis['max_length']}")
            print(f"  Std dev: {analysis['std_dev']}")
            print(f"  Accuracy: {analysis['accuracy_percent']}%")
            
            # Basic sanity checks for pathological curves
            assert analysis['num_segments'] > 0, f"No segments generated for {curve_name}"
            assert analysis['min_length'] > 0, f"Zero length segment in {curve_name}"
            assert analysis['max_length'] < 100, f"Extremely long segment {analysis['max_length']} in {curve_name}"
            
            # Check for reasonable consistency even with pathological shapes
            if analysis['std_dev'] > 0:
                coefficient_of_variation = analysis['std_dev'] / analysis['avg_length']
                assert coefficient_of_variation <= 1.0, f"Too much variation in {curve_name}: CV={coefficient_of_variation}"
        else:
            print(f"  No curve generated for {curve_name}")

if __name__ == "__main__":
    test_closure_segment_length()
    test_segment_length_consistency()
    test_pathological_curve_segments()
