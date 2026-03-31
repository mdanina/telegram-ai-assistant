# Consolidation Extraction Cookbook

Guide for processing and consolidating content from multiple related video transcripts.

## When to Consolidate

Consolidation is appropriate when:
- **Video Series**: Processing a multi-part tutorial series (e.g., "Claude Code Deep Dive Parts 1-5")
- **Same Author**: Multiple videos from the same creator covering related topics
- **Overlapping Topics**: Different videos covering similar ground with unique insights each
- **Knowledge Base Building**: Creating comprehensive documentation from scattered sources
- **Course Content**: Extracting from an entire video course or workshop

## Pre-Consolidation Checklist

Before starting consolidation:

1. **Inventory Videos**
   - [ ] List all transcripts to be consolidated
   - [ ] Note video dates/versions (newer content may supersede older)
   - [ ] Identify the primary/canonical source for each topic

2. **Assess Overlap**
   - [ ] Identify topics covered in multiple videos
   - [ ] Note which video has the most complete coverage per topic
   - [ ] Flag potentially conflicting information

3. **Set Output Mode**
   ```yaml
   output_mode: multi
   multi_file_structure:
     summary: true
     workflows: true
     commands: true
     golden_nuggets: true
     code_examples: true
   ```

4. **Define Scope**
   - [ ] Decide if extracting everything or specific categories
   - [ ] Set priority order for conflicting content
   - [ ] Establish naming conventions for output files

## Deduplication Strategies

### Framework Deduplication

When the same framework/concept appears in multiple videos:

1. **Identify Canonical Source**: Find the video with the most complete explanation
2. **Extract Primary Definition**: Use the canonical source for the main entry
3. **Supplement with Variations**: Add unique insights from other sources as notes
4. **Cross-Reference**: Note which videos discuss the framework

**Example:**
```markdown
## Agentic Workflow Pattern

**Primary Source**: Video 3 (most complete explanation)

[Main framework content from Video 3]

**Additional Insights:**
- Video 1 mentions specific use case: [detail]
- Video 5 adds advanced variation: [detail]

**Referenced in:** Videos 1, 3, 5, 7
```

### Command Deduplication

When CLI commands repeat across videos:

1. **Identify Unique Commands**: Filter out exact duplicates
2. **Merge Variations**: Combine commands that differ only in examples
3. **Preserve Context**: Note which video demonstrated each use case
4. **Group by Function**: Organize by what the command accomplishes

**Strategy:**
```markdown
## Git Commands

### git worktree add
Creates a new worktree for parallel development.

```bash
# Basic usage (Video 2)
git worktree add ../feature-branch feature-branch

# With new branch (Video 4)
git worktree add -b new-feature ../new-feature main
```

**Use Cases:**
- Parallel feature development (Video 2)
- Code review while working (Video 4)
- Testing in isolation (Video 6)
```

### Quote/Nugget Deduplication

When similar insights appear multiple times:

1. **Identify Core Insight**: Extract the essential point being made
2. **Keep Strongest Version**: Use the most clearly articulated version
3. **Note Variations**: If different phrasings add value, include as alternatives
4. **Attribute Properly**: Track which video(s) contain the insight

**Selection Criteria:**
- Clarity of expression
- Completeness of thought
- Presence of supporting example
- Relevance to target audience

**Example:**
```markdown
## Golden Nugget: Context Management

> "The context window is your most precious resource - treat every token like it costs money, because it does."

**Source**: Video 3 (selected as clearest articulation)
**Also discussed in**: Videos 1, 5 (less complete versions)
```

## Cross-Reference Strategy

Build connections between extracted content:

### 1. Topic Mapping
Create an index showing where each topic appears:
```markdown
## Topic Index

| Topic | Videos | Primary Source |
|-------|--------|----------------|
| MCP Servers | 2, 4, 7 | Video 4 |
| Git Worktrees | 1, 3 | Video 3 |
| Agentic Workflows | 3, 5, 6 | Video 5 |
```

### 2. Workflow Dependencies
Link workflows that build on each other:
```markdown
## Workflow: Advanced Agent Setup

**Prerequisites:**
- Basic Agent Pattern (see workflows.md#basic-agent)
- MCP Configuration (see workflows.md#mcp-setup)

**Builds upon:** Video 2 foundations
**Extended in:** Video 7
```

### 3. Command Context
Link commands to workflows where they're used:
```markdown
### claude --mcp-config

Used in workflows:
- MCP Server Setup (workflows.md#mcp-setup)
- Custom Tool Integration (workflows.md#custom-tools)
```

## Post-Consolidation Validation

After consolidation, verify:

1. **Completeness Check**
   - [ ] All significant content from each video captured
   - [ ] No major topics dropped during deduplication
   - [ ] All workflows have complete steps

2. **Consistency Check**
   - [ ] No contradictory information remains
   - [ ] Terminology is consistent throughout
   - [ ] Version numbers/dates are current

3. **Attribution Check**
   - [ ] Source videos properly credited
   - [ ] Cross-references are accurate
   - [ ] Links work correctly

4. **Quality Check**
   - [ ] Deduplication preserved best versions
   - [ ] Context maintained for commands/code
   - [ ] Golden nuggets are impactful

## Example: TAC Consolidation

The TAC (Tony's Agent Collaboration) consolidation demonstrates these principles:

**Source Material:**
- 7 IndyDevDan videos on Claude Code
- Overlapping coverage of agentic patterns, git workflows, MCP servers

**Consolidation Approach:**
1. Extracted each video individually with multi-file output
2. Identified canonical sources for each major topic
3. Deduplicated frameworks, keeping Video 5's agentic patterns as primary
4. Merged command references, grouping by function
5. Selected strongest golden nuggets, attributed to sources
6. Built cross-reference index in INDEX.md

**Output Structure:**
```
consolidated/
  INDEX.md           # Navigation and topic index
  summary.md         # Combined executive summary
  workflows.md       # All unique workflows, cross-referenced
  commands.md        # Deduplicated command reference
  golden-nuggets.md  # Curated insights with attribution
  code-examples.md   # All code with context
```

**Lessons Learned:**
- Start with the most comprehensive video for each topic
- Preserve unique perspectives even when consolidating
- Cross-references add significant navigation value
- INDEX.md is essential for multi-file output

## Quick Reference

| Task | Strategy |
|------|----------|
| Same concept, multiple videos | Use canonical source + supplement |
| Same command, different examples | Merge with grouped use cases |
| Similar quote, different wording | Keep strongest, note alternatives |
| Conflicting information | Use most recent, note discrepancy |
| Unique content | Preserve with full context |
