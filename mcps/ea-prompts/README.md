# EA Prompts MCP

A prompt library for Claude Code demonstrating the **Prompts** capability of MCP.

Part of the **Early AI Adopters Claude Code Fundamentals** course.

## What This Demonstrates

MCPs can provide three types of capabilities:
1. **Tools** - Actions Claude can take (like our ea-memory MCP)
2. **Resources** - Data Claude can access
3. **Prompts** - Pre-built instructions Claude can use

This MCP demonstrates the **Prompts** capability by providing reusable prompt templates.

## Built-in Prompts

| Prompt | Description | Arguments |
|--------|-------------|-----------|
| `code-review` | Review code for issues and improvements | code |
| `explain-code` | Explain code in plain English | code |
| `write-tests` | Generate test cases | code |
| `refactor` | Suggest refactoring improvements | code |
| `debug` | Help debug an error | error, code, steps |

## Tools

| Tool | Description |
|------|-------------|
| `ea_add_prompt` | Add a custom prompt to your library |
| `ea_list_prompts` | List all available prompts |
| `ea_remove_prompt` | Remove a custom prompt |

## Installation

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "ea-prompts": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ea-prompts", "python", "server.py"]
    }
  }
}
```

## Usage

### Using Built-in Prompts

In Claude Code, use `/prompt` followed by the prompt name:

```
/prompt code-review
```

Or use them directly in conversation - Claude will recognize when these prompts are available.

### Adding Custom Prompts

```
ea_add_prompt(
    name="summarize",
    description="Summarize a document concisely",
    template="Summarize the following in 3-5 bullet points:\n\n{content}",
    arguments="content"
)
```

### Listing Prompts

```
ea_list_prompts()
ea_list_prompts(include_templates=True)  # Show full templates
```

## Storage

Custom prompts are stored in `~/.ea-prompts/custom_prompts.json`.

## Why Prompts Matter

Instead of typing the same instructions repeatedly, prompts let you:
- Save proven prompt patterns
- Share prompts with your team
- Ensure consistency across sessions
- Build a library of specialized instructions

---

*Built for the Early AI Adopters community*
