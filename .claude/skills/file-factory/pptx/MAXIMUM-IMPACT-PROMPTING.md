# Maximum Impact Prompting Guide

This document captures the **reverse-engineered conversation patterns** and methodology for creating stunning PowerPoint presentations that push PPTX to its visual limits.

## The Iterative Enhancement Pattern

When users want "maximum visual impact" presentations, the conversation typically follows this escalation pattern:

### Phase 1: Initial Creation
```
USER: Create a presentation about [topic]
CLAUDE: [Creates standard professional slides]
```

### Phase 2: Visual Enhancement Request
```
USER: Make it more visually interesting / Push the limits / Make it pop
CLAUDE: [Applies advanced visual techniques from this guide]
```

### Phase 3: Maximum Content Request
```
USER: Add more content / Different themes per slide / Include charts, tables, stats
CLAUDE: [Applies the Maximum Content methodology below]
```

---

## The 6-Deck Methodology

When asked to "push PPTX limits" or create "visually stunning" presentations, generate **6 decks with 30 unique slides** organized as follows:

### Deck Organization

| Deck # | Theme Style | Mood | Slides |
|--------|------------|------|--------|
| 1 | Psychedelic Fractal | Mind-bending, neon | 5 |
| 2 | Cosmic Explosion | Energetic, explosive | 5 |
| 3 | Minimalistic Zen | Calm, focused | 5 |
| 4 | Visual Symphony | Elegant, refined | 5 |
| 5 | Maximum Impact | Bold, powerful | 5 |
| 6 | Fusion Gallery | Mixed styles | 5 |

### Per-Slide Requirements (Maximum Content Mode)

Each slide MUST contain:
- [ ] **Unique theme** - Different color palette from adjacent slides
- [ ] **Rasterized background** - Gradient or pattern PNG via Sharp
- [ ] **Data visualization** - Chart, table, or stat card
- [ ] **Typography hierarchy** - 3+ levels of text sizing
- [ ] **Decorative elements** - Borders, badges, dividers
- [ ] **Semi-transparent overlays** - Depth through layering

---

## Theme Rotation Matrix

When creating multiple slides with different themes, rotate through these palettes:

### Slide 1 Themes (Opening Impact)
| Theme | Background | Primary | Secondary | Accent |
|-------|------------|---------|-----------|--------|
| Neon Cyberpunk | #0A0020 | #FF00FF | #00FFFF | #39FF14 |
| Sunset Blaze | #1A0A0A | #FF6B35 | #FFD700 | #FF1493 |
| Ocean Deep | #001428 | #00D4FF | #7FFFD4 | #FF6B6B |

### Slide 2 Themes (Contrast Shift)
| Theme | Background | Primary | Secondary | Accent |
|-------|------------|---------|-----------|--------|
| Forest Mystery | #0A1A0A | #90EE90 | #FFD700 | #FF69B4 |
| Arctic Glow | #0A1428 | #E0FFFF | #87CEEB | #FF4500 |
| Desert Gold | #1A140A | #D4AF37 | #F5DEB3 | #8B4513 |

### Slide 3 Themes (Energy Peak)
| Theme | Background | Primary | Secondary | Accent |
|-------|------------|---------|-----------|--------|
| Cosmic Explosion | #1A0030 | #FF6B35 | #00D4FF | #FFD700 |
| Electric Storm | #0A0A1A | #00FFFF | #FF00FF | #FFFF00 |
| Volcanic Heat | #1A0A0A | #FF4500 | #FFD700 | #FF1493 |

### Slide 4 Themes (Calm Transition)
| Theme | Background | Primary | Secondary | Accent |
|-------|------------|---------|-----------|--------|
| Zen Balance | #F8F9FA | #212529 | #6C757D | #DC3545 |
| Minimalist Gray | #FAFAFA | #333333 | #666666 | #0066CC |
| Soft Lavender | #F5F0FF | #4A0080 | #9966CC | #FF69B4 |

