# PDF Processing Advanced Reference

This document contains advanced PDF processing features, detailed examples, and additional libraries not covered in the main skill instructions.

## Complexity Levels

Choose the appropriate complexity level for your PDF document:

| Level | Name | Layout | Graphics | Interactivity | Best For |
|-------|------|--------|----------|---------------|----------|
| **1** | Ultra-Minimalistic | Single column | None | None | Text exports, simple letters |
| **2** | Clean Professional | Headers/footers | Minimal | Links | Reports, proposals |
| **3** | Enhanced | Two-column | Images | TOC links | Guides, manuals |
| **4** | Complex | Multi-section | Charts, tables | Form fields | Brochures, catalogs |
| **5** | Extreme | Magazine style | Full graphics | Interactive | Portfolios, lookbooks |
| **6** | Ultra-Extreme | Art piece | Maximum | All features | Showcase documents |

---

### Level 1: Ultra-Minimalistic

Clean text documents with maximum whitespace. Content breathes.

**Characteristics:**
- Single column layout
- Generous margins (1"+)
- Single serif font (Times, Georgia)
- Black text only
- No images, tables, or graphics
- No headers/footers

**Python Pattern (reportlab):**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

doc = SimpleDocTemplate("level1_minimal.pdf", pagesize=letter,
    leftMargin=1*inch, rightMargin=1*inch,
    topMargin=1*inch, bottomMargin=1*inch)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title',
    fontName='Times-Bold', fontSize=18, spaceAfter=24,
    alignment=0)  # Left aligned
body_style = ParagraphStyle('Body',
    fontName='Times-Roman', fontSize=12, leading=18,
    spaceAfter=12)

elements = [
    Paragraph("Executive Summary", title_style),
    Spacer(1, 12),
    Paragraph("This document presents the key findings from our quarterly analysis. "
              "The results indicate steady growth across all segments.", body_style),
    Paragraph("Key metrics have improved by 15% year-over-year, exceeding initial "
              "projections and setting a strong foundation for continued expansion.", body_style),
]

doc.build(elements)
```

**JavaScript Pattern (pdf-lib):**
```javascript
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import fs from 'fs';

async function createMinimalPDF() {
    const pdfDoc = await PDFDocument.create();
    const timesRoman = await pdfDoc.embedFont(StandardFonts.TimesRoman);
    const timesBold = await pdfDoc.embedFont(StandardFonts.TimesRomanBold);

    const page = pdfDoc.addPage([612, 792]); // Letter size
    const { width, height } = page.getSize();
    const margin = 72; // 1 inch

    // Title
    page.drawText('Executive Summary', {
        x: margin,
        y: height - margin - 24,
        size: 18,
        font: timesBold,
        color: rgb(0, 0, 0)
    });

    // Body text
    page.drawText('This document presents the key findings from our quarterly analysis.', {
        x: margin,
        y: height - margin - 60,
        size: 12,
        font: timesRoman,
        color: rgb(0, 0, 0)
    });

    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('level1_minimal.pdf', pdfBytes);
}
```

---

### Level 2: Clean Professional

Balanced design with subtle structure. Professional without clutter.

**Characteristics:**
- Headers and footers with page numbers
- 2-3 colors (primary, accent, text)
- Section headings with color
- Basic tables for data
- Hyperlinks
- Professional sans-serif font

**Python Pattern (reportlab):**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Colors
PRIMARY = colors.HexColor('#1F4E79')
ACCENT = colors.HexColor('#2E75B6')
TEXT = colors.HexColor('#333333')

def header_footer(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFillColor(PRIMARY)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(72, 756, "Quarterly Report 2026")
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2)
    canvas.line(72, 750, 540, 750)
    # Footer
    canvas.setFillColor(TEXT)
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(306, 30, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate("level2_professional.pdf", pagesize=letter)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title',
    fontName='Helvetica-Bold', fontSize=24, textColor=PRIMARY,
    spaceAfter=20, alignment=1)
heading_style = ParagraphStyle('Heading',
    fontName='Helvetica-Bold', fontSize=14, textColor=PRIMARY,
    spaceBefore=20, spaceAfter=10)
body_style = ParagraphStyle('Body',
    fontName='Helvetica', fontSize=11, textColor=TEXT,
    leading=16, spaceAfter=10)

# Table data
table_data = [
    ['Metric', 'Q1', 'Q2', 'Q3', 'Q4'],
    ['Revenue', '$1.2M', '$1.4M', '$1.5M', '$1.8M'],
    ['Users', '12,500', '15,200', '18,400', '22,100'],
    ['Growth', '+12%', '+15%', '+18%', '+21%'],
]

table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F2F2')),
]))

elements = [
    Paragraph("Annual Performance Report", title_style),
    Paragraph("Key Metrics Overview", heading_style),
    Paragraph("The following table summarizes our quarterly performance metrics.", body_style),
    table,
]

doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
```

