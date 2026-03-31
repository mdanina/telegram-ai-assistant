"""
Style Presets for Artistic PDF Covers

Each module contains preset style functions for specific themes.
"""

from .cosmic import COSMIC_STYLES

# Add more as they're created:
# from .geometric import GEOMETRIC_STYLES
# from .organic import ORGANIC_STYLES
# from .experimental import EXPERIMENTAL_STYLES

ALL_STYLES = {}
ALL_STYLES.update(COSMIC_STYLES)

__all__ = ["COSMIC_STYLES", "ALL_STYLES"]
