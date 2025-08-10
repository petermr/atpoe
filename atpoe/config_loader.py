#!/usr/bin/env python3
"""
Configuration loader for AtPoE (Admitting the Possibilities of Error).
Provides validation and type checking for configuration settings.
"""

import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InitialCircleConfig:
    """Configuration for the initial circle."""
    color: str
    width: int
    style: str
    visible: bool
    
    def __post_init__(self):
        """Validate initial circle configuration."""
        if self.width < 1 or self.width > 20:
            raise ValueError("Initial circle width must be between 1 and 20")
        if self.style not in ["solid", "dashed", "dotted", "dash-dot"]:
            raise ValueError("Initial circle style must be one of: solid, dashed, dotted, dash-dot")


@dataclass
class BackgroundConfig:
    """Configuration for background settings."""
    color: str
    fill_enabled: bool


@dataclass
class AntialiasingConfig:
    """Configuration for antialiasing settings."""
    enabled: bool
    quality: str
    
    def __post_init__(self):
        """Validate antialiasing configuration."""
        if self.quality not in ["low", "medium", "high"]:
            raise ValueError("Antialiasing quality must be one of: low, medium, high")


@dataclass
class SegmentLengthConfig:
    """Configuration for segment length settings."""
    scale_factor: float
    min_value: int
    max_value: int
    
    def __post_init__(self):
        """Validate segment length configuration."""
        if self.scale_factor <= 0 or self.scale_factor > 10:
            raise ValueError("Scale factor must be between 0 and 10")
        if self.min_value < 1 or self.max_value > 100:
            raise ValueError("Segment length min/max values must be between 1 and 100")
        if self.min_value >= self.max_value:
            raise ValueError("Min value must be less than max value")


@dataclass
class CurveGenerationConfig:
    """Configuration for curve generation settings."""
    tangent_method: str
    sharp_point_threshold: float
    linear_extension_length: float
    parallel_tracking_distance: float
    
    def __post_init__(self):
        """Validate curve generation configuration."""
        if self.tangent_method not in ["3_point_average", "simple", "weighted"]:
            raise ValueError("Tangent method must be one of: 3_point_average, simple, weighted")
        if self.sharp_point_threshold < 0 or self.sharp_point_threshold > 180:
            raise ValueError("Sharp point threshold must be between 0 and 180 degrees")
        if self.linear_extension_length <= 0 or self.linear_extension_length > 50:
            raise ValueError("Linear extension length must be between 0 and 50 pixels")
        if self.parallel_tracking_distance <= 0 or self.parallel_tracking_distance > 50:
            raise ValueError("Parallel tracking distance must be between 0 and 50 pixels")


@dataclass
class DrawingConfig:
    """Configuration for drawing settings."""
    line_join: str
    line_cap: str
    
    def __post_init__(self):
        """Validate drawing configuration."""
        if self.line_join not in ["round", "bevel", "miter"]:
            raise ValueError("Line join must be one of: round, bevel, miter")
        if self.line_cap not in ["round", "square", "butt"]:
            raise ValueError("Line cap must be one of: round, square, butt")


@dataclass
class GraphicsBundleConfig:
    """Configuration for graphics bundle settings."""
    default_bundle: str
    save_custom_bundles: bool
    bundle_storage_path: str


@dataclass
class OutputConfig:
    """Configuration for output settings."""
    format: str
    quality: int
    dpi: int
    
    def __post_init__(self):
        """Validate output configuration."""
        if self.format not in ["png", "jpg", "svg"]:
            raise ValueError("Output format must be one of: png, jpg, svg")
        if self.quality < 1 or self.quality > 100:
            raise ValueError("Output quality must be between 1 and 100")
        if self.dpi < 72 or self.dpi > 600:
            raise ValueError("DPI must be between 72 and 600")


