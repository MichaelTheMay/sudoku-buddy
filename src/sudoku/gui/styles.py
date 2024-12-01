"""
Define styles and theme constants for the GUI.
Centralized management of colors, fonts, dimensions, and themes.
"""
from typing import Any, Dict, Tuple

# Base color palette
COLORS = {
    # Primary colors
    "primary": {
        "main": "#0078d4",
        "light": "#e6f7ff",
        "dark": "#005a9e",
        "contrast": "#ffffff",
    },
    # Semantic colors
    "semantic": {
        "success": "#28a745",
        "error": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8",
    },
    # Neutral colors
    "neutral": {
        "background": "#f0f0f0",
        "surface": "#ffffff",
        "text": {"primary": "#333333", "secondary": "#666666", "disabled": "#999999"},
        "border": {"light": "#e0e0e0", "medium": "#cccccc", "dark": "#333333"},
    },
    # State colors
    "state": {
        "hover": {"light": "#f5f5f5", "medium": "#e0e0e0", "dark": "#005a9e"},
        "focus": "#cceeff",
        "active": "#005a9e",
        "disabled": "#cccccc",
    },
}

# Font definitions
FONTS = {
    "family": {"primary": "Segoe UI", "monospace": "Consolas"},
    "size": {"xs": 8, "sm": 10, "md": 12, "lg": 14, "xl": 18, "xxl": 24},
    "weight": {"normal": "normal", "bold": "bold"},
}

# Dimension measurements
DIMENSIONS = {
    "spacing": {"xs": 2, "sm": 4, "md": 8, "lg": 12, "xl": 16},
    "border": {"thin": 1, "medium": 2, "thick": 3},
    "cell": {"width": 2, "size": 40},
    "padding": {"cell": 0, "button": 8, "container": 16},
}


def create_font(family: str, size: int, weight: str = "normal") -> Tuple[str, int, str]:
    """Create a font tuple with the specified properties."""
    return (FONTS["family"][family], FONTS["size"][size], FONTS["weight"][weight])


# Complete GUI styles mapping
GUI_STYLES = {
    "colors": {
        # Basic colors
        "background": COLORS["neutral"]["background"],
        "cell_bg": COLORS["neutral"]["surface"],
        "cell_text": COLORS["neutral"]["text"]["primary"],
        "button_bg": COLORS["primary"]["main"],
        "button_hover": COLORS["primary"]["dark"],
        # Highlight colors
        "highlight": COLORS["primary"]["light"],
        "focus": COLORS["state"]["focus"],
        "box_highlight": "#e8e8e8",  # Specific to Sudoku box highlighting
        # Border colors
        "border": COLORS["neutral"]["border"]["dark"],
        # State colors
        "readonly": COLORS["primary"]["main"],
        "error": COLORS["semantic"]["error"],
        "success": COLORS["semantic"]["success"],
        "warning": COLORS["semantic"]["warning"],
    },
    "fonts": {
        "cell": create_font("primary", "xl"),
        "button": create_font("primary", "md"),
        "label": create_font("primary", "md"),
        "small": create_font("primary", "sm"),
    },
    "dimensions": {
        "cell_width": DIMENSIONS["cell"]["width"],
        "cell_size": DIMENSIONS["cell"]["size"],
        "border_thick": DIMENSIONS["border"]["thick"],
        "border_thin": DIMENSIONS["border"]["thin"],
        "padding": DIMENSIONS["padding"]["container"],
    },
}


def get_theme_variant(theme_name: str = "default") -> Dict[str, Any]:
    """Get a specific theme variant of the GUI styles."""
    # Example of how to create theme variants
    themes = {
        "default": GUI_STYLES,
        "dark": {
            **GUI_STYLES,
            "colors": {
                **GUI_STYLES["colors"],
                "background": "#1e1e1e",
                "cell_bg": "#2d2d2d",
                "cell_text": "#ffffff",
                # Add more color overrides for dark theme
            },
        },
        "high_contrast": {
            **GUI_STYLES,
            "colors": {
                **GUI_STYLES["colors"],
                "background": "#ffffff",
                "cell_bg": "#ffffff",
                "cell_text": "#000000",
                "button_bg": "#000000",
                "button_hover": "#333333",
                # Add more color overrides for high contrast theme
            },
        },
    }
    return themes.get(theme_name, GUI_STYLES)


# Utility functions for style management
def get_color(category: str, key: str) -> str:
    """Get a color value from the color palette."""
    categories = category.split(".")
    current = COLORS
    for cat in categories:
        current = current.get(cat, {})
    return current.get(key, "")


def get_spacing(size: str) -> int:
    """Get a spacing value."""
    return DIMENSIONS["spacing"].get(size, DIMENSIONS["spacing"]["md"])


def get_font(
    size: str, family: str = "primary", weight: str = "normal"
) -> Tuple[str, int, str]:
    """Get a font tuple with the specified properties."""
    return create_font(family, size, weight)
