#!/usr/bin/env python3
"""
Cosmic Style Presets for Artistic PDF Covers

Styles: cosmic-explosion, fractal-universe, cosmic-mandala, quantum-field
Best for: Sci-fi, space themes, epic fantasy, philosophical works
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, Color
import random
import math

# Import components from parent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components import *


def create_cosmic_explosion(c, width, height, title="NOVA",
                           subtitle="Beyond the Event Horizon",
                           author="Author Name"):
    """
    Cosmic explosion with radial bursts and particle fields.

    Elements: ~10,000+
    Intensity: High
    """
    # Deep space background
    c.setFillColor(HexColor("#0a0a1a"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    colors = PALETTES["neon"]

    # Dual radial bursts
    draw_radial_burst(c, width/2, height/2, 48, 50, 400, colors, rotation=0.1)
    draw_radial_burst(c, width/2, height/2, 36, 80, 350, colors, rotation=0.15)

    # Particle field
    draw_particle_field(c, 0, 0, width, height, 300,
                       ["#ffffff", "#ffd700", "#ff69b4", "#00ffff"])

    # Concentric rings
    draw_concentric_rings(c, width/2, height/2, 150, 20,
                         ["#1a1a2e", "#16213e", "#0f3460", "#e94560"])

    # Spirals
    draw_spiral(c, width/2, height/2, 20, 180, 4, "#ffffff", 1.5)
    draw_spiral(c, width/2, height/2, 30, 200, 3.5, "#ff006e", 1)

    # Organic blobs
    for _ in range(8):
        bx = random.uniform(50, width - 50)
        by = random.uniform(50, height - 50)
        draw_organic_blob(c, bx, by, random.uniform(30, 80),
                         random.choice(colors), complexity=7)

    # Title
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 72)
    tw = c.stringWidth(title, "Helvetica-Bold", 72)
    c.drawString((width - tw)/2, height/2 + 20, title)

    c.setFont("Helvetica", 24)
    sw = c.stringWidth(subtitle, "Helvetica", 24)
    c.drawString((width - sw)/2, height/2 - 40, subtitle)

    c.setFont("Helvetica-Bold", 18)
    aw = c.stringWidth(author, "Helvetica-Bold", 18)
    c.drawString((width - aw)/2, 60, author)


def create_fractal_universe(c, width, height, title="INFINITE",
                           subtitle="Recursions of the Cosmos",
                           author="Author Name"):
    """
    Fractal universe with recursive patterns and Lissajous curves.

    Elements: ~15,000+
    Intensity: Extreme
    """
    # Gradient background
    for i in range(50):
        ratio = i / 50
        color = blend_colors("#0d0d0d", "#1a0a2e", ratio)
        c.setFillColor(color)
        c.rect(0, height * i / 50, width, height / 49 + 2, fill=1, stroke=0)

    # 2000 stars
    for _ in range(2000):
        sx = random.random() * width
        sy = random.random() * height
        c.setFillColor(Color(1, 1, 1, random.uniform(0.2, 1)))
        c.circle(sx, sy, random.uniform(0.5, 3), fill=1, stroke=0)

    colors = PALETTES["neon"]

    # Lissajous curves
    for i in range(8):
        a = random.randint(1, 7)
        b = random.randint(1, 7)
        delta = random.random() * math.pi
        draw_lissajous_curve(c, width/2, height/2, a, b, delta, 200, 250,
                            colors[i % len(colors)], points=800)

    # Recursive fractals
    draw_recursive_circles(c, width/2, height/2, 150, 0, 6, colors)

    for _ in range(4):
        fx = random.uniform(100, width - 100)
        fy = random.uniform(100, height - 100)
        draw_recursive_circles(c, fx, fy, 60, 0, 4, colors)

    # Concentric polygon spirals
    draw_concentric_polygon_spiral(c, width * 0.25, height * 0.7, 6, 30, 120, colors, 0.15)
    draw_concentric_polygon_spiral(c, width * 0.75, height * 0.3, 8, 25, 100, colors, -0.12)

    # Particle explosion
    draw_particle_explosion(c, width/2, height/2, 500, 350, colors)

    # Moiré patterns
    draw_moire_pattern(c, 100, height - 100, 40, 100, 15, 10, "#3a86ff")
    draw_moire_pattern(c, width - 100, 100, 40, 100, -15, 10, "#ff006e")

    # Title
    c.setFillColor(Color(1, 1, 1, 0.95))
    c.setFont("Helvetica-Bold", 84)
    tw = c.stringWidth(title, "Helvetica-Bold", 84)
    c.drawString((width - tw)/2, height/2 + 20, title)

    c.setFillColor(HexColor("#ffbe0b"))
    c.setFont("Helvetica", 24)
    sw = c.stringWidth(subtitle, "Helvetica", 24)
    c.drawString((width - sw)/2, height/2 - 30, subtitle)

    c.setFillColor(Color(1, 1, 1, 0.8))
    c.setFont("Helvetica-Bold", 16)
    aw = c.stringWidth(author, "Helvetica-Bold", 16)
    c.drawString((width - aw)/2, 50, author)


def create_cosmic_mandala(c, width, height, title="ENLIGHTENMENT",
                         subtitle="",
                         author="Author Name"):
    """
    Cosmic mandala with extreme detail.

    Elements: ~20,000+
    Intensity: Extreme
    """
    # Space background
    c.setFillColor(HexColor("#050505"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # 3000 stars
    colors = PALETTES["neon"]
    for _ in range(3000):
        sx = random.random() * width
        sy = random.random() * height
        brightness = random.uniform(0.1, 1)
        size = random.uniform(0.3, 2.5)

        if random.random() > 0.9:
            color = random.choice(colors)
            r, g, b = hex_to_rgb(color)
            c.setFillColor(Color(r, g, b, brightness))
        else:
            c.setFillColor(Color(1, 1, 1, brightness))
        c.circle(sx, sy, size, fill=1, stroke=0)

    # Nebula clouds
    nebula_colors = ["#ff006e", "#8338ec", "#3a86ff"]
    for _ in range(200):
        nx = width/2 + random.gauss(0, 150)
        ny = height/2 + random.gauss(0, 150)
        size = random.uniform(20, 80)
        color = random.choice(nebula_colors)
        r, g, b = hex_to_rgb(color)
        c.setFillColor(Color(r, g, b, 0.03))
        c.circle(nx, ny, size, fill=1, stroke=0)

    # MEGA mandala
    mandala_colors = ["#ff006e", "#fb5607", "#ffbe0b", "#06d6a0", "#3a86ff",
                     "#8338ec", "#ff006e", "#ffffff"]
    draw_complex_mandala(c, width/2, height/2, 280, 12, 8, mandala_colors)

    # Outer recursive circles
    for i in range(16):
        angle = 2 * math.pi * i / 16
        cx = width/2 + 320 * math.cos(angle)
        cy = height/2 + 320 * math.sin(angle)
        draw_recursive_circles(c, cx, cy, 40, 0, 4, mandala_colors)

    # Lissajous halo
    for i in range(12):
        draw_lissajous_curve(c, width/2, height/2, i + 1, i + 2, i * 0.3,
                            300 + i * 5, 300 + i * 5,
                            mandala_colors[i % len(mandala_colors)], 1000)

    # Central glow
    for i in range(30):
        radius = 30 - i
        alpha = 0.05 + (i / 30) * 0.1
        c.setFillColor(Color(1, 1, 1, alpha))
        c.circle(width/2, height/2, radius, fill=1, stroke=0)

    # Title
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 60)
    tw = c.stringWidth(title, "Helvetica-Bold", 60)
    c.drawString((width - tw)/2, 100, title)

    c.setFont("Helvetica", 16)
    aw = c.stringWidth(author, "Helvetica", 16)
    c.drawString((width - aw)/2, 60, author)


def create_quantum_field(c, width, height, title="QUANTUM",
                        subtitle="ENTANGLEMENT",
                        author="Author Name"):
    """
    Quantum field visualization with probability clouds.

    Elements: ~10,000+
    Intensity: High
    """
    # Dark base
    c.setFillColor(HexColor("#000510"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    quantum_colors = ["#00ffff", "#ff00ff", "#ffff00", "#00ff00"]

    # Probability clouds
    for _ in range(150):
        qx = random.random() * width
        qy = random.random() * height
        color = random.choice(quantum_colors)
        r, g, b = hex_to_rgb(color)

        for _ in range(20):
            offset_x = random.gauss(0, 30)
            offset_y = random.gauss(0, 30)
            size = random.uniform(5, 25)
            c.setFillColor(Color(r, g, b, 0.05))
            c.circle(qx + offset_x, qy + offset_y, size, fill=1, stroke=0)

    # Wave functions
    for i in range(20):
        color = quantum_colors[i % len(quantum_colors)]
        r, g, b = hex_to_rgb(color)
        c.setStrokeColor(Color(r, g, b, 0.5))
        c.setLineWidth(1)

        y_base = height * (i + 1) / 21
        frequency = random.uniform(0.01, 0.05)
        amplitude = random.uniform(20, 60)
        phase = random.uniform(0, 2 * math.pi)

        path = c.beginPath()
        for x in range(0, int(width), 3):
            y = y_base + amplitude * math.sin(x * frequency + phase)
            if x == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        c.drawPath(path, fill=0, stroke=1)

    # Spiral particle tracks
    for _ in range(30):
        start_x = random.random() * width
        start_y = random.random() * height

        color = random.choice(quantum_colors)
        r, g, b = hex_to_rgb(color)
        c.setStrokeColor(Color(r, g, b, 0.7))
        c.setLineWidth(1)

        path = c.beginPath()
        path.moveTo(start_x, start_y)
        for t in range(100):
            angle = t * 0.2 + random.uniform(-0.1, 0.1)
            radius = t * 0.5
            x = start_x + radius * math.cos(angle)
            y = start_y + radius * math.sin(angle)
            path.lineTo(x, y)
        c.drawPath(path, fill=0, stroke=1)

    # Interference pattern
    draw_interference_waves(c, width * 0.3, height * 0.3, width * 0.4, height * 0.4, 3,
                           ["#000510", "#001030", "#002050", "#003070", "#004090"])

    # Entanglement pairs
    for _ in range(10):
        p1 = (random.uniform(50, width-50), random.uniform(50, height-50))
        p2 = (random.uniform(50, width-50), random.uniform(50, height-50))

        for offset in range(5):
            c.setStrokeColor(Color(0, 1, 1, 0.2 - offset * 0.03))
            c.setLineWidth(5 - offset)
            c.line(p1[0], p1[1], p2[0], p2[1])

        c.setFillColor(HexColor("#00ffff"))
        c.circle(p1[0], p1[1], 5, fill=1, stroke=0)
        c.circle(p2[0], p2[1], 5, fill=1, stroke=0)

    # Title
    c.setFillColor(HexColor("#00ffff"))
    c.setFont("Helvetica-Bold", 64)
    tw = c.stringWidth(title, "Helvetica-Bold", 64)
    c.drawString((width - tw)/2, height - 80, title)

    c.setFillColor(HexColor("#ff00ff"))
    c.setFont("Helvetica-Bold", 48)
    sw = c.stringWidth(subtitle, "Helvetica-Bold", 48)
    c.drawString((width - sw)/2, height - 140, subtitle)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 14)
    aw = c.stringWidth(author, "Helvetica", 14)
    c.drawString((width - aw)/2, 40, author)


# Style registry for this module
COSMIC_STYLES = {
    "cosmic-explosion": create_cosmic_explosion,
    "fractal-universe": create_fractal_universe,
    "cosmic-mandala": create_cosmic_mandala,
    "quantum-field": create_quantum_field,
}
