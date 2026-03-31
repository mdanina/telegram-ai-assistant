---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xlsm, .csv, .tsv, etc) for: (1) Creating new spreadsheets with formulas and formatting, (2) Reading or analyzing data, (3) Modify existing spreadsheets while preserving formulas, (4) Data analysis and visualization in spreadsheets, or (5) Recalculating formulas"
license: Proprietary. LICENSE.txt has complete terms
---

# XLSX Creation, Editing, and Analysis

## Overview

A user may ask you to create, edit, or analyze the contents of an .xlsx file. You have different tools and workflows available for different tasks.

## Design Principles

**CRITICAL**: Before creating any spreadsheet, analyze the content and choose appropriate design elements:
1. **Consider the subject matter**: What is this spreadsheet about? Business, creative, technical?
2. **Check for branding**: If the user mentions a company/organization, consider their brand colors
3. **Match palette to content**: Select colors that reflect the subject
4. **State your approach**: Explain your design choices before writing code

**Requirements**:
- State your content-informed design approach BEFORE writing code
- Use Excel-compatible fonts: Calibri, Arial, Segoe UI, Tahoma, Verdana, Georgia
- Create clear visual hierarchy through size, weight, and color
- Ensure readability: strong contrast, appropriately sized text, clean alignment
- Be consistent: repeat patterns, spacing, and visual language across sheets

### Color Palette Selection

**Choosing colors creatively**:
- **Think beyond defaults**: What colors genuinely match this specific topic?
- **Consider multiple angles**: Topic, industry, mood, energy level, target audience
- **Be adventurous**: A healthcare spreadsheet doesn't have to be green
- **Build your palette**: Pick 3-5 colors that work together
- **Ensure contrast**: Text must be clearly readable on backgrounds

**Example color palettes** (use these to spark creativity):

| # | Name | Primary | Secondary | Accent | Background |
|---|------|---------|-----------|--------|------------|
| 1 | Corporate Blue | 1F4E79 | 2E75B6 | D6DCE4 | F2F2F2 |
| 2 | Tech Dark | 1A1A2E | 16213E | 0F3460 | E94560 |
| 3 | Forest Green | 2D5A4A | 4A7C59 | 8FC93A | F4F9F4 |
| 4 | Sunset Warm | C15937 | F97316 | FDE68A | FEF3C7 |
| 5 | Purple Depth | 5B2C6F | 8E44AD | D2B4DE | F5EEF8 |
| 6 | Ocean Teal | 0D7377 | 14A3C7 | 96D4D4 | E3F6F5 |
| 7 | Rose Gold | 9B2335 | CC8899 | F4C2C2 | FDF6F6 |
| 8 | Neon Night | 121212 | 2D2D2D | 00D4FF | FF00FF |
| 9 | Earthy Brown | 6B4423 | A0522D | DEB887 | FFF8DC |
| 10 | Lime Fresh | 32CD32 | 7CFC00 | ADFF2F | F0FFF0 |
| 11 | Berry Mix | 8B008B | C71585 | FF69B4 | FFF0F5 |
| 12 | Slate Modern | 2F4F4F | 708090 | B0C4DE | F0F8FF |
| 13 | Golden Luxury | 8B7500 | DAA520 | FFD700 | FFFAF0 |
| 14 | Coral Reef | FF6B6B | FF8E72 | FFC4A3 | FFF5F2 |
| 15 | Mint Cool | 00B894 | 55EFC4 | 81ECEC | E0FFFF |
| 16 | Charcoal Red | 292929 | 4A4A4A | E33737 | F8F8F8 |

**Pre-built Gradient Progressions** (8 shades, light to dark):
```python
BLUE_GRADIENT = ["E3F2FD", "BBDEFB", "90CAF9", "64B5F6", "42A5F5", "2196F3", "1E88E5", "1976D2"]
PURPLE_GRADIENT = ["F3E5F5", "E1BEE7", "CE93D8", "BA68C8", "AB47BC", "9C27B0", "8E24AA", "7B1FA2"]
GREEN_GRADIENT = ["E8F5E9", "C8E6C9", "A5D6A7", "81C784", "66BB6A", "4CAF50", "43A047", "388E3C"]
ORANGE_GRADIENT = ["FFF3E0", "FFE0B2", "FFCC80", "FFB74D", "FFA726", "FF9800", "FB8C00", "F57C00"]
PINK_GRADIENT = ["FCE4EC", "F8BBD9", "F48FB1", "F06292", "EC407A", "E91E63", "D81B60", "C2185B"]
RED_GRADIENT = ["FFEBEE", "FFCDD2", "EF9A9A", "E57373", "EF5350", "F44336", "E53935", "D32F2F"]
TEAL_GRADIENT = ["E0F2F1", "B2DFDB", "80CBC4", "4DB6AC", "26A69A", "009688", "00897B", "00796B"]
GOLD_GRADIENT = ["FFF8E1", "FFECB3", "FFE082", "FFD54F", "FFCA28", "FFC107", "FFB300", "FFA000"]
```

**Platform/Brand Colors**:
```python
YOUTUBE = "FF0000"
TIKTOK_CYAN = "00F2EA"
TIKTOK_PINK = "FF0050"
INSTAGRAM_PURPLE = "833AB4"
INSTAGRAM_PINK = "E1306C"
INSTAGRAM_ORANGE = "F77737"
TWITTER = "1DA1F2"
TWITCH = "9146FF"
SPOTIFY = "1DB954"
LINKEDIN = "0077B5"
FACEBOOK = "4267B2"
PINTEREST = "E60023"
DISCORD = "5865F2"
SLACK = "4A154B"
```

## Complexity Levels

Choose the appropriate complexity level for your spreadsheet:

| Level | Name | Formatting | Charts | Conditional | Best For |
|-------|------|-----------|--------|-------------|----------|
| **1** | Ultra-Minimalistic | Borders only | None | None | Data exports, raw tables |
| **2** | Clean Professional | Headers styled | 1 basic | None | Reports, proposals |
| **3** | Enhanced | Alternating rows | 1-2 | Basic | Dashboards, summaries |
| **4** | Complex | Multiple styles | 2-3 | Color scales | Financial models |
| **5** | Extreme | Dashboard layout | 3-4 | Icon sets | KPI dashboards |
| **6** | Ultra-Extreme | Full visual report | 4+ | All types | Executive dashboards |

