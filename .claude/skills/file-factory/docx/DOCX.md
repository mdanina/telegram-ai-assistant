---
name: docx
description: "Word document creation, editing, and analysis. When Claude needs to work with Word documents (.docx files) for: (1) Creating new documents from scratch, (2) Complex formatting and layouts, (3) Professional reports and brochures, (4) Table-based layouts, or any other document tasks"
license: Proprietary. LICENSE.txt has complete terms
---

# DOCX Creation, Editing, and Analysis

## Overview

Create professional Word documents using the **docx-js** library (JavaScript/Node.js). This workflow supports everything from ultra-minimalistic single-page documents to ultra-extreme multi-page brochures with complex layouts, images, and no empty space.

## Quick Start

```bash
# Ensure docx is installed globally
npm install -g docx

# Create a document
node create-document.js
```

## Complexity Levels

Choose the appropriate complexity level for your document:

| Level | Description | Use Case | Key Features |
|-------|-------------|----------|--------------|
| **Level 1: Ultra-Minimalistic** | Clean, sparse, maximum whitespace | Executive summaries, formal letters | Single font, no colors, simple paragraphs |
| **Level 2: Clean Professional** | Balanced design with subtle accents | Business reports, proposals | 2-3 colors, headers/footers, basic tables |
| **Level 3: Enhanced** | Visual hierarchy with design elements | Marketing docs, internal reports | Multiple styles, colored headers, images |
| **Level 4: Complex** | Rich layouts with multiple components | Brochures, product guides | Multi-column tables, stats bars, icons |
| **Level 5: Extreme** | Dense layouts with visual impact | Portfolio pieces, catalogs | Complex tables, every inch filled, themed |
| **Level 6: Ultra-Extreme** | Maximum density, artistic layouts | Showcase documents, art pieces | Zero whitespace, glowing borders, multi-image |

---

## Level 1: Ultra-Minimalistic

Clean, professional documents with maximum whitespace and simplicity.

```javascript
const { Document, Packer, Paragraph, TextRun } = require('docx');
const fs = require('fs');

const doc = new Document({
    styles: {
        default: { document: { run: { font: "Times New Roman", size: 24 } } }
    },
    sections: [{
        properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
        children: [
            new Paragraph({ children: [new TextRun({ text: "Executive Summary", bold: true, size: 28 })] }),
            new Paragraph({ children: [] }), // Spacer
            new Paragraph({ children: [new TextRun("This document presents our quarterly findings.")] }),
            new Paragraph({ children: [new TextRun("Key metrics have improved by 15% year-over-year.")] }),
        ]
    }]
});

Packer.toBuffer(doc).then(buffer => fs.writeFileSync("minimal.docx", buffer));
```

**Characteristics:**
- Single serif font (Times New Roman or Georgia)
- 1" margins all around
- No colors (black text only)
- No images or tables
- Generous line spacing
- Simple paragraph structure

---

## Level 2: Clean Professional

Balanced design with subtle accents and structure.

```javascript
const { Document, Packer, Paragraph, TextRun, Header, Footer, PageNumber,
        AlignmentType, Table, TableRow, TableCell, BorderStyle, WidthType } = require('docx');

const doc = new Document({
    styles: {
        default: { document: { run: { font: "Arial", size: 22 } } },
        paragraphStyles: [
            { id: "Title", name: "Title", basedOn: "Normal",
              run: { size: 48, bold: true, color: "2B579A" },
              paragraph: { spacing: { after: 200 }, alignment: AlignmentType.CENTER } },
            { id: "Heading1", name: "Heading 1", basedOn: "Normal",
              run: { size: 28, bold: true, color: "2B579A" },
              paragraph: { spacing: { before: 240, after: 120 } } },
        ]
    },
    sections: [{
        headers: { default: new Header({ children: [
            new Paragraph({ alignment: AlignmentType.RIGHT,
                children: [new TextRun({ text: "Company Name", size: 18, color: "666666" })] })
        ] }) },
        footers: { default: new Footer({ children: [
            new Paragraph({ alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "Page " }), new TextRun({ children: [PageNumber.CURRENT] })] })
        ] }) },
        children: [
            new Paragraph({ style: "Title", children: [new TextRun("Annual Report 2026")] }),
            new Paragraph({ style: "Heading1", children: [new TextRun("Overview")] }),
            new Paragraph({ children: [new TextRun("Our company has achieved significant growth...")] }),
        ]
    }]
});
```

