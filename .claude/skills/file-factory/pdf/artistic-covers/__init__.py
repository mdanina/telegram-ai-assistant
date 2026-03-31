"""
Artistic PDF Covers - Generative Art Book Cover System

Create stunning PDF covers using pure Python and reportlab.
No image generation models required.

Usage:
    from artistic_covers import ArtisticCoverGenerator

    gen = ArtisticCoverGenerator()
    gen.create_cover("cosmic-explosion", "output.pdf", title="MY BOOK")
"""

from .generator import (
    ArtisticCoverGenerator,
    create_quick_cover,
    list_available_styles,
    list_available_palettes,
)

from .components import (
    # Fractal components
    draw_recursive_circles,
    draw_recursive_triangles,

    # Curve components
    draw_lissajous_curve,
    draw_spiral,

    # Pattern components
    draw_flow_field,
    draw_voronoi_like,
    draw_geometric_mosaic,
    draw_moire_pattern,
    draw_interference_waves,

    # Shape components
    draw_radial_burst,
    draw_concentric_rings,
    draw_concentric_polygon_spiral,
    draw_complex_mandala,
    draw_op_art_squares,

    # Organic components
    draw_organic_blob,
    draw_flowing_waves,
    draw_generative_mountains,
    draw_dna_helix,

    # Particle/effect components
    draw_particle_field,
    draw_particle_explosion,
    draw_geometric_explosion,
    draw_scattered_polygons,
    draw_glitch_blocks,
    draw_halftone_gradient,

    # Typography components
    draw_abstract_typography,
    draw_text_texture,

    # Neural/tech components
    draw_neural_network,

    # Utilities
    hex_to_rgb,
    blend_colors,
    noise_1d,
    lissajous_point,

    # Palettes and presets
    PALETTES,
    STYLE_PRESETS,
)

__version__ = "1.0.0"
__all__ = [
    "ArtisticCoverGenerator",
    "create_quick_cover",
    "list_available_styles",
    "list_available_palettes",
    "PALETTES",
    "STYLE_PRESETS",
]
