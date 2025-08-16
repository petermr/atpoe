import streamlit as st
import math
import random
from PIL import Image, ImageDraw
import io
from atpoe.config_loader import load_config
# from tests.test_fog_polygon_generation import Point2D


# Simple graphics bundle system
class SimpleGraphicsBundle:
    def __init__(self, name, color, width):
        self.name = name
        self.color = color
        self.width = width

# def generate_initial_circle(center: Point2D, radius: float, num_points: int = 50):
#     """Generate initial circular curve with fewer points to prevent hanging."""
#     points = []
#     for i in range(num_points):
#         angle = 2 * math.pi * i / num_points
#         x = center.x + radius * math.cos(angle)
#         y = center.y + radius * math.sin(angle)
#         point = Point2D(x, y)
#         points.append(point)
#     return points, y

def generate_nested_curve_simple(outer_curve, distance: float, error: float, min_separation: float = 1.0, segment_length: float = 20.0):
    """
    Generate a nested curve by moving points inward with error, ensuring minimum separation.
    
    Date: 2024-12-19
    Description: Generate closed curve with config-validated segment length control and closure handling.
    """
    # Load configuration and validate segment length
    config = load_config()
    min_len, max_len = config.get_segment_length_range()
    
    if not (min_len <= segment_length <= max_len):
        raise ValueError(f"Segment length {segment_length} outside config range {min_len}-{max_len}")
    if not outer_curve or len(outer_curve) < 3:
        return []
    
    # Calculate center of outer curve
    center_x = sum(p[0] for p in outer_curve) / len(outer_curve)
    center_y = sum(p[1] for p in outer_curve) / len(outer_curve)
    
    new_curve = []
    current_point = outer_curve[0]  # Start with first point
    
    for i, point in enumerate(outer_curve):
        # Calculate direction from center to point
        dx = point[0] - center_x
        dy = point[1] - center_y
        
        # Normalize direction vector
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx /= length
            dy /= length
        
        # Move point inward by distance, ensuring minimum separation
        move_distance = max(distance, min_separation)
        new_x = point[0] - dx * move_distance
        new_y = point[1] - dy * move_distance
        
        # Add random error (but less for first and last points to ensure closure)
        if i == 0 or i == len(outer_curve) - 1:
            error_x = random.uniform(-error * 0.2, error * 0.2)
            error_y = random.uniform(-error * 0.2, error * 0.2)
        else:
            error_x = random.uniform(-error, error)
            error_y = random.uniform(-error, error)
        
        new_point = (new_x + error_x, new_y + error_y)
        
        # Check if this point is at proper segment length from current point
        if i > 0:
            current_distance = math.sqrt((new_point[0] - current_point[0])**2 + (new_point[1] - current_point[1])**2)
            if current_distance > segment_length * 1.5:  # Allow some flexibility
                # Interpolate to maintain segment length
                ratio = segment_length / current_distance
                new_point = (
                    current_point[0] + (new_point[0] - current_point[0]) * ratio,
                    current_point[1] + (new_point[1] - current_point[1]) * ratio
                )
        
        new_curve.append(new_point)
        current_point = new_point
    
    # RULE 1: Ensure the curve closes without gaps
    if len(new_curve) > 2:
        # Check distance from last to first point
        last_to_first_distance = math.sqrt(
            (new_curve[-1][0] - new_curve[0][0])**2 + 
            (new_curve[-1][1] - new_curve[0][1])**2
        )
        
        if last_to_first_distance <= segment_length * 1.2:  # Close enough to close
            # Force the last point to be exactly the same as the first point
            new_curve[-1] = new_curve[0]
        else:
            # Add intermediate points to close properly
            while last_to_first_distance > segment_length:
                # Add point at segment length from last point towards first
                dx = new_curve[0][0] - new_curve[-1][0]
                dy = new_curve[0][1] - new_curve[-1][1]
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    ratio = segment_length / length
                    new_point = (
                        new_curve[-1][0] + dx * ratio,
                        new_curve[-1][1] + dy * ratio
                    )
                    new_curve.append(new_point)
                    last_to_first_distance = math.sqrt(
                        (new_point[0] - new_curve[0][0])**2 + 
                        (new_point[1] - new_curve[0][1])**2
                    )
                else:
                    break
            
            # Final closure
            if last_to_first_distance <= segment_length * 1.2:
                new_curve[-1] = new_curve[0]
    
    return new_curve

def check_curve_inside_outer(inner_curve, outer_curve):
    """Check if inner curve is completely inside outer curve."""
    if not inner_curve or not outer_curve:
        return False
    
    # Calculate center of outer curve
    outer_center_x = sum(p[0] for p in outer_curve) / len(outer_curve)
    outer_center_y = sum(p[1] for p in outer_curve) / len(outer_curve)
    
    # Calculate radius of outer curve
    outer_radius = max(math.hypot(p[0] - outer_center_x, p[1] - outer_center_y) for p in outer_curve)
    
    # Check if all points of inner curve are inside outer curve
    for point in inner_curve:
        distance_from_center = math.hypot(point[0] - outer_center_x, point[1] - outer_center_y)
        if distance_from_center >= outer_radius:
            return False
    
    return True