---

### Level 1: Ultra-Minimalistic

Clean data presentation with minimal styling. Function over form.

**Characteristics:**
- Simple borders only (thin gray)
- No colors or fills
- Single font (Calibri 11pt)
- Left-aligned text, right-aligned numbers
- No merged cells
- No charts or conditional formatting

**Python Pattern:**
```python
from openpyxl import Workbook
from openpyxl.styles import Border, Side, Font, Alignment

wb = Workbook()
ws = wb.active
ws.title = "Data"

thin = Side(style='thin', color='CCCCCC')
border = Border(left=thin, right=thin, top=thin, bottom=thin)
font = Font(name='Calibri', size=11)

# Headers
headers = ['Product', 'Q1', 'Q2', 'Q3', 'Q4', 'Total']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(name='Calibri', size=11, bold=True)
    cell.border = border

# Data rows
data = [
    ['Widget A', 1200, 1350, 1400, 1500, '=SUM(B2:E2)'],
    ['Widget B', 800, 920, 1100, 1250, '=SUM(B3:E3)'],
]
for r, row_data in enumerate(data, 2):
    for c, value in enumerate(row_data, 1):
        cell = ws.cell(row=r, column=c, value=value)
        cell.font = font
        cell.border = border
        if c > 1:  # Numbers right-aligned
            cell.alignment = Alignment(horizontal='right')

wb.save('level1_minimal.xlsx')
```

---

### Level 2: Clean Professional

Balanced styling with header emphasis. Professional without clutter.

**Characteristics:**
- Colored header row (dark background, white text)
- Subtle alternating row colors (optional)
- 2-3 colors max
- Basic number formatting
- Column width optimization
- One simple chart (optional)

**Python Pattern:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Report"

# Colors
PRIMARY = "1F4E79"
HEADER_TEXT = "FFFFFF"
ALT_ROW = "F2F2F2"

thin = Side(style='thin', color='CCCCCC')
border = Border(left=thin, right=thin, top=thin, bottom=thin)

# Title
ws.merge_cells('A1:F1')
ws['A1'] = "Quarterly Sales Report"
ws['A1'].font = Font(name='Calibri', size=16, bold=True, color=PRIMARY)
ws['A1'].alignment = Alignment(horizontal='center')
ws.row_dimensions[1].height = 30

# Headers
headers = ['Product', 'Q1', 'Q2', 'Q3', 'Q4', 'Total']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=3, column=col, value=header)
    cell.font = Font(name='Calibri', size=11, bold=True, color=HEADER_TEXT)
    cell.fill = PatternFill(start_color=PRIMARY, end_color=PRIMARY, fill_type='solid')
    cell.alignment = Alignment(horizontal='center')
    cell.border = border

# Data with alternating rows
data = [
    ['Widget A', 1200, 1350, 1400, 1500, '=SUM(B4:E4)'],
    ['Widget B', 800, 920, 1100, 1250, '=SUM(B5:E5)'],
    ['Widget C', 2100, 2300, 2150, 2400, '=SUM(B6:E6)'],
]
for r, row_data in enumerate(data, 4):
    for c, value in enumerate(row_data, 1):
        cell = ws.cell(row=r, column=c, value=value)
        cell.font = Font(name='Calibri', size=11)
        cell.border = border
        if (r - 4) % 2 == 1:
            cell.fill = PatternFill(start_color=ALT_ROW, end_color=ALT_ROW, fill_type='solid')
        if c > 1:
            cell.number_format = '#,##0'
            cell.alignment = Alignment(horizontal='right')

# Column widths
widths = {'A': 15, 'B': 12, 'C': 12, 'D': 12, 'E': 12, 'F': 12}
for col, width in widths.items():
    ws.column_dimensions[col].width = width

wb.save('level2_professional.xlsx')
```

**Color Palette:**
```python
L2_CORPORATE = {
    "primary": "1F4E79",
    "accent": "2E75B6",
    "header_text": "FFFFFF",
    "alt_row": "F2F2F2",
    "text": "333333"
}
```

---

### Level 3: Enhanced

Visual hierarchy with multiple formatting elements. Engaging and informative.

**Characteristics:**
- Multiple header styles (title, section, column)
- Alternating row colors
- 3-4 colors with purpose
- Number formatting with symbols
- 1-2 charts
- Basic conditional formatting (data bars or color scale)
- Freeze panes

**Python Pattern:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import DataBarRule
from openpyxl.chart import BarChart, Reference

wb = Workbook()
ws = wb.active
ws.title = "Dashboard"

# Colors
PRIMARY = "2E75B6"
SECONDARY = "5B9BD5"
ACCENT = "ED7D31"
LIGHT_BG = "DEEBF7"
ALT_ROW = "F2F2F2"

thin = Side(style='thin', color='B4B4B4')
medium = Side(style='medium', color=PRIMARY)
border = Border(left=thin, right=thin, top=thin, bottom=thin)

# Title banner
ws.merge_cells('A1:G1')
ws['A1'] = "Sales Performance Dashboard"
ws['A1'].font = Font(name='Calibri', size=20, bold=True, color="FFFFFF")
ws['A1'].fill = PatternFill(start_color=PRIMARY, end_color=PRIMARY, fill_type='solid')
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[1].height = 40

# Section header
ws.merge_cells('A3:G3')
ws['A3'] = "Regional Performance"
ws['A3'].font = Font(name='Calibri', size=14, bold=True, color=PRIMARY)
ws['A3'].border = Border(bottom=medium)

# Column headers
headers = ['Region', 'Q1', 'Q2', 'Q3', 'Q4', 'Total', 'Trend']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=5, column=col, value=header)
    cell.font = Font(name='Calibri', size=11, bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color=SECONDARY, end_color=SECONDARY, fill_type='solid')
    cell.alignment = Alignment(horizontal='center')
    cell.border = border

# Data
data = [
    ['North', 45000, 52000, 48000, 61000, '=SUM(B6:E6)'],
    ['South', 38000, 41000, 44000, 47000, '=SUM(B7:E7)'],
    ['East', 52000, 55000, 58000, 62000, '=SUM(B8:E8)'],
    ['West', 41000, 43000, 46000, 51000, '=SUM(B9:E9)'],
]
for r, row_data in enumerate(data, 6):
    for c, value in enumerate(row_data, 1):
        cell = ws.cell(row=r, column=c, value=value)
        cell.font = Font(name='Calibri', size=11)
        cell.border = border
        if (r - 6) % 2 == 1:
            cell.fill = PatternFill(start_color=ALT_ROW, end_color=ALT_ROW, fill_type='solid')
        if c > 1:
            cell.number_format = '$#,##0'

# Data bars for Trend column
ws.conditional_formatting.add('F6:F9',
    DataBarRule(start_type='num', start_value=0, end_type='max',
                color=ACCENT, showValue=True))

# Freeze panes
ws.freeze_panes = 'B6'

# Add chart
chart = BarChart()
chart.title = "Quarterly Comparison"
chart.style = 10
data_ref = Reference(ws, min_col=2, min_row=5, max_col=5, max_row=9)
cats = Reference(ws, min_col=1, min_row=6, max_row=9)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats)
chart.width = 15
chart.height = 8
ws.add_chart(chart, "A12")

wb.save('level3_enhanced.xlsx')
```