**Color Palette:**
```python
L2_CORPORATE = {
    "primary": "#1F4E79",
    "accent": "#2E75B6",
    "text": "#333333",
    "light_bg": "#F2F2F2",
    "white": "#FFFFFF"
}
```

---

### Level 3: Enhanced

Visual hierarchy with intentional design. Engaging but not overwhelming.

**Characteristics:**
- Two-column layouts for content
- Section dividers with color bars
- 1-2 images per page
- Styled tables with alternating rows
- Table of contents with links
- 3-4 colors with clear purpose
- Callout boxes for emphasis

**Python Pattern (reportlab):**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus import KeepTogether, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Colors
PRIMARY = colors.HexColor('#2E75B6')
SECONDARY = colors.HexColor('#5B9BD5')
ACCENT = colors.HexColor('#ED7D31')
TEXT = colors.HexColor('#333333')
LIGHT_BG = colors.HexColor('#DEEBF7')

# Callout box style
def create_callout(text, color=ACCENT):
    callout_data = [[Paragraph(text, ParagraphStyle('Callout',
        fontName='Helvetica-Bold', fontSize=11, textColor=colors.white))]]
    callout = Table(callout_data, colWidths=[4*inch])
    callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return callout

# Two-column layout
def create_two_column(left_content, right_content):
    data = [[left_content, right_content]]
    table = Table(data, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return table

# Section divider
def section_divider(title):
    data = [[Paragraph(title, ParagraphStyle('SectionTitle',
        fontName='Helvetica-Bold', fontSize=14, textColor=colors.white))]]
    divider = Table(data, colWidths=[6.5*inch])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return divider
```

---

### Level 4: Complex

Rich layouts with multiple visual components. Information-dense but organized.

**Characteristics:**
- Multi-section layouts with sidebar
- 4-5 colors in cohesive palette
- Multiple charts and data tables
- Image galleries
- Form fields (fillable)
- Callout boxes and stat panels
- Page borders and decorative elements

**Python Pattern (reportlab):**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

# Dark theme colors
DARK_BG = colors.HexColor('#1F2937')
SURFACE = colors.HexColor('#374151')
PRIMARY = colors.HexColor('#3B82F6')
SUCCESS = colors.HexColor('#10B981')
WARNING = colors.HexColor('#F59E0B')
DANGER = colors.HexColor('#EF4444')
TEXT_LIGHT = colors.HexColor('#F9FAFB')
TEXT_MUTED = colors.HexColor('#9CA3AF')

# KPI Card
def create_kpi_card(title, value, change, color):
    data = [
        [Paragraph(title, ParagraphStyle('KPITitle',
            fontName='Helvetica', fontSize=9, textColor=TEXT_MUTED))],
        [Paragraph(value, ParagraphStyle('KPIValue',
            fontName='Helvetica-Bold', fontSize=28, textColor=TEXT_LIGHT))],
        [Paragraph(change, ParagraphStyle('KPIChange',
            fontName='Helvetica-Bold', fontSize=11, textColor=color))],
    ]
    card = Table(data, colWidths=[1.5*inch])
    card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SURFACE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (0, 0), 10),
        ('BOTTOMPADDING', (0, -1), (0, -1), 10),
        ('LINEBEFORE', (0, 0), (0, -1), 3, color),
    ]))
    return card

# Stats bar
def create_stats_bar(stats):
    cells = []
    for label, value, color in stats:
        cells.append([
            Paragraph(value, ParagraphStyle('StatValue',
                fontName='Helvetica-Bold', fontSize=20, textColor=color, alignment=1)),
            Paragraph(label, ParagraphStyle('StatLabel',
                fontName='Helvetica', fontSize=9, textColor=TEXT_MUTED, alignment=1)),
        ])

    data = [[Table(cell, colWidths=[1.2*inch]) for cell in cells]]
    bar = Table(data, colWidths=[1.2*inch] * len(stats))
    bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    return bar

# Bar chart
def create_bar_chart(data, categories, title):
    drawing = Drawing(400, 200)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data
    bc.categoryAxis.categoryNames = categories
    bc.valueAxis.valueMin = 0
    bc.bars[0].fillColor = PRIMARY

    drawing.add(bc)
    drawing.add(String(200, 180, title, fontSize=12, fillColor=TEXT_LIGHT, textAnchor='middle'))

    return drawing
```

**Color Palette:**
```python
L4_DARK_THEME = {
    "background": "#1F2937",
    "surface": "#374151",
    "primary": "#3B82F6",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text_light": "#F9FAFB",
    "text_muted": "#9CA3AF"
}
```

---

### Level 5: Extreme

Dense layouts with strong visual impact. Every inch serves a purpose.

**Characteristics:**
- Magazine-style layouts
- 5-6 colors in themed palette
- Full-bleed images and backgrounds
- Multiple charts per page
- Sidebar navigation panels
- Thick colored borders
- Stat callouts with icons
- Pull quotes with styling

**Python Pattern (reportlab):**
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

# Cyberpunk theme
BG = colors.HexColor('#0A0A0F')
SURFACE = colors.HexColor('#1A1A2E')
NEON_BLUE = colors.HexColor('#00D4FF')
PURPLE = colors.HexColor('#8B5CF6')
PINK = colors.HexColor('#EC4899')
GREEN = colors.HexColor('#10B981')
GOLD = colors.HexColor('#FBBF24')

def create_extreme_pdf():
    c = canvas.Canvas("level5_extreme.pdf", pagesize=letter)
    width, height = letter

    # Full page dark background
    c.setFillColor(BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Neon header bar
    c.setFillColor(SURFACE)
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)

    # Glow border on header
    c.setStrokeColor(NEON_BLUE)
    c.setLineWidth(3)
    c.line(0, height - 60, width, height - 60)

    # Title with neon effect
    c.setFillColor(NEON_BLUE)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 40, "◈ ANALYTICS DASHBOARD ◈")

    # Stats cards row
    card_width = 120
    card_height = 80
    cards = [
        ("$4.2M", "Revenue", NEON_BLUE),
        ("847K", "Users", PURPLE),
        ("2.1M", "Sessions", PINK),
        ("4.7%", "Conversion", GREEN),
    ]

    x_start = 36
    for i, (value, label, color) in enumerate(cards):
        x = x_start + i * (card_width + 20)
        y = height - 160

        # Card background with glow border
        c.setFillColor(SURFACE)
        c.setStrokeColor(color)
        c.setLineWidth(2)
        c.roundRect(x, y, card_width, card_height, 5, fill=True, stroke=True)

        # Value
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(x + card_width/2, y + 45, value)

        # Label
        c.setFillColor(color)
        c.setFont("Helvetica", 10)
        c.drawCentredString(x + card_width/2, y + 15, label)

    # Heat map section
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(36, height - 200, "◆ PERFORMANCE MATRIX")

    # Draw heat map grid
    cell_size = 40
    for row in range(4):
        for col in range(7):
            x = 36 + col * cell_size
            y = height - 280 - row * cell_size
            # Gradient color based on position
            intensity = (row * 7 + col) / 28
            r = int(0x1A + (0x8B - 0x1A) * intensity)
            g = int(0x1A + (0x5C - 0x1A) * intensity)
            b = int(0x2E + (0xF6 - 0x2E) * intensity)
            c.setFillColor(colors.HexColor(f'#{r:02X}{g:02X}{b:02X}'))
            c.rect(x, y, cell_size - 2, cell_size - 2, fill=True, stroke=False)

    c.save()
