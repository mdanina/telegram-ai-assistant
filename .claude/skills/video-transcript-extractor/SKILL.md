---
name: video-transcript-extractor
description: Extract structured content from video transcripts including workflows, golden nuggets, commands, and code examples. Use when working with video transcripts, extracting video content, finding golden nuggets, or analyzing tutorial videos.
tools:
  - mcp__omni-cortex__cortex_recall
  - mcp__omni-cortex__cortex_remember
---

# Video Transcript Extractor

Extract and structure valuable content from video transcripts including workflows, key insights, commands, and code examples.

## Pre-Extraction Context

Before extracting content:
- Recall previous extractions on similar topics: `cortex_recall: "transcript {topic}"`
- Check for existing patterns: `cortex_recall: "video extraction"`
- Use recalled context to optimize extraction strategy

## Purpose

Transform raw video transcripts into structured, actionable documentation. Extract workflows, golden nuggets (key insights), terminal commands, code snippets, and step-by-step processes from tutorial videos and technical presentations.

## Variables

```yaml
# Content Types to Extract
extract_workflows: true           # Extract step-by-step workflows
extract_golden_nuggets: true      # Extract key insights and tips
extract_commands: true             # Extract terminal/CLI commands
extract_code: true                 # Extract code examples
extract_timestamps: true           # Preserve timestamp references

# Output Format
markdown_format: true              # Output as Markdown
include_toc: true                  # Include Table of Contents
group_by_topic: true               # Group related items together

# Output Mode Configuration
output_mode: single | multi        # single = one file, multi = split by category
multi_file_structure:
  summary: true                    # Generate summary.md
  workflows: true                  # Generate workflows.md
  commands: true                   # Generate commands.md
  golden_nuggets: true             # Generate golden-nuggets.md
  code_examples: true              # Generate code-examples.md
output_directory: ./               # Target directory for output files
```

## Instructions

### 1. Understand the Request

Determine what type of content extraction is needed:
- Full transcript analysis
- Specific workflow extraction
- Golden nugget mining
- Command/code extraction only

### 2. Choose Output Mode

Select the appropriate output mode based on your needs:

**Single File Mode** (`output_mode: single`)
- Best for: Individual video transcripts, quick extractions, small to medium content
- Output: One comprehensive markdown file with all extracted content
- Use when: You need a single portable document or are processing one video

**Multi-File Mode** (`output_mode: multi`)
- Best for: Large extractions, video series consolidation, reference documentation
- Output: Separate files per category (summary.md, workflows.md, commands.md, etc.)
- Use when:
  - Processing multiple related videos
  - Building a knowledge base from a series
  - Content will be referenced separately by category
  - Consolidating overlapping content from multiple sources

**Benefits of Multi-File Output:**
- **Navigability**: Jump directly to specific content types
- **Maintainability**: Update categories independently
- **Reusability**: Reference individual files in other documentation
- **Consolidation**: Merge content from multiple extractions cleanly
- **Version control**: Track changes per category

For multi-video consolidation workflows, see [consolidation-extraction.md](cookbook/consolidation-extraction.md).
For multi-file output templates, see [multi-file-output-template.md](templates/multi-file-output-template.md).

### 3. Select Extraction Route

Based on the user's expertise level and request, read the appropriate cookbook:

**Beginner Extraction**: If user is new to video content extraction or wants basic walkthrough
- Read [beginner-extraction.md](cookbook/beginner-extraction.md)

**Intermediate Extraction**: If user wants focused extraction with specific patterns
- Read [intermediate-extraction.md](cookbook/intermediate-extraction.md)

**Advanced Extraction**: If user wants comprehensive multi-pass analysis with cross-referencing
- Read [advanced-extraction.md](cookbook/advanced-extraction.md)

### 4. Apply Templates

Use the appropriate template based on content type:
- Video extraction template: [video-extraction-template.md](templates/video-extraction-template.md)
- Workflow template: [workflow-template.md](templates/workflow-template.md)
- Golden nugget format: [golden-nugget-format.md](templates/golden-nugget-format.md)
- Multi-file output: [multi-file-output-template.md](templates/multi-file-output-template.md)

### 5. Process the Transcript

1. Read the transcript file (supports .txt, .srt, .md formats)
2. Identify structural patterns (timestamps, speaker changes, topic shifts)
3. Extract content according to enabled variables
4. Apply templates to structure output
5. Validate extracted content for completeness

### 6. Generate Structured Output

Create comprehensive documentation with:
- Executive summary
- Table of contents (if enabled)
- Workflows with step numbers
- Golden nuggets with context
- Commands with descriptions
- Code examples with annotations
- Timestamp references for verification

## Workflow

```
1. User provides transcript → Understand content type and scope
2. Determine expertise level → Select appropriate cookbook route
3. Read cookbook instructions → Load extraction patterns
4. Apply templates → Structure the output format
5. Process transcript → Extract and categorize content
6. Generate documentation → Create final structured output
```

## Examples

### Example 1: Extract Full Workflow
```
Extract the complete workflow from this Claude Code tutorial transcript
```

### Example 2: Golden Nuggets Only
```
Extract just the golden nuggets and key insights from video-transcript.txt
```

### Example 3: Commands and Code
```
Extract all terminal commands and code examples from the transcript, preserve timestamps
```

### Example 4: Custom Extraction
```
From this transcript, extract:
- The main workflow (step-by-step)
- Top 5 golden nuggets
- All git commands mentioned
```

---

## Post-Extraction Memory

Store extraction results: `cortex_remember`
- Content: Video topic, key workflows extracted, golden nuggets count, notable findings
- Tags: ["transcript", "{video_topic}", "extraction"]
- Type: "knowledge"
- Include high-value insights for future reference
