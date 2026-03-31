---
name: security-audit
description: |
  Beginner-friendly security audit for apps. Checks for common vulnerabilities
  including exposed secrets, production readiness, and authentication issues.
  Use when: (1) checking for exposed API keys/secrets, (2) verifying app is
  ready for production deployment, (3) auditing authentication and authorization,
  (4) running a full security check before launch.
  Triggers: "security check", "audit my app", "check for vulnerabilities",
  "is my app secure", "security audit", "check my app for security issues"
---

# Security Audit Skill

A guided security audit for apps you're building. Checks for common vulnerabilities beginners encounter.

## Decision Tree

When triggered, use AskUserQuestion to present these options:

| Option | Description | Reference |
|--------|-------------|-----------|
| **Quick Secrets Check** | Check for exposed API keys and secrets | → [quick-secrets-check.md](references/quick-secrets-check.md) |
| **Pre-Deploy Check** | Verify production readiness | → [pre-deploy-check.md](references/pre-deploy-check.md) |
| **Auth Check** | Verify protected routes are secure | → [auth-check.md](references/auth-check.md) |
| **Full Audit** | Run all three checks | → Run all in sequence |

## Workflow Routing

Based on user selection:

- **Quick Secrets Check** → Load references/quick-secrets-check.md → Execute → Report
- **Pre-Deploy Check** → Load references/pre-deploy-check.md → Execute → Report
- **Auth Check** → Load references/auth-check.md → Execute → Report
- **Full Audit** → Run all three in sequence → Combine and report all findings

## Output Format

All workflows report in this format:

```
Security Check: [Check Name]
══════════════════════════════════════

✓ PASSED: [What passed]
✗ ISSUE:  [What failed]
          [Explanation of the issue]
          [How to fix it]

Summary: X passed, Y issues found
```

## Behavior Notes

- REPORTS issues but does not auto-fix them
- Explanations are beginner-friendly (no jargon)
- Each issue includes "How to fix it" guidance
- Keep severity simple - just "needs attention"