```

**Color Palette (Cyberpunk):**
```python
L5_CYBERPUNK = {
    "background": "#0A0A0F",
    "surface": "#1A1A2E",
    "neonBlue": "#00D4FF",
    "electricPurple": "#8B5CF6",
    "cyberPink": "#EC4899",
    "matrixGreen": "#10B981",
    "gold": "#FBBF24",
    "text": "#FFFFFF",
    "muted": "#94A3B8"
}
```

---

### Level 6: Ultra-Extreme

Maximum density, artistic expression. PDFs as visual experiences.

**Characteristics:**
- Zero empty space
- 6+ colors in bold themed palette
- Glow effects and neon borders
- Every area filled with content
- Decorative separators (◈◆★⚡)
- Code-style data displays
- Multiple overlapping elements
- Art-piece quality layouts

**Python Pattern (reportlab):**
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Ultra theme
BG = colors.HexColor('#0A0A0F')
DARK = colors.HexColor('#0D1117')
SURFACE = colors.HexColor('#161B22')
PANEL = colors.HexColor('#1A1A2E')
NEON = colors.HexColor('#00D4FF')
PURPLE = colors.HexColor('#8B5CF6')
PINK = colors.HexColor('#EC4899')
GREEN = colors.HexColor('#10B981')
GOLD = colors.HexColor('#FBBF24')

def create_ultra_extreme_pdf():
    c = canvas.Canvas("level6_ultra_extreme.pdf", pagesize=letter)
    width, height = letter

    # Full dark background
    c.setFillColor(BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # === GLOWING HEADER ===
    # Gradient border effect (multiple lines)
    for i, color in enumerate([NEON, PURPLE, PINK]):
        c.setStrokeColor(color)
        c.setLineWidth(2)
        c.line(0, height - 50 - i*2, width, height - 50 - i*2)

    c.setFillColor(DARK)
    c.rect(0, height - 48, width, 48, fill=True, stroke=False)

    c.setFillColor(NEON)
    c.setFont("Courier-Bold", 20)
    c.drawCentredString(width/2, height - 32, "◈◈◈ QUANTUM ANALYTICS NEXUS ◈◈◈")

    # === MEGA STATS PANEL ===
    stats = [
        ("◆ COMPUTE", "1.2 ZF", NEON),
        ("◆ MODELS", "847K", PURPLE),
        ("◆ TOKENS", "4.2T", PINK),
        ("◆ LATENCY", "0.3ms", GREEN),
    ]

    panel_width = 130
    x_start = 20
    for i, (label, value, color) in enumerate(stats):
        x = x_start + i * (panel_width + 10)
        y = height - 140

        # Panel background
        c.setFillColor(PANEL)
        c.rect(x, y, panel_width, 80, fill=True, stroke=False)

        # Glow left border
        c.setStrokeColor(color)
        c.setLineWidth(4)
        c.line(x, y, x, y + 80)

        # Label
        c.setFillColor(color)
        c.setFont("Courier", 9)
        c.drawCentredString(x + panel_width/2, y + 60, label)

        # Value
        c.setFillColor(colors.white)
        c.setFont("Courier-Bold", 24)
        c.drawCentredString(x + panel_width/2, y + 25, value)

        # Glow bar under value
        c.setFillColor(color)
        c.rect(x + 5, y + 5, panel_width - 10, 4, fill=True, stroke=False)

    # === CODE-STYLE DATA STREAM ===
    c.setFillColor(DARK)
    c.rect(20, height - 280, 300, 120, fill=True, stroke=False)

    c.setFillColor(GREEN)
    c.setFont("Courier", 10)
    c.drawString(30, height - 175, "// LIVE_DATA_STREAM")

    code_data = [
        ("timestamp:", "2026-01-04T14:32:17Z", NEON),
        ("inference:", "quantum_v4.model", PURPLE),
        ("throughput:", "1,847,293 tok/s", PINK),
        ("accuracy:", "99.847%", GREEN),
    ]

    y_pos = height - 195
    for key, val, color in code_data:
        c.setFillColor(colors.HexColor('#6A9955'))
        c.setFont("Courier", 9)
        c.drawString(35, y_pos, f"  {key}")
        c.setFillColor(color)
        c.drawString(110, y_pos, val)
        y_pos -= 18

    # === DUAL HEAT MAPS ===
    import random
    random.seed(42)

    c.setFillColor(PURPLE)
    c.setFont("Courier-Bold", 11)
    c.drawString(20, height - 310, "◆ NEURAL ACTIVITY")

    cell_size = 25
    for row in range(5):
        for col in range(10):
            x = 20 + col * cell_size
            y = height - 430 + row * cell_size
            val = random.randint(40, 100)
            intensity = (val - 40) / 60
            r = int(0x1A + (0xEC - 0x1A) * intensity)
            g = int(0x1A + (0x48 - 0x1A) * intensity)
            b = int(0x2E + (0x99 - 0x2E) * intensity)
            c.setFillColor(colors.HexColor(f'#{r:02X}{g:02X}{b:02X}'))
            c.rect(x, y, cell_size - 1, cell_size - 1, fill=True, stroke=False)

    c.setFillColor(NEON)
    c.setFont("Courier-Bold", 11)
    c.drawString(300, height - 310, "◆ EFFICIENCY MAP")

    for row in range(5):
        for col in range(10):
            x = 300 + col * cell_size
            y = height - 430 + row * cell_size
            val = random.randint(60, 100)
            intensity = (val - 60) / 40
            r = int(0x0D + (0x10 - 0x0D) * intensity)
            g = int(0x11 + (0xB9 - 0x11) * intensity)
            b = int(0x17 + (0x81 - 0x17) * intensity)
            c.setFillColor(colors.HexColor(f'#{r:02X}{g:02X}{b:02X}'))
            c.rect(x, y, cell_size - 1, cell_size - 1, fill=True, stroke=False)

    # === DECORATIVE FOOTER ===
    c.setFillColor(DARK)
    c.rect(0, 20, width, 30, fill=True, stroke=False)
    c.setFillColor(GOLD)
    c.setFont("Courier", 10)
    c.drawCentredString(width/2, 32, "★ " * 30)

    c.save()
```

