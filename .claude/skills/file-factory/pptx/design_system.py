#!/usr/bin/env python3
"""
Shared Design System for Professional Presentations
Provides consistent colors, typography, and helper functions across all decks
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Professional Color Palette
PRIMARY = RGBColor(30, 41, 59)      # Dark slate - Main text/elements
ACCENT = RGBColor(99, 102, 241)     # Indigo - Highlights and accents
GRAY = RGBColor(148, 163, 184)      # Slate gray - Secondary elements
WHITE = RGBColor(255, 255, 255)     # White - Backgrounds/contrast

# Tier colors for ranking tables
S_TIER_COLOR = ACCENT
A_TIER_COLOR = GRAY
B_TIER_COLOR = RGBColor(200, 200, 200)

# Typography Sizes
TITLE_SIZE = Pt(48)      # Title slides
HEADER_SIZE = Pt(36)     # Section headers
CONTENT_SIZE = Pt(20)    # Body text, bullet points
SMALL_SIZE = Pt(16)      # Captions, footnotes
TABLE_SIZE = Pt(14)      # Table content


def create_presentation():
    """Create a new presentation with widescreen format"""
    prs = Presentation()
    prs.slide_width = Inches(16)   # 16:9 widescreen
    prs.slide_height = Inches(9)
    return prs


def add_title_slide(prs, title, subtitle):
    """Add a title slide with diagonal accent shape"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # Add diagonal accent shape
    accent_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(-2), Inches(-2),
        Inches(10), Inches(6)
    )
    accent_shape.fill.solid()
    accent_shape.fill.fore_color.rgb = ACCENT
    accent_shape.line.fill.background()
    accent_shape.rotation = 15

    # Add title
    title_box = slide.shapes.add_textbox(Inches(2), Inches(3), Inches(12), Inches(2))
    title_frame = title_box.text_frame
    title_frame.clear()
    p = title_frame.add_paragraph()
    p.text = title
    p.font.size = TITLE_SIZE
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    # Add subtitle
    subtitle_box = slide.shapes.add_textbox(Inches(2), Inches(5.5), Inches(10), Inches(1))
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.clear()
    p = subtitle_frame.add_paragraph()
    p.text = subtitle
    p.font.size = Pt(24)
    p.font.color.rgb = GRAY

    return slide


def add_standard_slide(prs, title, bullet_points):
    """Add a standard content slide with accent line and bullet points"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # Add accent line at top
    line = slide.shapes.add_connector(1, Inches(0), Inches(0.5), Inches(16), Inches(0.5))
    line.line.width = Pt(3)
    line.line.color.rgb = ACCENT

    # Add title
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.8), Inches(14), Inches(1))
    p = title_box.text_frame.add_paragraph()
    p.text = title
    p.font.size = HEADER_SIZE
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    # Add content
    content_box = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(13), Inches(5.5))
    for item in bullet_points:
        p = content_box.text_frame.add_paragraph()
        p.text = item
        p.font.size = CONTENT_SIZE
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(16)
        p.level = 0

    return slide


def add_tier_table_slide(prs, title, tier_data):
    """
    Add a slide with a formatted tier table
    tier_data: list of dicts with keys 'tier', 'tool', 'features', 'reasoning'
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Add accent line
    line = slide.shapes.add_connector(1, Inches(0), Inches(0.5), Inches(16), Inches(0.5))
    line.line.width = Pt(3)
    line.line.color.rgb = ACCENT

    # Add title
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.8), Inches(14), Inches(1))
    p = title_box.text_frame.add_paragraph()
    p.text = title
    p.font.size = HEADER_SIZE
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    # Add table
    rows = len(tier_data) + 1  # +1 for header
    cols = 4
    table = slide.shapes.add_table(rows, cols, Inches(1), Inches(2.5), Inches(14), Inches(5)).table

    # Set column widths
    table.columns[0].width = Inches(1.5)  # Tier
    table.columns[1].width = Inches(4)    # Tool
    table.columns[2].width = Inches(5)    # Features
    table.columns[3].width = Inches(3.5)  # Reasoning

    # Header row
    headers = ['Tier', 'Tool', 'Key Features', 'Reasoning']
    for col_idx, header in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY
        cell.text_frame.paragraphs[0].font.color.rgb = WHITE
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = TABLE_SIZE

    # Data rows
    for row_idx, data in enumerate(tier_data, start=1):
        # Tier cell with color
        tier_cell = table.cell(row_idx, 0)
        tier_cell.text = data['tier']
        tier_cell.fill.solid()
        if data['tier'].startswith('S'):
            tier_cell.fill.fore_color.rgb = S_TIER_COLOR
            tier_cell.text_frame.paragraphs[0].font.color.rgb = WHITE
        elif data['tier'].startswith('A'):
            tier_cell.fill.fore_color.rgb = A_TIER_COLOR
            tier_cell.text_frame.paragraphs[0].font.color.rgb = WHITE
        else:
            tier_cell.fill.fore_color.rgb = B_TIER_COLOR
        tier_cell.text_frame.paragraphs[0].font.bold = True
        tier_cell.text_frame.paragraphs[0].font.size = TABLE_SIZE

        # Other cells
        for col_idx, key in enumerate(['tool', 'features', 'reasoning'], start=1):
            cell = table.cell(row_idx, col_idx)
            cell.text = data[key]
            cell.text_frame.paragraphs[0].font.size = TABLE_SIZE
            cell.text_frame.paragraphs[0].font.color.rgb = PRIMARY

    return slide


