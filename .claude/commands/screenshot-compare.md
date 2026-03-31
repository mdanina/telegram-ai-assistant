---
description: Quick utility to take before/after screenshots of any localhost app
allowed-tools: Bash, Glob, ToolSearch
model: sonnet
argument-hint: <url> [description]
---

# EA-Screenshot-Compare Command

Utility command for quickly capturing screenshots during development.

## Arguments

- `<url>` - URL to capture (required, e.g., http://localhost:5173)
- `[description]` - Optional description for filename (e.g., "login-page")

## Workflow

### Step 1: Parse Arguments

Check if URL is provided:
- If missing: "Error: URL required. Usage: /EA-screenshot-compare <url> [description]"
- If provided but invalid: Check if it starts with http:// or https://

Default description if not provided: "screenshot"

### Step 2: Ensure Directory Exists

```bash
mkdir -p validation/screenshots
```

### Step 3: Determine Next Screenshot Number

Find existing screenshots for today:
```
Glob: validation/screenshots/*_$(date +%Y-%m-%d)_*.png
```

Parse to find the highest number:
- If none exist: next = 01
- If exist: next = max + 1

Format: `{NN:02d}_{YYYY-MM-DD}_{description}.png`

Example: `03_2026-02-05_dashboard.png`

### Step 4: Load Playwright MCP Tools

Use ToolSearch to load Playwright:
```
ToolSearch: "playwright navigate screenshot"
```

### Step 5: Navigate and Capture

Navigate to URL:
```
mcp__playwright__browser_navigate:
  url: "<provided url>"
```

Wait 2 seconds for page load:
```bash
sleep 2
```

Take screenshot:
```
mcp__playwright__browser_screenshot:
  name: "{NN}_{date}_{description}"
  fullPage: true
```

### Step 6: Report Success

Display:
```
📸 Screenshot captured successfully!

File: validation/screenshots/{NN}_{date}_{description}.png
URL: {url}

Saved to validation log.
```

### Step 7: Update Validation Log

Append to `validation/validation-log.md`:

```markdown
## [YYYY-MM-DD HH:MM] Screenshot Captured

- **File**: `validation/screenshots/{filename}`
- **URL**: {url}
- **Description**: {description}
```

Create the log file with header if it doesn't exist:
```markdown
# Validation Log

Screenshots and validation events are logged here.

---
```

## Examples

```bash
# Basic screenshot
/EA-screenshot-compare http://localhost:5173

# With description
/EA-screenshot-compare http://localhost:5173 login-page

# Different port
/EA-screenshot-compare http://localhost:3000 dashboard-view
```

## Error Handling

- If URL is invalid: "Error: Invalid URL format. Use http:// or https://"
- If page fails to load: "Error: Could not load {url}. Is the server running?"
- If Playwright fails: Show error and suggest checking MCP configuration

## Notes

- Screenshots are numbered sequentially per day
- Numbering resets to 01 each day
- Use kebab-case for descriptions (login-page, not "login page")
- Full-page screenshots capture the entire scrollable area
- Browser remains open for subsequent screenshots (better performance)