**Themed Palettes for Level 5-6:**
```python
# Cyberpunk
CYBERPUNK = {
    "bg": "#0A0A0F", "surface": "#1A1A2E",
    "neon": "#00D4FF", "purple": "#8B5CF6", "pink": "#EC4899",
    "green": "#10B981", "gold": "#FBBF24"
}

# Anthropic
ANTHROPIC = {
    "bg": "#1F2937", "surface": "#374151",
    "orange": "#DA7756", "coral": "#F5D0C0",
    "green": "#10B981", "blue": "#3B82F6"
}

# Google
GOOGLE = {
    "bg": "#FFFFFF", "surface": "#F8F9FA",
    "blue": "#4285F4", "red": "#EA4335",
    "yellow": "#FBBC04", "green": "#34A853", "purple": "#8E24AA"
}
```

---

### Level Selection Guide

| User Says | Recommended Level |
|-----------|-------------------|
| "Simple PDF" | Level 1 |
| "Professional report" | Level 2 |
| "User guide" / "Manual" | Level 3 |
| "Brochure" / "Catalog" | Level 4 |
| "Portfolio" / "Lookbook" | Level 5 |
| "Push the limits" / "Art piece" | Level 6 |

---

## pypdfium2 Library (Apache/BSD License)

### Overview
pypdfium2 is a Python binding for PDFium (Chromium's PDF library). It's excellent for fast PDF rendering, image generation, and serves as a PyMuPDF replacement.

### Render PDF to Images
```python
import pypdfium2 as pdfium
from PIL import Image

# Load PDF
pdf = pdfium.PdfDocument("document.pdf")

# Render page to image
page = pdf[0]  # First page
bitmap = page.render(
    scale=2.0,  # Higher resolution
    rotation=0  # No rotation
)

# Convert to PIL Image
img = bitmap.to_pil()
img.save("page_1.png", "PNG")

# Process multiple pages
for i, page in enumerate(pdf):
    bitmap = page.render(scale=1.5)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.jpg", "JPEG", quality=90)
```

### Extract Text with pypdfium2
```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    text = page.get_text()
    print(f"Page {i+1} text length: {len(text)} chars")
```

## JavaScript Libraries

### pdf-lib (MIT License)

pdf-lib is a powerful JavaScript library for creating and modifying PDF documents in any JavaScript environment.

#### Load and Manipulate Existing PDF
```javascript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

async function manipulatePDF() {
    // Load existing PDF
    const existingPdfBytes = fs.readFileSync('input.pdf');
    const pdfDoc = await PDFDocument.load(existingPdfBytes);

    // Get page count
    const pageCount = pdfDoc.getPageCount();
    console.log(`Document has ${pageCount} pages`);

    // Add new page
    const newPage = pdfDoc.addPage([600, 400]);
    newPage.drawText('Added by pdf-lib', {
        x: 100,
        y: 300,
        size: 16
    });

    // Save modified PDF
    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('modified.pdf', pdfBytes);
}
```

#### Create Complex PDFs from Scratch
```javascript
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import fs from 'fs';

async function createPDF() {
    const pdfDoc = await PDFDocument.create();

    // Add fonts
    const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
    const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

    // Add page
    const page = pdfDoc.addPage([595, 842]); // A4 size
    const { width, height } = page.getSize();

    // Add text with styling
    page.drawText('Invoice #12345', {
        x: 50,
        y: height - 50,
        size: 18,
        font: helveticaBold,
        color: rgb(0.2, 0.2, 0.8)
    });

    // Add rectangle (header background)
    page.drawRectangle({
        x: 40,
        y: height - 100,
        width: width - 80,
        height: 30,
        color: rgb(0.9, 0.9, 0.9)
    });

    // Add table-like content
    const items = [
        ['Item', 'Qty', 'Price', 'Total'],
        ['Widget', '2', '$50', '$100'],
        ['Gadget', '1', '$75', '$75']
    ];

    let yPos = height - 150;
    items.forEach(row => {
        let xPos = 50;
        row.forEach(cell => {
            page.drawText(cell, {
                x: xPos,
                y: yPos,
                size: 12,
                font: helveticaFont
            });
            xPos += 120;
        });
        yPos -= 25;
    });

    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('created.pdf', pdfBytes);
}
```

#### Advanced Merge and Split Operations
```javascript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

async function mergePDFs() {
    // Create new document
    const mergedPdf = await PDFDocument.create();

    // Load source PDFs
    const pdf1Bytes = fs.readFileSync('doc1.pdf');
    const pdf2Bytes = fs.readFileSync('doc2.pdf');

    const pdf1 = await PDFDocument.load(pdf1Bytes);
    const pdf2 = await PDFDocument.load(pdf2Bytes);

    // Copy pages from first PDF
    const pdf1Pages = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices());
    pdf1Pages.forEach(page => mergedPdf.addPage(page));

    // Copy specific pages from second PDF (pages 0, 2, 4)
    const pdf2Pages = await mergedPdf.copyPages(pdf2, [0, 2, 4]);
    pdf2Pages.forEach(page => mergedPdf.addPage(page));

    const mergedPdfBytes = await mergedPdf.save();
    fs.writeFileSync('merged.pdf', mergedPdfBytes);
}
```

### pdfjs-dist (Apache License)

PDF.js is Mozilla's JavaScript library for rendering PDFs in the browser.

#### Basic PDF Loading and Rendering
```javascript
import * as pdfjsLib from 'pdfjs-dist';

// Configure worker (important for performance)
pdfjsLib.GlobalWorkerOptions.workerSrc = './pdf.worker.js';

async function renderPDF() {
    // Load PDF
    const loadingTask = pdfjsLib.getDocument('document.pdf');
    const pdf = await loadingTask.promise;

    console.log(`Loaded PDF with ${pdf.numPages} pages`);

    // Get first page
    const page = await pdf.getPage(1);
    const viewport = page.getViewport({ scale: 1.5 });

    // Render to canvas
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.height = viewport.height;
    canvas.width = viewport.width;

    const renderContext = {
        canvasContext: context,
        viewport: viewport
    };

    await page.render(renderContext).promise;
    document.body.appendChild(canvas);
}
```

#### Extract Text with Coordinates
```javascript
import * as pdfjsLib from 'pdfjs-dist';

async function extractText() {
    const loadingTask = pdfjsLib.getDocument('document.pdf');
    const pdf = await loadingTask.promise;

    let fullText = '';

    // Extract text from all pages
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();

        const pageText = textContent.items
            .map(item => item.str)
            .join(' ');

        fullText += `\n--- Page ${i} ---\n${pageText}`;

        // Get text with coordinates for advanced processing
        const textWithCoords = textContent.items.map(item => ({
            text: item.str,
            x: item.transform[4],
            y: item.transform[5],
            width: item.width,
            height: item.height
        }));
    }

    console.log(fullText);
    return fullText;
}
```

#### Extract Annotations and Forms
```javascript
import * as pdfjsLib from 'pdfjs-dist';

async function extractAnnotations() {
    const loadingTask = pdfjsLib.getDocument('annotated.pdf');
    const pdf = await loadingTask.promise;

    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const annotations = await page.getAnnotations();

        annotations.forEach(annotation => {
            console.log(`Annotation type: ${annotation.subtype}`);
            console.log(`Content: ${annotation.contents}`);
            console.log(`Coordinates: ${JSON.stringify(annotation.rect)}`);
        });
    }
}
```

## Advanced Command-Line Operations

### poppler-utils Advanced Features

#### Extract Text with Bounding Box Coordinates
```bash
# Extract text with bounding box coordinates (essential for structured data)
pdftotext -bbox-layout document.pdf output.xml

# The XML output contains precise coordinates for each text element
```

#### Advanced Image Conversion
```bash
# Convert to PNG images with specific resolution
pdftoppm -png -r 300 document.pdf output_prefix

# Convert specific page range with high resolution
pdftoppm -png -r 600 -f 1 -l 3 document.pdf high_res_pages

# Convert to JPEG with quality setting
pdftoppm -jpeg -jpegopt quality=85 -r 200 document.pdf jpeg_output
```

#### Extract Embedded Images
```bash
# Extract all embedded images with metadata
pdfimages -j -p document.pdf page_images

# List image info without extracting
pdfimages -list document.pdf

# Extract images in their original format
pdfimages -all document.pdf images/img
```

### qpdf Advanced Features

#### Complex Page Manipulation
```bash
# Split PDF into groups of pages
qpdf --split-pages=3 input.pdf output_group_%02d.pdf

# Extract specific pages with complex ranges
qpdf input.pdf --pages input.pdf 1,3-5,8,10-end -- extracted.pdf

# Merge specific pages from multiple PDFs
qpdf --empty --pages doc1.pdf 1-3 doc2.pdf 5-7 doc3.pdf 2,4 -- combined.pdf
```

#### PDF Optimization and Repair
```bash
# Optimize PDF for web (linearize for streaming)
qpdf --linearize input.pdf optimized.pdf

# Remove unused objects and compress
qpdf --optimize-level=all input.pdf compressed.pdf

# Attempt to repair corrupted PDF structure
qpdf --check input.pdf
qpdf --fix-qdf damaged.pdf repaired.pdf

# Show detailed PDF structure for debugging
qpdf --show-all-pages input.pdf > structure.txt
```

#### Advanced Encryption
```bash
# Add password protection with specific permissions
qpdf --encrypt user_pass owner_pass 256 --print=none --modify=none -- input.pdf encrypted.pdf

# Check encryption status
qpdf --show-encryption encrypted.pdf

# Remove password protection (requires password)
qpdf --password=secret123 --decrypt encrypted.pdf decrypted.pdf
```

## Advanced Python Techniques

### pdfplumber Advanced Features

#### Extract Text with Precise Coordinates
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    
    # Extract all text with coordinates
    chars = page.chars
    for char in chars[:10]:  # First 10 characters
        print(f"Char: '{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")
    
    # Extract text by bounding box (left, top, right, bottom)
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

#### Advanced Table Extraction with Custom Settings
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]
    
    # Extract tables with custom settings for complex layouts
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)
    
    # Visual debugging for table extraction
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