def draw_curves_simple(draw, curves, bundle):
    """
    Draw curves using the specified graphics bundle.
    
    Date: 2024-12-19
    Description: Draw curves with config-based drawing settings.
    """
    if not curves:
        return
    
    # Convert hex color to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    color = hex_to_rgb(bundle.color)
    
    # Draw each curve
    for curve in curves:
        if len(curve) < 2:
            continue
            
        # Draw line segments
        for i in range(len(curve) - 1):
            start_point = curve[i]
            end_point = curve[i + 1]
            draw.line([start_point, end_point], fill=color, width=int(bundle.width))

def main():
    st.set_page_config(page_title="AtPoE - Multi-Bundle Stable", page_icon="🎨", layout="wide")
    st.title("🎨 AtPoE - Multi-Bundle Interactive Curve Generator")
    st.markdown("Generate curves with different graphics bundles interactively")
    
    # Initialize session state
    if 'all_curves' not in st.session_state:
        st.session_state.all_curves = []
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    if 'bundle_history' not in st.session_state:
        st.session_state.bundle_history = []
    
    # Sidebar for all controls
    with st.sidebar:
        st.header("🎛️ AtPoE Controls")
        
        # Line type configuration
        st.subheader("🎨 Line Type Configuration")
        
        # Line type selector
        line_name = st.text_input("Line Name", value="Custom Line", key="line_name")
        
        # Color picker
        fill_color = st.color_picker("Fill Colour", value="#000000", key="color_picker")
        
        # Width slider
        line_width = st.slider("Width", 0.5, 5.0, 2.0, 0.1, key="width_slider")
        
        # Antialias checkbox
        use_antialias = st.checkbox("Antialias", value=True, key="antialias_checkbox")
        
        # Create bundle from user input
        selected_bundle = SimpleGraphicsBundle(line_name, fill_color, line_width)
        
        # Display bundle info
        st.info(f"**{selected_bundle.name}**\n"
               f"Color: {selected_bundle.color}\n"
               f"Width: {selected_bundle.width}px")
        
        # Parameters for current bundle
        st.subheader("⚙️ Parameters")
        num_curves = st.slider("Number of Curves", 1, 30, 3, key="curves_slider")
        error_level = st.slider("Error Level", 0.0, 6.0, 1.5, 0.1, key="error_slider")
        curve_distance = st.slider("Curve Separation", 0.0, 15.0, 8.0, 0.1, key="distance_slider")
        # Load config for segment length constraints
        config = load_config()
        min_len, max_len = config.get_segment_length_range()
        segment_length = st.slider("Segment Length", float(min_len), float(max_len), 3.0, 0.1, key="segment_slider")
        min_inter_curve = st.slider("Minimum Inter-Curve", 1.0, 4.0, 1.0, 0.1, key="inter_curve_slider")
        canvas_size = st.selectbox("Canvas Size", [800, 1000, 1200, 1500], index=1, key="canvas_slider")
        
        # Action buttons
        st.subheader("🎯 Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            add_bundle_clicked = st.button("➕ Add Bundle", type="primary", key="add_bundle_btn")
        
        with col2:
            clear_all_clicked = st.button("🗑️ Clear All", key="clear_all_btn")
            
        with col3:
            stop_clicked = st.button("⏹️ Stop", key="stop_btn")
        
        # Bundle history
        if st.session_state.bundle_history:
            st.subheader("📚 Bundle History")
            for i, (bundle_name, curves_count) in enumerate(st.session_state.bundle_history):
                st.write(f"{i+1}. {bundle_name} ({curves_count} curves)")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎨 Generated Curves")
        
        # Handle button clicks
        if add_bundle_clicked:
            try:
                # Generate curves for current bundle
                center_x = canvas_size / 2
                center_y = canvas_size / 2
                
                # Create new image or use existing
                if st.session_state.current_image is None:
                    image = Image.new('RGB', (canvas_size, canvas_size), 'white')
                    draw = ImageDraw.Draw(image)
                    # Start with outer circle for first bundle
                    radius = min(canvas_size / 2 - 50, 300)
                    start_curve = generate_initial_circle(center_x, center_y, radius)
                else:
                    # Load existing image
                    image = st.session_state.current_image
                    draw = ImageDraw.Draw(image)
                    # Continue from the last curve of the previous bundle
                    if st.session_state.all_curves:
                        last_bundle_curves = st.session_state.all_curves[-1]
                        if last_bundle_curves:
                            start_curve = last_bundle_curves[-1]  # Use the innermost curve
                        else:
                            # Fallback to outer circle if no previous curves
                            radius = min(canvas_size / 2 - 50, 300)
                            start_curve = generate_initial_circle(center_x, center_y, radius)
                    else:
                        # Fallback to outer circle if no previous curves
                        radius = min(canvas_size / 2 - 50, 300)
                        start_curve = generate_initial_circle(center_x, center_y, radius)
                
                # Generate curves for this bundle, starting from the last curve
                bundle_curves = []
                
                for i in range(num_curves):
                    if i == 0:
                        # First curve: generate inward from the starting curve
                        # This ensures proper continuity and closure
                        curve = generate_nested_curve_simple(
                            start_curve, curve_distance, error_level, min_inter_curve
                        )
                    else:
                        # Nested curves continue inward from the previous curve in this bundle
                        curve = generate_nested_curve_simple(
                            bundle_curves[i-1], curve_distance, error_level, min_inter_curve
                        )
                    
                    # RULE 3: Ensure curve is inside existing curves without overlap
                    if curve:
                        # Check if this curve is inside the previous curve
                        if i == 0 and st.session_state.all_curves:
                            # For first curve of new bundle, check against last curve of previous bundle
                            last_prev_curve = st.session_state.all_curves[-1][-1]
                            if not check_curve_inside_outer(curve, last_prev_curve):
                                # Adjust curve to be inside
                                curve = generate_nested_curve_simple(
                                    last_prev_curve, min_inter_curve, error_level * 0.5, min_inter_curve
                                )
                        elif i > 0:
                            # For subsequent curves, check against previous curve in this bundle
                            if not check_curve_inside_outer(curve, bundle_curves[i-1]):
                                # Adjust curve to be inside
                                curve = generate_nested_curve_simple(
                                    bundle_curves[i-1], min_inter_curve, error_level * 0.5, min_inter_curve
                                )
                        
                        if curve:
                            bundle_curves.append(curve)
                
                # Draw curves with current bundle
                draw_curves_simple(draw, bundle_curves, selected_bundle)
                
                # Update session state
                st.session_state.all_curves.append(bundle_curves)
                st.session_state.current_image = image
                st.session_state.bundle_history.append((selected_bundle.name, num_curves))
                
                st.success(f"✅ Added {num_curves} curves with '{selected_bundle.name}' bundle!")
                
            except Exception as e:
                st.error(f"❌ Error generating curves: {str(e)}")
        
        elif clear_all_clicked:
            st.session_state.all_curves = []
            st.session_state.current_image = None
            st.session_state.bundle_history = []
            st.info("🗑️ All curves cleared!")
        
        # Display current image
        if st.session_state.current_image:
            # Create a container for the image with parameter overlay
            image_container = st.container()
            
            with image_container:
                # Display parameters in top left
                st.markdown(f"""
                <div style="position: absolute; top: 10px; left: 10px; background: rgba(255,255,255,0.9); 
                padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; z-index: 1000;">
                <strong>Parameters Used:</strong><br>
                Curves: {num_curves}<br>
                Error: {error_level}<br>
                Separation: {curve_distance}<br>
                Segment Length: {segment_length}<br>
                Min Inter-Curve: {min_inter_curve}<br>
                Width: {line_width}<br>
                Color: {fill_color}
                </div>
                """, unsafe_allow_html=True)
                
                st.image(st.session_state.current_image, use_container_width=True)
            
            # File save section
            st.subheader("💾 File Save")
            
            # File type selector
            file_type = st.selectbox("File Type", ["PNG", "SVG"], key="file_type_selector")
            
            # File name input
            file_name = st.text_input("File Name", value=f"atpoe_curves_{len(st.session_state.bundle_history)}_bundles", key="file_name_input")
            
            # Download buttons
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                if file_type == "PNG":
                    # Convert PIL image to bytes for download
                    img_buffer = io.BytesIO()
                    st.session_state.current_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download PNG",
                        data=img_buffer.getvalue(),
                        file_name=f"{file_name}.png",
                        mime="image/png"
                    )
                else:  # SVG
                    # For now, we'll save as PNG but with SVG extension
                    # TODO: Implement proper SVG generation
                    img_buffer = io.BytesIO()
                    st.session_state.current_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download SVG",
                        data=img_buffer.getvalue(),
                        file_name=f"{file_name}.svg",
                        mime="image/svg+xml"
                    )
        else:
            st.info("🎨 Click 'Add Bundle' to start generating curves!")
    
    with col2:
        st.subheader("📊 Status")
        
        # Current status
        total_bundles = len(st.session_state.bundle_history)
        total_curves = sum(curves_count for _, curves_count in st.session_state.bundle_history)
        
        st.metric("Total Bundles", total_bundles)
        st.metric("Total Curves", total_curves)
        
        if selected_bundle:
            st.metric("Selected Bundle", selected_bundle.name)
        
        # Current parameters
        st.subheader("⚙️ Current Parameters")
        st.write(f"**Curves:** {num_curves}")
        st.write(f"**Error Level:** {error_level}")
        st.write(f"**Curve Distance:** {curve_distance}")
        st.write(f"**Canvas Size:** {canvas_size}x{canvas_size}")
        
        # Instructions
        st.subheader("📖 Instructions")
        st.markdown("""
        1. **Select a graphics bundle** from the dropdown
        2. **Adjust parameters** as needed
        3. **Click 'Add Bundle'** to generate curves
        4. **Repeat** with different bundles
        5. **Download** your final composition
        
        **Tip:** Use thick curves as separators between different style groups!
        """)

if __name__ == "__main__":
    main()