---

### Level 4: Complex

Rich dashboard with multiple data sections. Information-dense but organized.

**Characteristics:**
- Dashboard-style layout with cards/sections
- 4-5 colors in cohesive palette
- Multiple charts (2-3)
- KPI callouts with large numbers
- Sparklines or mini-charts
- Color scales and icon sets
- Multiple tables with distinct styling
- Named ranges for navigation

**Python Pattern:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import ColorScaleRule, IconSetRule
from openpyxl.chart import PieChart, BarChart, Reference

wb = Workbook()
ws = wb.active
ws.title = "Executive Dashboard"
ws.sheet_properties.tabColor = "1F4E79"

# Theme colors
DARK_BG = "1F2937"
SURFACE = "374151"
PRIMARY = "3B82F6"
SUCCESS = "10B981"
WARNING = "F59E0B"
DANGER = "EF4444"
TEXT_LIGHT = "F9FAFB"
TEXT_MUTED = "9CA3AF"

thin = Side(style='thin', color='4B5563')
border = Border(left=thin, right=thin, top=thin, bottom=thin)

# Apply dark background to visible area
for row in range(1, 35):
    for col in range(1, 15):
        ws.cell(row=row, column=col).fill = PatternFill(
            start_color=DARK_BG, end_color=DARK_BG, fill_type='solid')

# Header bar
ws.merge_cells('A1:N1')
ws['A1'] = "EXECUTIVE DASHBOARD | Q4 2026"
ws['A1'].font = Font(name='Calibri', size=18, bold=True, color=TEXT_LIGHT)
ws['A1'].fill = PatternFill(start_color=PRIMARY, end_color=PRIMARY, fill_type='solid')
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[1].height = 45

# KPI Cards (row 3-6)
kpis = [
    ("Revenue", "$2.4M", "+18%", SUCCESS),
    ("Customers", "12,847", "+5%", SUCCESS),
    ("Churn Rate", "2.1%", "-0.3%", SUCCESS),
    ("NPS Score", "72", "+4", WARNING),
]

col = 1
for title, value, change, color in kpis:
    # Card background
    for r in range(3, 7):
        for c in range(col, col + 3):
            ws.cell(row=r, column=c).fill = PatternFill(
                start_color=SURFACE, end_color=SURFACE, fill_type='solid')
            ws.cell(row=r, column=c).border = Border(
                left=Side(style='medium', color=color),
                right=Side(style='thin', color='4B5563'),
                top=Side(style='thin', color='4B5563'),
                bottom=Side(style='thin', color='4B5563'))

    ws.merge_cells(f'{chr(64+col)}3:{chr(64+col+2)}3')
    ws.cell(row=3, column=col, value=title).font = Font(
        name='Calibri', size=10, color=TEXT_MUTED)
    ws.cell(row=3, column=col).alignment = Alignment(horizontal='center')

    ws.merge_cells(f'{chr(64+col)}4:{chr(64+col+2)}5')
    ws.cell(row=4, column=col, value=value).font = Font(
        name='Calibri', size=28, bold=True, color=TEXT_LIGHT)
    ws.cell(row=4, column=col).alignment = Alignment(horizontal='center', vertical='center')

    ws.merge_cells(f'{chr(64+col)}6:{chr(64+col+2)}6')
    ws.cell(row=6, column=col, value=change).font = Font(
        name='Calibri', size=12, bold=True, color=color)
    ws.cell(row=6, column=col).alignment = Alignment(horizontal='center')

    col += 4

# Data table section (row 8+)
ws.merge_cells('A8:G8')
ws['A8'] = "Regional Performance"
ws['A8'].font = Font(name='Calibri', size=14, bold=True, color=PRIMARY)
ws['A8'].fill = PatternFill(start_color=DARK_BG, end_color=DARK_BG, fill_type='solid')

# Table headers
table_headers = ['Region', 'Revenue', 'Target', '% Achieved', 'Status']
for c, header in enumerate(table_headers, 1):
    cell = ws.cell(row=9, column=c, value=header)
    cell.font = Font(name='Calibri', size=11, bold=True, color=TEXT_LIGHT)
    cell.fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type='solid')
    cell.border = border
    cell.alignment = Alignment(horizontal='center')

# Table data
table_data = [
    ['North America', 850000, 800000, '=B10/C10', '=IF(D10>=1,"On Track","At Risk")'],
    ['Europe', 620000, 700000, '=B11/C11', '=IF(D11>=1,"On Track","At Risk")'],
    ['Asia Pacific', 480000, 450000, '=B12/C12', '=IF(D12>=1,"On Track","At Risk")'],
    ['Latin America', 290000, 300000, '=B13/C13', '=IF(D13>=1,"On Track","At Risk")'],
]
for r, row_data in enumerate(table_data, 10):
    for c, value in enumerate(row_data, 1):
        cell = ws.cell(row=r, column=c, value=value)
        cell.font = Font(name='Calibri', size=11, color=TEXT_LIGHT)
        cell.fill = PatternFill(start_color=DARK_BG, end_color=DARK_BG, fill_type='solid')
        cell.border = border
        if c in [2, 3]:
            cell.number_format = '$#,##0'
        elif c == 4:
            cell.number_format = '0.0%'

