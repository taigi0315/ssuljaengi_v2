# Story Workflow Fix Summary

## Issues Fixed

### 1. Invalid Gemini Model Name
**Problem**: The code was using `gemini-2.5-flash-latest` which doesn't exist, causing 404 errors.

**Solution**: Changed to `gemini-2.0-flash-exp` in:
- `backend/app/config.py` (default value)
- `backend/.env.example` (documentation)

### 2. Infinite Loop in Workflow Graph
**Problem**: The workflow had a loop: `writer → evaluator → rewriter → evaluator → ...` which could exceed the 25-step recursion limit.

**Solution**: Simplified the workflow to a single-pass design:
- `writer → evaluator → (if score < threshold) → rewriter → END`
- After rewrite, workflow goes directly to END (no loop back to evaluator)
- Changed `should_rewrite()` to only allow rewrite when `rewrite_count == 0`

### 3. Added Recursion Limit Safety
**Problem**: No explicit recursion limit was set.

**Solution**: Added `config={"recursion_limit": 10}` when invoking the workflow in `backend/app/routers/story.py`

## Workflow Flow (After Fix)

```
START
  ↓
Writer (generates initial story)
  ↓
Evaluator (scores the story)
  ↓
Decision: score < threshold AND rewrite_count == 0?
  ├─ YES → Rewriter (improves story) → END
  └─ NO → END
```

## Maximum Iterations
- **Before**: Could loop up to 25 times (recursion limit)
- **After**: Maximum 3 nodes (writer → evaluator → rewriter)

## Files Modified
1. `backend/app/config.py` - Updated default Gemini model name
2. `backend/app/workflows/story_workflow.py` - Fixed workflow graph and routing logic
3. `backend/app/routers/story.py` - Added recursion limit config
4. `backend/.env.example` - Updated example model name
