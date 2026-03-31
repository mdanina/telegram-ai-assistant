# File Factory Skill

Unified skill for professional document creation across all Office formats (PowerPoint, Excel, Word, PDF).

## Directory Structure

```
file-factory/
├── SKILL.md                    # Main skill entry point with format routing
├── README.md                   # This file
│
├── pptx/                       # PowerPoint/Presentation workflows
│   ├── PPTX.md                # Main PPTX documentation
│   ├── html2pptx.md           # HTML to PowerPoint conversion guide
│   ├── ooxml.md               # Office Open XML technical reference
│   ├── design_system.py       # Shared design system and helper functions
│   ├── scripts/               # Python and JavaScript utilities
│   │   ├── html2pptx.js      # HTML to PPTX conversion library
│   │   ├── inventory.py      # Extract text inventory from slides
│   │   ├── replace.py        # Replace text in slides
│   │   ├── rearrange.py      # Duplicate and reorder slides
│   │   └── thumbnail.py      # Create slide thumbnail grids
│   └── ooxml/                 # OOXML manipulation tools
│       └── scripts/
│           ├── pack.py        # Repack PPTX from directory
│           ├── unpack.py      # Unpack PPTX to directory
│           ├── validate.py    # Validate OOXML structure
│           └── validation/    # Validation modules
│
├── xlsx/                       # Excel/Spreadsheet workflows
│   └── XLSX.md                # Coming soon
│
├── docx/                       # Word/Document workflows
│   └── DOCX.md                # Coming soon
│
├── pdf/                        # PDF workflows
│   ├── PDF.md                 # Main PDF documentation
│   ├── forms.md               # PDF form handling guide
│   ├── reference.md           # PDF reference documentation
│   └── scripts/               # PDF utilities
│       ├── check_bounding_boxes.py
│       ├── check_fillable_fields.py
│       ├── extract_form_field_info.py
│       ├── fill_fillable_fields.py
│       └── fill_pdf_form_with_annotations.py
│
├── themes/                     # Cross-format theming
│   └── THEMES.md              # Coming soon
│
└── cookbook/                   # Recipe-style guides
    ├── tier-rankings.md       # Creating tier ranking presentations
    └── curriculum-slides.md   # Educational content presentations
```

## Format Detection

The skill automatically routes to the correct workflow based on keywords:

- **PPTX:** presentation, slides, deck, powerpoint, pptx
- **XLSX:** spreadsheet, excel, xlsx, data table
- **DOCX:** document, word, docx, report
- **PDF:** pdf, extract, form, pdf form
- **Themes:** theme, styling, color scheme, branding

## Current Status

### Complete
- **PPTX:** Full documentation, scripts, and workflows
  - Creating from scratch (html2pptx workflow)
  - Editing existing presentations (OOXML workflow)
  - Template-based creation
  - Design system with helper functions
  - Cookbooks for common patterns
- **PDF:** Full documentation and form-filling utilities
- **DOCX:** Full documentation with 6 complexity levels
  - Creating from scratch (docx-js workflow)
  - Ultra-minimalistic to Ultra-extreme complexity levels
  - Table-based page-filling layouts
  - Themed color palettes (Cyberpunk, Anthropic, Google, etc.)
  - Professional templates and patterns
- **Themes:** Full theming system with 10 presets
- **Complexity Levels:** Cross-format complexity guide (COMPLEXITY_LEVELS.md)

### Coming Soon
- **XLSX:** Excel spreadsheet creation and editing

## Key Features

### PPTX Workflows
1. **HTML to PowerPoint** - Convert styled HTML to PPTX with accurate positioning
2. **OOXML Editing** - Direct XML manipulation for complex edits
3. **Template-based** - Duplicate and customize existing presentations
4. **Design System** - Consistent colors, typography, and layouts

### PDF Workflows
1. **Form Filling** - Fill fillable PDF forms programmatically
2. **Form Analysis** - Extract and analyze form field information
3. **Annotation-based Filling** - Fill non-fillable PDFs using annotations

## Usage Example

The skill is invoked automatically when you mention relevant keywords:

```
"Create a presentation about our Q4 results"
→ Routes to PPTX workflow

"Fill out this PDF form"
→ Routes to PDF workflow

"Create a spreadsheet with sales data"
→ Routes to XLSX workflow (when available)
```

## Cookbooks

Recipe-style guides for common patterns:

- **tier-rankings.md** - Create tier-based ranking tables (S/A/B tiers)
- **curriculum-slides.md** - Educational and training presentations

## Design Philosophy

1. **Format-specific expertise** - Each format has dedicated documentation
2. **Shared utilities** - Common patterns abstracted to design system
3. **Progressive disclosure** - Main SKILL.md routes to detailed guides
4. **Recipe patterns** - Cookbooks for frequently used workflows
5. **Validation first** - All workflows include validation steps

## Dependencies

### PPTX
- markitdown - Text extraction from presentations
- pptxgenjs - Creating presentations via html2pptx
- playwright - HTML rendering
- sharp - Image processing
- python-pptx - PPTX manipulation (design_system.py)

### PDF
- PyPDF2 - PDF manipulation
- pdf2image - Convert PDF pages to images
- reportlab - PDF creation

### DOCX
- docx - Word document generation (npm install -g docx)

### Coming Soon
- openpyxl (XLSX)

## Migration Notes

This skill consolidates:
- `pptx` skill → `file-factory/pptx/`
- `pdf` skill → `file-factory/pdf/`
- `presentation-generator` → `file-factory/pptx/` (design_system.py + cookbooks)

Future migrations:
- `xlsx` skill → `file-factory/xlsx/`
- `docx` skill → `file-factory/docx/`