class Config:
    """Main configuration class with validation."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration from YAML file."""
        self.config_path = config_path
        self._load_config()
    
    def _load_config(self):
        """Load and validate configuration from YAML file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        # Load and validate each section
        self.initial_circle = InitialCircleConfig(**config_data.get('initial_circle', {}))
        self.background = BackgroundConfig(**config_data.get('background', {}))
        self.antialiasing = AntialiasingConfig(**config_data.get('antialiasing', {}))
        self.segment_length = SegmentLengthConfig(**config_data.get('segment_length', {}))
        self.curve_generation = CurveGenerationConfig(**config_data.get('curve_generation', {}))
        self.drawing = DrawingConfig(**config_data.get('drawing', {}))
        self.graphics_bundle = GraphicsBundleConfig(**config_data.get('graphics_bundle', {}))
        self.output = OutputConfig(**config_data.get('output', {}))
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
    
    def get_initial_circle_color(self) -> str:
        """Get initial circle color."""
        return self.initial_circle.color
    
    def get_initial_circle_width(self) -> int:
        """Get initial circle width."""
        return self.initial_circle.width
    
    def get_initial_circle_style(self) -> str:
        """Get initial circle style."""
        return self.initial_circle.style
    
    def is_initial_circle_visible(self) -> bool:
        """Check if initial circle should be visible."""
        return self.initial_circle.visible
    
    def get_background_color(self) -> str:
        """Get background color."""
        return self.background.color
    
    def is_background_fill_enabled(self) -> bool:
        """Check if background fill is enabled."""
        return self.background.fill_enabled
    
    def is_antialiasing_enabled(self) -> bool:
        """Check if antialiasing is enabled."""
        return self.antialiasing.enabled
    
    def get_antialiasing_quality(self) -> str:
        """Get antialiasing quality."""
        return self.antialiasing.quality
    
    def get_segment_length_scale_factor(self) -> float:
        """Get segment length scale factor."""
        return self.segment_length.scale_factor
    
    def get_segment_length_range(self) -> tuple:
        """Get segment length min/max range."""
        return (self.segment_length.min_value, self.segment_length.max_value)
    
    def get_tangent_method(self) -> str:
        """Get tangent calculation method."""
        return self.curve_generation.tangent_method
    
    def get_sharp_point_threshold(self) -> float:
        """Get sharp point detection threshold in degrees."""
        return self.curve_generation.sharp_point_threshold
    
    def get_linear_extension_length(self) -> float:
        """Get linear extension length for convex sharp points."""
        return self.curve_generation.linear_extension_length
    
    def get_parallel_tracking_distance(self) -> float:
        """Get parallel tracking distance for concave sharp points."""
        return self.curve_generation.parallel_tracking_distance
    
    def get_drawing_line_join(self) -> str:
        """Get line join style."""
        return self.drawing.line_join
    
    def get_drawing_line_cap(self) -> str:
        """Get line cap style."""
        return self.drawing.line_cap
    
    def get_default_bundle_name(self) -> str:
        """Get default graphics bundle name."""
        return self.graphics_bundle.default_bundle
    
    def should_save_custom_bundles(self) -> bool:
        """Check if custom bundles should be saved."""
        return self.graphics_bundle.save_custom_bundles
    
    def get_bundle_storage_path(self) -> str:
        """Get bundle storage path."""
        return self.graphics_bundle.bundle_storage_path
    
    def get_output_format(self) -> str:
        """Get output format."""
        return self.output.format
    
    def get_output_quality(self) -> int:
        """Get output quality."""
        return self.output.quality
    
    def get_output_dpi(self) -> int:
        """Get output DPI."""
        return self.output.dpi


def load_config(config_path: str = "config.yaml") -> Config:
    """Convenience function to load configuration."""
    return Config(config_path)


# Default configuration values for fallback
DEFAULT_CONFIG = {
    'initial_circle': {
        'color': 'red',
        'width': 3,
        'style': 'solid',
        'visible': True
    },
    'background': {
        'color': 'white',
        'fill_enabled': True
    },
    'antialiasing': {
        'enabled': True,
        'quality': 'high'
    },
    'segment_length': {
        'scale_factor': 1.0,
        'min_value': 3,
        'max_value': 30
    },
    'drawing': {
        'line_join': 'round',
        'line_cap': 'round'
    },
    'graphics_bundle': {
        'default_bundle': 'Classic Black',
        'save_custom_bundles': True,
        'bundle_storage_path': 'custom_bundles/'
    },
    'output': {
        'format': 'png',
        'quality': 95,
        'dpi': 300
    }
}
