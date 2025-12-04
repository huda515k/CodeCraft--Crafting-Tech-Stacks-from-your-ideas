# frontend_generator/models.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class ComponentType(str, Enum):
    """Types of UI components"""
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    HEADER = "header"
    FOOTER = "footer"
    NAVBAR = "navbar"
    SIDEBAR = "sidebar"
    MODAL = "modal"
    DROPDOWN = "dropdown"
    FORM = "form"
    LIST = "list"
    LIST_ITEM = "list-item"  # For list items
    GRID = "grid"
    CONTAINER = "container"
    TEXT = "text"
    PARAGRAPH = "paragraph"  # Added for paragraphs
    IMAGE = "image"
    LINK = "link"
    ICON = "icon"
    ICON_WRAPPER = "icon-wrapper"  # Added for icon wrappers
    LOGO = "logo"  # Added for logos
    LOGO_GROUP = "logo-group"  # Added for logo groups
    HEADING = "heading"  # Added for headings (h1, h2, etc.)
    HEADING_GROUP = "heading-group"  # Added for heading groups
    H1 = "h1"  # Added for h1 elements
    H2 = "h2"  # Added for h2 elements
    H3 = "h3"  # Added for h3 elements
    SCREEN = "screen"  # Added for screen/container
    BLOCK = "block"  # Added for block/container elements
    DIVIDER = "divider"
    BADGE = "badge"
    AVATAR = "avatar"
    AVATAR_ICON = "avatar-icon"  # Added for avatar icons
    TABS = "tabs"
    ACCORDION = "accordion"
    CAROUSEL = "carousel"
    CUSTOM = "custom"

class LayoutType(str, Enum):
    """Layout types"""
    FLEX = "flex"
    GRID = "grid"
    BLOCK = "block"
    INLINE = "inline"
    RELATIVE = "relative"
    ABSOLUTE = "absolute"
    FIXED = "fixed"

class Position(BaseModel):
    """Component position information"""
    x: Optional[Union[float, str]] = Field(default=None, description="X coordinate")
    y: Optional[Union[float, str]] = Field(default=None, description="Y coordinate")
    width: Optional[Union[float, str]] = Field(default=None, description="Width (pixels, percentage, viewport units, or CSS calc)")
    height: Optional[Union[float, str]] = Field(default=None, description="Height (pixels, percentage, viewport units, or CSS calc)")
    
    @field_validator('x', 'y', 'width', 'height', mode='before')
    @classmethod
    def parse_position_value(cls, v):
        """Handle both numeric and CSS string values for position dimensions"""
        if v is None:
            return None
        # If it's already a string (CSS value like '100vh', 'auto', 'calc(...)', '100%'), return as-is
        if isinstance(v, str):
            return v
        # If it's a number, return as float
        if isinstance(v, (int, float)):
            return float(v)
        # Try to convert to string as fallback
        return str(v)

class Color(BaseModel):
    """Color information"""
    hex: Optional[str] = Field(default=None, description="Hex color code")
    rgb: Optional[str] = Field(default=None, description="RGB color")
    rgba: Optional[str] = Field(default=None, description="RGBA color")
    name: Optional[str] = Field(default=None, description="Color name if known")

class Typography(BaseModel):
    """Typography information"""
    font_family: Optional[str] = Field(default=None, description="Font family")
    font_size: Optional[str] = Field(default=None, description="Font size")
    font_weight: Optional[str] = Field(default=None, description="Font weight")
    line_height: Optional[str] = Field(default=None, description="Line height")
    color: Optional[Color] = Field(default=None, description="Text color")
    text_align: Optional[str] = Field(default=None, description="Text alignment")

class Spacing(BaseModel):
    """Spacing information"""
    margin: Optional[str] = Field(default=None, description="Margin")
    padding: Optional[str] = Field(default=None, description="Padding")
    gap: Optional[str] = Field(default=None, description="Gap for flex/grid")

class Border(BaseModel):
    """Border information"""
    width: Optional[str] = Field(default=None, description="Border width")
    style: Optional[str] = Field(default=None, description="Border style")
    color: Optional[Color] = Field(default=None, description="Border color")
    radius: Optional[str] = Field(default=None, description="Border radius")

