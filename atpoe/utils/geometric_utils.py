"""
Date: 2024-08-20
Description: Geometric utility functions for polygon generation and testing
"""

import numpy as np

def bounding_polygon(centre=(500, 500), radius=500, npoints=1000):
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