**Characteristics:**
- Professional sans-serif font (Arial)
- 2-3 accent colors max
- Headers and footers with page numbers
- Basic styles for titles and headings
- Simple tables for data
- Appropriate whitespace

---

## Level 3-4: Enhanced to Complex

See the full `docx-js.md` reference for detailed syntax. Key additions:

- **Multiple paragraph styles** with visual hierarchy
- **Numbered and bulleted lists** with custom symbols
- **Tables with colored headers** and borders
- **Images** with proper sizing
- **Multi-column layouts** using table grids

---

## Level 5-6: Extreme to Ultra-Extreme

For maximum visual impact documents with zero empty space.

### Color Palette Setup

```javascript
// Cyberpunk/AI Theme
const C = {
    neonBlue: "00D4FF",
    electricPurple: "8B5CF6",
    cyberPink: "EC4899",
    matrixGreen: "10B981",
    deepBlack: "0A0A0F",
    gold: "FBBF24",
    silver: "94A3B8",
    white: "FFFFFF",
};

// Anthropic Theme
const C = {
    anthropicOrange: "DA7756",
    darkOrange: "C4613C",
    lightOrange: "F5D0C0",
    codeGreen: "10B981",
    terminalBlue: "3B82F6",
    charcoal: "1F2937",
    slate: "475569",
    white: "FFFFFF",
};

// Google/Modern Theme
const C = {
    googleBlue: "4285F4",
    googleRed: "EA4335",
    googleYellow: "FBBC04",
    googleGreen: "34A853",
    bananaYellow: "FFE135",
    geminiPurple: "8E24AA",
    deepBlue: "1A237E",
    white: "FFFFFF",
};
```

### Border Helper Functions

```javascript
const border = (color = "333333", size = 1) => ({ style: BorderStyle.SINGLE, size, color });
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const cellB = { top: border(), bottom: border(), left: border(), right: border() };
const thickB = (c) => ({ top: border(c, 3), bottom: border(c, 3), left: border(c, 3), right: border(c, 3) });
const glowB = (c) => ({ top: border(c, 4), bottom: border(c, 4), left: border(c, 4), right: border(c, 4) }); // Glow effect!
```

### Ultra-Extreme Styles

```javascript
const doc = new Document({
    styles: {
        default: { document: { run: { font: "Segoe UI", size: 20 } } },
        paragraphStyles: [
            { id: "CyberTitle", name: "Cyber Title", basedOn: "Normal",
              run: { size: 80, bold: true, color: C.neonBlue, font: "Impact" },
              paragraph: { spacing: { before: 0, after: 0 }, alignment: AlignmentType.CENTER } },
            { id: "NeonHeader", name: "Neon Header", basedOn: "Normal",
              run: { size: 36, bold: true, color: C.electricPurple, font: "Arial Black" },
              paragraph: { spacing: { before: 200, after: 100 } } },
            { id: "GlowText", name: "Glow Text", basedOn: "Normal",
              run: { size: 24, bold: true, color: C.matrixGreen, font: "Consolas" },
              paragraph: { spacing: { before: 50, after: 50 } } },
            { id: "DataStream", name: "Data Stream", basedOn: "Normal",
              run: { size: 16, color: C.neonBlue, font: "Courier New" },
              paragraph: { spacing: { before: 20, after: 20 } } },
        ]
    },
    numbering: {
        config: [
            { reference: "cyber-bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "⚡", alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 400, hanging: 200 } } } }] },
            { reference: "matrix-bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "◆", alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 400, hanging: 200 } } } }] },
            { reference: "check-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "✓", alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 400, hanging: 200 } } } }] },
            { reference: "star-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "★", alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 400, hanging: 200 } } } }] },
            { reference: "arrow-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "→", alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 400, hanging: 200 } } } }] },
        ]
    },
    // ... sections
});
```

