# Document Complexity Levels Guide

This guide defines 6 complexity levels that apply across all file formats (PPTX, DOCX, XLSX, PDF). Use this to calibrate document complexity based on user requirements.

## Quick Reference

| Level | Name | Density | Colors | Images | Best For |
|-------|------|---------|--------|--------|----------|
| 1 | Ultra-Minimalistic | Sparse | 1 (black) | None | Formal letters, legal docs |
| 2 | Clean Professional | Balanced | 2-3 | Optional | Reports, proposals |
| 3 | Enhanced | Moderate | 3-4 | 1-2 | Marketing, guides |
| 4 | Complex | Dense | 4-5 | 2-4 | Brochures, catalogs |
| 5 | Extreme | Very Dense | 5-6 | 4-6 | Portfolios, showcases |
| 6 | Ultra-Extreme | Maximum | 6+ themed | 6+ | Art pieces, demos |

---

## Level 1: Ultra-Minimalistic

**Philosophy**: Maximum whitespace, minimum elements. Let content breathe.

### Characteristics
- **Typography**: Single font family (serif preferred: Times New Roman, Georgia)
- **Colors**: Black text only, no accent colors
- **Spacing**: Generous margins (1"+), liberal line spacing (1.5-2x)
- **Elements**: Text paragraphs only, no tables, images, or graphics
- **Headers/Footers**: None or minimal (page numbers only)

### Use Cases
- Executive summaries
- Formal letters
- Legal documents
- Academic papers
- Meeting minutes

### Example Elements
```
Font: Times New Roman 12pt
Margins: 1" all sides
Line spacing: 1.5
Colors: Black (#000000) only
```

---

## Level 2: Clean Professional

**Philosophy**: Balanced design with subtle structure. Professional without being plain.

### Characteristics
- **Typography**: Professional font (Arial, Calibri), 2 sizes max
- **Colors**: 2-3 colors (primary dark, accent, neutral)
- **Spacing**: Standard margins (0.75-1"), organized sections
- **Elements**: Basic tables, headers/footers, page numbers
- **Structure**: Clear hierarchy with headings

### Use Cases
- Business reports
- Proposals
- Internal communications
- Technical documentation
- Standard presentations

### Example Color Palette
```
Primary: #2B579A (Corporate Blue)
Accent: #666666 (Gray)
Background: #FFFFFF (White)
```

---

## Level 3: Enhanced

**Philosophy**: Visual hierarchy with intentional design elements. Engaging but not overwhelming.

### Characteristics
- **Typography**: 2-3 font sizes, bold/italic variations
- **Colors**: 3-4 colors with clear purpose
- **Spacing**: Strategic whitespace, section dividers
- **Elements**: Styled tables, images, callout boxes
- **Structure**: Multiple heading levels, visual breaks

### Use Cases
- Marketing documents
- Product guides
- Training materials
- Newsletters
- Internal presentations

### Design Elements
- Colored section headers
- Table headers with background color
- 1-2 relevant images
- Bullet points with custom styling
- Simple borders/dividers

---

## Level 4: Complex

**Philosophy**: Rich layouts with multiple visual components. Information-dense but organized.

### Characteristics
- **Typography**: 3-4 styles, decorative headers
- **Colors**: 4-5 colors, cohesive palette
- **Spacing**: Tight but balanced, every area used purposefully
- **Elements**: Multi-column layouts, data tables, charts, multiple images
- **Structure**: Sidebar content, callout boxes, icons

### Use Cases
- Brochures
- Product catalogs
- Detailed reports
- Project portfolios
- External presentations

### Design Elements
- Multi-column table layouts
- Stats bars with icons
- Comparison tables
- Image galleries
- Sidebar information panels
- Custom bullet symbols

---

## Level 5: Extreme

**Philosophy**: Dense layouts with strong visual impact. Every inch serves a purpose.

### Characteristics
- **Typography**: 4-5 styles including display fonts
- **Colors**: 5-6 colors, themed palette
- **Spacing**: Minimal whitespace, tight margins (0.25-0.5")
- **Elements**: Complex tables as layout containers, many images, decorative borders
- **Structure**: Page-filling layouts, overlapping visual elements

### Use Cases
- Portfolio pieces
- Product showcases
- Event programs
- Trade show materials
- Sales decks

### Design Techniques
- Table-based layouts filling entire pages
- Colored backgrounds on most elements
- Multiple images per page
- Custom bullet symbols (⚡ ◆ ★ ✓ →)
- Thick colored borders
- Stats bars and data callouts

---

## Level 6: Ultra-Extreme

**Philosophy**: Maximum density, artistic expression. Documents as visual experiences.

### Characteristics
- **Typography**: 5+ styles, display/impact fonts, varied sizes
- **Colors**: 6+ colors, bold themed palettes
- **Spacing**: Zero empty space, content touches all edges
- **Elements**: Every page densely packed with tables, images, text, icons
- **Structure**: Art-piece quality, deliberate visual chaos organized

### Use Cases
- Showcase documents
- Demo/test files
- Art pieces
- Visual portfolios
- Maximum capability demonstrations

### Design Techniques

#### Themed Color Palettes
```javascript
// Cyberpunk Theme
{ neonBlue: "00D4FF", electricPurple: "8B5CF6", cyberPink: "EC4899", matrixGreen: "10B981", deepBlack: "0A0A0F" }

// Anthropic Theme
{ anthropicOrange: "DA7756", darkOrange: "C4613C", lightOrange: "F5D0C0", codeGreen: "10B981", terminalBlue: "3B82F6" }

// Google Theme
{ googleBlue: "4285F4", googleRed: "EA4335", googleYellow: "FBBC04", googleGreen: "34A853", deepBlue: "1A237E" }
```

#### Glow Border Effect
```javascript
const glowB = (c) => ({ top: border(c, 4), bottom: border(c, 4), left: border(c, 4), right: border(c, 4) });
```

#### Page-Filling Strategy
1. Use full-width tables as page containers
2. Nest content in table cells with colored backgrounds
3. Minimize or eliminate margins
4. Use decorative border rows between sections
5. Fill every cell with content (text, images, or decorative elements)

---

## Format-Specific Applications

### PPTX (PowerPoint)
| Level | Slides | Elements per Slide | Animations |
|-------|--------|-------------------|------------|
| 1 | Text-only | 1-2 | None |
| 2 | Title + bullets | 2-3 | Minimal |
| 3 | Text + image | 3-4 | Subtle |
| 4 | Multi-column | 4-6 | Moderate |
| 5 | Full coverage | 6-8 | Coordinated |
| 6 | Edge-to-edge | 8+ | Full suite |

### DOCX (Word)
| Level | Tables | Images | Styles |
|-------|--------|--------|--------|
| 1 | None | None | 1 |
| 2 | Basic data | Optional | 2-3 |
| 3 | Styled | 1-2 | 3-4 |
| 4 | Layout grids | 2-4 | 4-5 |
| 5 | Page containers | 4-6 | 5-6 |
| 6 | Full page tables | 6+ | 6+ |

### XLSX (Excel)
| Level | Formatting | Charts | Conditional |
|-------|-----------|--------|-------------|
| 1 | Borders only | None | None |
| 2 | Headers styled | 1 basic | None |
| 3 | Alternating rows | 1-2 | Basic |
| 4 | Multiple styles | 2-3 | Color scales |
| 5 | Dashboard layout | 3-4 | Icon sets |
| 6 | Full visual report | 4+ | All types |

### PDF
| Level | Layout | Graphics | Interactivity |
|-------|--------|----------|---------------|
| 1 | Single column | None | None |
| 2 | Headers/footers | Minimal | Links |
| 3 | Two-column | Images | TOC links |
| 4 | Complex layout | Charts | Form fields |
| 5 | Magazine style | Full graphics | Interactive |
| 6 | Art piece | Maximum | All features |

---

## Complexity Selection Guide

**DEFAULT SETTING: Level 4-5 with Light Theme**

Unless the user explicitly requests simpler documents, default to Level 4 (Complex) or Level 5 (Extreme) with a professional light theme. This ensures information-rich, visually polished output.

When user requests a document, assess:

1. **Explicit request**: Did they mention "simple", "minimal"? → Use lower level. Otherwise default to Level 4-5.
2. **Purpose**: Formal/legal = lower (Level 2-3), everything else = Level 4-5
3. **Audience**: Any professional audience benefits from Level 4-5 polish
4. **Content volume**: More content = excellent fit for Level 4-5 density
5. **Theme**: Always use light theme (white/light gray backgrounds) unless user requests dark

### Default Mappings (Updated)
- No specification given → **Level 4-5 with light theme** (DEFAULT)
- "Simple" / "minimal" → Level 1-2
- "Clean" / "basic" → Level 2-3
- "Professional" → Level 4 (not Level 2-3)
- "Report" / "document" → Level 4
- "Marketing brochure" → Level 4-5
- "Product catalog" → Level 5
- "Showcase/portfolio" → Level 5
- "Push the limits" / "Go extreme" → Level 6
- "Art piece" / "No empty space" → Level 6

### Default Light Theme Palette
```
Primary:     #1F4E79 (Corporate Blue)
Secondary:   #2E75B6 (Light Blue)
Accent:      #059669 (Green)
Warning:     #DC2626 (Red)
Purple:      #7C3AED (Purple)
Text Dark:   #1F2937
Text Muted:  #6B7280
Background:  #FFFFFF (White)
Surface:     #F8F9FA (Light Gray)
Light BG:    #F3F4F6
```

---

## Implementation Checklist by Level

### Level 1
- [ ] Single font family
- [ ] No colors besides black
- [ ] Generous whitespace
- [ ] Text-only content

### Level 2
- [ ] Professional font
- [ ] 2-3 accent colors
- [ ] Headers and footers
- [ ] Basic styling

### Level 3
- [ ] Multiple heading styles
- [ ] Styled tables
- [ ] 1-2 images
- [ ] Section dividers

### Level 4
- [ ] Multi-column layouts
- [ ] Comparison tables
- [ ] Multiple images
- [ ] Custom bullets
- [ ] Stats/data callouts

### Level 5
- [ ] Table-based layouts
- [ ] Themed color palette
- [ ] Colored backgrounds
- [ ] Thick borders
- [ ] Every section filled

### Level 6
- [ ] Zero whitespace
- [ ] Glow border effects
- [ ] Full-page tables
- [ ] 6+ images
- [ ] Decorative elements
- [ ] Themed headers/footers
- [ ] Custom bullet symbols
- [ ] Art-piece quality
