"""
Streamlit interface for drawing analysis
Date: 2025-01-27 (system date of generation)
Description: Analyze monochromatic drawings with concentric curves using preprocessing pipeline
"""

import streamlit as st
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import sknw
import networkx as nx
from skimage import morphology, filters, measure, segmentation
from skimage.morphology import disk, opening, closing, erosion, dilation
from skimage.filters import unsharp_mask
from skimage.measure import label
import io

# Page configuration
st.set_page_config(
    page_title="AtPoE Drawing Analysis",
    page_icon="🔬",
    layout="wide"
)

def load_image_from_drawings_folder(filename):
    """
    Load image from drawings folder
    Date: 2025-01-27
    Description: Load PNG/JPEG images from the drawings directory
    """
    drawings_path = Path("drawings")
    if not drawings_path.exists():
        st.error("Drawings folder not found!")
        return None
    
    image_path = drawings_path / filename
    if not image_path.exists():
        st.error(f"Image {filename} not found in drawings folder!")
        return None
    
    try:
        image = Image.open(image_path)
        return np.array(image)
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def monochromatize_image(image, threshold=128):
    """
    Step 1: Convert image to monochromatic (black/white)
    Date: 2025-01-27
    Description: Convert to grayscale then to binary using threshold
    """
    if len(image.shape) == 3:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Convert to binary
    binary = (gray < threshold).astype(np.uint8) * 255
    return binary


def remove_noise(image, kernel_size=3):
    """
    Step 2: Remove noise using morphological operations
    Date: 2025-01-27
    Description: Apply opening and closing to remove small noise artifacts
    """
    # Create kernel
    kernel = disk(kernel_size)
    
    # Apply opening (erosion followed by dilation) to remove small noise
    opened = opening(image, kernel)
    
    # Apply closing (dilation followed by erosion) to fill small gaps
    closed = closing(opened, kernel)
    
    return closed

def sharpen_image(image, radius=1, amount=1):
    """
    Step 3: Sharpen image edges
    Date: 2025-01-27
    Description: Use unsharp masking to enhance edge definition
    """
    # Convert to float for processing
    image_float = image.astype(np.float64) / 255.0
    
    # Apply unsharp mask
    sharpened = unsharp_mask(image_float, radius=radius, amount=amount)
    
    # Convert back to uint8
    sharpened = (sharpened * 255).astype(np.uint8)
    
    return sharpened

def enhance_curves(image, erode_size=2, dilate_size=2):
    """
    Step 4: Enhance and clean curves
    Date: 2025-01-27
    Description: Apply erosion-dilation and morphological closing
    """
    # Erode to thin curves
    erode_kernel = disk(erode_size)
    eroded = erosion(image, erode_kernel)
    
    # Dilate to restore thickness
    dilate_kernel = disk(dilate_size)
    dilated = dilation(eroded, dilate_kernel)
    
    # Morphological closing to fill gaps
    close_kernel = disk(3)
    closed = closing(dilated, close_kernel)
    
    return closed

def create_skeleton(image, remove_hair_length=1, prune_skeleton=False):
    """
    Create 1-pixel skeleton using sknw
    Date: 2025-01-27
    Description: Generate skeleton and optionally remove hair
    """
    # Convert to binary if needed
    if image.max() > 1:
        binary = (image > 128).astype(np.uint8)
    else:
        binary = image.astype(np.uint8)
    
    # Create skeleton using sknw
    skeleton_graph = sknw.build_sknw(binary)
    
    # Convert graph back to binary image for visualization
    skeleton_image = np.zeros_like(binary)
    for edge in skeleton_graph.edges():
        # Get coordinates of edge endpoints
        start_node = skeleton_graph.nodes[edge[0]]
        end_node = skeleton_graph.nodes[edge[1]]
        
        # Draw line between nodes
        start_coords = (int(start_node['o'][1]), int(start_node['o'][0]))
        end_coords = (int(end_node['o'][1]), int(end_node['o'][0]))
        
        # Use OpenCV to draw line
        cv2.line(skeleton_image, start_coords, end_coords, 255, 1)
    
    # Remove hair if requested (simplified approach)
    if remove_hair_length > 0:
        # Remove small connected components
        skeleton_clean = morphology.remove_small_objects(
            skeleton_image > 0, min_size=remove_hair_length + 1
        ).astype(np.uint8) * 255
    else:
        skeleton_clean = skeleton_image
    
    return skeleton_clean, skeleton_graph

def analyze_topology(skeleton_graph):
    """
    Analyze skeleton topology using networkx
    Date: 2025-01-27
    Description: Analyze the skeleton graph structure
    """
    # Get basic graph properties
    num_nodes = skeleton_graph.number_of_nodes()
    num_edges = skeleton_graph.number_of_edges()
    
    # Find connected components (potential curves)
    components = list(nx.connected_components(skeleton_graph))
    num_components = len(components)
    
    return {
        'graph': skeleton_graph,
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'num_components': num_components,
        'components': components
    }

