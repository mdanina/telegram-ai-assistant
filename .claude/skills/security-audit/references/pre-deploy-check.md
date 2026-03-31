# Pre-Deploy Check

Verify your app is ready for production deployment.

## What This Checks

1. Known vulnerabilities in dependencies
2. Security headers configured
3. HTTPS enforced
4. Error messages don't leak information

## Workflow

### Check 1: Dependency Vulnerabilities

```
1. Detect package manager (npm, yarn, pnpm, pip, etc.)
2. Run appropriate audit command:
   - npm: npm audit --json
   - yarn: yarn audit --json
   - pip: pip-audit
3. Report high and critical vulnerabilities
```

**If vulnerabilities found:**
```
✗ ISSUE: X vulnerable dependencies found

Your dependencies have known security issues:

HIGH: lodash < 4.17.21 - Prototype Pollution
  Found in: package.json → lodash@4.17.19
  Fix: npm update lodash

CRITICAL: axios < 0.21.1 - Server-Side Request Forgery
  Found in: package.json → axios@0.19.0
  Fix: npm update axios

How to fix:
1. Run: npm audit fix
2. For issues that can't auto-fix, manually update in package.json
3. Test your app after updates
```

### Check 2: Security Headers

```
1. Look for header configuration in:
   - next.config.js (Next.js)
   - server.js / app.js (Express)
   - vercel.json / netlify.toml
   - middleware files
2. Check for these headers:
   - X-Content-Type-Options
   - X-Frame-Options
   - Content-Security-Policy (optional for beginners)
```

**If headers missing:**
```
✗ ISSUE: Security headers not configured

Security headers tell browsers how to handle your site safely.
Common headers protect against:
- Clickjacking (X-Frame-Options)
- MIME sniffing attacks (X-Content-Type-Options)

How to fix (Next.js example):
// next.config.js
module.exports = {
  async headers() {
    return [{
      source: '/(.*)',
      headers: [
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
      ],
    }]
  }
}
```

### Check 3: HTTPS Enforcement

```
1. Check for HTTPS redirect configuration
2. Look for HSTS header (Strict-Transport-Security)
3. Check if mixed content (http:// resources on https:// page) exists
```

**If HTTPS not enforced:**
```
✗ ISSUE: HTTPS not enforced

Users can access your site via http:// which is insecure.
Passwords, API keys, and user data could be intercepted.

How to fix:
Most hosting platforms (Vercel, Netlify, Heroku) handle this automatically.

If self-hosting, add HTTPS redirect:
// Express example
app.use((req, res, next) => {
  if (req.header('x-forwarded-proto') !== 'https') {
    res.redirect(`https://${req.header('host')}${req.url}`)
  } else {
    next()
  }
})
```

### Check 4: Error Message Sanitization

```
1. Search for error handling code
2. Check if stack traces are exposed to users
3. Look for environment checks (only show details in development)
```

**If detailed errors exposed:**
```
✗ ISSUE: Detailed error messages exposed in production

Found error handler that shows stack traces:
  app.use((err, req, res) => {
    res.status(500).json({ error: err.stack }) // Leaks internal details!
  })

Stack traces reveal:
- Internal file paths
- Library versions
- Code structure

How to fix:
app.use((err, req, res) => {
  if (process.env.NODE_ENV === 'production') {
    res.status(500).json({ error: 'Something went wrong' })
  } else {
    res.status(500).json({ error: err.stack }) // Only in development
  }
})
```

## Final Report

```
Pre-Deploy Check Complete
═════════════════════════

[List all checks with ✓ or ✗]

Summary: X of 4 checks passed

[If any issues: "Fix these issues before deploying to production"]
[If all pass: "Your app looks ready for deployment!"]
```
