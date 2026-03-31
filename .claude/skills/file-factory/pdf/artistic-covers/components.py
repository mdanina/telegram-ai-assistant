#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artistic PDF Cover Components Library

A comprehensive collection of generative art functions for creating
stunning PDF covers using pure Python and reportlab.

No image generation models required - pure mathematical beauty.
"""

import math
import random
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple (0-1 range)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))


def blend_colors(color1: str, color2: str, ratio: float) -> Color:
    """Blend two hex colors by ratio (0-1)."""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    return Color(
        r1 + (r2 - r1) * ratio,
        g1 + (g2 - g1) * ratio,
        b1 + (b2 - b1) * ratio
    )


def noise_1d(x: float, octaves: int = 4) -> float:
    """Simple 1D noise function for organic variation."""
    result = 0
    amplitude = 1
    frequency = 1
    for _ in range(octaves):
        result += amplitude * math.sin(x * frequency + random.random() * 0.1)
        amplitude *= 0.5
        frequency *= 2
    return result


def lissajous_point(t: float, a: int, b: int, delta: float,
                    scale_x: float, scale_y: float) -> tuple:
    """Calculate point on Lissajous curve."""
    x = scale_x * math.sin(a * t + delta)
    y = scale_y * math.sin(b * t)
    return x, y


# =============================================================================
# FRACTAL COMPONENTS
# =============================================================================

def draw_recursive_circles(c: canvas.Canvas, cx: float, cy: float,
                           radius: float, depth: int, max_depth: int,
                           colors: list) -> None:
    """
    Draw recursive circles creating fractal-like pattern.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        radius: Starting radius
        depth: Current recursion depth
        max_depth: Maximum recursion depth (recommended: 4-6)
        colors: List of hex color strings
    """
    if depth > max_depth or radius < 2:
        return

    color = colors[depth % len(colors)]
    r, g, b = hex_to_rgb(color)
    alpha = 0.8 - (depth * 0.1)
    c.setFillColor(Color(r, g, b, max(0.1, alpha)))
    c.circle(cx, cy, radius, fill=1, stroke=0)

    num_children = 4 if depth < 3 else 3
    for i in range(num_children):
        angle = (2 * math.pi * i / num_children) + (depth * 0.3)
        new_cx = cx + radius * 0.6 * math.cos(angle)
        new_cy = cy + radius * 0.6 * math.sin(angle)
        draw_recursive_circles(c, new_cx, new_cy, radius * 0.45,
                              depth + 1, max_depth, colors)


def draw_recursive_triangles(c: canvas.Canvas, cx: float, cy: float,
                             size: float, depth: int, max_depth: int,
                             rotation: float, colors: list) -> None:
    """
    Draw Sierpinski-like recursive triangles.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        size: Triangle size
        depth: Current recursion depth
        max_depth: Maximum depth (recommended: 4-5)
        rotation: Initial rotation in radians
        colors: List of hex color strings
    """
    if depth > max_depth or size < 3:
        return

    color = colors[depth % len(colors)]
    r, g, b = hex_to_rgb(color)
    c.setFillColor(Color(r, g, b, 0.7))

    path = c.beginPath()
    for i in range(3):
        angle = rotation + (2 * math.pi * i / 3) - math.pi/2
        px = cx + size * math.cos(angle)
        py = cy + size * math.sin(angle)
        if i == 0:
            path.moveTo(px, py)
        else:
            path.lineTo(px, py)
    path.close()
    c.drawPath(path, fill=1, stroke=0)

    for i in range(3):
        angle = rotation + (2 * math.pi * i / 3) - math.pi/2
        new_cx = cx + size * 0.5 * math.cos(angle)
        new_cy = cy + size * 0.5 * math.sin(angle)
        draw_recursive_triangles(c, new_cx, new_cy, size * 0.5,
                                depth + 1, max_depth, rotation + 0.1, colors)


# =============================================================================
# CURVE COMPONENTS
# =============================================================================

def draw_lissajous_curve(c: canvas.Canvas, cx: float, cy: float,
                         a: int, b: int, delta: float,
                         scale_x: float, scale_y: float,
                         color: str, points: int = 500) -> None:
    """
    Draw beautiful Lissajous curve.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        a, b: Frequency parameters (try primes for interesting patterns)
        delta: Phase shift
        scale_x, scale_y: Size scaling
        color: Hex color string
        points: Number of points (more = smoother, 500-1000 recommended)
    """
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(1.5)

    path = c.beginPath()
    for i in range(points + 1):
        t = (2 * math.pi * i / points)
        x, y = lissajous_point(t, a, b, delta, scale_x, scale_y)
        if i == 0:
            path.moveTo(cx + x, cy + y)
        else:
            path.lineTo(cx + x, cy + y)
    c.drawPath(path, fill=0, stroke=1)


def draw_spiral(c: canvas.Canvas, cx: float, cy: float,
                start_radius: float, end_radius: float,
                turns: float, color: str, line_width: float = 2) -> None:
    """
    Draw spiral pattern.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        start_radius: Inner radius
        end_radius: Outer radius
        turns: Number of spiral turns
        color: Hex color string
        line_width: Stroke width
    """
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(line_width)

    points = 200
    path = c.beginPath()
    for i in range(points):
        t = i / points
        angle = turns * 2 * math.pi * t
        radius = start_radius + (end_radius - start_radius) * t
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(px, py)
        else:
            path.lineTo(px, py)
    c.drawPath(path, fill=0, stroke=1)


# =============================================================================
# PATTERN COMPONENTS
# =============================================================================

def draw_flow_field(c: canvas.Canvas, x: float, y: float,
                    width: float, height: float, resolution: int,
                    colors: list, noise_scale: float = 0.02) -> None:
    """
    Draw flow field with thousands of noise-directed vectors.

    Args:
        c: ReportLab canvas
        x, y: Starting coordinates
        width, height: Field dimensions
        resolution: Grid cell size (smaller = more vectors)
        colors: List of hex colors
        noise_scale: Noise frequency (0.01-0.05 typical)
    """
    cols = int(width / resolution)
    rows = int(height / resolution)

    for row in range(rows):
        for col in range(cols):
            px = x + col * resolution
            py = y + row * resolution

            angle = noise_1d(px * noise_scale) + noise_1d(py * noise_scale)
            angle *= math.pi * 2

            length = resolution * 0.8
            ex = px + length * math.cos(angle)
            ey = py + length * math.sin(angle)

            color = colors[int((col + row) * 0.5) % len(colors)]
            r, g, b = hex_to_rgb(color)
            c.setStrokeColor(Color(r, g, b, 0.6))
            c.setLineWidth(0.5)
            c.line(px, py, ex, ey)


def draw_voronoi_like(c: canvas.Canvas, x: float, y: float,
                      width: float, height: float, num_points: int,
                      colors: list) -> None:
    """
    Draw Voronoi-like cellular pattern.

    Args:
        c: ReportLab canvas
        x, y: Starting coordinates
        width, height: Pattern dimensions
        num_points: Number of cell centers (20-50 typical)
        colors: List of hex colors
    """
    points = [(x + random.random() * width, y + random.random() * height)
              for _ in range(num_points)]

    cell_size = 8
    for py in range(int(y), int(y + height), cell_size):
        for px in range(int(x), int(x + width), cell_size):
            min_dist = float('inf')
            nearest_idx = 0
            for i, (px2, py2) in enumerate(points):
                dist = math.sqrt((px - px2)**2 + (py - py2)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = i

            color = colors[nearest_idx % len(colors)]
            r, g, b = hex_to_rgb(color)
            alpha = max(0.3, 1 - min_dist / 150)
            c.setFillColor(Color(r, g, b, alpha))
            c.rect(px, py, cell_size, cell_size, fill=1, stroke=0)


def draw_geometric_mosaic(c: canvas.Canvas, x: float, y: float,
                          width: float, height: float, cell_size: float,
                          colors: list) -> None:
    """
    Draw geometric mosaic with 6 pattern types per cell.

    Patterns: solid, diagonal split, circle in square, quarter circle,
    stripes, diamond.
    """
    cols = int(width / cell_size)
    rows = int(height / cell_size)

    for row in range(rows):
        for col in range(cols):
            cx = x + col * cell_size
            cy = y + row * cell_size

            pattern = random.randint(0, 5)
            color1 = random.choice(colors)
            color2 = random.choice(colors)

            if pattern == 0:  # Solid
                c.setFillColor(HexColor(color1))
                c.rect(cx, cy, cell_size, cell_size, fill=1, stroke=0)
            elif pattern == 1:  # Diagonal split
                c.setFillColor(HexColor(color1))
                path = c.beginPath()
                path.moveTo(cx, cy)
                path.lineTo(cx + cell_size, cy)
                path.lineTo(cx + cell_size, cy + cell_size)
                path.close()
                c.drawPath(path, fill=1, stroke=0)
                c.setFillColor(HexColor(color2))
                path = c.beginPath()
                path.moveTo(cx, cy)
                path.lineTo(cx, cy + cell_size)
                path.lineTo(cx + cell_size, cy + cell_size)
                path.close()
                c.drawPath(path, fill=1, stroke=0)
            elif pattern == 2:  # Circle in square
                c.setFillColor(HexColor(color1))
                c.rect(cx, cy, cell_size, cell_size, fill=1, stroke=0)
                c.setFillColor(HexColor(color2))
                c.circle(cx + cell_size/2, cy + cell_size/2,
                        cell_size/2.5, fill=1, stroke=0)
            elif pattern == 3:  # Quarter circle
                c.setFillColor(HexColor(color1))
                c.rect(cx, cy, cell_size, cell_size, fill=1, stroke=0)
                c.setFillColor(HexColor(color2))
                c.wedge(cx, cy, cx + cell_size, cy + cell_size, 0, 90, fill=1, stroke=0)
            elif pattern == 4:  # Stripes
                c.setFillColor(HexColor(color1))
                c.rect(cx, cy, cell_size, cell_size, fill=1, stroke=0)
                c.setFillColor(HexColor(color2))
                for s in range(3):
                    c.rect(cx + s * cell_size/3, cy, cell_size/6, cell_size, fill=1, stroke=0)
            else:  # Diamond
                c.setFillColor(HexColor(color1))
                c.rect(cx, cy, cell_size, cell_size, fill=1, stroke=0)
                c.setFillColor(HexColor(color2))
                path = c.beginPath()
                path.moveTo(cx + cell_size/2, cy)
                path.lineTo(cx + cell_size, cy + cell_size/2)
                path.lineTo(cx + cell_size/2, cy + cell_size)
                path.lineTo(cx, cy + cell_size/2)
                path.close()
                c.drawPath(path, fill=1, stroke=0)


def draw_moire_pattern(c: canvas.Canvas, cx: float, cy: float,
                       num_lines: int, radius: float,
                       offset_x: float, offset_y: float, color: str) -> None:
    """
    Draw moiré interference pattern with offset circle grids.

    Args:
        c: ReportLab canvas
        cx, cy: Center of first circle set
        num_lines: Number of concentric circles
        radius: Maximum radius
        offset_x, offset_y: Offset for second set (creates interference)
        color: Hex color string
    """
    r, g, b = hex_to_rgb(color)
    c.setStrokeColor(Color(r, g, b, 0.4))
    c.setLineWidth(0.5)

    for i in range(num_lines):
        r_val = (i + 1) * (radius / num_lines)
        c.circle(cx, cy, r_val, fill=0, stroke=1)

    for i in range(num_lines):
        r_val = (i + 1) * (radius / num_lines)
        c.circle(cx + offset_x, cy + offset_y, r_val, fill=0, stroke=1)


def draw_interference_waves(c: canvas.Canvas, x: float, y: float,
                            width: float, height: float, num_sources: int,
                            colors: list) -> None:
    """
    Draw wave interference pattern from multiple sources.

    Creates mesmerizing interference patterns based on distance
    from randomly placed wave sources.
    """
    sources = [(x + random.random() * width, y + random.random() * height)
               for _ in range(num_sources)]

    cell_size = 6
    for py in range(int(y), int(y + height), cell_size):
        for px in range(int(x), int(x + width), cell_size):
            interference = 0
            for sx, sy in sources:
                dist = math.sqrt((px - sx)**2 + (py - sy)**2)
                interference += math.sin(dist * 0.1)

            interference = (interference / num_sources + 1) / 2
            color_idx = int(interference * (len(colors) - 1))
            color = colors[min(color_idx, len(colors) - 1)]
            c.setFillColor(HexColor(color))
            c.rect(px, py, cell_size, cell_size, fill=1, stroke=0)


# =============================================================================
# SHAPE COMPONENTS
# =============================================================================

def draw_radial_burst(c: canvas.Canvas, cx: float, cy: float,
                      num_rays: int, inner_r: float, outer_r: float,
                      colors: list, rotation: float = 0) -> None:
    """
    Draw radial burst pattern with alternating colored segments.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        num_rays: Number of ray segments (24-48 typical)
        inner_r: Inner radius
        outer_r: Outer radius
        colors: List of hex colors (will cycle)
        rotation: Rotation offset in radians
    """
    for i in range(num_rays):
        angle = rotation + (2 * math.pi * i / num_rays)
        next_angle = rotation + (2 * math.pi * (i + 0.5) / num_rays)

        color = colors[i % len(colors)]
        c.setFillColor(HexColor(color))

        path = c.beginPath()
        path.moveTo(cx + inner_r * math.cos(angle), cy + inner_r * math.sin(angle))
        path.lineTo(cx + outer_r * math.cos(angle), cy + outer_r * math.sin(angle))
        path.lineTo(cx + outer_r * math.cos(next_angle), cy + outer_r * math.sin(next_angle))
        path.lineTo(cx + inner_r * math.cos(next_angle), cy + inner_r * math.sin(next_angle))
        path.close()
        c.drawPath(path, fill=1, stroke=0)


def draw_concentric_rings(c: canvas.Canvas, cx: float, cy: float,
                          max_radius: float, num_rings: int,
                          colors: list, vary_width: bool = True) -> None:
    """Draw concentric rings with alternating colors."""
    for i in range(num_rings, 0, -1):
        ratio = i / num_rings
        radius = max_radius * ratio
        color = colors[i % len(colors)]
        c.setFillColor(HexColor(color))
        c.circle(cx, cy, radius, fill=1, stroke=0)


def draw_concentric_polygon_spiral(c: canvas.Canvas, cx: float, cy: float,
                                   sides: int, num_layers: int, max_radius: float,
                                   colors: list, rotation_increment: float = 0.1) -> None:
    """
    Draw spiraling concentric polygons.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        sides: Number of polygon sides (5-12 work well)
        num_layers: Number of concentric layers (20-50)
        max_radius: Outer radius
        colors: List of hex colors
        rotation_increment: Rotation per layer in radians
    """
    for layer in range(num_layers):
        ratio = (num_layers - layer) / num_layers
        radius = max_radius * ratio
        rotation = layer * rotation_increment

        color = colors[layer % len(colors)]
        r, g, b = hex_to_rgb(color)
        c.setStrokeColor(Color(r, g, b, 0.8))
        c.setLineWidth(1)

        path = c.beginPath()
        for i in range(sides + 1):
            angle = rotation + (2 * math.pi * i / sides)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            if i == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)
        c.drawPath(path, fill=0, stroke=1)


def draw_complex_mandala(c: canvas.Canvas, cx: float, cy: float,
                         radius: float, rings: int, petals_per_ring: int,
                         colors: list) -> None:
    """
    Draw extremely complex mandala with petal shapes.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        radius: Outer radius
        rings: Number of concentric rings (6-12)
        petals_per_ring: Base petals (multiplied by ring number)
        colors: List of hex colors
    """
    for ring in range(rings):
        ring_radius = radius * (ring + 1) / rings
        num_petals = petals_per_ring * (ring + 1)

        for petal in range(num_petals):
            angle = (2 * math.pi * petal / num_petals) + (ring * 0.1)
            petal_length = radius / rings * 0.8
            petal_width = petal_length * 0.3

            px = cx + ring_radius * math.cos(angle)
            py = cy + ring_radius * math.sin(angle)

            color = colors[(ring + petal) % len(colors)]
            r, g, b = hex_to_rgb(color)
            c.setFillColor(Color(r, g, b, 0.7))

            c.saveState()
            c.translate(px, py)
            c.rotate(angle * 180 / math.pi + 90)

            path = c.beginPath()
            for i in range(20):
                t = i / 19
                curve_x = petal_width * math.sin(t * math.pi)
                curve_y = petal_length * t
                if i == 0:
                    path.moveTo(curve_x, curve_y)
                else:
                    path.lineTo(curve_x, curve_y)
            for i in range(20):
                t = 1 - i / 19
                curve_x = -petal_width * math.sin(t * math.pi)
                curve_y = petal_length * t
                path.lineTo(curve_x, curve_y)
            path.close()
            c.drawPath(path, fill=1, stroke=0)
            c.restoreState()

        c.setStrokeColor(HexColor(colors[ring % len(colors)]))
        c.setLineWidth(0.5)
        c.circle(cx, cy, ring_radius, fill=0, stroke=1)


def draw_op_art_squares(c: canvas.Canvas, cx: float, cy: float,
                        size: float, num_squares: int, colors: list) -> None:
    """
    Draw op-art concentric rotating squares.

    Creates optical illusion with rotating nested squares.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        size: Outer square size
        num_squares: Number of nested squares (20-40)
        colors: Two colors for alternation
    """
    for i in range(num_squares):
        ratio = (num_squares - i) / num_squares
        sq_size = size * ratio
        rotation = i * 0.08

        color = colors[i % 2]
        c.setFillColor(HexColor(color))

        c.saveState()
        c.translate(cx, cy)
        c.rotate(rotation * 180 / math.pi)
        c.rect(-sq_size/2, -sq_size/2, sq_size, sq_size, fill=1, stroke=0)
        c.restoreState()


# =============================================================================
# ORGANIC COMPONENTS
# =============================================================================

def draw_organic_blob(c: canvas.Canvas, cx: float, cy: float,
                      base_radius: float, color: str, complexity: int = 5) -> None:
    """
    Draw organic, blob-like shape using noise.

    Args:
        c: ReportLab canvas
        cx, cy: Center coordinates
        base_radius: Base size
        color: Hex color string
        complexity: Noise complexity (3-10, higher = more irregular)
    """
    r, g, b = hex_to_rgb(color)
    c.setFillColor(Color(r, g, b, 0.7))

    points = 50
    path = c.beginPath()
    for i in range(points):
        angle = (2 * math.pi * i / points)
        noise = sum(math.sin(angle * (j + 1) * 2 + j) * (base_radius / (j + 2))
                   for j in range(complexity))
        radius = base_radius + noise * 0.3
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(px, py)
        else:
            path.lineTo(px, py)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def draw_flowing_waves(c: canvas.Canvas, start_y: float, width: float,
                       num_waves: int, amplitude: float, wavelength: float,
                       colors: list) -> None:
    """
    Draw flowing organic wave patterns.

    Args:
        c: ReportLab canvas
        start_y: Starting Y position (top of waves)
        width: Wave width
        num_waves: Number of wave layers (8-15)
        amplitude: Wave height
        wavelength: Distance between peaks
        colors: List of hex colors
    """
    for i in range(num_waves):
        y_offset = start_y - i * (amplitude * 1.5)
        color = colors[i % len(colors)]
        r, g, b = hex_to_rgb(color)
        c.setFillColor(Color(r, g, b, 0.7))

        path = c.beginPath()
        path.moveTo(0, y_offset)

        for x in range(0, int(width) + 10, 5):
            y = y_offset + amplitude * math.sin((x / wavelength) * 2 * math.pi + i * 0.5)
            path.lineTo(x, y)

        path.lineTo(width, 0)
        path.lineTo(0, 0)
        path.close()
        c.drawPath(path, fill=1, stroke=0)


def draw_generative_mountains(c: canvas.Canvas, x: float, y: float,
                              width: float, height: float, num_layers: int,
                              colors: list) -> None:
    """
    Draw generative mountain range with noise.

    Creates layered mountain silhouettes with atmospheric perspective.
    """
    for layer in range(num_layers):
        color = colors[layer % len(colors)]
        r, g, b = hex_to_rgb(color)
        c.setFillColor(Color(r, g, b, 0.8))

        base_y = y + (layer * height / num_layers)

        path = c.beginPath()
        path.moveTo(x, base_y)

        num_points = 50
        for i in range(num_points + 1):
            px = x + (i / num_points) * width
            peak_height = 0
            for octave in range(4):
                freq = (octave + 1) * 0.5
                amp = height / (num_layers * (octave + 1))
                peak_height += amp * math.sin(px * freq * 0.02 + layer + octave)

            py = base_y + peak_height * (1 - layer / num_layers)
            path.lineTo(px, py)

        path.lineTo(x + width, y)
        path.lineTo(x, y)
        path.close()
        c.drawPath(path, fill=1, stroke=0)


def draw_dna_helix(c: canvas.Canvas, x: float, y: float, height: float,
                   num_rungs: int, colors: list) -> None:
    """
    Draw DNA double helix structure.

    Args:
        c: ReportLab canvas
        x: Center X position
        y: Bottom Y position
        height: Total helix height
        num_rungs: Number of base pair rungs (30-50)
        colors: List of hex colors for rungs/nodes
    """
    rung_spacing = height / num_rungs
    amplitude = 40

    for i in range(num_rungs):
        t = i / num_rungs * 4 * math.pi
        y_pos = y + i * rung_spacing

        x1 = x + amplitude * math.sin(t)
        x2 = x + amplitude * math.sin(t + math.pi)

        color = colors[i % len(colors)]
        c.setStrokeColor(HexColor(color))
        c.setLineWidth(3)
        c.line(x1, y_pos, x2, y_pos)

        c.setFillColor(HexColor(colors[(i + 1) % len(colors)]))
        c.circle(x1, y_pos, 5, fill=1, stroke=0)
        c.circle(x2, y_pos, 5, fill=1, stroke=0)


# =============================================================================
# PARTICLE/EFFECT COMPONENTS
# =============================================================================

def draw_particle_field(c: canvas.Canvas, x: float, y: float,
                        width: float, height: float, num_particles: int,
                        colors: list, shapes: list = None) -> None:
    """
    Draw field of random particles creating texture.

    Args:
        c: ReportLab canvas
        x, y: Starting coordinates
        width, height: Field dimensions
        num_particles: Number of particles (100-500 typical)
        colors: List of hex colors
        shapes: List of shape types ['circle', 'square', 'triangle']
    """
    if shapes is None:
        shapes = ['circle', 'square', 'triangle']

    for _ in range(num_particles):
        px = x + random.random() * width
        py = y + random.random() * height
        size = random.uniform(2, 15)
        color = random.choice(colors)
        alpha = random.uniform(0.3, 1.0)

        r, g, b = hex_to_rgb(color)
        c.setFillColor(Color(r, g, b, alpha))

        shape = random.choice(shapes)
        if shape == 'circle':
            c.circle(px, py, size, fill=1, stroke=0)
        elif shape == 'square':
            c.rect(px - size/2, py - size/2, size, size, fill=1, stroke=0)
        elif shape == 'triangle':
            path = c.beginPath()
            path.moveTo(px, py + size)
            path.lineTo(px - size * 0.866, py - size * 0.5)
            path.lineTo(px + size * 0.866, py - size * 0.5)
            path.close()
            c.drawPath(path, fill=1, stroke=0)


def draw_particle_explosion(c: canvas.Canvas, cx: float, cy: float,
                            num_particles: int, max_radius: float,
                            colors: list) -> None:
    """
    Draw explosive particle burst from center.

    Particles are distributed with square root for even visual density.
    Size and opacity decrease with distance from center.
    """
    shapes = ['circle', 'square', 'triangle']

    for _ in range(num_particles):
        angle = random.random() * 2 * math.pi
        dist = random.random() ** 0.5 * max_radius

        px = cx + dist * math.cos(angle)
        py = cy + dist * math.sin(angle)

        size = max(1, 8 * (1 - dist / max_radius) + random.uniform(0, 4))

        color = random.choice(colors)
        r, g, b = hex_to_rgb(color)
        alpha = 0.9 * (1 - dist / max_radius) + 0.1
        c.setFillColor(Color(r, g, b, alpha))

        shape = random.choice(shapes)
        if shape == 'circle':
            c.circle(px, py, size, fill=1, stroke=0)
        elif shape == 'square':
            c.rect(px - size/2, py - size/2, size, size, fill=1, stroke=0)
        else:
            path = c.beginPath()
            path.moveTo(px, py + size)
            path.lineTo(px - size * 0.866, py - size * 0.5)
            path.lineTo(px + size * 0.866, py - size * 0.5)
            path.close()
            c.drawPath(path, fill=1, stroke=0)


def draw_geometric_explosion(c: canvas.Canvas, cx: float, cy: float,
                             num_shapes: int, max_radius: float,
                             colors: list) -> None:
    """
    Draw explosion of various geometric shapes (3-6 sided + stars).
    """
    shape_types = ['circle', 'square', 'triangle', 'pentagon', 'hexagon', 'star']

    for _ in range(num_shapes):
        angle = random.random() * 2 * math.pi
        dist = random.random() ** 0.7 * max_radius

        px = cx + dist * math.cos(angle)
        py = cy + dist * math.sin(angle)
        size = random.uniform(5, 40) * (1 - dist / max_radius * 0.5)
        rotation = random.uniform(0, 2 * math.pi)

        color = random.choice(colors)
        r, g, b = hex_to_rgb(color)
        c.setFillColor(Color(r, g, b, random.uniform(0.3, 0.9)))

        shape = random.choice(shape_types)

        if shape == 'circle':
            c.circle(px, py, size, fill=1, stroke=0)
        elif shape == 'square':
            c.saveState()
            c.translate(px, py)
            c.rotate(rotation * 180 / math.pi)
            c.rect(-size/2, -size/2, size, size, fill=1, stroke=0)
            c.restoreState()
        else:
            sides = {'triangle': 3, 'pentagon': 5, 'hexagon': 6, 'star': 10}[shape]
            path = c.beginPath()
            for i in range(sides):
                a = rotation + (2 * math.pi * i / sides)
                r_val = size * 0.4 if (shape == 'star' and i % 2 == 1) else size
                x2 = px + r_val * math.cos(a)
                y2 = py + r_val * math.sin(a)
                if i == 0:
                    path.moveTo(x2, y2)
                else:
                    path.lineTo(x2, y2)
            path.close()
            c.drawPath(path, fill=1, stroke=0)


def draw_scattered_polygons(c: canvas.Canvas, x: float, y: float,
                            width: float, height: float, num_shapes: int,
                            colors: list, max_size: float = 80) -> None:
    """Draw scattered irregular polygons with randomized vertices."""
    for _ in range(num_shapes):
        cx = x + random.random() * width
        cy = y + random.random() * height
        size = random.uniform(20, max_size)
        sides = random.randint(3, 8)
        rotation = random.uniform(0, 2 * math.pi)

        color = random.choice(colors)
        r, g, b = hex_to_rgb(color)
        alpha = random.uniform(0.4, 0.9)
        c.setFillColor(Color(r, g, b, alpha))

        path = c.beginPath()
        for i in range(sides):
            angle = rotation + (2 * math.pi * i / sides)
            r_var = size * random.uniform(0.7, 1.3)
            px = cx + r_var * math.cos(angle)
            py = cy + r_var * math.sin(angle)
            if i == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)
        path.close()
        c.drawPath(path, fill=1, stroke=0)


def draw_glitch_blocks(c: canvas.Canvas, x: float, y: float,
                       width: float, height: float, num_blocks: int,
                       colors: list) -> None:
    """
    Draw glitch-art style displaced blocks with ghost offsets.
    """
    for _ in range(num_blocks):
        bx = x + random.random() * width
        by = y + random.random() * height
        bw = random.uniform(20, 150)
        bh = random.uniform(5, 30)

        color = random.choice(colors)
        r, g, b = hex_to_rgb(color)
        c.setFillColor(Color(r, g, b, random.uniform(0.6, 1.0)))
        c.rect(bx, by, bw, bh, fill=1, stroke=0)

        if random.random() > 0.5:
            offset = random.uniform(-10, 10)
            c.setFillColor(Color(r, g, b, 0.3))
            c.rect(bx + offset, by + offset, bw, bh, fill=1, stroke=0)


def draw_halftone_gradient(c: canvas.Canvas, x: float, y: float,
                           width: float, height: float, color: str,
                           direction: str = 'horizontal') -> None:
    """
    Draw halftone dot gradient.

    Args:
        c: ReportLab canvas
        x, y: Starting coordinates
        width, height: Gradient dimensions
        color: Hex color string
        direction: 'horizontal', 'vertical', or 'radial'
    """
    r, g, b = hex_to_rgb(color)
    c.setFillColor(Color(r, g, b, 1))

    spacing = 8
    cols = int(width / spacing)
    rows = int(height / spacing)

    for row in range(rows):
        for col in range(cols):
            cx = x + col * spacing + spacing/2
            cy = y + row * spacing + spacing/2

            if direction == 'horizontal':
                ratio = col / cols
            elif direction == 'vertical':
                ratio = row / rows
            else:
                dx = (col / cols) - 0.5
                dy = (row / rows) - 0.5
                ratio = 1 - min(1, math.sqrt(dx*dx + dy*dy) * 2)

            dot_size = spacing * 0.4 * ratio
            if dot_size > 0.5:
                c.circle(cx, cy, dot_size, fill=1, stroke=0)


# =============================================================================
# TYPOGRAPHY COMPONENTS
# =============================================================================

def draw_abstract_typography(c: canvas.Canvas, text: str, x: float, y: float,
                             font_size: float, color: str,
                             style: str = 'normal') -> None:
    """
    Draw text with abstract styling.

    Args:
        c: ReportLab canvas
        text: Text to draw
        x, y: Position
        font_size: Base font size
        color: Hex color string
        style: 'normal', 'scattered', 'stacked', or 'outlined'
    """
    c.setFillColor(HexColor(color))

    if style == 'scattered':
        for i, char in enumerate(text):
            cx = x + i * font_size * 0.8 + random.uniform(-10, 10)
            cy = y + random.uniform(-15, 15)
            rot = random.uniform(-15, 15)
            c.saveState()
            c.translate(cx, cy)
            c.rotate(rot)
            c.setFont("Helvetica-Bold", font_size + random.uniform(-10, 10))
            c.drawString(0, 0, char)
            c.restoreState()
    elif style == 'stacked':
        for i, char in enumerate(text):
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(x, y - i * font_size * 0.9, char)
    elif style == 'outlined':
        c.setStrokeColor(HexColor(color))
        c.setLineWidth(2)
        c.setFont("Helvetica-Bold", font_size)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            c.drawString(x + offset[0], y + offset[1], text)
    else:
        c.setFont("Helvetica-Bold", font_size)
        c.drawString(x, y, text)


def draw_text_texture(c: canvas.Canvas, x: float, y: float,
                      width: float, height: float, words: str,
                      font_size_range: tuple, colors: list) -> None:
    """
    Fill area with repeated words as visual texture.

    Args:
        c: ReportLab canvas
        x, y: Starting coordinates
        width, height: Area dimensions
        words: Space-separated word string
        font_size_range: (min_size, max_size) tuple
        colors: List of hex colors
    """
    words_list = words.split()

    current_y = y + height
    while current_y > y:
        current_x = x
        while current_x < x + width:
            word = random.choice(words_list)
            size = random.uniform(font_size_range[0], font_size_range[1])
            color = random.choice(colors)
            r, g, b = hex_to_rgb(color)
            c.setFillColor(Color(r, g, b, random.uniform(0.1, 0.5)))
            c.setFont("Helvetica", size)

            rotation = random.uniform(-20, 20)
            c.saveState()
            c.translate(current_x, current_y)
            c.rotate(rotation)
            c.drawString(0, 0, word)
            c.restoreState()

            current_x += size * len(word) * 0.5 + random.uniform(5, 20)
        current_y -= random.uniform(15, 30)


# =============================================================================
# NEURAL/TECH COMPONENTS
# =============================================================================

def draw_neural_network(c: canvas.Canvas, x: float, y: float,
                        width: float, height: float, layers: int,
                        nodes_per_layer: list, colors: list) -> None:
    """
    Draw neural network visualization.

    Args:
        c: ReportLab canvas
        x, y: Starting coordinates
        width, height: Network dimensions
        layers: Number of layers
        nodes_per_layer: List of node counts per layer
        colors: List of hex colors for layers
    """
    layer_spacing = width / (layers + 1)
    node_positions = []

    for layer in range(layers):
        layer_x = x + layer_spacing * (layer + 1)
        nodes = nodes_per_layer[layer] if layer < len(nodes_per_layer) else nodes_per_layer[-1]
        node_spacing = height / (nodes + 1)

        layer_nodes = []
        for node in range(nodes):
            node_y = y + node_spacing * (node + 1)
            layer_nodes.append((layer_x, node_y))

            color = colors[layer % len(colors)]
            c.setFillColor(HexColor(color))
            c.circle(layer_x, node_y, 8, fill=1, stroke=0)

        node_positions.append(layer_nodes)

    c.setStrokeColor(Color(0.5, 0.5, 0.5, 0.2))
    c.setLineWidth(0.5)
    for layer in range(len(node_positions) - 1):
        for node1 in node_positions[layer]:
            for node2 in node_positions[layer + 1]:
                c.line(node1[0], node1[1], node2[0], node2[1])


# =============================================================================
# COLOR PALETTES
# =============================================================================

PALETTES = {
    "neon": ["#ff006e", "#8338ec", "#3a86ff", "#06d6a0", "#ffbe0b"],
    "cosmic": ["#0d0d0d", "#1a0a2e", "#ff006e", "#00ffff", "#ffffff"],
    "organic": ["#1a535c", "#4ecdc4", "#ff6b6b", "#ffe66d", "#ffffff"],
    "retro": ["#0d0221", "#ff00ff", "#00ffff", "#ffff00", "#ff6b6b"],
    "earth": ["#4a7c59", "#f9a620", "#b7472a", "#f5f3ed", "#2c1810"],
    "glitch": ["#ff0000", "#00ff00", "#0000ff", "#ff00ff", "#00ffff", "#ffff00"],
    "quantum": ["#00ffff", "#ff00ff", "#ffff00", "#00ff00", "#ffffff"],
    "minimal": ["#000000", "#ffffff", "#ff3366"],
    "sunset": ["#e76f51", "#f4a261", "#e9c46a", "#264653"],
    "galaxy": ["#2b1e3e", "#4a4e8f", "#a490c2", "#e6e6fa"],
    "tech": ["#0066ff", "#00ffff", "#1e1e1e", "#ffffff"],
    "botanical": ["#4a7c59", "#f9a620", "#b7472a", "#f5f3ed"],
    "golden": ["#f4a900", "#c1666b", "#d4b896", "#4a403a"],
    "arctic": ["#e8f4f8", "#a8dadc", "#457b9d", "#1d3557"],
    "fire": ["#ff0000", "#ff4500", "#ff8c00", "#ffd700", "#ffffe0"],
    "ocean": ["#006994", "#40a4df", "#8ed1fc", "#e0f7fa"],
    "abstract_full": [
        "#ff006e", "#fb5607", "#ffbe0b", "#06d6a0", "#3a86ff",
        "#8338ec", "#ffffff", "#ff0000", "#00ff00", "#0000ff"
    ],
}


# =============================================================================
# STYLE PRESETS
# =============================================================================

STYLE_PRESETS = {
    "cosmic-explosion": {
        "components": ["radial_burst", "particle_field", "spiral",
                       "concentric_rings", "organic_blob"],
        "palette": "neon",
        "intensity": "high",
        "background": "#0a0a1a"
    },
    "fractal-universe": {
        "components": ["recursive_circles", "lissajous_curve",
                       "particle_explosion", "moire_pattern", "concentric_polygon_spiral"],
        "palette": "cosmic",
        "intensity": "extreme",
        "background": "gradient"
    },
    "geometric-chaos": {
        "components": ["geometric_mosaic", "scattered_polygons",
                       "glitch_blocks", "line_field"],
        "palette": "glitch",
        "intensity": "high",
        "background": "gradient"
    },
    "organic-flow": {
        "components": ["flowing_waves", "organic_blob",
                       "halftone_gradient", "particle_field"],
        "palette": "organic",
        "intensity": "medium",
        "background": "gradient"
    },
    "retro-futurism": {
        "components": ["perspective_grid", "neon_sun",
                       "glitch_blocks", "chrome_text"],
        "palette": "retro",
        "intensity": "medium",
        "background": "#0d0221"
    },
    "minimalist-bold": {
        "components": ["single_shape", "accent_dots"],
        "palette": "minimal",
        "intensity": "low",
        "background": "#ffffff"
    },
    "psychedelic-mandala": {
        "components": ["complex_mandala", "radial_burst",
                       "organic_blob", "concentric_rings"],
        "palette": "neon",
        "intensity": "high",
        "background": "#1a0533"
    },
    "maximalist": {
        "components": ["all"],
        "palette": "abstract_full",
        "intensity": "extreme",
        "background": "gradient"
    },
    "ultimate-chaos": {
        "components": ["all"],
        "palette": "abstract_full",
        "intensity": "maximum",
        "background": "gradient"
    }
}