### Slide 5 Themes (Closing Power)
| Theme | Background | Primary | Secondary | Accent |
|-------|------------|---------|-----------|--------|
| Art Deco Gold | #0A0020 | #D4AF37 | #F5F5DC | #8B0000 |
| Royal Purple | #1A0030 | #9966CC | #FFD700 | #FF1493 |
| Midnight Elegance | #0D1B2A | #C9A227 | #FFFAF0 | #DC143C |

---

## Chart & Data Visualization Patterns

### Chart Types per Theme

| Theme Style | Best Chart Type | Color Strategy |
|-------------|----------------|----------------|
| Psychedelic | Pie/Donut | Neon gradient fills |
| Cosmic | Area/Line | Glow effects on lines |
| Minimalist | Bar/Column | Monochrome with accent |
| Industrial | Horizontal Bar | Dark with neon accent |
| Elegant | Line/Area | Metallic gradients |

### Stat Card Templates

**Neon Style:**
```html
<div style="background: rgba(0,0,0,0.8); border: 3pt solid #39FF14;
            padding: 20pt; text-align: center;">
  <p style="font-size: 48pt; color: #39FF14;">87%</p>
  <p style="font-size: 14pt; color: #FFFFFF;">METRIC NAME</p>
</div>
```

**Elegant Style:**
```html
<div style="background: rgba(212,175,55,0.15); border: 2pt solid #D4AF37;
            padding: 20pt; text-align: center;">
  <p style="font-size: 42pt; color: #D4AF37; font-family: Georgia;">$2.4M</p>
  <p style="font-size: 12pt; color: #F5F5DC;">REVENUE TARGET</p>
</div>
```

**Minimalist Style:**
```html
<div style="background: #FFFFFF; border-left: 6pt solid #333333;
            padding: 20pt;">
  <p style="font-size: 54pt; color: #333333;">42</p>
  <p style="font-size: 11pt; color: #666666;">Projects Completed</p>
</div>
```

---

## Table Styling Per Theme

### Neon Tables
```javascript
{
  border: { pt: 2, color: '39FF14' },
  fill: { color: '000000' },
  color: '39FF14',
  fontSize: 10,
  valign: 'middle',
  align: 'center'
}
```

### Elegant Tables
```javascript
{
  border: { pt: 1, color: 'D4AF37' },
  fill: { color: '0A0020' },
  color: 'F5F5DC',
  fontFace: 'Georgia',
  fontSize: 11
}
```

### Minimalist Tables
```javascript
{
  border: { pt: 0.5, color: 'E0E0E0' },
  fill: { color: 'FFFFFF' },
  color: '333333',
  fontSize: 10,
  valign: 'middle'
}
```

---

## Background Pattern Library