class Shadow(BaseModel):
    """Shadow/Box shadow information"""
    x: Optional[Union[str, int, float]] = Field(default=None, description="X offset")
    y: Optional[Union[str, int, float]] = Field(default=None, description="Y offset")
    blur: Optional[Union[str, int, float]] = Field(default=None, description="Blur radius")
    spread: Optional[Union[str, int, float]] = Field(default=None, description="Spread radius")
    color: Optional[Union[Color, str]] = Field(default=None, description="Shadow color")
    
    @field_validator('x', 'y', 'blur', 'spread', mode='before')
    @classmethod
    def parse_shadow_dimension(cls, v):
        """Convert shadow dimensions from int/float to string with px"""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, (int, float)):
            return f"{v}px"
        return str(v)
    
    @field_validator('color', mode='before')
    @classmethod
    def parse_shadow_color(cls, v):
        """Parse shadow color from string, dict, or Color object"""
        if v is None:
            return None
        if isinstance(v, Color):
            return v
        if isinstance(v, dict):
            return Color(**v)
        if isinstance(v, str):
            # Handle color strings like 'rgba(0, 0, 0, 0.1)', 'rgb(255, 255, 255)', '#ffffff'
            if v.startswith('rgba'):
                return Color(rgba=v)
            elif v.startswith('rgb'):
                return Color(rgb=v)
            elif v.startswith('#'):
                return Color(hex=v)
            else:
                # Try as hex or rgb
                if '#' in v:
                    return Color(hex=v)
                elif 'rgb' in v.lower():
                    return Color(rgb=v)
                else:
                    return Color(hex=v)  # Default to hex
        return v

class Style(BaseModel):
    """Complete style information for a component"""
    position: Optional[Position] = Field(default=None, description="Position information")
    background_color: Optional[Color] = Field(default=None, description="Background color")
    typography: Optional[Typography] = Field(default=None, description="Typography settings")
    spacing: Optional[Spacing] = Field(default=None, description="Spacing settings")
    border: Optional[Union[Border, str, Dict[str, Any]]] = Field(default=None, description="Border settings")
    shadow: Optional[Shadow] = Field(default=None, description="Shadow settings")
    layout_type: Optional[LayoutType] = Field(default=None, description="Layout type")
    width: Optional[Union[str, int, float]] = Field(default=None, description="Width")
    height: Optional[Union[str, int, float]] = Field(default=None, description="Height")
    display: Optional[str] = Field(default=None, description="Display type")
    flex_direction: Optional[str] = Field(default=None, description="Flex direction")
    justify_content: Optional[str] = Field(default=None, description="Justify content")
    align_items: Optional[str] = Field(default=None, description="Align items")
    grid_template_columns: Optional[str] = Field(default=None, description="Grid columns")
    grid_template_rows: Optional[str] = Field(default=None, description="Grid rows")
    z_index: Optional[int] = Field(default=None, description="Z-index")
    opacity: Optional[float] = Field(default=None, description="Opacity")
    
    @field_validator('border', mode='before')
    @classmethod
    def parse_border(cls, v):
        """Parse border from string, dict, or Border object"""
        if v is None:
            return None
        if isinstance(v, Border):
            return v
        if isinstance(v, dict):
            return Border(**v)
        if isinstance(v, str):
            # Parse CSS border string like "1px solid #ffffff" or "1px solid"
            import re
            parts = v.split()
            border_width = parts[0] if len(parts) > 0 else None
            border_style = parts[1] if len(parts) > 1 else None
            border_color = None
            if len(parts) >= 3:
                # Color might be hex, rgb, or rgba
                color_str = parts[2]
                if color_str.startswith('#'):
                    border_color = Color(hex=color_str)
                elif color_str.startswith('rgb'):
                    border_color = Color(rgb=color_str)
                else:
                    # Try as hex or rgb
                    border_color = Color(hex=color_str) if '#' in color_str else Color(rgb=color_str)
            
            return Border(
                width=border_width,
                style=border_style,
                color=border_color
            )
        return v
    
    @field_validator('layout_type', mode='before')
    @classmethod
    def normalize_style_layout_type(cls, v):
        """Normalize layout type for style field"""
        if v is None:
            return None
        if isinstance(v, LayoutType):
            return v
        
        # Convert to string and normalize
        original_type = str(v)
        type_str = original_type.lower().strip()
        
        # Handle complex strings like "graphic-design/absolute-positioning"
        layout_keywords = {
            'flex': LayoutType.FLEX,
            'flexbox': LayoutType.FLEX,
            'grid': LayoutType.GRID,
            'block': LayoutType.BLOCK,
            'inline': LayoutType.INLINE,
            'relative': LayoutType.RELATIVE,
            'absolute': LayoutType.ABSOLUTE,
            'fixed': LayoutType.FIXED,
        }
        
        # Check if any keyword is in the string
        for keyword, enum_value in layout_keywords.items():
            if keyword in type_str:
                return enum_value
        
        # Try direct match
        for enum_value in LayoutType:
            if enum_value.value == type_str:
                return enum_value
        
        # Try case-insensitive match
        for enum_value in LayoutType:
            if enum_value.value.lower() == type_str.lower():
                return enum_value
        
        # Default to None if not found (since it's optional)
        print(f"Warning: Style layout type '{original_type}' not recognized, using None")
        return None
    
    @field_validator('width', 'height', mode='before')
    @classmethod
    def parse_dimension(cls, v):
        """Convert width/height from int/float to string with px"""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return f"{v}px"
        if isinstance(v, str):
            return v
        return str(v)

