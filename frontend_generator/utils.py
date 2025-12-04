# frontend_generator/utils.py

from PIL import Image
import base64
from io import BytesIO
from typing import Tuple, Optional

def validate_image_format(image_data: str) -> bool:
    """
    Validate if the base64 image data is in a supported format
    """
    try:
        image_bytes = base64.b64decode(image_data)
        with Image.open(BytesIO(image_bytes)) as img:
            format_name = img.format
            return format_name in ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP']
    except Exception:
        return False

def enhance_image_for_analysis(image_data: str) -> str:
    """
    Enhance image for better AI analysis
    Currently returns the same image, but can be extended with:
    - Contrast adjustment
    - Noise reduction
    - Resolution upscaling
    """
    # For now, just return the original image
    # Future: Add image enhancement algorithms
    return image_data

def get_image_dimensions(image_data: str) -> Optional[Tuple[int, int]]:
    """
    Get image dimensions (width, height)
    """
    try:
        image_bytes = base64.b64decode(image_data)
        with Image.open(BytesIO(image_bytes)) as img:
            return img.size  # Returns (width, height)
    except Exception:
        return None

def sanitize_component_name(name: str) -> str:
    """
    Sanitize component name for use in React component names
    """
    import re
    # Remove special characters, keep alphanumeric and spaces
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    # Capitalize first letter of each word
    words = name.split()
    return ''.join(word.capitalize() for word in words) if words else "Component"

def css_value_to_pixels(value: str) -> Optional[float]:
    """
    Convert CSS value to pixels
    Supports: px, rem, em, %
    """
    if not value:
        return None
    
    try:
        value = value.strip().lower()
        
        if value.endswith('px'):
            return float(value[:-2])
        elif value.endswith('rem'):
            # Assume 1rem = 16px (common default)
            return float(value[:-3]) * 16
        elif value.endswith('em'):
            # Assume 1em = 16px (common default)
            return float(value[:-2]) * 16
        elif value.endswith('%'):
            # Can't convert % to pixels without context
            return None
        else:
            # Try to parse as number (assumes pixels)
            return float(value)
    except (ValueError, AttributeError):
        return None

def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
    """
    Convert hex color to RGB tuple
    """
    if not hex_color:
        return None
    
    hex_color = hex_color.lstrip('#')
    
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return None

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB to hex color
    """
    return f"#{r:02x}{g:02x}{b:02x}"

