"""
Segment analysis utilities - 2024-12-19
Helper functions for analyzing curve segments and lengths.
"""

import math
from typing import List, Tuple, Dict, Any
from ..config_loader import load_config

def analyze_curve_segments(curve: List[Tuple[float, float]], target_length: float) -> Dict[str, Any]:
    """
    Calculate segment statistics for debugging.
    
    Date: 2024-12-19
    Description: Analyze segment lengths in a curve and compare to config-validated target length.
    
    Args:
        curve: List of (x, y) points forming the curve
        target_length: Expected segment length
    
    Returns:
        Dictionary with segment statistics
    """
    # Validate target length against config constraints
    config = load_config()
    min_len, max_len = config.get_segment_length_range()
    
    if not (min_len <= target_length <= max_len):
        raise ValueError(f"Target length {target_length} outside config range {min_len}-{max_len}")
    if len(curve) < 2:
        return {
            'num_segments': 0,
            'avg_length': 0,
            'min_length': 0,
            'max_length': 0,
            'std_dev': 0,
            'accuracy_percent': 0,
            'segment_lengths': []
        }
    
    segment_lengths = get_segment_lengths(curve)
    
    if not segment_lengths:
        return {
            'num_segments': 0,
            'avg_length': 0,
            'min_length': 0,
            'max_length': 0,
            'std_dev': 0,
            'accuracy_percent': 0,
            'segment_lengths': []
        }
    
    avg_length = round(sum(segment_lengths) / len(segment_lengths), 2)
    min_length = min(segment_lengths)
    max_length = max(segment_lengths)
    
    # Calculate standard deviation
    variance = sum((length - avg_length) ** 2 for length in segment_lengths) / len(segment_lengths)
    std_dev = round(math.sqrt(variance), 2)
    
    # Calculate accuracy as percentage
    accuracy_percent = round((1 - abs(avg_length - target_length) / target_length) * 100, 2)
    
    return {
        'num_segments': len(segment_lengths),
        'avg_length': avg_length,
        'min_length': min_length,
        'max_length': max_length,
        'std_dev': std_dev,
        'accuracy_percent': accuracy_percent,
        'segment_lengths': segment_lengths
    }

def get_segment_lengths(curve: List[Tuple[float, float]]) -> List[float]:
    """
    Extract segment lengths from curve points.
    
    Date: 2024-12-19
    Description: Calculate distances between consecutive points in a curve.
    
    Args:
        curve: List of (x, y) points forming the curve
    
    Returns:
        List of segment lengths
    """
    if len(curve) < 2:
        return []
    
    segment_lengths = []
    for i in range(len(curve) - 1):
        p1 = curve[i]
        p2 = curve[i + 1]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        segment_lengths.append(round(length, 2))
    
    return segment_lengths