# Color scale for % Achieved
ws.conditional_formatting.add('D10:D13',
    ColorScaleRule(
        start_type='num', start_value=0.8, start_color='EF4444',
        mid_type='num', mid_value=1.0, mid_color='F59E0B',
        end_type='num', end_value=1.2, end_color='10B981'))

wb.save('level4_complex.xlsx')
```

**Color Palette (Dark Theme):**
```python
L4_DARK_DASHBOARD = {
    "background": "1F2937",
    "surface": "374151",
    "border": "4B5563",
    "primary": "3B82F6",
    "success": "10B981",
    "warning": "F59E0B",
    "danger": "EF4444",
    "text_light": "F9FAFB",
    "text_muted": "9CA3AF"
}
```

---

### Level 5: Extreme

Dense visual dashboard with maximum data presentation. Every cell purposeful.

**Characteristics:**
- Full dashboard with multiple sections
- 5-6 colors in themed palette
- 3-4 charts of different types
- Sparklines in data tables
- Heat maps for matrix data
- Icon sets for status indicators
- Progress bars using cells
- Multiple KPI panels
- Custom cell "charts" using fills

**Python Pattern:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import ColorScaleRule, IconSetRule, DataBarRule

wb = Workbook()
ws = wb.active
ws.title = "Analytics Hub"
ws.sheet_properties.tabColor = "8B5CF6"

# Cyberpunk theme
BG = "0A0A0F"
SURFACE = "1A1A2E"
NEON_BLUE = "00D4FF"
PURPLE = "8B5CF6"
PINK = "EC4899"
GREEN = "10B981"
GOLD = "FBBF24"
TEXT = "FFFFFF"
MUTED = "94A3B8"

thin = Side(style='thin', color='30363D')
glow_blue = Side(style='medium', color=NEON_BLUE)
glow_purple = Side(style='medium', color=PURPLE)
glow_pink = Side(style='medium', color=PINK)

# Full dark background
for row in range(1, 40):
    for col in range(1, 20):
        ws.cell(row=row, column=col).fill = PatternFill(
            start_color=BG, end_color=BG, fill_type='solid')

# Neon header
ws.merge_cells('A1:S1')
ws['A1'] = "◈ ANALYTICS COMMAND CENTER ◈"
ws['A1'].font = Font(name='Calibri', size=20, bold=True, color=NEON_BLUE)
ws['A1'].fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type='solid')
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
for col in range(1, 20):
    ws.cell(row=1, column=col).border = Border(
        bottom=Side(style='thick', color=NEON_BLUE))
ws.row_dimensions[1].height = 40

# Stats row (using cells as visual bars)
stats = [
    ("REVENUE", "$4.2M", NEON_BLUE, "+24%"),
    ("USERS", "847K", PURPLE, "+18%"),
    ("SESSIONS", "2.1M", PINK, "+31%"),
    ("CONVERSION", "4.7%", GREEN, "+0.8%"),
]

col = 1
for label, value, color, change in stats:
    # Stat card
    for r in range(3, 6):
        for c in range(col, col + 4):
            cell = ws.cell(row=r, column=c)
            cell.fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type='solid')
            cell.border = Border(
                left=Side(style='thick', color=color) if c == col else thin,
                right=thin, top=thin, bottom=thin)

    ws.merge_cells(f'{chr(64+col)}3:{chr(64+col+3)}3')
    ws.cell(row=3, column=col, value=label).font = Font(size=9, color=color, bold=True)
    ws.cell(row=3, column=col).alignment = Alignment(horizontal='center')

    ws.merge_cells(f'{chr(64+col)}4:{chr(64+col+3)}4')
    ws.cell(row=4, column=col, value=value).font = Font(size=24, color=TEXT, bold=True)
    ws.cell(row=4, column=col).alignment = Alignment(horizontal='center')

    ws.merge_cells(f'{chr(64+col)}5:{chr(64+col+3)}5')
    ws.cell(row=5, column=col, value=f"⚡ {change}").font = Font(size=11, color=GREEN)
    ws.cell(row=5, column=col).alignment = Alignment(horizontal='center')

    col += 5

# Heat map matrix section
ws.merge_cells('A7:H7')
ws['A7'] = "◆ PERFORMANCE MATRIX"
ws['A7'].font = Font(size=12, bold=True, color=PURPLE)

matrix_headers = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
for c, header in enumerate(matrix_headers, 2):
    cell = ws.cell(row=8, column=c, value=header)
    cell.font = Font(size=9, color=MUTED)
    cell.fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type='solid')
    cell.alignment = Alignment(horizontal='center')

weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
matrix_data = [
    [85, 92, 78, 95, 88, 45, 52],
    [90, 87, 91, 82, 94, 48, 55],
    [76, 89, 93, 88, 91, 51, 49],
    [94, 91, 85, 97, 89, 53, 58],
]

for r, (week, values) in enumerate(zip(weeks, matrix_data), 9):
    ws.cell(row=r, column=1, value=week).font = Font(size=9, color=MUTED)
    ws.cell(row=r, column=1).fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type='solid')
    for c, val in enumerate(values, 2):
        cell = ws.cell(row=r, column=c, value=val)
        cell.alignment = Alignment(horizontal='center')
        cell.font = Font(size=10, color=TEXT)

# Apply heat map
ws.conditional_formatting.add('B9:H12',
    ColorScaleRule(
        start_type='min', start_color='1A1A2E',
        mid_type='percentile', mid_value=50, mid_color=PURPLE,
        end_type='max', end_color=PINK))

# Visual progress bars using cells
ws.merge_cells('A14:H14')
ws['A14'] = "◆ GOAL PROGRESS"
ws['A14'].font = Font(size=12, bold=True, color=PINK)

goals = [
    ("Revenue Target", 0.82),
    ("User Growth", 0.94),
    ("Engagement", 0.71),
]

for r, (goal, pct) in enumerate(goals, 15):
    ws.cell(row=r, column=1, value=goal).font = Font(size=10, color=TEXT)
    ws.cell(row=r, column=1).fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type='solid')

    # Progress bar (10 cells)
    filled = int(pct * 10)
    for c in range(2, 12):
        cell = ws.cell(row=r, column=c)
        if c - 2 < filled:
            cell.fill = PatternFill(start_color=NEON_BLUE, end_color=NEON_BLUE, fill_type='solid')
        else:
            cell.fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type='solid')
        cell.border = Border(top=thin, bottom=thin)

    ws.cell(row=r, column=12, value=f"{int(pct*100)}%").font = Font(size=10, color=NEON_BLUE, bold=True)

wb.save('level5_extreme.xlsx')
```

