"""
Date: 2025-08-10
Description: Visualization utility functions for polygon testing
"""

import math
from pathlib import Path
from lxml import etree
COORD_DECIMALS = 2



def validate_direction_continuity(unique_points, max_turn_angle=30.0):
    """
    Date: 2025-08-10
    Description: Validate that consecutive segments maintain direction continuity
    
    Args:
        unique_points: List of polygon points
        max_turn_angle: Maximum allowed turn angle in degrees
    
    Returns:
        bool: True if all segments have reasonable turn angles
    """
    for i in range(1, len(unique_points) - 1):
        prev_point = unique_points[i - 1]
        curr_point = unique_points[i]
        next_point = unique_points[i + 1]

        # Calculate direction vectors
        vec_prev_x = curr_point[0] - prev_point[0]
        vec_prev_y = curr_point[1] - prev_point[1]
        vec_curr_x = next_point[0] - curr_point[0]
        vec_curr_y = next_point[1] - curr_point[1]

        # Calculate angles
        prev_angle = math.degrees(math.atan2(vec_prev_y, vec_prev_x))
        curr_angle = math.degrees(math.atan2(vec_curr_y, vec_curr_x))

        # Calculate turn angle (handle angle wrapping)
        turn_angle = abs(curr_angle - prev_angle)
        if turn_angle > 180:
            turn_angle = 360 - turn_angle

        print(f"  Segment {i}: {prev_point} -> {curr_point} -> {next_point}, turn_angle = {turn_angle:.1f}°")

        # Assert that turn angle is reasonable (should be < max_turn_angle degrees for very smooth curves)
        # Allow some flexibility for pathological cases
        assert turn_angle < max_turn_angle, (
            f"Segment {i} has too sharp a turn: "
            f"turn_angle = {turn_angle:.1f}° (should be < {max_turn_angle}°)"
        )

    return True


def format_coordinate(value, decimal_places=2):
    """
    Date: 2025-08-10
    Description: Format coordinate value with limited decimal places for SVG
    """
    return f"{value:.{decimal_places}f}"


def create_success_visualization(outer_polygon, inner_polygon, elapsed_time, segment_length, target_separation):
    """
    Date: 2025-08-10
    Description: Create visualization for successful polygon generation using proper XML methods
    """
    # Constants for visualization
    MARGIN = 50
    GRID_SIZE = 100
    FONT_FAMILY = "Arial"
    SUCCESS_TITLE = "✅ SUCCESS: Fog-Based Polygon Generation"
    COORD_DECIMALS = 2  # Limit decimal places in SVG coordinates
    
    # Create SVG with proper viewBox and styling
    svg_file = Path("temp", "test_generate_single_inner_polygon.svg")

    # Calculate bounding box for proper viewBox
    all_points = outer_polygon + inner_polygon
    min_x = min(p[0] for p in all_points) - MARGIN
    max_x = max(p[0] for p in all_points) + MARGIN
    min_y = min(p[1] for p in all_points) - MARGIN
    max_y = max(p[1] for p in all_points) + MARGIN
    width = max_x - min_x
    height = max_y - min_y

    # Create SVG root element
    svg = etree.Element("svg", 
                       xmlns="http://www.w3.org/2000/svg",
                       viewBox=f"{min_x} {min_y} {width} {height}")

    # Add grid (optional, for reference)
    for x in range(int(min_x), int(max_x) + GRID_SIZE, GRID_SIZE):
        etree.SubElement(svg, "line", 
                        x1=format_coordinate(x, COORD_DECIMALS), y1=format_coordinate(min_y, COORD_DECIMALS), 
                        x2=format_coordinate(x, COORD_DECIMALS), y2=format_coordinate(max_y, COORD_DECIMALS),
                        stroke="#f0f0f0", stroke_width="0.5")
    
    for y in range(int(min_y), int(max_y) + GRID_SIZE, GRID_SIZE):
        etree.SubElement(svg, "line", 
                        x1=format_coordinate(min_x, COORD_DECIMALS), y1=format_coordinate(y, COORD_DECIMALS), 
                        x2=format_coordinate(max_x, COORD_DECIMALS), y2=format_coordinate(y, COORD_DECIMALS),
                        stroke="#f0f0f0", stroke_width="0.5")

    # Outer polygon (blue, thin line)
    outer_coords = " ".join([f"{x},{y}" for x, y in outer_polygon])
    etree.SubElement(svg, "polygon", 
                    points=outer_coords,
                    fill="none", stroke="blue", stroke_width="2", opacity="0.7")

    # Inner polygon (red, very thin line)
    inner_coords = " ".join([f"{format_coordinate(x, COORD_DECIMALS)},{format_coordinate(y, COORD_DECIMALS)}" for x, y in inner_polygon[:-1]])  # Exclude duplicate start point
    etree.SubElement(svg, "polygon", 
                    points=inner_coords,
                    fill="none", stroke="red", stroke_width="0.5")
    
    # Add small markers at each point to show individual segments
    for i, point in enumerate(inner_polygon[:-1]):  # Exclude duplicate start point
        x, y = point
        # Small circle marker at each point
        etree.SubElement(svg, "circle",
                        cx=format_coordinate(x, COORD_DECIMALS), cy=format_coordinate(y, COORD_DECIMALS), r="1.5",
                        fill="red", stroke="none")
        
        # Add point number for debugging (every 100th point to avoid clutter)
        if i % 100 == 0:
            etree.SubElement(svg, "text",
                            x=format_coordinate(x + 5, COORD_DECIMALS), y=format_coordinate(y - 5, COORD_DECIMALS),
                            font_family=FONT_FAMILY, font_size="8", fill="red").text = str(i)

    # Add title and labels
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 20, COORD_DECIMALS), y=format_coordinate(min_y + 30, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="16", fill="black").text = SUCCESS_TITLE
    
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 20, COORD_DECIMALS), y=format_coordinate(min_y + 50, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="12", fill="black").text = f"Segment Length: {segment_length}, Target Separation: {target_separation}"
    
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 20, COORD_DECIMALS), y=format_coordinate(min_y + 70, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="12", fill="black").text = f"Execution Time: {elapsed_time:.2f}s, Points: {len(inner_polygon)}"

    # Write SVG to file
    with open(svg_file, "wb") as f:
        f.write(etree.tostring(svg, pretty_print=True, encoding="utf-8"))

    # Convert SVG to PNG using a simple approach (if available)
    png_file = Path("temp", "test_generate_single_inner_polygon.png")
    try:
        # Try to use cairosvg if available for high-quality conversion
        import cairosvg

        cairosvg.svg2png(url=str(svg_file), write_to=str(png_file), output_width=1200, output_height=1000)
        print(f"📊 PNG visualization saved to: {png_file} (using cairosvg)")
    except ImportError:
        # Fallback: just save SVG and inform user
        print(f"📊 SVG visualization saved to: {svg_file}")
        print("💡 To convert to PNG, install cairosvg: pip install cairosvg")
        print("   Or open the SVG in a browser and save as PNG")

    print(f"📊 SVG visualization saved to: {svg_file}")