def add_comparison_slide(prs, title, left_header, left_items, right_header, right_items):
    """Add a two-column comparison slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Add accent line
    line = slide.shapes.add_connector(1, Inches(0), Inches(0.5), Inches(16), Inches(0.5))
    line.line.width = Pt(3)
    line.line.color.rgb = ACCENT

    # Add title
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.8), Inches(14), Inches(1))
    p = title_box.text_frame.add_paragraph()
    p.text = title
    p.font.size = HEADER_SIZE
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    # Left column header
    left_header_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(1), Inches(2.5),
        Inches(6.5), Inches(0.6)
    )
    left_header_box.fill.solid()
    left_header_box.fill.fore_color.rgb = GRAY
    left_header_box.text_frame.text = left_header
    left_header_box.text_frame.paragraphs[0].font.color.rgb = WHITE
    left_header_box.text_frame.paragraphs[0].font.bold = True
    left_header_box.text_frame.paragraphs[0].font.size = Pt(22)
    left_header_box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Right column header
    right_header_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(8.5), Inches(2.5),
        Inches(6.5), Inches(0.6)
    )
    right_header_box.fill.solid()
    right_header_box.fill.fore_color.rgb = ACCENT
    right_header_box.text_frame.text = right_header
    right_header_box.text_frame.paragraphs[0].font.color.rgb = WHITE
    right_header_box.text_frame.paragraphs[0].font.bold = True
    right_header_box.text_frame.paragraphs[0].font.size = Pt(22)
    right_header_box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Left column content
    left_content = slide.shapes.add_textbox(Inches(1.5), Inches(3.5), Inches(6), Inches(4.5))
    for item in left_items:
        p = left_content.text_frame.add_paragraph()
        p.text = item
        p.font.size = CONTENT_SIZE
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(12)

    # Right column content
    right_content = slide.shapes.add_textbox(Inches(8.8), Inches(3.5), Inches(6), Inches(4.5))
    for item in right_items:
        p = right_content.text_frame.add_paragraph()
        p.text = item
        p.font.size = CONTENT_SIZE
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(12)

    return slide


def add_image_slide(prs, title, image_path, caption=""):
    """Add a slide with an embedded image"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Add accent line
    line = slide.shapes.add_connector(1, Inches(0), Inches(0.5), Inches(16), Inches(0.5))
    line.line.width = Pt(3)
    line.line.color.rgb = ACCENT

    # Add title
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.8), Inches(14), Inches(1))
    p = title_box.text_frame.add_paragraph()
    p.text = title
    p.font.size = HEADER_SIZE
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    # Add image
    slide.shapes.add_picture(
        image_path,
        Inches(2), Inches(2.5),
        width=Inches(12)
    )

    # Add caption if provided
    if caption:
        caption_box = slide.shapes.add_textbox(Inches(2), Inches(7.5), Inches(12), Inches(0.8))
        p = caption_box.text_frame.add_paragraph()
        p.text = caption
        p.font.size = SMALL_SIZE
        p.font.color.rgb = GRAY
        p.alignment = PP_ALIGN.CENTER

    return slide