**Color Palette (Cyberpunk):**
```python
L5_CYBERPUNK = {
    "background": "0A0A0F",
    "surface": "1A1A2E",
    "neonBlue": "00D4FF",
    "electricPurple": "8B5CF6",
    "cyberPink": "EC4899",
    "matrixGreen": "10B981",
    "gold": "FBBF24",
    "text": "FFFFFF",
    "muted": "94A3B8"
}
```

---

### Level 6: Ultra-Extreme

Maximum visual density. Spreadsheets as data art.

**Characteristics:**
- Zero empty cells in visible area
- 6+ colors in bold themed palette
- Glow effects (thick colored borders)
- Every row/column styled
- Multiple heat maps
- Decorative headers with symbols (◈◆★⚡)
- Code-style data displays
- Animated-looking progress indicators
- Full conditional formatting suite

**Python Pattern:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import ColorScaleRule

wb = Workbook()
ws = wb.active
ws.title = "NEURAL_HUB"
ws.sheet_properties.tabColor = "00D4FF"

# Ultra theme
BG = "0A0A0F"
DARK = "0D1117"
SURFACE = "161B22"
PANEL = "1A1A2E"
NEON = "00D4FF"
PURPLE = "8B5CF6"
PINK = "EC4899"
GREEN = "10B981"
GOLD = "FBBF24"
RED = "EF4444"

# Glow borders
def glow(color):
    return Side(style='thick', color=color)

# Fill entire visible area
for row in range(1, 50):
    for col in range(1, 25):
        ws.cell(row=row, column=col).fill = PatternFill(
            start_color=BG, end_color=BG, fill_type='solid')

# === HEADER WITH GLOW ===
for col in range(1, 21):
    ws.cell(row=1, column=col).fill = PatternFill(start_color=DARK, end_color=DARK, fill_type='solid')
    ws.cell(row=1, column=col).border = Border(
        top=glow(NEON), bottom=glow(NEON),
        left=glow(NEON) if col == 1 else None,
        right=glow(NEON) if col == 20 else None)

ws.merge_cells('A1:T1')
ws['A1'] = "◈◈◈ QUANTUM ANALYTICS NEXUS ◈◈◈"
ws['A1'].font = Font(name='Consolas', size=18, bold=True, color=NEON)
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[1].height = 45

# === DECORATIVE SEPARATOR ===
ws.merge_cells('A2:T2')
ws['A2'] = "═" * 80
ws['A2'].font = Font(size=8, color=PURPLE)
ws['A2'].alignment = Alignment(horizontal='center')
ws.row_dimensions[2].height = 12

# === MEGA STATS PANEL ===
mega_stats = [
    ("◆ COMPUTE", "1.2 ZF", NEON),
    ("◆ MODELS", "847K", PURPLE),
    ("◆ TOKENS", "4.2T", PINK),
    ("◆ LATENCY", "0.3ms", GREEN),
    ("◆ UPTIME", "99.97%", GOLD),
]

col = 1
for label, value, color in mega_stats:
    for r in range(3, 7):
        for c in range(col, col + 4):
            cell = ws.cell(row=r, column=c)
            cell.fill = PatternFill(start_color=PANEL, end_color=PANEL, fill_type='solid')
            if c == col:
                cell.border = Border(left=glow(color))
            elif c == col + 3:
                cell.border = Border(right=Side(style='thin', color='30363D'))

    ws.merge_cells(f'{chr(64+col)}3:{chr(64+col+3)}3')
    ws.cell(row=3, column=col, value=label).font = Font(name='Consolas', size=9, color=color)
    ws.cell(row=3, column=col).alignment = Alignment(horizontal='center')

    ws.merge_cells(f'{chr(64+col)}4:{chr(64+col+3)}5')
    ws.cell(row=4, column=col, value=value).font = Font(name='Consolas', size=28, bold=True, color="FFFFFF")
    ws.cell(row=4, column=col).alignment = Alignment(horizontal='center', vertical='center')

    # Glow bar under value
    for c in range(col, col + 4):
        ws.cell(row=6, column=c).fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
    ws.row_dimensions[6].height = 4

    col += 4

# === CODE-STYLE DATA STREAM ===
ws.merge_cells('A8:J8')
ws['A8'] = "// LIVE_DATA_STREAM"
ws['A8'].font = Font(name='Consolas', size=10, color=GREEN)
ws['A8'].fill = PatternFill(start_color=DARK, end_color=DARK, fill_type='solid')

code_data = [
    ("timestamp:", "2026-01-04T14:32:17Z", NEON),
    ("inference:", "quantum_v4.model", PURPLE),
    ("throughput:", "1,847,293 tok/s", PINK),
    ("accuracy:", "99.847%", GREEN),
    ("status:", "OPTIMAL", GOLD),
]

for r, (key, val, color) in enumerate(code_data, 9):
    ws.cell(row=r, column=1, value=f"  {key}").font = Font(name='Consolas', size=9, color='6A9955')
    ws.cell(row=r, column=1).fill = PatternFill(start_color=DARK, end_color=DARK, fill_type='solid')
    ws.merge_cells(f'B{r}:J{r}')
    ws.cell(row=r, column=2, value=val).font = Font(name='Consolas', size=9, color=color)
    ws.cell(row=r, column=2).fill = PatternFill(start_color=DARK, end_color=DARK, fill_type='solid')

# === DUAL HEAT MAPS ===
# Heat map 1
ws.merge_cells('A15:J15')
ws['A15'] = "◆ NEURAL ACTIVITY MATRIX"
ws['A15'].font = Font(name='Consolas', size=11, bold=True, color=PURPLE)

import random
random.seed(42)
for r in range(16, 22):
    for c in range(1, 11):
        val = random.randint(40, 100)
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = Font(name='Consolas', size=9, color="FFFFFF")
        cell.alignment = Alignment(horizontal='center')