def create_failure_visualization(outer_polygon, error_message, elapsed_time, max_points, max_time, segment_length, target_separation):
    """
    Date: 2025-08-10
    Description: Create visualization for failed polygon generation using proper XML methods
    """
    # Constants for visualization
    MARGIN = 50
    GRID_SIZE = 100
    FONT_FAMILY = "Arial"
    FAILURE_TITLE = "❌ FAILURE: Fog-Based Polygon Generation"
    ERROR_BOX_WIDTH = 400
    ERROR_BOX_HEIGHT = 120
    
    # Create SVG with proper viewBox and styling
    svg_file = Path("temp", "test_generate_single_inner_polygon.svg")

    # Calculate bounding box for proper viewBox
    min_x = min(p[0] for p in outer_polygon) - MARGIN
    max_x = max(p[0] for p in outer_polygon) + MARGIN
    min_y = min(p[1] for p in outer_polygon) - MARGIN
    max_y = max(p[1] for p in outer_polygon) + MARGIN
    width = max_x - min_x
    height = max_y - min_y

    # Create SVG root element
    svg = etree.Element("svg", 
                       xmlns="http://www.w3.org/2000/svg",
                       viewBox=f"{min_x} {min_y} {width} {height}")

    # Add grid (optional, for reference)
    for x in range(int(min_x), int(max_x) + GRID_SIZE, GRID_SIZE):
        etree.SubElement(svg, "line", 
                        x1=format_coordinate(x, COORD_DECIMALS), y1=format_coordinate(min_y, COORD_DECIMALS), 
                        x2=format_coordinate(x, COORD_DECIMALS), y2=format_coordinate(max_y, COORD_DECIMALS),
                        stroke="#f0f0f0", stroke_width="0.5")
    
    for y in range(int(min_y), int(max_y) + GRID_SIZE, GRID_SIZE):
        etree.SubElement(svg, "line", 
                        x1=format_coordinate(min_x, COORD_DECIMALS), y1=format_coordinate(y, COORD_DECIMALS), 
                        x2=format_coordinate(max_x, COORD_DECIMALS), y2=format_coordinate(y, COORD_DECIMALS),
                        stroke="#f0f0f0", stroke_width="0.5")

    # Outer polygon (blue, thin line)
    outer_coords = " ".join([f"{format_coordinate(x, COORD_DECIMALS)},{format_coordinate(y, COORD_DECIMALS)}" for x, y in outer_polygon])
    etree.SubElement(svg, "polygon", 
                    points=outer_coords,
                    fill="none", stroke="blue", stroke_width="2", opacity="0.7")

    # Add error message box
    etree.SubElement(svg, "rect", 
                    x=format_coordinate(min_x + 20, COORD_DECIMALS), y=format_coordinate(min_y + 20, COORD_DECIMALS),
                    width=str(ERROR_BOX_WIDTH), height=str(ERROR_BOX_HEIGHT),
                    fill="red", opacity="0.1", stroke="red", stroke_width="1")
    
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 30, COORD_DECIMALS), y=format_coordinate(min_y + 45, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="16", fill="red").text = f"❌ FAILURE: {error_message}"
    
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 30, COORD_DECIMALS), y=format_coordinate(min_y + 65, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="12", fill="red").text = f"Execution Time: {elapsed_time:.2f}s"
    
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 30, COORD_DECIMALS), y=format_coordinate(min_y + 85, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="12", fill="red").text = f"Point Limit: {max_points}"
    
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 30, COORD_DECIMALS), y=format_coordinate(min_y + 105, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="12", fill="red").text = f"Time Limit: {max_time}s"

    # Add title
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 20, COORD_DECIMALS), y=format_coordinate(min_y + 150, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="16", fill="black").text = FAILURE_TITLE
    
    etree.SubElement(svg, "text", 
                    x=format_coordinate(min_x + 20, COORD_DECIMALS), y=format_coordinate(min_y + 170, COORD_DECIMALS),
                    font_family=FONT_FAMILY, font_size="12", fill="black").text = f"Segment Length: {segment_length}, Target Separation: {target_separation}"

    # Write SVG to file
    with open(svg_file, "wb") as f:
        f.write(etree.tostring(svg, pretty_print=True, encoding="utf-8"))

    print(f"📊 Failure visualization saved to: {svg_file}")
