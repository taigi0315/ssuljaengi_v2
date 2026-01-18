# Quick Fix Reference Card

## What Was Fixed

### 🔧 Issue 1: Model Name Error
- **Error:** `404 models/gemini-2.5-flash-latest is not found`
- **Fix:** Changed to `gemini-2.0-flash-exp` in `backend/app/config.py`

### 🔧 Issue 2: Recursion Limit Error  
- **Error:** `GraphRecursionError: Recursion limit of 25 reached`
- **Fix:** Simplified workflow to single-pass (no loop back after rewrite)
- **File:** `backend/app/workflows/story_workflow.py`

### 🔧 Issue 3: JSON Parsing Errors
- **Error:** `JSONDecodeError: Unterminated string starting at line X`
- **Fix:** Implemented Pydantic structured output
- **Files:** 
  - `backend/app/services/webtoon_writer.py`
  - `backend/app/services/story_evaluator.py`

## How to Test

```bash
# 1. Restart backend
cd backend
./run.sh

# 2. Test story generation
# - Go to frontend
# - Search for Reddit post
# - Click "Generate Story"
# - Should complete without errors

# 3. Test webtoon generation
# - Click "Generate Webtoon" on generated story
# - Should create script with characters and panels
# - No JSON errors should appear
```

## Expected Behavior

### Story Generation
- ✅ Completes in ~10-30 seconds
- ✅ Returns evaluation score
- ✅ May rewrite once if score < 7.0
- ✅ No recursion errors

### Webtoon Generation
- ✅ Completes in ~10-20 seconds
- ✅ Returns 8-16 panels
- ✅ Returns character descriptions
- ✅ No JSON parsing errors

## Key Changes

| Component | Before | After |
|-----------|--------|-------|
| Model | gemini-2.5-flash-latest | gemini-2.0-flash-exp |
| Workflow | Loop (writer→eval→rewrite→eval) | Single-pass (writer→eval→rewrite→END) |
| Max Iterations | 25+ | 3 |
| JSON Parsing | Manual with json.loads() | Structured output with Pydantic |
| Validation | None | Automatic schema validation |

## Rollback (If Needed)

If issues occur, revert these files:
```bash
git checkout backend/app/config.py
git checkout backend/app/workflows/story_workflow.py
git checkout backend/app/routers/story.py
git checkout backend/app/services/webtoon_writer.py
git checkout backend/app/services/story_evaluator.py
```

## Support

Check these logs if issues persist:
- Story generation: Look for "Workflow X completed"
- Webtoon generation: Look for "Webtoon script created"
- Errors: Look for "ERROR" level logs with stack traces
