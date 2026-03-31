# Pivot Strategies Reference

When Time Travel reverts to a checkpoint, you must choose a **fundamentally different approach**. This reference helps identify alternative strategies based on the type of failure encountered.

---

## Quick Decision Matrix

| Error Category | First Pivot | Second Pivot | Last Resort |
|----------------|-------------|--------------|-------------|
| Import/Module | Use stdlib alternative | Implement manually | Simplify scope |
| Build/Compile | Check versions/deps | Simplify types | Remove feature |
| Test Failure | Change test strategy | Mock less, use real | Reduce coverage |
| API/Interface | Read actual source | Use different endpoint | Direct implementation |
| Performance | Different algorithm | Reduce scope | Accept tradeoff |
| Timeout | Chunk/batch work | Async approach | Increase limits |

---

## Import/Module Errors

### Symptoms
- `ModuleNotFoundError`
- `ImportError`
- `Cannot find module`
- Version conflicts

### Pivot Strategies

**Level 1: Alternative Library**
```
Failed: import pandas
Pivot to: import csv (stdlib)

Failed: import requests
Pivot to: import urllib.request (stdlib)

Failed: import pydantic
Pivot to: dataclasses (stdlib)
```

**Level 2: Manual Implementation**
```
Failed: Both pandas and csv caused issues
Pivot to: Manual string parsing with split/strip

Failed: Complex HTTP library
Pivot to: Simple socket-based request
```

**Level 3: Scope Reduction**
```
Failed: Full feature with dependencies
Pivot to: Minimal viable version without the problematic dependency
```

---

## Build/Compile Errors

### Symptoms
- Type errors
- Syntax errors
- Missing dependencies
- Version mismatches

### Pivot Strategies

**Level 1: Version/Dependency Fix**
```
Failed: Build with latest version
Pivot to: Pin to known-working version

Failed: Complex type annotations
Pivot to: Simpler types, add # type: ignore where needed
```

**Level 2: Architecture Simplification**
```
Failed: Generic typed implementation
Pivot to: Concrete types only

Failed: Async implementation
Pivot to: Synchronous first, convert later
```

**Level 3: Feature Removal**
```
Failed: Full feature causes cascading build failures
Pivot to: Stub implementation that compiles, TODO for later
```

---

## Test Failures

### Symptoms
- Assertion failures
- Timeout in tests
- Flaky tests
- Mock/fixture issues

### Pivot Strategies

**Level 1: Test Strategy Change**
```
Failed: Unit tests with heavy mocking
Pivot to: Integration tests with real components

Failed: Testing internal implementation
Pivot to: Testing public interface only
```

**Level 2: Reduce Mocking**
```
Failed: Complex mock setup
Pivot to: Use real database/API with test data

Failed: Mock returning wrong type
Pivot to: Create real fixture factory
```

**Level 3: Coverage Reduction**
```
Failed: 100% coverage goal causing issues
Pivot to: Critical path coverage only (happy path + main error cases)
```

---

## API/Interface Errors

### Symptoms
- Method not found
- Wrong number of arguments
- Type mismatch
- Unexpected return value

### Pivot Strategies

**Level 1: Source Code Verification**
```
Failed: Assumed API based on documentation
Pivot to: Read actual source code, verify signatures

Failed: Used outdated API
Pivot to: Check current version's interface
```

**Level 2: Alternative Endpoint/Method**
```
Failed: Complex endpoint with many params
Pivot to: Simpler endpoint, process result differently

Failed: Bulk API
Pivot to: Individual calls with batching
```

**Level 3: Direct Implementation**
```
Failed: Using library wrapper
Pivot to: Direct HTTP/protocol implementation

Failed: SDK method
Pivot to: Raw API call with manual serialization
```

---

## Performance/Timeout Issues

### Symptoms
- Operation timeout
- Memory exhaustion
- CPU spike
- Slow response

### Pivot Strategies

**Level 1: Algorithm Change**
```
Failed: O(n^2) algorithm on large dataset
Pivot to: O(n log n) or O(n) alternative

Failed: Loading all data into memory
Pivot to: Streaming/chunked processing
```

**Level 2: Scope Reduction**
```
Failed: Processing entire dataset
Pivot to: Sample or paginated processing

Failed: Complex calculation
Pivot to: Approximation or cached result
```

**Level 3: Accept Tradeoff**
```
Failed: Trying to optimize within constraints
Pivot to: Increase timeout/memory limits with justification

Failed: Real-time requirement
Pivot to: Async/background processing
```

---

## Context/State Errors

### Symptoms
- Undefined variable
- Null pointer
- State corruption
- Race condition

### Pivot Strategies

**Level 1: Explicit State Management**
```
Failed: Implicit state assumptions
Pivot to: Explicit state passing between functions

Failed: Global state mutation
Pivot to: Immutable state with copies
```

**Level 2: Isolation**
```
Failed: Shared state between components
Pivot to: Isolated state per component

Failed: Async state updates
Pivot to: Synchronous with locks/queues
```

**Level 3: Simplification**
```
Failed: Complex state machine
Pivot to: Linear flow without state

Failed: Distributed state
Pivot to: Single source of truth
```

---

## File/IO Errors

### Symptoms
- File not found
- Permission denied
- Encoding errors
- Path issues

### Pivot Strategies

**Level 1: Path/Permission Fix**
```
Failed: Relative path assumption
Pivot to: Absolute path with Path(__file__).parent

Failed: Permission error
Pivot to: Use temp directory or user home
```

**Level 2: Encoding Handling**
```
Failed: UTF-8 assumption
Pivot to: Detect encoding or use binary mode

Failed: Line ending issues
Pivot to: Universal newlines mode
```

**Level 3: Alternative Storage**
```
Failed: File system operations
Pivot to: In-memory with optional persistence

Failed: Complex file format
Pivot to: Simple JSON or plain text
```

---

## General Pivot Principles

### The 10x Simpler Rule
When pivoting, aim for an approach that is **10x simpler** than what failed. Complexity breeds failure.

### The "What If It Didn't Exist" Test
Ask: "If this library/feature/approach didn't exist, how would I solve this?"

### The Minimum Viable Pivot
1. What is the **absolute minimum** that satisfies the requirement?
2. Implement that first
3. Add complexity only if minimum works

### The Reversal Check
Before implementing a pivot:
- [ ] Is this genuinely different from what failed?
- [ ] Does this avoid the root cause of the failure?
- [ ] Is this simpler, not more complex?

---

## Anti-Patterns to Avoid

### "Just Try Harder"
**Wrong**: Same approach with minor tweaks
**Right**: Fundamentally different strategy

### "Add More Abstraction"
**Wrong**: Wrap failing code in more layers
**Right**: Remove abstraction, go direct

### "Upgrade Everything"
**Wrong**: Update all dependencies hoping it fixes
**Right**: Identify specific version that works

### "Catch All Exceptions"
**Wrong**: Suppress errors to make tests pass
**Right**: Fix root cause or change approach