### Table-Based Page Filling

The key to zero-whitespace documents is using tables as layout containers:

```javascript
// Full-width stats bar (6 columns)
new Table({
    columnWidths: [1700, 1700, 1700, 1700, 1700, 1700], // Total ~10200 DXA
    rows: [new TableRow({ children: [
        new TableCell({ borders: cellB, shading: { fill: C.deepBlack, type: ShadingType.CLEAR },
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "🧠", size: 28 })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$184B", bold: true, size: 24, color: C.neonBlue })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Market 2026", size: 14, color: C.silver })] })
            ] }),
        // ... repeat for other cells
    ]})]
}),

// Two-column content layout
new Table({
    columnWidths: [5100, 5100],
    rows: [new TableRow({ children: [
        new TableCell({ borders: glowB(C.electricPurple), shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
            children: [
                // Left column content - text, bullets, etc.
            ] }),
        new TableCell({ borders: glowB(C.cyberPink), shading: { fill: "1A1A2E", type: ShadingType.CLEAR },
            children: [
                // Right column content - image, more text
                new Paragraph({ alignment: AlignmentType.CENTER, children: [
                    new ImageRun({ type: "jpg", data: imageBuffer, transformation: { width: 250, height: 180 } })
                ] }),
            ] }),
    ]})]
}),
```

### Images in Ultra-Extreme Documents

```javascript
// Load images at the top
const aiBrain = fs.readFileSync('./images/ai-brain.jpg');
const aiRobot = fs.readFileSync('./images/ai-robot.jpg');

// Use in table cells
new TableCell({
    borders: thickB(C.neonBlue),
    shading: { fill: C.deepBlack, type: ShadingType.CLEAR },
    children: [
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
            new ImageRun({ type: "jpg", data: aiBrain, transformation: { width: 200, height: 150 },
                altText: { title: "AI Brain", description: "Neural network visualization", name: "ai-brain" } })
        ] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
            new TextRun({ text: "Neural Architecture", bold: true, size: 18, color: C.neonBlue })
        ] }),
    ]
}),
```

### Decorative Elements

```javascript
// Decorative border row
new Table({
    columnWidths: [10200],
    rows: [new TableRow({ children: [
        new TableCell({ borders: glowB(C.neonBlue), shading: { fill: C.deepBlack, type: ShadingType.CLEAR },
            children: [new Paragraph({ alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈", size: 18, color: C.neonBlue })] })]
        })
    ]})]
}),

// Code block style
new Table({
    columnWidths: [10200],
    rows: [new TableRow({ children: [
        new TableCell({ borders: border(C.matrixGreen, 2), shading: { fill: "0D1117", type: ShadingType.CLEAR },
            children: [
                new Paragraph({ children: [new TextRun({ text: "// Initialize AI Model", color: "6A9955", font: "Consolas", size: 18 })] }),
                new Paragraph({ children: [new TextRun({ text: "const model = await Claude.init();", color: C.matrixGreen, font: "Consolas", size: 18 })] }),
                new Paragraph({ children: [new TextRun({ text: "const response = await model.generate(prompt);", color: C.neonBlue, font: "Consolas", size: 18 })] }),
            ]
        })
    ]})]
}),
```

---

## Headers and Footers

### Professional Headers

```javascript
headers: {
    default: new Header({
        children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            shading: { fill: C.deepBlack, type: ShadingType.CLEAR },
            children: [
                new TextRun({ text: "◈ ", color: C.neonBlue, size: 16 }),
                new TextRun({ text: "DOCUMENT TITLE", bold: true, size: 16, color: C.neonBlue }),
                new TextRun({ text: " ◈ ", color: C.cyberPink, size: 16 }),
                new TextRun({ text: "2026 EDITION", size: 16, color: C.matrixGreen }),
            ]
        })]
    })
},
```