### reportlab Advanced Features

#### Create Professional Reports with Tables
```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Sample data
data = [
    ['Product', 'Q1', 'Q2', 'Q3', 'Q4'],
    ['Widgets', '120', '135', '142', '158'],
    ['Gadgets', '85', '92', '98', '105']
]

# Create PDF with table
doc = SimpleDocTemplate("report.pdf")
elements = []

# Add title
styles = getSampleStyleSheet()
title = Paragraph("Quarterly Sales Report", styles['Title'])
elements.append(title)

# Add table with advanced styling
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(table)

doc.build(elements)
```

## Complex Workflows

### Extract Figures/Images from PDF

#### Method 1: Using pdfimages (fastest)
```bash
# Extract all images with original quality
pdfimages -all document.pdf images/img
```

#### Method 2: Using pypdfium2 + Image Processing
```python
import pypdfium2 as pdfium
from PIL import Image
import numpy as np

def extract_figures(pdf_path, output_dir):
    pdf = pdfium.PdfDocument(pdf_path)
    
    for page_num, page in enumerate(pdf):
        # Render high-resolution page
        bitmap = page.render(scale=3.0)
        img = bitmap.to_pil()
        
        # Convert to numpy for processing
        img_array = np.array(img)
        
        # Simple figure detection (non-white regions)
        mask = np.any(img_array != [255, 255, 255], axis=2)
        
        # Find contours and extract bounding boxes
        # (This is simplified - real implementation would need more sophisticated detection)
        
        # Save detected figures
        # ... implementation depends on specific needs
```