### Spiral Pattern (Psychedelic)
```javascript
async function createSpiralBackground(colors, filename) {
  const width = 1920, height = 1080;
  const turns = 8, points = 200;
  let paths = '';

  for (let i = 0; i < points; i++) {
    const t = (i / points) * turns * 2 * Math.PI;
    const r = (i / points) * Math.min(width, height) * 0.45;
    const x = width/2 + r * Math.cos(t);
    const y = height/2 + r * Math.sin(t);
    const hue = (i / points) * 360;

    paths += `<circle cx="${x}" cy="${y}" r="${3 + (i/points)*5}"
              fill="hsl(${hue}, 100%, 50%)" fill-opacity="${0.3 + (i/points)*0.7}"/>`;
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
    <rect width="100%" height="100%" fill="${colors.bg}"/>
    ${paths}
  </svg>`;

  await sharp(Buffer.from(svg)).png().toFile(filename);
}
```

### Starburst Pattern (Cosmic)
```javascript
async function createStarburstBackground(colors, filename) {
  const width = 1920, height = 1080;
  const rays = 36;
  let paths = '';

  for (let i = 0; i < rays; i++) {
    const angle = (i / rays) * 2 * Math.PI;
    const x2 = width/2 + Math.cos(angle) * 1500;
    const y2 = height/2 + Math.sin(angle) * 1500;
    const hue = (i / rays) * 360;

    paths += `<line x1="${width/2}" y1="${height/2}" x2="${x2}" y2="${y2}"
              stroke="hsl(${hue}, 100%, 50%)" stroke-width="8" stroke-opacity="0.6"/>`;
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
    <defs>
      <radialGradient id="g">
        <stop offset="0%" style="stop-color:${colors.center}"/>
        <stop offset="100%" style="stop-color:${colors.edge}"/>
      </radialGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
    ${paths}
  </svg>`;

  await sharp(Buffer.from(svg)).png().toFile(filename);
}
```

### Geometric Grid (Minimalist)
```javascript
async function createGeometricGrid(colors, filename) {
  const width = 1920, height = 1080;
  const gridSize = 60;
  let paths = '';

  for (let x = 0; x <= width; x += gridSize) {
    paths += `<line x1="${x}" y1="0" x2="${x}" y2="${height}"
              stroke="${colors.grid}" stroke-width="0.5" stroke-opacity="0.3"/>`;
  }
  for (let y = 0; y <= height; y += gridSize) {
    paths += `<line x1="0" y1="${y}" x2="${width}" y2="${y}"
              stroke="${colors.grid}" stroke-width="0.5" stroke-opacity="0.3"/>`;
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
    <rect width="100%" height="100%" fill="${colors.bg}"/>
    ${paths}
  </svg>`;

  await sharp(Buffer.from(svg)).png().toFile(filename);
}
```

---

## Content Density Guidelines

### Low Density (Zen/Minimalist)
- 1-2 text elements
- 1 large focal point
- Maximum whitespace
- No more than 20 words

### Medium Density (Professional)
- 3-5 text elements
- 1 chart OR 1 table
- Balanced whitespace
- 30-50 words

### High Density (Maximum Impact)
- 6+ text elements
- Chart AND table AND stat card
- Layered overlays
- 50+ words with visual hierarchy

---

## Prompt Triggers

When user says any of these, activate Maximum Impact Mode:

| Trigger Phrase | Action |
|---------------|--------|
| "push the limits" | Full 6-deck methodology |
| "visually stunning" | Advanced effects + layering |
| "wow factor" | Neon glow + bold contrasts |
| "different themes per slide" | Theme rotation matrix |
| "include everything" | High density mode |
| "charts, tables, stats" | Full data visualization |
| "psychedelic" | Psychedelic theme set |
| "cosmic" | Cosmic explosion theme |
| "minimalist but impactful" | Zen + strategic accents |
| "maximum content" | All visual elements per slide |

---

## Quick Checklist: Maximum Impact Slide

Before finalizing each slide:

- [ ] Unique theme applied (different from adjacent slides)
- [ ] Rasterized gradient/pattern background (PNG)
- [ ] At least one semi-transparent overlay shape
- [ ] Extreme typography contrast (3:1+ size ratio)
- [ ] Glow effect on primary text or element
- [ ] Data visualization present (chart/table/stat)
- [ ] Decorative accent (border, badge, or divider)
- [ ] High contrast verified (text readable on background)

---

## File Naming Convention

When creating maximum impact decks:

```
workspace/
  psychedelic-decks/
    Psychedelic-Fractal-Universe.pptx
    Cosmic-Explosion.pptx
    Minimalistic.pptx
    Visual-Symphony.pptx
    Maximum-Impact.pptx
    Fusion-Gallery.pptx
```

---

## Memory: Key Learnings

Store these patterns when creating presentations:

1. **Rasterize everything complex** - Gradients, patterns, icons as PNG first
2. **Layer for depth** - Background + shapes + cards + text + accents
3. **Theme variety** - Each slide distinct yet cohesive overall
4. **Data everywhere** - Every slide benefits from visual data
5. **Glow for impact** - Neon effects transform ordinary to extraordinary
6. **Contrast is king** - High contrast = high impact