### Footers with Page Numbers

```javascript
footers: {
    default: new Footer({
        children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
                new TextRun({ text: "Page ", size: 14 }),
                new TextRun({ children: [PageNumber.CURRENT], size: 14, bold: true }),
                new TextRun({ text: " of ", size: 14 }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 14, bold: true }),
            ]
        })]
    })
},
```

---

## Page Breaks

```javascript
// Manual page break (must be inside a Paragraph!)
new Paragraph({ children: [new PageBreak()] }),

// Or use pageBreakBefore on a paragraph
new Paragraph({
    pageBreakBefore: true,
    children: [new TextRun("This starts on a new page")]
}),
```

---

## Comparison Tables

```javascript
new Table({
    columnWidths: [2550, 2550, 2550, 2550],
    rows: [
        // Header row
        new TableRow({ children: [
            new TableCell({ shading: { fill: C.charcoal, type: ShadingType.CLEAR }, children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Feature", bold: true, color: C.white })] })
            ] }),
            new TableCell({ shading: { fill: C.googleBlue, type: ShadingType.CLEAR }, children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Product A", bold: true, color: C.white })] })
            ] }),
            new TableCell({ shading: { fill: C.googleGreen, type: ShadingType.CLEAR }, children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Product B", bold: true, color: C.white })] })
            ] }),
            new TableCell({ shading: { fill: C.googleRed, type: ShadingType.CLEAR }, children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Product C", bold: true, color: C.white })] })
            ] }),
        ] }),
        // Data rows with alternating colors
        new TableRow({ children: [
            new TableCell({ shading: { fill: "F5F5F5", type: ShadingType.CLEAR }, children: [
                new Paragraph({ children: [new TextRun({ text: "Speed", bold: true })] })
            ] }),
            new TableCell({ shading: { fill: "E3F2FD", type: ShadingType.CLEAR }, children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("⚡ Fast")] })
            ] }),
            // ... more cells
        ] }),
    ]
}),
```

---

## Pricing Grids

```javascript
// Three-tier pricing layout
new Table({
    columnWidths: [3400, 3400, 3400],
    rows: [new TableRow({ children: [
        // Basic Tier
        new TableCell({ borders: thickB(C.silver), shading: { fill: "F8FAFC", type: ShadingType.CLEAR },
            verticalAlign: VerticalAlign.TOP,
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "BASIC", bold: true, size: 28, color: C.slate })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$0/mo", bold: true, size: 40, color: C.charcoal })] }),
                new Paragraph({ numbering: { reference: "check-list", level: 0 }, children: [new TextRun("Feature 1")] }),
                new Paragraph({ numbering: { reference: "check-list", level: 0 }, children: [new TextRun("Feature 2")] }),
            ] }),
        // Pro Tier (highlighted)
        new TableCell({ borders: glowB(C.googleBlue), shading: { fill: C.googleBlue, type: ShadingType.CLEAR },
            verticalAlign: VerticalAlign.TOP,
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "★ PRO ★", bold: true, size: 28, color: C.white })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$29/mo", bold: true, size: 40, color: C.white })] }),
                // ... features
            ] }),
        // Enterprise Tier
        new TableCell({ borders: thickB(C.gold), shading: { fill: "FFFBEB", type: ShadingType.CLEAR },
            verticalAlign: VerticalAlign.TOP,
            children: [
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ENTERPRISE", bold: true, size: 28, color: C.gold })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Custom", bold: true, size: 40, color: C.charcoal })] }),
                // ... features
            ] }),
    ]})]
}),
```

---

## Best Practices

### Page Space Utilization (CRITICAL)

**Problem**: Documents often have excessive whitespace at the bottom of pages when using hard page breaks after each section, leaving half-empty pages.

**Solutions**:

1. **Avoid unnecessary page breaks** - Let content flow naturally between sections
   ```javascript
   // BAD: Forces new page even with remaining space
   new Paragraph({ children: [new PageBreak()] }),

   // GOOD: Let content flow, only break when truly needed
   // (no page break between related sections)
   ```