def main():
    st.title("🔬 AtPoE Drawing Analysis Interface")
    st.markdown("Analyze monochromatic drawings with concentric curves")
    
    # Sidebar for parameters
    st.sidebar.header("Parameters")
    
    # File selection
    drawings_path = Path("drawings")
    if drawings_path.exists():
        image_files = list(drawings_path.glob("*.png")) + list(drawings_path.glob("*.jpg")) + list(drawings_path.glob("*.jpeg"))
        if image_files:
            selected_file = st.sidebar.selectbox(
                "Select Image",
                [f.name for f in image_files],
                index=0
            )
        else:
            st.sidebar.error("No images found in drawings folder")
            return
    else:
        st.sidebar.error("Drawings folder not found")
        return
    
    # Load image
    image = load_image_from_drawings_folder(selected_file)
    if image is None:
        return
    
    # Display original image
    st.subheader("Original Image")
    st.image(image, caption=f"Original: {selected_file}", use_container_width=True)
    
    # Preprocessing parameters
    st.sidebar.subheader("Preprocessing Parameters")
    
    # Step 1: Monochromatization
    threshold = st.sidebar.slider("Binary Threshold", 0, 255, 128, key="threshold")
    
    # Step 2: Noise removal
    noise_kernel = st.sidebar.slider("Noise Removal Kernel", 1, 10, 3, key="noise_kernel")
    
    # Step 3: Sharpening
    sharpen_radius = st.sidebar.slider("Sharpen Radius", 0.1, 5.0, 1.0, key="sharpen_radius")
    sharpen_amount = st.sidebar.slider("Sharpen Amount", 0.1, 3.0, 1.0, key="sharpen_amount")
    
    # Step 4: Curve enhancement
    erode_size = st.sidebar.slider("Erode Size", 1, 5, 2, key="erode_size")
    dilate_size = st.sidebar.slider("Dilate Size", 1, 5, 2, key="dilate_size")
    
    # Skeletonization parameters
    st.sidebar.subheader("Skeletonization Parameters")
    remove_hair_length = st.sidebar.slider("Remove Hair Length", 0, 10, 1, key="hair_length")
    prune_skeleton = st.sidebar.checkbox("Prune Skeleton", value=False, key="prune")
    
    # Process button
    if st.sidebar.button("Process Image", type="primary"):
        # Step 1: Monochromatization
        st.subheader("Step 1: Monochromatization")
        binary = monochromatize_image(image, threshold)
        st.image(binary, caption="Binary Image", use_container_width=True)
        
        # Step 2: Noise removal
        st.subheader("Step 2: Noise Removal")
        denoised = remove_noise(binary, noise_kernel)
        st.image(denoised, caption="Noise Removed", use_container_width=True)
        
        # Step 3: Sharpening
        st.subheader("Step 3: Sharpening")
        sharpened = sharpen_image(denoised, sharpen_radius, sharpen_amount)
        st.image(sharpened, caption="Sharpened", use_container_width=True)
        
        # Step 4: Curve enhancement
        st.subheader("Step 4: Curve Enhancement")
        enhanced = enhance_curves(sharpened, erode_size, dilate_size)
        st.image(enhanced, caption="Curves Enhanced", use_container_width=True)
        
        # Skeletonization
        st.subheader("Skeletonization")
        skeleton, skeleton_graph = create_skeleton(enhanced, remove_hair_length, prune_skeleton)
        st.image(skeleton, caption="1-Pixel Skeleton", use_container_width=True)
        
        # Topology analysis
        st.subheader("Topology Analysis")
        topology = analyze_topology(skeleton_graph)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nodes", topology['num_nodes'])
        with col2:
            st.metric("Edges", topology['num_edges'])
        with col3:
            st.metric("Components", topology['num_components'])
        
        # Show code for each operation
        st.subheader("Code Used for Each Operation")
        
        with st.expander("Step 1: Monochromatization Code"):
            st.code("""
def monochromatize_image(image, threshold=128):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    binary = (gray < threshold).astype(np.uint8) * 255
    return binary
            """, language="python")
        
        with st.expander("Step 2: Noise Removal Code"):
            st.code("""
def remove_noise(image, kernel_size=3):
    kernel = disk(kernel_size)
    opened = opening(image, kernel)  # Remove small noise
    closed = closing(opened, kernel)  # Fill small gaps
    return closed
            """, language="python")
        
        with st.expander("Step 3: Sharpening Code"):
            st.code("""
def sharpen_image(image, radius=1, amount=1):
    image_float = image.astype(np.float64) / 255.0
    sharpened = unsharp_mask(image_float, radius=radius, amount=amount)
    return (sharpened * 255).astype(np.uint8)
            """, language="python")
        
        with st.expander("Step 4: Curve Enhancement Code"):
            st.code("""
def enhance_curves(image, erode_size=2, dilate_size=2):
    erode_kernel = disk(erode_size)
    eroded = erosion(image, erode_kernel)
    
    dilate_kernel = disk(dilate_size)
    dilated = dilation(eroded, dilate_kernel)
    
    close_kernel = disk(3)
    closed = closing(dilated, close_kernel)
    return closed
            """, language="python")
        
        with st.expander("Skeletonization Code"):
            st.code("""
def create_skeleton(image, remove_hair_length=1, prune_skeleton=False):
    binary = (image > 128).astype(np.uint8) if image.max() > 1 else image.astype(np.uint8)
    skeleton = sknw.build_sknw(binary)
    
    if remove_hair_length > 0:
        skeleton_clean = morphology.remove_small_objects(
            skeleton, min_size=remove_hair_length + 1
        )
    else:
        skeleton_clean = skeleton
    
    return skeleton_clean, skeleton
            """, language="python")

if __name__ == "__main__":
    main()