ws.conditional_formatting.add('A16:J21',
    ColorScaleRule(
        start_type='min', start_color=DARK,
        mid_type='percentile', mid_value=50, mid_color=PURPLE,
        end_type='max', end_color=PINK))

# Heat map 2
ws.merge_cells('L15:T15')
ws['L15'] = "◆ EFFICIENCY DISTRIBUTION"
ws['L15'].font = Font(name='Consolas', size=11, bold=True, color=NEON)

for r in range(16, 22):
    for c in range(12, 21):
        val = random.randint(60, 100)
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = Font(name='Consolas', size=9, color="FFFFFF")
        cell.alignment = Alignment(horizontal='center')

ws.conditional_formatting.add('L16:T21',
    ColorScaleRule(
        start_type='min', start_color=DARK,
        mid_type='percentile', mid_value=50, mid_color=NEON,
        end_type='max', end_color=GREEN))

# === BOTTOM DECORATIVE BAR ===
ws.merge_cells('A23:T23')
ws['A23'] = "★ " * 40
ws['A23'].font = Font(size=8, color=GOLD)
ws['A23'].alignment = Alignment(horizontal='center')
ws['A23'].fill = PatternFill(start_color=DARK, end_color=DARK, fill_type='solid')

wb.save('level6_ultra_extreme.xlsx')
```

**Themed Palettes for Level 5-6:**
```python
# Cyberpunk
CYBERPUNK = {
    "bg": "0A0A0F", "surface": "1A1A2E",
    "neon": "00D4FF", "purple": "8B5CF6", "pink": "EC4899",
    "green": "10B981", "gold": "FBBF24"
}

# Anthropic
ANTHROPIC = {
    "bg": "1F2937", "surface": "374151",
    "orange": "DA7756", "coral": "F5D0C0",
    "green": "10B981", "blue": "3B82F6"
}

# Google
GOOGLE = {
    "bg": "FFFFFF", "surface": "F8F9FA",
    "blue": "4285F4", "red": "EA4335",
    "yellow": "FBBC04", "green": "34A853", "purple": "8E24AA"
}
```

---

### Level Selection Guide

| User Says | Recommended Level |
|-----------|-------------------|
| "Simple data table" | Level 1 |
| "Professional report" | Level 2 |
| "Dashboard" | Level 3-4 |
| "Executive dashboard" | Level 4-5 |
| "Analytics command center" | Level 5 |
| "Push the limits" / "Data art" | Level 6 |

---

## Requirements for Outputs

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Run validation after creation to catch errors before delivery

### Preserve Existing Templates
When updating existing files:
- Study and EXACTLY match existing format, style, and conventions
- Never impose standardized formatting on files with established patterns
- Existing template conventions ALWAYS override these guidelines

## Financial Model Standards

### Color Coding (Industry Standard)
Unless otherwise stated by the user or existing template:
- **Blue text (0000FF)**: Hardcoded inputs users will change
- **Black text (000000)**: ALL formulas and calculations
- **Green text (008000)**: Links from other worksheets
- **Red text (FF0000)**: External links to other files
- **Yellow background (FFFF00)**: Key assumptions needing attention

### Number Formatting
| Type | Format | Example |
|------|--------|---------|
| Currency | `"$"#,##0` | $1,250 |
| Currency (decimals) | `"$"#,##0.00` | $1,250.00 |
| Thousands | `#,##0` | 1,250 |
| Percentage | `0.0%` | 12.5% |
| Percentage (signed) | `+0.0%;-0.0%` | +12.5% |
| Multiples | `0.0"x"` | 2.5x |
| Years | Text or `0` | 2024 |
| Negative in parens | `#,##0;(#,##0)` | (1,250) |
| Zero as dash | `#,##0;(#,##0);"-"` | - |
| Minutes | `0.0" min"` | 8.5 min |
| Hours | `#,##0" hrs"` | 42 hrs |

### Formula Construction Rules
- Place ALL assumptions in separate, labeled cells
- Use cell references instead of hardcoded values: `=B5*(1+$B$6)` not `=B5*1.05`
- Document sources for hardcodes in adjacent cells or comments

## Visual Details Options

### Border & Frame Treatments
```python
from openpyxl.styles import Border, Side

# Border styles
thin = Side(style='thin', color='CCCCCC')
medium = Side(style='medium', color='666666')
thick = Side(style='thick', color='333333')
double = Side(style='double', color='000000')
dashed = Side(style='dashed', color='999999')

# Common border patterns
all_borders = Border(left=thin, right=thin, top=thin, bottom=thin)
header_border = Border(left=thin, right=thin, top=medium, bottom=medium)
total_border = Border(top=thin, bottom=double)
bottom_only = Border(bottom=medium)
box_frame = Border(left=thick, right=thick, top=thick, bottom=thick)
```

### Typography Treatments
```python
from openpyxl.styles import Font

# Font hierarchy
title_font = Font(name='Calibri', size=22, bold=True, color='1F4E79')
header_font = Font(name='Calibri', size=14, bold=True, color='FFFFFF')
subheader_font = Font(name='Calibri', size=12, bold=True, color='333333')
body_font = Font(name='Calibri', size=11, color='000000')
caption_font = Font(name='Calibri', size=9, italic=True, color='666666')
metric_font = Font(name='Calibri', size=16, bold=True)  # For KPI values
small_font = Font(name='Calibri', size=8, color='999999')
```

### Layout Innovations
- **Dashboard Cards**: Group related metrics in bordered sections
- **KPI Panels**: Large numbers with labels and sparklines
- **Heat Maps**: Color-coded matrices for quick pattern recognition
- **Split Layouts**: Multiple data tables side by side
- **Navigation Panels**: Color-coded sheet tabs for workbook organization

## Helper Functions Library

