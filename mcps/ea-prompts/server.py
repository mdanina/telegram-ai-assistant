#!/usr/bin/env python3
"""EA Prompts MCP - Prompt library for Claude Code.

A beginner-friendly prompt management system demonstrating the Prompts capability.
Part of the Early AI Adopters Claude Code Fundamentals course.

This MCP demonstrates the "Prompts" capability of MCP - providing
pre-built prompt templates that Claude can use.

Prompts provided (via MCP Prompts capability):
- code-review: Review code for issues and improvements
- explain-code: Explain what code does in plain English
- write-tests: Generate test cases for code
- refactor: Suggest refactoring improvements
- debug: Help debug an error or issue

Tools provided:
- ea_add_prompt: Add a custom prompt to your library
- ea_list_prompts: List all available prompts
- ea_remove_prompt: Remove a custom prompt
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP

# === Server Metadata ===
SERVER_METADATA = {
    "name": "ea-prompts",
    "version": "1.0.0",
    "author": "Early AI Adopters",
    "course": "Claude Code Fundamentals",
    "module": "04 - MCP Servers",
    "description": "Prompt library demonstrating MCP Prompts capability",
    "capabilities": ["tools", "prompts"],
    "tools": [
        {"name": "ea_add_prompt", "description": "Add a custom prompt to your library"},
        {"name": "ea_list_prompts", "description": "List all available prompts"},
        {"name": "ea_remove_prompt", "description": "Remove a custom prompt"},
        {"name": "ea_prompts_status", "description": "Get server status and metadata"},
    ],
    "prompts": [
        {"name": "code-review", "description": "Review code for issues and improvements"},
        {"name": "explain-code", "description": "Explain what code does in plain English"},
        {"name": "write-tests", "description": "Generate test cases for code"},
        {"name": "refactor", "description": "Suggest refactoring improvements"},
        {"name": "debug", "description": "Help debug an error or issue"},
    ],
    "storage_location": "~/.ea-prompts/custom_prompts.json",
}

# Initialize the MCP server
mcp = FastMCP(
    name="ea-prompts",
    instructions="Prompt library demonstrating MCP Prompts capability"
)

# === Built-in Prompts ===

BUILTIN_PROMPTS = {
    "code-review": {
        "name": "code-review",
        "description": "Review code for issues, bugs, and improvements",
        "template": """Review the following code for:
1. Potential bugs or errors
2. Security vulnerabilities
3. Performance issues
4. Code style and readability
5. Suggested improvements

Code to review:
{code}

Provide specific, actionable feedback.""",
        "arguments": [{"name": "code", "description": "The code to review", "required": True}],
        "builtin": True
    },
    "explain-code": {
        "name": "explain-code",
        "description": "Explain what code does in plain English",
        "template": """Explain the following code in plain English, suitable for a beginner:

1. What does this code do overall?
2. Break down each major section
3. Explain any complex or unusual patterns
4. Mention any potential issues or edge cases

Code to explain:
{code}""",
        "arguments": [{"name": "code", "description": "The code to explain", "required": True}],
        "builtin": True
    },
    "write-tests": {
        "name": "write-tests",
        "description": "Generate test cases for code",
        "template": """Generate comprehensive test cases for the following code:

1. Unit tests for each function/method
2. Edge cases and boundary conditions
3. Error handling scenarios
4. Integration points (if applicable)

Use appropriate testing framework based on the language.

Code to test:
{code}""",
        "arguments": [{"name": "code", "description": "The code to test", "required": True}],
        "builtin": True
    },
    "refactor": {
        "name": "refactor",
        "description": "Suggest refactoring improvements",
        "template": """Analyze this code for refactoring opportunities:

1. DRY (Don't Repeat Yourself) violations
2. Functions that are too long
3. Poor naming
4. Missing abstractions
5. Simplification opportunities

Provide the refactored version with explanations.

Code to refactor:
{code}""",
        "arguments": [{"name": "code", "description": "The code to refactor", "required": True}],
        "builtin": True
    },
    "debug": {
        "name": "debug",
        "description": "Help debug an error or issue",
        "template": """Help debug this issue:

Error/Problem:
{error}

Relevant code:
{code}

Steps to reproduce (if known):
{steps}

Analyze and suggest:
1. Likely cause of the issue
2. How to fix it
3. How to prevent similar issues""",
        "arguments": [
            {"name": "error", "description": "The error message or problem description", "required": True},
            {"name": "code", "description": "The relevant code", "required": True},
            {"name": "steps", "description": "Steps to reproduce (optional)", "required": False}
        ],
        "builtin": True
    }
}


# === Pydantic Input Models ===

class AddPromptInput(BaseModel):
    """Input for adding a custom prompt."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        description="Unique name for the prompt (lowercase, hyphens allowed)",
        min_length=2,
        max_length=50
    )
    description: str = Field(
        ...,
        description="What this prompt does",
        min_length=5,
        max_length=200
    )
    template: str = Field(
        ...,
        description="The prompt template (use {arg_name} for variables)",
        min_length=10,
        max_length=5000
    )
    arguments: Optional[str] = Field(
        default=None,
        description="Comma-separated list of argument names (e.g., 'code,context')"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-z][a-z0-9-]*$', v):
            raise ValueError("Name must be lowercase letters, numbers, and hyphens only, starting with a letter")
        return v


class ListPromptsInput(BaseModel):
    """Input for listing prompts."""
    model_config = ConfigDict(str_strip_whitespace=True)

    include_templates: bool = Field(
        default=False,
        description="Show full template text (default: False)"
    )


class RemovePromptInput(BaseModel):
    """Input for removing a custom prompt."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        description="The prompt name to remove"
    )
    confirm: bool = Field(
        default=False,
        description="Must be True to confirm deletion"
    )


# === Storage ===

def get_storage_path() -> Path:
    """Get the path to the prompts storage file."""
    storage_dir = Path.home() / ".ea-prompts"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir / "custom_prompts.json"


def load_custom_prompts() -> dict:
    """Load custom prompts from storage."""
    storage_path = get_storage_path()
    if storage_path.exists():
        try:
            return json.loads(storage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_custom_prompts(prompts: dict) -> None:
    """Save custom prompts to storage."""
    storage_path = get_storage_path()
    storage_path.write_text(json.dumps(prompts, indent=2), encoding="utf-8")


def get_all_prompts() -> dict:
    """Get all prompts (builtin + custom)."""
    all_prompts = dict(BUILTIN_PROMPTS)
    custom = load_custom_prompts()
    all_prompts.update(custom)
    return all_prompts


# === Register MCP Prompts ===

@mcp.prompt()
def code_review(code: str) -> str:
    """Review code for issues and improvements."""
    return BUILTIN_PROMPTS["code-review"]["template"].format(code=code)


@mcp.prompt()
def explain_code(code: str) -> str:
    """Explain what code does in plain English."""
    return BUILTIN_PROMPTS["explain-code"]["template"].format(code=code)


@mcp.prompt()
def write_tests(code: str) -> str:
    """Generate test cases for code."""
    return BUILTIN_PROMPTS["write-tests"]["template"].format(code=code)


@mcp.prompt()
def refactor(code: str) -> str:
    """Suggest refactoring improvements."""
    return BUILTIN_PROMPTS["refactor"]["template"].format(code=code)


@mcp.prompt()
def debug(error: str, code: str, steps: str = "Not provided") -> str:
    """Help debug an error or issue."""
    return BUILTIN_PROMPTS["debug"]["template"].format(error=error, code=code, steps=steps)


# === Tools ===

@mcp.tool(
    name="ea_add_prompt",
    annotations={
        "title": "Add Custom Prompt",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def ea_add_prompt(params: AddPromptInput) -> str:
    """Add a custom prompt to your library.

    Create a reusable prompt template that can be used later.
    Use {arg_name} syntax in templates for variable substitution.

    Args:
        params: AddPromptInput containing:
            - name (str): Unique name for the prompt (lowercase, hyphens only)
            - description (str): What this prompt does
            - template (str): The prompt template with {variables}
            - arguments (Optional[str]): Comma-separated argument names

    Returns:
        str: Confirmation with prompt details

    Examples:
        - Add a summarize prompt with one argument
        - Add a comparison prompt with two arguments (code1, code2)
    """
    if params.name in BUILTIN_PROMPTS:
        return f"Error: '{params.name}' is a built-in prompt and cannot be overwritten."

    # Parse arguments
    arg_list = []
    if params.arguments:
        for arg in params.arguments.split(","):
            arg = arg.strip()
            if arg:
                arg_list.append({
                    "name": arg,
                    "description": f"Value for {arg}",
                    "required": True
                })

    prompt = {
        "name": params.name,
        "description": params.description,
        "template": params.template,
        "arguments": arg_list,
        "builtin": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    custom = load_custom_prompts()
    custom[params.name] = prompt
    save_custom_prompts(custom)

    args_display = ', '.join(a['name'] for a in arg_list) if arg_list else 'none'
    return f"""Custom prompt added: {params.name}
