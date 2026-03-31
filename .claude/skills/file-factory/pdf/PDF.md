---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need to fill out a PDF form, read forms.md and follow its instructions.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see forms.md) | See forms.md |

## Artistic PDF Covers (NEW)

Create stunning generative-art style book covers using pure Python - no image generation models required!

### Quick Start

```python
from artistic_covers.generator import ArtisticCoverGenerator

gen = ArtisticCoverGenerator()

# Single style
gen.create_cover("cosmic-explosion", "cover.pdf", title="MY BOOK")

# Blend multiple styles
gen.create_cover(
    styles=["fractal", "particles", "mandala"],
    intensity="extreme",
    output="blended.pdf"
)
```

### Available Styles

| Category | Styles |
|----------|--------|
| **Cosmic** | `cosmic-explosion`, `fractal-universe`, `cosmic-mandala`, `quantum-field` |
| **Geometric** | `geometric-chaos`, `minimalist-bold`, `brutalist`, `op-art`, `data-viz` |
| **Organic** | `organic-flow`, `botanical`, `bio-mechanical` |
| **Retro/Art** | `retro-futurism`, `abstract-expressionist`, `psychedelic-mandala`, `glitch-reality` |
| **Extreme** | `maximalist`, `ultimate-chaos` |

### Intensity Levels

- `minimal`: 100-500 elements, clean and elegant
- `low`: 500-1000 elements, subtle artistic touches
- `medium`: 1000-5000 elements, clearly artistic
- `high`: 5000-15000 elements, impressive statement
- `extreme`: 15000-40000 elements, mind-blowing
- `maximum`: 40000-60000+ elements, absolute chaos

### Blendable Components

```python
styles=["fractal", "particles", "mandala", "lissajous",
        "voronoi", "flow", "waves", "mosaic", "glitch",
        "polygons", "dna", "mountains", "interference",
        "moire", "spirals", "opart", "text_texture"]

# Or use everything:
styles=["all"]
```

### Color Palettes

```python
palette="neon"     # Vibrant pink, purple, blue, green, gold
palette="cosmic"   # Space black with neon accents
palette="organic"  # Teal, coral, yellow naturals
palette="retro"    # Synthwave purple, magenta, cyan
palette="glitch"   # Pure RGB primaries
palette="minimal"  # Black, white, accent
```

**Full documentation**: See `artistic-covers/ARTISTIC-STYLES.md`

**Meta-prompt for extending**: See `artistic-covers/META-PROMPT.md`

## PDF from HTML Slides (Playwright + pdf-lib)

When you have HTML slides (e.g., from the PPTX workflow) and need to generate a PDF:

### Dependencies

Install in `pptx/scripts/node_modules`:
```bash
cd C:\Users\Tony\.claude\skills\file-factory\pptx\scripts
npm install pdf-lib
```

Note: `playwright` is already installed in this location.

### Build Script Example

Create `build_pdf.js` in your workspace:

```javascript
const { chromium } = require('C:/Users/Tony/.claude/skills/file-factory/pptx/node_modules/playwright');
const { PDFDocument } = require('C:/Users/Tony/.claude/skills/file-factory/pptx/scripts/node_modules/pdf-lib');
const fs = require('fs');
const path = require('path');

async function buildPDF() {
    const slideDir = './slides';  // Directory with HTML files
    const outputPath = './output.pdf';

    const slides = [
        'slide01.html',
        'slide02.html',
        // ... add all slides
    ];

    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.setViewportSize({ width: 960, height: 540 });

    const pdfBuffers = [];

    for (const slideFile of slides) {
        const slidePath = path.join(slideDir, slideFile);
        await page.goto(`file:///${slidePath.replace(/\\/g, '/')}`);
        await page.waitForLoadState('networkidle');

        // IMPORTANT: Use 'in' units, not 'pt' (Playwright doesn't support pt)
        const pdfBuffer = await page.pdf({
            width: '10in',      // 720pt = 10in at 72dpi
            height: '5.625in', // 405pt = 5.625in (16:9 aspect)
            printBackground: true,
            margin: { top: 0, right: 0, bottom: 0, left: 0 }
        });
        pdfBuffers.push(pdfBuffer);
    }

    await browser.close();

    // Merge all PDFs
    const mergedPdf = await PDFDocument.create();
    for (const pdfBuffer of pdfBuffers) {
        const pdf = await PDFDocument.load(pdfBuffer);
        const pages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
        pages.forEach(p => mergedPdf.addPage(p));
    }

    fs.writeFileSync(outputPath, await mergedPdf.save());
    console.log(`PDF saved to: ${outputPath}`);
}

buildPDF().catch(console.error);
```

### Key Notes

- **Dimension units**: Playwright accepts `in`, `mm`, `cm` - NOT `pt`
- **16:9 slides**: Use `width: '10in'`, `height: '5.625in'`
- **4:3 slides**: Use `width: '10in'`, `height: '7.5in'`
- **Dependencies location**: `pptx/scripts/node_modules` (same as PPTX pipeline)

## Next Steps

- For advanced pypdfium2 usage, see reference.md
- For JavaScript libraries (pdf-lib), see reference.md
- If you need to fill out a PDF form, follow the instructions in forms.md
- For troubleshooting guides, see reference.md
- **For artistic book covers**, see `artistic-covers/ARTISTIC-STYLES.md`
- **For HTML slides to PDF**, see the Playwright + pdf-lib section above
