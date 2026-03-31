---
description: Capture screenshots for visual verification using Playwright
allowed-tools: Bash, Read, Write, Glob, mcp__playwright__browser_navigate, mcp__playwright__browser_screenshot, mcp__playwright__browser_close
model: sonnet
argument-hint: <url> [--name <description>] [--full-page] [--selector <css>]
---

# EA-Visual-Verify Command

Capture screenshots using Playwright MCP for visual verification of UI states.

## Arguments

- `<url>` - URL to capture (required)
- `--name <description>` - Screenshot description for filename (default: "screenshot")
- `--full-page` - Capture full page scroll
- `--selector <css>` - Capture specific element only

## Screenshot Storage

- **Location**: `validation/screenshots/`
- **Format**: `NN_YYYY-MM-DD_description.png`
- **Examples**:
  - `01_2026-01-25_login-page.png`
  - `02_2026-01-25_dashboard-loaded.png`

## Workflow

### Step 1: Ensure Directory Exists

Create the screenshots directory if it doesn't exist:
```bash
mkdir -p validation/screenshots
```

### Step 2: Determine Screenshot Number

Find the highest existing number for today's date:

```
Glob: validation/screenshots/*_YYYY-MM-DD_*.png
```

Parse existing files to find the next number:
- If no files exist for today: next number = 01
- If files exist: next number = max(existing) + 1

Example logic:
```
existing files: 01_2026-01-25_login.png, 02_2026-01-25_home.png
next number: 03
```

### Step 3: Navigate to URL

Use Playwright MCP to navigate:
```
mcp__playwright__browser_navigate:
  url: "<provided url>"
```

Wait for the page to fully load (network idle).

### Step 4: Capture Screenshot

Generate the filename:
```
filename = "{NN:02d}_{YYYY-MM-DD}_{description}.png"
```

Use Playwright MCP to capture:
```
mcp__playwright__browser_screenshot:
  name: "{filename without extension}"
  fullPage: true/false (based on --full-page argument)
  selector: "<css>" (if --selector provided)
```

### Step 5: Save Screenshot

Move/copy the screenshot to the validation directory:
```
validation/screenshots/{filename}
```

### Step 6: Log the Capture

Append an entry to `validation/validation-log.md`:

```markdown
## [YYYY-MM-DD HH:MM] Screenshot Captured

- **File**: `validation/screenshots/NN_YYYY-MM-DD_description.png`
- **URL**: [captured url]
- **Full Page**: yes/no
- **Selector**: [css selector or "none"]
- **Notes**: [any observations about the page state]
```

Create the log file if it doesn't exist with a header:
```markdown
# Validation Log

Screenshots and validation events are logged here.

---
```

### Step 7: Close Browser (Optional)

If no more screenshots are needed:
```
mcp__playwright__browser_close
```

## Output

Report the capture:
```
Screenshot captured successfully!

File: validation/screenshots/NN_YYYY-MM-DD_description.png
URL: [url]
Size: [dimensions if available]

Logged to: validation/validation-log.md
```

## Error Handling

- If URL is not provided: "Error: URL is required. Usage: /EA-visual-verify <url>"
- If Playwright fails to navigate: Report the error and suggest checking the URL
- If screenshot fails: Report the specific error from Playwright

## Notes

- Screenshots are numbered sequentially within each day
- Numbering resets to 01 on a new day
- Descriptions should be kebab-case (login-page, not login page)
- The validation log provides a chronological record of all captures