### Batch PDF Processing with Error Handling
```python
import os
import glob
from pypdf import PdfReader, PdfWriter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_process_pdfs(input_dir, operation='merge'):
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if operation == 'merge':
        writer = PdfWriter()
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Processed: {pdf_file}")
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")
                continue
        
        with open("batch_merged.pdf", "wb") as output:
            writer.write(output)
    
    elif operation == 'extract_text':
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                output_file = pdf_file.replace('.pdf', '.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                logger.info(f"Extracted text from: {pdf_file}")
                
            except Exception as e:
                logger.error(f"Failed to extract text from {pdf_file}: {e}")
                continue
```

### Advanced PDF Cropping
```python
from pypdf import PdfWriter, PdfReader

reader = PdfReader("input.pdf")
writer = PdfWriter()

# Crop page (left, bottom, right, top in points)
page = reader.pages[0]
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750

writer.add_page(page)
with open("cropped.pdf", "wb") as output:
    writer.write(output)
```

## Performance Optimization Tips

### 1. For Large PDFs
- Use streaming approaches instead of loading entire PDF in memory
- Use `qpdf --split-pages` for splitting large files
- Process pages individually with pypdfium2

### 2. For Text Extraction
- `pdftotext -bbox-layout` is fastest for plain text extraction
- Use pdfplumber for structured data and tables
- Avoid `pypdf.extract_text()` for very large documents