### Reusable Style Functions
```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

thin = Side(style='thin', color='CCCCCC')

def create_header_style(bg_color, text_color="FFFFFF"):
    """Create consistent header styling"""
    return {
        'font': Font(bold=True, color=text_color, size=11),
        'fill': PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid"),
        'alignment': Alignment(horizontal='center', vertical='center'),
        'border': Border(left=thin, right=thin, top=thin, bottom=thin)
    }

def apply_style(cell, style_dict):
    """Apply a style dictionary to a cell"""
    for key, value in style_dict.items():
        setattr(cell, key, value)

def create_title_banner(ws, start_col, end_col, row, title, subtitle, main_color, accent_color):
    """Create a visually striking title banner with main title and subtitle"""
    # Main title row
    ws.merge_cells(f'{get_column_letter(start_col)}{row}:{get_column_letter(end_col)}{row}')
    title_cell = ws.cell(row=row, column=start_col, value=title)
    title_cell.font = Font(bold=True, size=22, color="FFFFFF")
    title_cell.fill = PatternFill(start_color=main_color, end_color=main_color, fill_type="solid")
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[row].height = 35

    # Accent bar
    ws.merge_cells(f'{get_column_letter(start_col)}{row+1}:{get_column_letter(end_col)}{row+1}')
    accent_cell = ws.cell(row=row+1, column=start_col, value=subtitle)
    accent_cell.font = Font(bold=True, size=10, color=main_color)
    accent_cell.fill = PatternFill(start_color=accent_color, end_color=accent_color, fill_type="solid")
    accent_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[row+1].height = 20

def create_data_table(ws, headers, data, start_row, start_col, header_color, alt_row_color=None):
    """Create a formatted data table with headers and optional alternating rows"""
    # Headers
    for c, header in enumerate(headers, start=start_col):
        cell = ws.cell(row=start_row, column=c, value=header)
        apply_style(cell, create_header_style(header_color))

    # Data rows
    for r, row_data in enumerate(data, start=start_row + 1):
        for c, value in enumerate(row_data, start=start_col):
            cell = ws.cell(row=r, column=c, value=value)
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            if alt_row_color and (r - start_row) % 2 == 0:
                cell.fill = PatternFill(start_color=alt_row_color, end_color=alt_row_color, fill_type="solid")

    return start_row + len(data) + 1  # Return next available row

def set_column_widths(ws, widths_dict):
    """Set multiple column widths at once. widths_dict = {'A': 15, 'B': 20, ...}"""
    for col, width in widths_dict.items():
        ws.column_dimensions[col].width = width
```

### Conditional Formatting Patterns
```python
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, CellIsRule, IconSetRule

# Heat map (low=red, mid=yellow, high=green)
def add_heatmap(ws, cell_range):
    ws.conditional_formatting.add(cell_range,
        ColorScaleRule(
            start_type='min', start_color='F8696B',
            mid_type='percentile', mid_value=50, mid_color='FFEB84',
            end_type='max', end_color='63BE7B'
        ))

# Data bars (visual bar in cell)
def add_data_bars(ws, cell_range, color='638EC6'):
    ws.conditional_formatting.add(cell_range,
        DataBarRule(
            start_type='num', start_value=0,
            end_type='max',
            color=color,
            showValue=True
        ))

# Highlight cells above/below threshold
def add_threshold_highlighting(ws, cell_range, threshold, above_color='C6EFCE', below_color='FFC7CE'):
    ws.conditional_formatting.add(cell_range,
        CellIsRule(operator='greaterThan', formula=[str(threshold)],
                   fill=PatternFill(start_color=above_color, end_color=above_color, fill_type='solid')))
    ws.conditional_formatting.add(cell_range,
        CellIsRule(operator='lessThan', formula=[str(threshold)],
                   fill=PatternFill(start_color=below_color, end_color=below_color, fill_type='solid')))

# Status icons (arrows, flags, etc.)
def add_icon_set(ws, cell_range, icon_style='3Arrows'):
    ws.conditional_formatting.add(cell_range,
        IconSetRule(icon_style=icon_style, type='num',
                    values=[0, 33, 67]))
```

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python.**

### WRONG - Hardcoding
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000 - BAD!
```

### CORRECT - Using Formulas
```python
sheet['B10'] = '=SUM(B2:B9)'  # Dynamic - GOOD!
```

This applies to ALL calculations. The spreadsheet must recalculate when data changes.

## Excel File Workflows

### Workflow Overview
1. **Choose tool**: pandas for data analysis, openpyxl for formulas/formatting
2. **Plan layout**: Sketch merged regions and table positions first
3. **Create/Load**: Create new workbook or load existing file
4. **Modify**: Add data, formulas, and formatting
5. **Save**: Write to file
6. **Recalculate** (if using formulas): Run recalc.py script
7. **Validate**: Check for errors and fix

### Creating New Excel Files
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Dashboard"
ws.sheet_properties.tabColor = "1F4E79"  # Tab color

# Add data
ws['A1'] = 'Revenue Report'
ws['A1'].font = Font(bold=True, size=18)

# Add formula
ws['B10'] = '=SUM(B2:B9)'

# Formatting
ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
ws['A1'].font = Font(bold=True, color='FFFFFF', size=14)
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

# Column width
ws.column_dimensions['A'].width = 20

# Freeze panes
ws.freeze_panes = 'B2'

wb.save('output.xlsx')
```

### Editing Existing Excel Files
```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
ws = wb.active  # or wb['SheetName']

# Modify
ws['A1'] = 'New Value'
ws.insert_rows(2)
ws.delete_cols(3)

# Add new sheet
new_ws = wb.create_sheet('NewSheet')
new_ws['A1'] = 'Data'

wb.save('modified.xlsx')
```

### Reading and Analyzing Data
```python
import pandas as pd

# Read single sheet
df = pd.read_excel('file.xlsx')

# Read all sheets
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)

# Analyze
df.head()      # Preview
df.info()      # Column info
df.describe()  # Statistics

# Write back
df.to_excel('output.xlsx', index=False)
```

## Merged Cells Best Practices

### Critical Rule: Merge BEFORE Write
```python
# WRONG - Will error
ws['B5'] = "Title"
ws.merge_cells('B5:E5')

# CORRECT - Merge first, then write
ws.merge_cells('B5:E5')
ws['B5'] = "Title"
ws['B5'].font = Font(bold=True)
```

### Non-Overlapping Regions
```python
# WRONG - Overlapping ranges
ws.merge_cells('B5:T5')   # Spans B to T
ws['L5'] = "Title"        # ERROR: L5 is inside merge!

# CORRECT - Non-overlapping with gap
ws.merge_cells('B5:J5')   # Columns B-J
ws.merge_cells('L5:T5')   # Columns L-T (gap at K)
ws['B5'] = "Title 1"
ws['L5'] = "Title 2"
```

