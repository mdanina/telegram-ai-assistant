# Curriculum Slides Cookbook

## Purpose
Guide for creating educational and learning content presentations with clear structure and visual hierarchy.

## When to Use
- Educational course materials
- Training presentations
- Workshop slides
- Tutorial or how-to decks
- Learning roadmaps

## Recommended Structure

### 1. Introduction Slide
- Course/topic title
- Learning objectives
- Instructor/presenter info

### 2. Overview Slide
- Module breakdown
- Key concepts covered
- Prerequisites (if any)

### 3. Content Slides
- One concept per slide
- Clear headers
- Bullet points for key info
- Visual examples when possible

### 4. Summary/Review Slide
- Recap key learnings
- Next steps
- Resources for further learning

## Example Usage

```python
from templates.design_system import *

prs = create_presentation()

# Title slide
add_title_slide(prs, "Introduction to Python", "A Beginner's Course")

# Learning objectives
add_standard_slide(prs, "What You'll Learn", [
    "Python syntax and basic data types",
    "Control flow: loops and conditionals",
    "Functions and modules",
    "Working with files and data",
    "Building simple applications"
])

# Module breakdown
add_standard_slide(prs, "Course Modules", [
    "Module 1: Getting Started (2 hours)",
    "Module 2: Core Concepts (4 hours)",
    "Module 3: Practical Projects (6 hours)",
    "Module 4: Advanced Topics (4 hours)"
])

# Content example
add_standard_slide(prs, "Variables and Data Types", [
    "Variables store data: x = 10",
    "String: text data 'hello'",
    "Integer: whole numbers 42",
    "Float: decimal numbers 3.14",
    "Boolean: True or False"
])

# Comparison slide for contrasting concepts
add_comparison_slide(
    prs,
    "Lists vs Tuples",
    "Lists",
    [
        "Mutable (can be changed)",
        "Use square brackets: [1, 2, 3]",
        "Methods: append(), remove()",
        "Best for changing data"
    ],
    "Tuples",
    [
        "Immutable (cannot be changed)",
        "Use parentheses: (1, 2, 3)",
        "Faster than lists",
        "Best for fixed data"
    ]
)

# Summary slide
add_standard_slide(prs, "Key Takeaways", [
    "Python is readable and beginner-friendly",
    "Variables and data types are foundational",
    "Practice is essential for mastery",
    "Resources available in course materials"
])

prs.save("python_intro_curriculum.pptx")
```

## Best Practices

### Content Organization
- **One topic per slide**: Don't overcrowd
- **Progressive complexity**: Build on previous concepts
- **Visual hierarchy**: Headers, subheaders, bullets
- **White space**: Don't fill every inch

### Text Guidelines
- **Bullet points**: 3-7 items max per slide
- **Text length**: 6-8 words per bullet
- **Avoid paragraphs**: Use concise phrases
- **Consistent tense**: Usually present tense

### Visual Elements
- **Code examples**: Use monospace font (requires custom formatting)
- **Diagrams**: Import as images via `add_image_slide()`
- **Comparisons**: Use two-column layout
- **Process flows**: Number steps clearly

### Engagement
- **Questions**: Add "Think About" slides
- **Activities**: "Try This" practice slides
- **Checkpoints**: "Quiz Yourself" review slides
- **Resources**: Links and references slide

## Common Slide Types

### Concept Introduction
```python
add_standard_slide(prs, "New Concept Name", [
    "Definition in simple terms",
    "Why it matters",
    "Key characteristics",
    "Common use cases"
])
```

### Step-by-Step Process
```python
add_standard_slide(prs, "How to [Do Something]", [
    "Step 1: First action",
    "Step 2: Second action",
    "Step 3: Third action",
    "Step 4: Final step"
])
```

### Compare and Contrast
```python
add_comparison_slide(prs, "Option A vs Option B",
    "Option A", ["Pro 1", "Pro 2", "Pro 3"],
    "Option B", ["Pro 1", "Pro 2", "Pro 3"]
)
```

### Summary/Recap
```python
add_standard_slide(prs, "What We Learned", [
    "Core concept 1",
    "Core concept 2",
    "Core concept 3",
    "Next: What's coming up"
])
```

## Tips for Different Learning Levels

### Beginner Content
- More explanation per concept
- Frequent review/recap slides
- Simple language
- Many examples

### Intermediate Content
- Faster pace
- Comparisons and trade-offs
- Build on fundamentals
- Practical applications

### Advanced Content
- Dense information acceptable
- Focus on edge cases
- Performance considerations
- Real-world scenarios