### 3. For Image Extraction
- `pdfimages` is much faster than rendering pages
- Use low resolution for previews, high resolution for final output

### 4. For Form Filling
- pdf-lib maintains form structure better than most alternatives
- Pre-validate form fields before processing

### 5. Memory Management
```python
# Process PDFs in chunks
def process_large_pdf(pdf_path, chunk_size=10):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    for start_idx in range(0, total_pages, chunk_size):
        end_idx = min(start_idx + chunk_size, total_pages)
        writer = PdfWriter()
        
        for i in range(start_idx, end_idx):
            writer.add_page(reader.pages[i])
        
        # Process chunk
        with open(f"chunk_{start_idx//chunk_size}.pdf", "wb") as output:
            writer.write(output)
```

## Troubleshooting Common Issues

### Encrypted PDFs
```python
# Handle password-protected PDFs
from pypdf import PdfReader

try:
    reader = PdfReader("encrypted.pdf")
    if reader.is_encrypted:
        reader.decrypt("password")
except Exception as e:
    print(f"Failed to decrypt: {e}")
```

### Corrupted PDFs
```bash
# Use qpdf to repair
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

### Text Extraction Issues
```python
# Fallback to OCR for scanned PDFs
import pytesseract
from pdf2image import convert_from_path

def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for i, image in enumerate(images):
        text += pytesseract.image_to_string(image)
    return text
```

## License Information

- **pypdf**: BSD License
- **pdfplumber**: MIT License
- **pypdfium2**: Apache/BSD License
- **reportlab**: BSD License
- **poppler-utils**: GPL-2 License
- **qpdf**: Apache License
- **pdf-lib**: MIT License
- **pdfjs-dist**: Apache License