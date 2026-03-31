#!/usr/bin/env python3
"""
Artistic Cover Generator

Main entry point for creating stunning PDF book covers using
generative art techniques. No image generation models required.

Usage:
    generator = ArtisticCoverGenerator()
    generator.create_cover("cosmic-explosion", "output.pdf", title="MY BOOK")

    # Or blend styles:
    generator.create_cover(
        styles=["fractal", "particles", "mandala"],
        intensity="extreme",
        output="blended.pdf"
    )
"""

import os
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas

# Add parent to path for component imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from components import *


class ArtisticCoverGenerator:
    """
    Main generator for artistic PDF covers.

    Supports single styles, blended styles, and intensity control.
    """

    def __init__(self, pagesize=letter):
        self.pagesize = pagesize
        self.width, self.height = pagesize

        # Import all style modules
        self._load_styles()

    def _load_styles(self):
        """Load available styles from style modules."""
        self.styles = {}

        # Cosmic styles
        try:
            from styles.cosmic import COSMIC_STYLES
            self.styles.update(COSMIC_STYLES)
        except ImportError:
            pass

        # Add more style modules here as they're created
        # from styles.geometric import GEOMETRIC_STYLES
        # from styles.organic import ORGANIC_STYLES
        # etc.

    def list_styles(self):
        """Return list of available style names."""
        return list(self.styles.keys())

    def list_palettes(self):
        """Return available color palettes."""
        return list(PALETTES.keys())

    def create_cover(self, style=None, output="cover.pdf",
                     title="TITLE", subtitle="", author="Author Name",
                     styles=None, intensity="high", blend_mode="layered",
                     palette=None, custom_colors=None):
        """
        Create an artistic cover.

        Args:
            style: Single style name (e.g., "cosmic-explosion")
            output: Output PDF filename
            title: Book title
            subtitle: Subtitle text
            author: Author name
            styles: List of styles to blend (alternative to single style)
            intensity: "minimal", "low", "medium", "high", "extreme", "maximum"
            blend_mode: "layered", "integrated", "sectioned", "dominant"
            palette: Palette name from PALETTES
            custom_colors: Custom color list (overrides palette)

        Returns:
            str: Path to created PDF
        """
        c = canvas.Canvas(output, pagesize=self.pagesize)

        if style and style in self.styles:
            # Single style
            self.styles[style](c, self.width, self.height,
                             title=title, subtitle=subtitle, author=author)
        elif styles:
            # Blended styles
            self._create_blended(c, styles, intensity, blend_mode,
                               title, subtitle, author,
                               palette, custom_colors)
        else:
            raise ValueError(f"Unknown style: {style}. Available: {self.list_styles()}")

        c.save()
        return output

    def _create_blended(self, c, styles, intensity, blend_mode,
                       title, subtitle, author, palette, custom_colors):
        """Create a cover blending multiple styles/components."""
        colors = custom_colors or PALETTES.get(palette, PALETTES["neon"])

        # Determine element counts based on intensity
        intensity_map = {
            "minimal": {"particles": 100, "shapes": 20, "fractals": 2},
            "low": {"particles": 300, "shapes": 50, "fractals": 3},
            "medium": {"particles": 500, "shapes": 100, "fractals": 4},
            "high": {"particles": 1000, "shapes": 200, "fractals": 5},
            "extreme": {"particles": 2000, "shapes": 400, "fractals": 6},
            "maximum": {"particles": 3000, "shapes": 600, "fractals": 7},
        }
        params = intensity_map.get(intensity, intensity_map["high"])

        # Background gradient
        for i in range(50):
            ratio = i / 50
            color = blend_colors(colors[0], colors[-1], ratio)
            c.setFillColor(color)
            c.rect(0, self.height * i / 50, self.width, self.height / 49 + 2, fill=1, stroke=0)

        # Apply each component
        component_map = {
            "fractal": lambda: draw_recursive_circles(
                c, self.width/2, self.height/2, 150, 0, params["fractals"], colors),
            "particles": lambda: draw_particle_explosion(
                c, self.width/2, self.height/2, params["particles"], 350, colors),
            "mandala": lambda: draw_complex_mandala(
                c, self.width/2, self.height/2, 200, 8, 6, colors),
            "lissajous": lambda: [draw_lissajous_curve(
                c, self.width/2, self.height/2, i+2, i+3, i*0.5, 200, 250,
                colors[i % len(colors)], 600) for i in range(5)],
            "voronoi": lambda: draw_voronoi_like(
                c, 0, 0, self.width, self.height, 30, colors),
            "flow": lambda: draw_flow_field(
                c, 0, 0, self.width, self.height, 15, colors),
            "waves": lambda: draw_flowing_waves(
                c, self.height, self.width, 10, 60, 150, colors),
            "mosaic": lambda: draw_geometric_mosaic(
                c, 0, 0, self.width, self.height * 0.4, 40, colors),
            "glitch": lambda: draw_glitch_blocks(
                c, 0, self.height * 0.3, self.width, self.height * 0.4,
                params["shapes"] // 2, colors),
            "polygons": lambda: draw_scattered_polygons(
                c, 0, 0, self.width, self.height, params["shapes"], colors),
            "dna": lambda: draw_dna_helix(
                c, self.width/2, 50, self.height - 100, 40, colors),
            "mountains": lambda: draw_generative_mountains(
                c, 0, 0, self.width, self.height * 0.4, 6, colors),
            "interference": lambda: draw_interference_waves(
                c, 0, 0, self.width, self.height, 4, colors),
            "moire": lambda: draw_moire_pattern(
                c, self.width/2, self.height/2, 50, 200, 20, 15, colors[0]),
            "spirals": lambda: [draw_concentric_polygon_spiral(
                c, self.width * (i+1) / 4, self.height/2, 6+i, 25, 100, colors, 0.1)
                for i in range(3)],
            "opart": lambda: draw_op_art_squares(
                c, self.width/2, self.height/2, 200, 30, ["#ffffff", "#000000"]),
            "text_texture": lambda: draw_text_texture(
                c, 0, 0, self.width, self.height,
                "ABSTRACT ART DESIGN CREATIVE VISUAL",
                (8, 20), colors),
        }

        # Apply requested components
        for style_name in styles:
            if style_name == "all":
                for component in component_map.values():
                    component()
            elif style_name in component_map:
                component_map[style_name]()

        # Add title
        c.setFillColor(Color(1, 1, 1, 0.95))
        c.setFont("Helvetica-Bold", 72)
        tw = c.stringWidth(title, "Helvetica-Bold", 72)
        c.drawString((self.width - tw)/2, self.height/2 + 20, title)

        if subtitle:
            c.setFillColor(HexColor(colors[1] if len(colors) > 1 else colors[0]))
            c.setFont("Helvetica", 24)
            sw = c.stringWidth(subtitle, "Helvetica", 24)
            c.drawString((self.width - sw)/2, self.height/2 - 30, subtitle)

        c.setFillColor(Color(1, 1, 1, 0.8))
        c.setFont("Helvetica-Bold", 16)
        aw = c.stringWidth(author, "Helvetica-Bold", 16)
        c.drawString((self.width - aw)/2, 50, author)

    def create_multi_page(self, styles_list, output="covers.pdf",
                         title="COLLECTION", author="Author Name"):
        """
        Create multi-page PDF with different cover per page.

        Args:
            styles_list: List of style names or style configs
            output: Output PDF filename
            title: Base title (will be modified per page)
            author: Author name
        """
        c = canvas.Canvas(output, pagesize=self.pagesize)

        for i, style in enumerate(styles_list):
            if isinstance(style, str):
                style_name = style
                page_title = title
                page_subtitle = ""
            else:
                style_name = style.get("style", "cosmic-explosion")
                page_title = style.get("title", title)
                page_subtitle = style.get("subtitle", "")

            if style_name in self.styles:
                self.styles[style_name](c, self.width, self.height,
                                       title=page_title,
                                       subtitle=page_subtitle,
                                       author=author)
            if i < len(styles_list) - 1:
                c.showPage()

        c.save()
        return output


# Convenience functions
def create_quick_cover(style, output, title, author=""):
    """Quick one-liner to create a cover."""
    gen = ArtisticCoverGenerator()
    return gen.create_cover(style, output, title=title, author=author)


def list_available_styles():
    """List all available styles."""
    gen = ArtisticCoverGenerator()
    return gen.list_styles()


def list_available_palettes():
    """List all available color palettes."""
    return list(PALETTES.keys())


if __name__ == "__main__":
    # Demo
    print("Available styles:", list_available_styles())
    print("Available palettes:", list_available_palettes())

    gen = ArtisticCoverGenerator()

    # Example: Single style
    gen.create_cover("cosmic-explosion", "demo_cosmic.pdf",
                    title="COSMIC", subtitle="A Space Odyssey", author="Demo Author")

    # Example: Blended
    gen.create_cover(
        styles=["fractal", "particles", "lissajous"],
        intensity="high",
        output="demo_blend.pdf",
        title="BLENDED",
        palette="neon"
    )

    print("Demo PDFs created!")