### Layout Planning
Before coding complex layouts:
1. Sketch merged regions on paper/whiteboard
2. Identify column boundaries between sections
3. Leave gap columns between adjacent merged regions
4. Test incrementally - run script after each major section

## Visual Excel Techniques

### Dark Theme with Neon Accents
```python
DARK_BG = "121212"
NEON_BLUE = "00D4FF"
NEON_PINK = "FF00FF"
NEON_GREEN = "00FF88"

# Apply dark background
for row in range(1, 50):
    for col in range(1, 25):
        ws.cell(row=row, column=col).fill = PatternFill(
            start_color=DARK_BG, end_color=DARK_BG, fill_type="solid"
        )

# Neon accent header
for col in range(2, 20):
    cell = ws.cell(row=2, column=col)
    cell.fill = PatternFill(start_color=NEON_BLUE, end_color=NEON_BLUE, fill_type="solid")
    cell.font = Font(bold=True, color=DARK_BG)
```

### Gradient Effects
```python
GRADIENT = ["E3F2FD", "90CAF9", "42A5F5", "1E88E5", "1565C0"]

for col, color in enumerate(GRADIENT, start=2):
    ws.cell(row=5, column=col).fill = PatternFill(
        start_color=color, end_color=color, fill_type="solid"
    )
```

### Shadow Effect Cards
```python
def create_shadow_card(ws, start_row, start_col, height, width, main_color, shadow_color):
    """Create a card with shadow effect for depth"""
    # Main card
    for r in range(start_row, start_row + height):
        for c in range(start_col, start_col + width):
            ws.cell(row=r, column=c).fill = PatternFill(
                start_color=main_color, end_color=main_color, fill_type="solid"
            )
    # Shadow (bottom and right edges)
    for c in range(start_col + 1, start_col + width + 1):
        ws.cell(row=start_row + height, column=c).fill = PatternFill(
            start_color=shadow_color, end_color=shadow_color, fill_type="solid"
        )
    for r in range(start_row + 1, start_row + height + 1):
        ws.cell(row=r, column=start_col + width).fill = PatternFill(
            start_color=shadow_color, end_color=shadow_color, fill_type="solid"
        )
```

### Visual Bar Charts Using Cells
```python
values = [45, 78, 92, 65, 88]  # Percentages
max_val = max(values)
BAR_COLOR = "4CAF50"
EMPTY_COLOR = "EEEEEE"

for col, val in enumerate(values, start=3):
    bar_height = int((val / max_val) * 10)  # Max 10 cells tall
    for row_offset in range(10):
        cell = ws.cell(row=15 - row_offset, column=col)
        if row_offset < bar_height:
            cell.fill = PatternFill(start_color=BAR_COLOR, end_color=BAR_COLOR, fill_type="solid")
        else:
            cell.fill = PatternFill(start_color=EMPTY_COLOR, end_color=EMPTY_COLOR, fill_type="solid")
```

### Heat Map Matrix
```python
def create_heatmap_cells(ws, data_matrix, start_row, start_col, gradient):
    """Create a heat map using cell fills based on values"""
    max_val = max(max(row) for row in data_matrix)

    for r, row_data in enumerate(data_matrix, start=start_row):
        for c, val in enumerate(row_data, start=start_col):
            cell = ws.cell(row=r, column=c, value=val)
            intensity = int((val / max_val) * (len(gradient) - 1))
            color = gradient[min(intensity, len(gradient) - 1)]
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
            if intensity >= len(gradient) // 2:
                cell.font = Font(color="FFFFFF", bold=True)
```

## Recalculating Formulas

Excel files created by openpyxl contain formulas as strings but not calculated values. Use the `recalc.py` script:

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

Example:
```bash
python scripts/recalc.py output.xlsx 60
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors
- Returns JSON with detailed error locations

### Interpreting Output
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## Formula Verification Checklist

### Essential Verification
- [ ] Test 2-3 sample references before building full model
- [ ] Confirm Excel column mapping (column 64 = BL, not BK)
- [ ] Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)

### Common Pitfalls
- [ ] Handle NaN with `pd.notna()`
- [ ] Check for division by zero (#DIV/0!)
- [ ] Verify all cell references exist (#REF!)
- [ ] Use correct cross-sheet format: `Sheet1!A1`

### Testing Strategy
- [ ] Start small: test on 2-3 cells before applying broadly
- [ ] Verify dependencies: check all referenced cells exist
- [ ] Test edge cases: zero, negative, and large values

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple exports
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (A1 = row=1, column=1)
- Use `data_only=True` to read calculated values (WARNING: formulas are lost if saved)
- For large files: use `read_only=True` or `write_only=True`

### Working with pandas
```python
# Specify data types
df = pd.read_excel('file.xlsx', dtype={'id': str})

# Read specific columns for large files
df = pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])

# Handle dates
df = pd.read_excel('file.xlsx', parse_dates=['date_column'])
```

## Windows-Specific Notes

### Python Path Issues
Use full path on Windows:
```bash
"C:\Users\Tony\AppData\Local\Microsoft\WindowsApps\python.exe" script.py
```

### Console Encoding
Avoid Unicode (emojis) in print statements - Windows console uses cp1252:
```python
# Will fail:
print("Created successfully")

# Safe:
print("[OK] Created successfully")
```

## Code Style Guidelines

### For Python Code
- Write minimal, concise code
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

### For Excel Files
- Add comments to cells with complex formulas
- Document data sources for hardcoded values
- Include notes for key calculations

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `#REF!` | Invalid cell reference | Check formula references exist |
| `#DIV/0!` | Division by zero | Add IF check: `=IF(B2=0,0,A2/B2)` |
| `#VALUE!` | Wrong data type | Verify cell contains expected type |
| `#NAME?` | Unknown function | Check spelling, use English function names |
| `MergedCell is read-only` | Writing to merged cell | Merge BEFORE writing |
| `UnicodeEncodeError` | Emoji in print | Use ASCII-safe messages |

## Dependencies

Required packages:
- **openpyxl**: `pip install openpyxl` (Excel file manipulation)
- **pandas**: `pip install pandas` (data analysis)
- **LibreOffice**: For formula recalculation (install separately)