class ComponentProperty(BaseModel):
    """Property definition for a component"""
    name: str = Field(..., description="Property name")
    type: str = Field(..., description="Property type (string, number, boolean, etc.)")
    required: bool = Field(default=False, description="Whether property is required")
    default_value: Optional[Any] = Field(default=None, description="Default value")
    
    @field_validator('type', mode='before')
    @classmethod
    def normalize_property_type(cls, v):
        """Handle cases where Gemini returns 'value' instead of 'type'"""
        if isinstance(v, dict):
            # If it's a dict, try to extract type or value
            return v.get('type') or v.get('value') or 'string'
        return v or 'string'

class UIComponent(BaseModel):
    """UI Component definition"""
    id: str = Field(..., description="Unique component identifier")
    name: str = Field(..., description="Component name")
    type: ComponentType = Field(..., description="Component type")
    position: Optional[Position] = Field(default=None, description="Component position (can also be in style.position)")
    style: Optional[Style] = Field(default=None, description="Component style")
    children: List[str] = Field(default_factory=list, description="Child component IDs")
    parent_id: Optional[str] = Field(default=None, description="Parent component ID")
    properties: List[ComponentProperty] = Field(default_factory=list, description="Component properties")
    text_content: Optional[str] = Field(default=None, description="Text content if text component")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    
    @field_validator('type', mode='before')
    @classmethod
    def normalize_component_type(cls, v):
        """Normalize component type strings to enum values"""
        if isinstance(v, ComponentType):
            return v
        
        # Convert to string and normalize
        original_type = str(v)
        type_str = original_type.lower().strip()
        
        # Map common variations (check before replacing underscores)
        type_mapping = {
            'list_item': 'list-item',
            'logo_group': 'logo-group',
            'heading_group': 'heading-group',
            'icon_wrapper': 'icon-wrapper',
            'avatar_icon': 'avatar-icon',
            'h1': 'h1',
            'h2': 'h2',
            'h3': 'h3',
            'h4': 'h4',
            'h5': 'h5',
            'h6': 'h6',
            'p': 'paragraph',
            'para': 'paragraph',
        }
        
        # Check mapping first (with underscores)
        if type_str in type_mapping:
            type_str = type_mapping[type_str]
        else:
            # Handle underscores -> hyphens if not in mapping
            type_str = type_str.replace('_', '-')
        
        # Try to find matching enum value
        for enum_value in ComponentType:
            if enum_value.value == type_str:
                return enum_value
        
        # If not found, try case-insensitive match
        for enum_value in ComponentType:
            if enum_value.value.lower() == type_str.lower():
                return enum_value
        
        # Default to custom if not found
        print(f"Warning: Component type '{original_type}' not recognized, using 'custom'")
        return ComponentType.CUSTOM
    
    @field_validator('children', mode='before')
    @classmethod
    def normalize_children(cls, v):
        """Normalize children field - extract IDs from nested objects if needed"""
        if v is None:
            return []
        if not isinstance(v, list):
            return []
        
        normalized = []
        for child in v:
            if isinstance(child, str):
                # Already a string ID, use as-is
                normalized.append(child)
            elif isinstance(child, dict):
                # Extract ID from nested component object
                child_id = child.get('id')
                if child_id:
                    normalized.append(str(child_id))
                else:
                    # If no ID, try to use name or generate one
                    child_name = child.get('name')
                    if child_name:
                        print(f"Warning: Child component missing 'id', using 'name' as fallback: {child_name}")
                        normalized.append(str(child_name))
            else:
                # Try to convert to string
                normalized.append(str(child))
        
        return normalized