2. **Use space-filling elements** - Add callout boxes, key takeaways, or tip sections to utilize remaining space
   ```javascript
   // Helper function for callout boxes that fill space
   function createCalloutBox(title, content, color, bgColor) {
       return new Table({
           columnWidths: [10200],
           rows: [new TableRow({ children: [
               new TableCell({
                   borders: { left: border(color, 8), top: noBorder, bottom: noBorder, right: noBorder },
                   shading: { fill: bgColor, type: ShadingType.CLEAR },
                   children: [
                       new Paragraph({ children: [new TextRun({ text: title, bold: true, color: color })] }),
                       ...content.map(text => new Paragraph({ children: [new TextRun(text)] }))
                   ]
               })
           ]})]
       });
   }
   ```

3. **Use two-column layouts** - Present related content side-by-side to maximize width usage
   ```javascript
   new Table({
       columnWidths: [5100, 5100],
       rows: [new TableRow({ children: [
           new TableCell({ /* left column */ }),
           new TableCell({ /* right column */ })
       ]})]
   });
   ```

4. **Reduce margins for content-heavy documents** - Use 0.5" margins (720 DXA) instead of 1"
   ```javascript
   page: { margin: { top: 720, right: 720, bottom: 720, left: 720 } }
   ```

5. **Add "Key Takeaways" boxes at section ends** - Summarize key points and fill remaining space

6. **Strategic page breaks only** - Use `pageBreakBefore: true` only when starting a major new chapter

**Goal**: Maximize content per page without cramming. Fewer pages with well-utilized space is better than many half-empty pages.

### Image Management
1. **Download images first** and validate file sizes (> 1KB)
2. **Load images at script start** using `fs.readFileSync()`
3. **Always specify `type`** parameter ("jpg", "png", etc.)
4. **Use consistent dimensions** within the same layout

### Table Layouts
1. **Calculate total width**: Letter size with 0.5" margins = ~10200 DXA (1" margins = ~9360 DXA)
2. **Always use `ShadingType.CLEAR`** to prevent black backgrounds
3. **Set columnWidths at table level** AND width on each cell
4. **Use `verticalAlign: VerticalAlign.TOP`** for consistent cell alignment
5. **Use tables for layout** - Tables are excellent for creating multi-column layouts and space-filling boxes

### Color Usage
1. **Define palette at top** of script for easy modification
2. **Use hex colors without #** (e.g., "FF0000" not "#FF0000")
3. **Test contrast** - ensure text is readable on backgrounds
4. **Consistent theming** - stick to 4-6 colors maximum
5. **Define light background variants** - Use for callout boxes and alternating table rows

### Performance
1. **Reuse border objects** instead of creating new ones
2. **Use helper functions** for common patterns (callouts, code blocks, stat cards)
3. **Minimize image sizes** - resize before embedding

---

## Reusable Helper Functions

Use these helper functions to create consistent, space-efficient layouts:

```javascript
// Border helpers
const border = (color = "CCCCCC", size = 1) => ({ style: BorderStyle.SINGLE, size, color });
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const accentBorder = (c, s = 2) => ({ top: border(c, s), bottom: border(c, s), left: border(c, s), right: border(c, s) });
const leftAccentBorder = (c) => ({ top: noBorder, bottom: noBorder, left: border(c, 8), right: noBorder });

// Callout box - great for tips, warnings, key points
function createCalloutBox(title, contentLines, accentColor, bgColor) {
    return new Table({
        columnWidths: [10200],
        rows: [new TableRow({ children: [
            new TableCell({
                borders: leftAccentBorder(accentColor),
                shading: { fill: bgColor, type: ShadingType.CLEAR },
                children: [
                    new Paragraph({ spacing: { before: 100, after: 50 }, children: [
                        new TextRun({ text: title, bold: true, size: 22, color: accentColor })
                    ] }),
                    ...contentLines.map(text => new Paragraph({
                        spacing: { after: 80 },
                        children: [new TextRun({ text, size: 20 })]
                    }))
                ]
            })
        ]})]
    });
}

// Key takeaways box - summarize section key points
function createKeyPointsBox(points, color = "3B82F6") {
    return new Table({
        columnWidths: [10200],
        rows: [new TableRow({ children: [
            new TableCell({
                borders: accentBorder(color),
                shading: { fill: "EFF6FF", type: ShadingType.CLEAR },
                children: [
                    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 100 }, children: [
                        new TextRun({ text: "KEY TAKEAWAYS", bold: true, size: 24, color: color })
                    ] }),
                    ...points.map(point => new Paragraph({
                        spacing: { after: 80 }, indent: { left: 200 },
                        children: [
                            new TextRun({ text: "▸ ", color: color, size: 20 }),
                            new TextRun({ text: point, size: 20 })
                        ]
                    })),
                    new Paragraph({ children: [] })
                ]
            })
        ]})]
    });
}

// Two-column layout
function createTwoColumnLayout(leftContent, rightContent, leftBg = "F3F4F6", rightBg = "FFFFFF") {
    return new Table({
        columnWidths: [5100, 5100],
        rows: [new TableRow({ children: [
            new TableCell({
                borders: { top: border(), bottom: border(), left: border(), right: border() },
                shading: { fill: leftBg, type: ShadingType.CLEAR },
                verticalAlign: VerticalAlign.TOP,
                children: leftContent  // Array of Paragraph elements
            }),
            new TableCell({
                borders: { top: border(), bottom: border(), left: border(), right: border() },
                shading: { fill: rightBg, type: ShadingType.CLEAR },
                verticalAlign: VerticalAlign.TOP,
                children: rightContent  // Array of Paragraph elements
            })
        ]})]
    });
}

// Code block
function createCodeBlock(lines) {
    return new Table({
        columnWidths: [10200],
        rows: [new TableRow({ children: [
            new TableCell({
                borders: accentBorder("10B981", 1),
                shading: { fill: "1F2937", type: ShadingType.CLEAR },
                children: lines.map(line => new Paragraph({
                    spacing: { before: 40, after: 40 },
                    children: [new TextRun({
                        text: line.text,
                        font: "Consolas",
                        size: 20,
                        color: line.color || "FFFFFF"
                    })]
                }))
            })
        ]})]
    });
}

// Stat card for metrics display
function createStatCard(stat, label, color) {
    return new TableCell({
        borders: accentBorder(color),
        shading: { fill: "1F2937", type: ShadingType.CLEAR },
        children: [
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80 }, children: [
                new TextRun({ text: stat, bold: true, size: 48, color: color })
            ] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [
                new TextRun({ text: label, size: 18, color: "FFFFFF" })
            ] })
        ]
    });
}
```

---

## Critical Rules (from docx-js.md)

1. **PageBreak MUST be inside Paragraph** - standalone PageBreak creates invalid XML
2. **ALWAYS use ShadingType.CLEAR** for table cell shading
3. **NEVER use `\n` for line breaks** - use separate Paragraph elements
4. **ImageRun REQUIRES `type` parameter** - always specify image format
5. **Use LevelFormat.BULLET constant** for bullets, not string "bullet"
6. **Each numbering reference is independent** - same reference continues numbering
7. **Avoid excessive page breaks** - let content flow naturally for better space utilization

---

## Dependencies

Required (should already be installed):
- **docx**: `npm install -g docx` (Word document generation)

---

## Complete Example: Ultra-Extreme Document

See `docx-js.md` for the full library reference and the generated example scripts in your output folder for complete working implementations.

Example output files from testing:
- `create-ai-revolution-doc.js` → AI_Revolution_ULTRA_EXTREME.docx
- `create-claude-code-doc.js` → Claude_Code_Mastery_ULTRA_EXTREME.docx
- `create-nano-banana-doc.js` → Nano_Banana_Pro_ULTRA_EXTREME.docx

These serve as templates for creating similarly complex documents.
