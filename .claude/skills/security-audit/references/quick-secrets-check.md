# Quick Secrets Check

Check for exposed API keys and secrets - the most common security mistake.

## What This Checks

1. Is .env in .gitignore?
2. Are secrets exposed to the browser? (NEXT_PUBLIC_, VITE_, REACT_APP_)
3. Are there hardcoded secrets in the code?

## Workflow

### Check 1: .env in .gitignore

```
1. Look for .gitignore file in project root
2. Check if it contains ".env" or ".env*" or "*.env"
3. Report result
```

**If .env is NOT in .gitignore:**
```
✗ ISSUE: .env file is not in .gitignore

Your .env file contains secrets (API keys, passwords). If it's not in
.gitignore, it could accidentally be committed to git and shared publicly.

How to fix:
1. Open .gitignore (create it if it doesn't exist)
2. Add these lines:
   .env
   .env.*
   .env.local
3. If you already committed .env, you'll need to rotate your secrets
```

### Check 2: Browser-Exposed Secrets

```
1. Search codebase for: NEXT_PUBLIC_, REACT_APP_, VITE_
2. For each found, check if it looks like a secret:
   - Contains "KEY", "SECRET", "TOKEN", "PASSWORD", "API"
   - Looks like a key pattern (sk-, pk-, etc.)
3. Report any secrets that shouldn't be public
```

**If browser-exposed secrets found:**
```
✗ ISSUE: Secret exposed to browser via [VARIABLE_NAME]

Variables starting with NEXT_PUBLIC_, REACT_APP_, or VITE_ are sent to
the browser. Anyone can see them in the browser's developer tools!

Found: NEXT_PUBLIC_STRIPE_SECRET_KEY (in .env.local)

How to fix:
1. Remove the NEXT_PUBLIC_ prefix (rename to STRIPE_SECRET_KEY)
2. Only access this variable in server-side code
3. Public keys (like Stripe's publishable key) are OK to expose
```

### Check 3: Hardcoded Secrets

```
1. Search code files for patterns like:
   - api_key = "sk-..."
   - password = "..."
   - token = "..."
   - secret = "..."
2. Ignore comments and example placeholders
3. Report any hardcoded values that look like real secrets
```

**If hardcoded secrets found:**
```
✗ ISSUE: Hardcoded secret in [file:line]

Found what looks like a hardcoded API key:
  const apiKey = "sk-ant-abc123..."

Hardcoded secrets in code can be:
- Committed to git accidentally
- Seen by anyone with code access
- Hard to rotate if compromised

How to fix:
1. Move the secret to your .env file:
   ANTHROPIC_API_KEY=sk-ant-abc123...

2. Update your code to read from environment:
   const apiKey = process.env.ANTHROPIC_API_KEY

3. Rotate this key since it was in your code
```

## Final Report

```
Quick Secrets Check Complete
════════════════════════════

[List all checks with ✓ or ✗]

Summary: X of 3 checks passed

[If any issues, remind them to fix before deploying]
```
