"""
Test file for segment analysis functions - 2024-12-19
Tests the segment analysis utilities.
"""

import sys
import os
import pytest

from atpoe.utils.segment_analysis import analyze_curve_segments, get_segment_lengths
from atpoe.config_loader import load_config

def test_segment_analysis():
    """
    Test the segment analysis functions.
    
    Date: 2024-12-19
    Description: Test segment analysis utilities with various curve types.
    """
    
    # Test 1: Simple square curve
    print("=== Test 1: Square Curve ===")
    square_curve = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    # Use config-validated target length
    config = load_config()
    min_len, max_len = config.get_segment_length_range()
    target_length = 10.0  # This should be validated by analyze_curve_segments
    
    segment_lengths = get_segment_lengths(square_curve)
    print(f"Segment lengths: {segment_lengths}")
    
    # Assert segment lengths are correct
    assert len(segment_lengths) == 4, f"Expected 4 segments, got {len(segment_lengths)}"
    assert all(length == pytest.approx(10.0) for length in segment_lengths), f"All segments should be 10.0, got {segment_lengths}"
    
    analysis = analyze_curve_segments(square_curve, target_length)
    print(f"Analysis: {analysis}")
    
    # Assert analysis results
    assert analysis['num_segments'] == 4, f"Expected 4 segments, got {analysis['num_segments']}"
    assert analysis['avg_length'] == pytest.approx(10.0), f"Expected avg 10.0, got {analysis['avg_length']}"
    assert analysis['min_length'] == pytest.approx(10.0), f"Expected min 10.0, got {analysis['min_length']}"
    assert analysis['max_length'] == pytest.approx(10.0), f"Expected max 10.0, got {analysis['max_length']}"
    assert analysis['std_dev'] == pytest.approx(0.0), f"Expected std_dev 0.0, got {analysis['std_dev']}"
    assert analysis['accuracy_percent'] == pytest.approx(100.0), f"Expected accuracy 100.0, got {analysis['accuracy_percent']}"
    
    # Test 2: Empty curve
    print("\n=== Test 2: Empty Curve ===")
    empty_curve = []
    analysis = analyze_curve_segments(empty_curve, target_length)
    print(f"Empty curve analysis: {analysis}")
    
    # Assert empty curve results
    assert analysis['num_segments'] == 0, f"Expected 0 segments, got {analysis['num_segments']}"
    assert analysis['avg_length'] == pytest.approx(0.0), f"Expected avg 0, got {analysis['avg_length']}"
    assert analysis['segment_lengths'] == [], f"Expected empty list, got {analysis['segment_lengths']}"
    
    # Test 3: Single point
    print("\n=== Test 3: Single Point ===")
    single_point = [(5, 5)]
    analysis = analyze_curve_segments(single_point, target_length)
    print(f"Single point analysis: {analysis}")
    
    # Assert single point results
    assert analysis['num_segments'] == 0, f"Expected 0 segments, got {analysis['num_segments']}"
    assert analysis['avg_length'] == pytest.approx(0.0), f"Expected avg 0, got {analysis['avg_length']}"
    assert analysis['segment_lengths'] == [], f"Expected empty list, got {analysis['segment_lengths']}"
    
    # Test 4: Irregular curve
    print("\n=== Test 4: Irregular Curve ===")
    irregular_curve = [(0, 0), (5, 0), (10, 5), (5, 10), (0, 5), (0, 0)]
    analysis = analyze_curve_segments(irregular_curve, target_length)
    print(f"Irregular curve analysis: {analysis}")
    
    # Assert irregular curve results
    assert analysis['num_segments'] == 5, f"Expected 5 segments, got {analysis['num_segments']}"
    assert 6.0 <= analysis['avg_length'] <= 7.0, f"Expected avg between 6-7, got {analysis['avg_length']}"
    assert analysis['min_length'] == pytest.approx(5.0), f"Expected min 5.0, got {analysis['min_length']}"
    assert 7.0 <= analysis['max_length'] <= 8.0, f"Expected max between 7-8, got {analysis['max_length']}"
    assert analysis['std_dev'] > 0, f"Expected positive std_dev, got {analysis['std_dev']}"
    assert 60.0 <= analysis['accuracy_percent'] <= 70.0, f"Expected accuracy 60-70%, got {analysis['accuracy_percent']}"
    
    print("All tests passed!")

if __name__ == "__main__":
    test_segment_analysis()