class LayoutStructure(BaseModel):
    """Layout structure information"""
    type: LayoutType = Field(..., description="Layout type")
    width: Optional[str] = Field(default=None, description="Overall width")
    height: Optional[str] = Field(default=None, description="Overall height")
    max_width: Optional[str] = Field(default=None, description="Max width")
    background_color: Optional[Color] = Field(default=None, description="Background color")
    padding: Optional[str] = Field(default=None, description="Padding")
    
    @field_validator('type', mode='before')
    @classmethod
    def normalize_layout_type(cls, v):
        """Normalize layout type strings to enum values"""
        if isinstance(v, LayoutType):
            return v
        
        # Convert to string and normalize
        original_type = str(v)
        type_str = original_type.lower().strip()
        
        # Handle complex strings like "graphic-design/absolute-positioning"
        # Extract the actual layout type from the string
        layout_keywords = {
            'flex': LayoutType.FLEX,
            'flexbox': LayoutType.FLEX,
            'grid': LayoutType.GRID,
            'block': LayoutType.BLOCK,
            'inline': LayoutType.INLINE,
            'relative': LayoutType.RELATIVE,
            'absolute': LayoutType.ABSOLUTE,
            'fixed': LayoutType.FIXED,
        }
        
        # Check if any keyword is in the string
        for keyword, enum_value in layout_keywords.items():
            if keyword in type_str:
                return enum_value
        
        # Try direct match
        for enum_value in LayoutType:
            if enum_value.value == type_str:
                return enum_value
        
        # Try case-insensitive match
        for enum_value in LayoutType:
            if enum_value.value.lower() == type_str.lower():
                return enum_value
        
        # Default to block if not found
        print(f"Warning: Layout type '{original_type}' not recognized, using 'block'")
        return LayoutType.BLOCK

class ColorPalette(BaseModel):
    """Extracted color palette"""
    primary: Optional[Color] = Field(default=None, description="Primary color")
    secondary: Optional[Color] = Field(default=None, description="Secondary color")
    accent: Optional[Color] = Field(default=None, description="Accent color")
    background: Optional[Color] = Field(default=None, description="Background color")
    text: Optional[Color] = Field(default=None, description="Text color")
    border: Optional[Color] = Field(default=None, description="Border color")
    custom: List[Color] = Field(default_factory=list, description="Custom colors")

class UIAnalysis(BaseModel):
    """Complete UI analysis result"""
    project_name: Optional[str] = Field(default=None, description="Project name")
    layout: Optional[LayoutStructure] = Field(default=None, description="Layout structure")
    components: List[UIComponent] = Field(default_factory=list, description="List of components")
    color_palette: Optional[ColorPalette] = Field(default=None, description="Color palette")
    typography: Optional[Typography] = Field(default=None, description="Default typography")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic config to allow partial data"""
        extra = "allow"  # Allow extra fields that aren't in the model

class UIProcessingRequest(BaseModel):
    """Request model for UI processing"""
    image_data: Optional[str] = Field(default=None, description="Base64 encoded image data")
    image_url: Optional[str] = Field(default=None, description="URL to the UI image")
    additional_context: Optional[str] = Field(default=None, description="Additional context or instructions")
    framework: str = Field(default="react", description="Target framework (react, vue, etc.)")
    styling_approach: str = Field(default="css-modules", description="Styling approach (css-modules, tailwind, styled-components)")

class UIProcessingResponse(BaseModel):
    """Response model for UI processing"""
    success: bool = Field(..., description="Whether processing was successful")
    ui_analysis: Optional[UIAnalysis] = Field(default=None, description="Extracted UI analysis")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    processing_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Processing metadata")

class CodeGenerationRequest(BaseModel):
    """Request for code generation"""
    ui_analysis: UIAnalysis = Field(..., description="UI analysis result")
    framework: str = Field(default="react", description="Target framework")
    styling_approach: str = Field(default="css-modules", description="Styling approach")
    include_typescript: bool = Field(default=True, description="Include TypeScript")
    component_structure: str = Field(default="functional", description="Component structure (functional, class)")

class GeneratedProject(BaseModel):
    """Generated project information"""
    project_name: str = Field(..., description="Project name")
    files: Dict[str, str] = Field(..., description="Dictionary of file paths to content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Project metadata")

