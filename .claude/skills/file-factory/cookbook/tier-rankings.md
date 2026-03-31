# Tier Rankings Cookbook

## Purpose
Guide for creating tier-based ranking presentations with consistent formatting and color coding.

## When to Use
- User needs to rank tools, technologies, or options
- Comparative analysis presentations
- Evaluation or assessment decks
- "Best of" or recommendation slides

## Tier System
- **S-Tier**: Best in class, exceptional, highly recommended
- **A-Tier**: Excellent, strong choice, reliable
- **B-Tier**: Good, acceptable, serviceable
- (Can extend to C, D, F if needed)

## Color Coding
- S-Tier: Accent color (indigo) with white text
- A-Tier: Gray color with white text
- B-Tier: Light gray with dark text

## Example Usage

```python
from templates.design_system import *

prs = create_presentation()

# Title slide
add_title_slide(prs, "AI Tools Tier Rankings", "Comparative Analysis")

# Tier ranking slide
tier_data = [
    {
        'tier': 'S-Tier',
        'tool': 'Claude Code',
        'features': 'Full autonomy, MCP integration, Skills system',
        'reasoning': 'Most advanced agentic coding'
    },
    {
        'tier': 'A-Tier',
        'tool': 'GitHub Copilot',
        'features': 'Excellent autocomplete, chat interface',
        'reasoning': 'Strong IDE integration'
    },
    {
        'tier': 'B-Tier',
        'tool': 'TabNine',
        'features': 'Code completion, multiple languages',
        'reasoning': 'Good but limited reasoning'
    }
]

add_tier_table_slide(prs, "AI Coding Tools Rankings", tier_data)

prs.save("tier_rankings.pptx")
```

## Best Practices
1. Keep feature descriptions concise (2-3 key points)
2. Reasoning should explain tier placement clearly
3. Use consistent criteria across all items
4. Limit to 5-8 items per slide for readability
5. Consider multiple slides for large datasets
6. Add context slide before rankings if needed

## Data Structure
Each tier item must have:
- `tier`: String (e.g., "S-Tier", "A-Tier")
- `tool`: Name of item being ranked
- `features`: Key characteristics (comma-separated)
- `reasoning`: Why it's in this tier

## Variations
- **Custom columns**: Modify table structure for different data
- **Extended tiers**: Add C/D/F tiers by updating color coding
- **Visual indicators**: Add icons or badges (requires additional code)
- **Multiple categories**: Create separate slides for different evaluation criteria
