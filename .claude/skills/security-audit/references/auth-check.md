# Auth Check

Verify your authentication and authorization are properly implemented.

## What This Checks

1. Are sensitive routes protected?
2. Can users access other users' data?

## Workflow

### Check 1: Protected Routes

```
1. Find all API routes/endpoints in the project
2. Categorize each as:
   - Public (should be accessible without login)
   - Protected (should require authentication)
3. Check if protected routes have auth middleware/checks
```

**Present route table:**
```
Route Analysis
══════════════

| Route | Method | Auth Required? | Auth Implemented? |
|-------|--------|---------------|-------------------|
| /api/users/:id | GET | Yes | ✗ No |
| /api/posts | GET | No | - |
| /api/posts | POST | Yes | ✓ Yes |
| /api/admin/users | GET | Yes | ✗ No |
```

**If unprotected routes found:**
```
✗ ISSUE: Sensitive routes lack authentication

Found routes that should require login but don't:

/api/users/:id (GET) - Returns user data
  Anyone can access any user's information!

/api/admin/users (GET) - Lists all users
  Admin routes are accessible to everyone!

How to fix:
Add authentication middleware to these routes.

Example (Express + JWT):
// Before (unprotected)
app.get('/api/users/:id', getUserById)

// After (protected)
app.get('/api/users/:id', authMiddleware, getUserById)
```

### Check 2: User Data Isolation

```
1. Find routes that access user-specific data
2. Check if they verify the requesting user owns the data
3. Look for patterns like:
   - /api/users/:id where :id comes from URL (dangerous!)
   - /api/profile where user comes from session (safer)
```

**If data leakage possible:**
```
✗ ISSUE: Users may access other users' data

Found route vulnerable to data leakage:

// routes/users.js:25
app.get('/api/users/:id', authMiddleware, async (req, res) => {
  const user = await User.findById(req.params.id)  // Uses URL parameter!
  res.json(user)
})

Problem: User A can request /api/users/B_ID and see User B's data.

How to fix:
Option 1 - Use session user (for "my data" routes):
app.get('/api/profile', authMiddleware, async (req, res) => {
  const user = await User.findById(req.user.id)  // Uses logged-in user
  res.json(user)
})

Option 2 - Verify ownership (for routes that need ID):
app.get('/api/users/:id', authMiddleware, async (req, res) => {
  if (req.params.id !== req.user.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Not authorized' })
  }
  const user = await User.findById(req.params.id)
  res.json(user)
})
```

## Final Report

```
Auth Check Complete
═══════════════════

Routes analyzed: X
  - Public routes: Y
  - Protected routes: Z

[List all checks with ✓ or ✗]

Summary: X of 2 checks passed

[If issues: "These auth issues could let attackers access user data"]
[If all pass: "Your authentication looks solid!"]
```