Description: {params.description}
Arguments: {args_display}

Use with: /prompt {params.name}"""


@mcp.tool(
    name="ea_list_prompts",
    annotations={
        "title": "List Available Prompts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_list_prompts(params: ListPromptsInput) -> str:
    """List all available prompts.

    Shows both built-in prompts and any custom prompts you've added.

    Args:
        params: ListPromptsInput containing:
            - include_templates (bool): Show full template text (default: False)

    Returns:
        str: List of prompts with descriptions

    Examples:
        - "List prompts" -> shows names and descriptions
        - "List prompts with templates" -> shows full template text
    """
    all_prompts = get_all_prompts()

    if not all_prompts:
        return "No prompts available."

    output = ["# Available Prompts\n"]
    output.append("## Built-in Prompts\n")

    for name, prompt in sorted(all_prompts.items()):
        if prompt.get("builtin"):
            args = ", ".join(a["name"] for a in prompt.get("arguments", []))
            output.append(f"### {name}")
            output.append(f"**Description:** {prompt['description']}")
            output.append(f"**Arguments:** {args or 'none'}")
            if params.include_templates:
                output.append(f"\n```\n{prompt['template']}\n```")
            output.append("")

    # Custom prompts
    custom = load_custom_prompts()
    if custom:
        output.append("## Custom Prompts\n")
        for name, prompt in sorted(custom.items()):
            args = ", ".join(a["name"] for a in prompt.get("arguments", []))
            output.append(f"### {name}")
            output.append(f"**Description:** {prompt['description']}")
            output.append(f"**Arguments:** {args or 'none'}")
            if params.include_templates:
                output.append(f"\n```\n{prompt['template']}\n```")
            output.append("")

    output.append(f"**Total:** {len(BUILTIN_PROMPTS)} built-in, {len(custom)} custom")

    return "\n".join(output)


@mcp.tool(
    name="ea_remove_prompt",
    annotations={
        "title": "Remove Custom Prompt",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_remove_prompt(params: RemovePromptInput) -> str:
    """Remove a custom prompt.

    Only custom prompts can be removed. Built-in prompts are permanent.

    Args:
        params: RemovePromptInput containing:
            - name (str): The prompt name to remove
            - confirm (bool): Must be True to confirm deletion

    Returns:
        str: Confirmation or error message

    Examples:
        - "Remove my-prompt" -> asks for confirmation
        - "Remove my-prompt with confirm=True" -> deletes the prompt
    """
    if not params.confirm:
        return "Set confirm=True to delete. This cannot be undone."

    if params.name in BUILTIN_PROMPTS:
        return f"Error: '{params.name}' is a built-in prompt and cannot be removed."

    custom = load_custom_prompts()
    if params.name not in custom:
        return f"Custom prompt not found: {params.name}. Use ea_list_prompts to see available prompts."

    del custom[params.name]
    save_custom_prompts(custom)

    return f"Removed custom prompt: {params.name}"


@mcp.tool(
    name="ea_prompts_status",
    annotations={
        "title": "Server Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_prompts_status() -> str:
    """Get server status and metadata.

    Returns information about this MCP server including version,
    available tools, prompts, and current statistics.

    Use this to verify the server is running and see what it can do.

    Returns:
        str: Server metadata and status formatted as markdown
    """
    custom = load_custom_prompts()
    storage_path = get_storage_path()

    tools_list = "\n".join(f"  - **{t['name']}**: {t['description']}" for t in SERVER_METADATA["tools"])
    prompts_list = "\n".join(f"  - **{p['name']}**: {p['description']}" for p in SERVER_METADATA["prompts"])

    return f"""# {SERVER_METADATA['name']} v{SERVER_METADATA['version']}

**Author:** {SERVER_METADATA['author']}
**Course:** {SERVER_METADATA['course']}
**Module:** {SERVER_METADATA['module']}

## Description
{SERVER_METADATA['description']}

## Capabilities
This MCP demonstrates both **Tools** and **Prompts** capabilities.

## Available Tools
{tools_list}

## Built-in Prompts
{prompts_list}

## Current Stats
- **Built-in prompts:** {len(BUILTIN_PROMPTS)}
- **Custom prompts:** {len(custom)}
- **Storage path:** {storage_path}

## Status: CONNECTED
Server is running and ready to accept commands."""


# === Entry Point ===

if __name__ == "__main__":
    mcp.run()
