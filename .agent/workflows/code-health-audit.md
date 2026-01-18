# Code Health Audit Report

**Date**: 2026-01-18
**Status**: Active - Issues identified, refactoring in progress

## Executive Summary

| Category | Backend | Frontend | Total |
|----------|---------|----------|-------|
| Dead Code | 1 | 1 | 2 |
| Unused Imports | 4 | 1 | 5 |
| DRY Violations | 6+ | 5+ | 11+ |
| Complexity Issues | 4 files | 5 files | 9 files |
| Type Issues | - | 6 | 6 |
| Commented Code | 0 | 1 (114 lines) | 1 |

## Critical Issues (High Priority)

### 1. Long Functions Violating Single Responsibility

| File | Function | Lines | Recommendation |
|------|----------|-------|----------------|
| `backend/app/routers/webtoon.py` | `generate_scene_image()` | 178 | Split into helpers |
| `backend/app/services/webtoon_writer.py` | `_fill_missing_fields_in_dict()` | 186 | Extract per-section handlers |
| `backend/app/services/video_service.py` | `generate_video()` | 168 | Extract frame/ffmpeg logic |
| `backend/app/routers/webtoon.py` | `generate_character_image()` | 70 | Extract logging/error handling |

### 2. Duplicate Code Patterns

#### Backend: Image Selection Logic (DRY Violation)
**Files**: `backend/app/routers/webtoon.py`
**Lines**: 185-217 and 549-584

Both `select_character_image()` and `select_scene_image()` contain identical selection logic:
```python
for image in images:
    if img["id"] == image_id:
        for other in images:
            other["is_selected"] = False
        img["is_selected"] = True
        break
```
**Fix**: Extract to `_mark_image_selected(image_list, image_id)` utility.

#### Frontend: formatGenreName Duplicated 5 Times
**Files**:
- `src/components/StoryBuilder.tsx:16`
- `src/components/CharacterImageGenerator.tsx:144`
- `src/components/SceneImageGeneratorV2.tsx:387`
- `src/components/SceneImageGenerator.tsx:175`
- `src/components/ScriptPreview.tsx:44`

**Fix**: Move to `src/utils/formatters.ts` and import everywhere.

#### Frontend: formatNumber Duplicated
**Files**:
- `src/components/ResultItem.tsx:27`
- `src/components/RedditPostDisplay.tsx:5`

**Fix**: Move to `src/utils/formatters.ts`.

#### Frontend: DEFAULT_SUBREDDITS Duplicated
**Files**:
- `src/components/SearchControls.tsx:14-51`
- `src/components/SubredditSelector.tsx:6-43`

**Fix**: Move to `src/lib/constants.ts`.

### 3. Dead Code

#### Backend: Unused _generate_placeholder Method
**File**: `backend/app/services/image_generator.py:476-495`
**Issue**: Method defined but never called anywhere.
**Fix**: Delete the method.

#### Frontend: Commented Implementation
**File**: `src/components/PostCountInput.tsx:1-114`
**Issue**: 114 lines of old implementation commented out.
**Fix**: Delete commented code (version control preserves history).

### 4. Unused Imports

| File | Import | Line |
|------|--------|------|
| `backend/app/routers/webtoon.py` | `subprocess`, `tempfile` (function-level) | 625-627 |
| `backend/app/routers/webtoon.py` | Redundant model imports | 383 |
| `backend/app/routers/character_library.py` | `Dict`, `Any` | 10 |
| `frontend/src/components/VisualFeedback.tsx` | `useEffect` | 3 |

### 5. TypeScript Issues

#### @ts-ignore Comments
**File**: `src/components/CharacterImageDisplay.tsx:392-395`
**Issue**: Using `// @ts-ignore` to access props incorrectly.
**Fix**: Fix the prop destructuring pattern.

#### Unsafe `any` Types
| File | Line | Context |
|------|------|---------|
| `src/lib/apiClient.ts` | 36, 376, 463, 516, 549 | API response typing |
| `src/components/SceneImageGeneratorV2.tsx` | 160, 165 | `parseDialogues` parameter |
| `src/components/ScriptPreview.tsx` | 123, 150 | `index` should be `number` |

## Medium Priority Issues

### 1. Complex Components (>200 Lines)

| Component | Lines | Issue |
|-----------|-------|-------|
| `SceneImageGeneratorV2.tsx` | 817 | Multiple concerns, 7+ useEffects |
| `VideoGenerator.tsx` | 462 | Canvas logic mixed with rendering |
| `CharacterImageDisplay.tsx` | 450 | Form + display + download mixed |
| `page.tsx` | 420 | Tab management + all features |

### 2. Inconsistent Session Storage Usage

Some components use `useSessionStorage` hook, others use direct `sessionStorage` API:
- **Hook users**: `app/page.tsx`
- **Direct API users**: `SubredditSelector.tsx`, `StoryBuilder.tsx`, `CharacterImageGenerator.tsx`

**Fix**: Standardize on the hook pattern.

### 3. Repeated Error Handling Patterns

**Backend**: 13+ instances of:
```python
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail=f"...")
```

**Frontend**: 12+ instances of:
```typescript
if (!response.ok) {
  const errorData = await response.json().catch(() => ({...}));
  throw new Error(errorData.error?.message || `HTTP ${response.status}`);
}
```

**Fix**: Create centralized error handling utilities.

### 4. Repeated 404 Validation

**Backend**: 13+ instances of:
```python
if resource_id not in storage:
    raise HTTPException(status_code=404, detail="X not found")
```

**Fix**: Create `require_resource(storage, id, type)` helper.

## Low Priority Issues

### 1. Naming Improvements Needed

| Current | Suggested | File |
|---------|-----------|------|
| `image_key` | `character_storage_key` | `webtoon.py:263` |
| `_get_base_style()` | `_infer_character_base_style()` | `image_generator.py:245` |
| `draggingBubble` | `draggingDialogueBubble` | `SceneImageGeneratorV2.tsx` |

### 2. Missing Type Definitions

Frontend types don't fully match backend models:
- Backend `Character` has `reference_tag`, `visual_description` not in frontend
- Backend `Panel` has `composition_notes` not in frontend

## Refactoring Plan

### Phase 1: Quick Wins (Low Risk)
1. ~~Delete dead code (`_generate_placeholder`, commented PostCountInput)~~
2. ~~Remove unused imports~~
3. ~~Extract `formatGenreName`, `formatNumber` to utils~~
4. ~~Move `DEFAULT_SUBREDDITS` to constants~~

### Phase 2: DRY Consolidation (Medium Risk)
1. Extract image selection utility
2. Create error handling utilities (backend + frontend)
3. Create resource validation helper
4. Standardize session storage usage

### Phase 3: Complexity Reduction (Higher Risk)
1. Refactor `generate_scene_image()` into helpers
2. Split `_fill_missing_fields_in_dict()` into handlers
3. Break up `SceneImageGeneratorV2.tsx` component
4. Extract video canvas logic to utilities

## Files Changed Log

| Date | File | Change | Status |
|------|------|--------|--------|
| 2026-01-18 | This audit | Created | Complete |
| 2026-01-18 | `image_generator.py` | Removed unused `_generate_placeholder()` | Complete |
| 2026-01-18 | `character_library.py` | Removed unused imports | Complete |
| 2026-01-18 | `PostCountInput.tsx` | Deleted 114 lines of commented code | Complete |
| 2026-01-18 | `formatters.ts` | Created shared utility module | Complete |
| 2026-01-18 | 7 components | Consolidated `formatGenreName`/`formatNumber` | Complete |

---

## For Next Agent

### State of the Code
- Audit complete, issues identified
- No changes made yet (documentation phase)

### Dependencies
- Backend requires FFmpeg for video generation
- Frontend requires Next.js 16+ features
- Both require API keys for Reddit and Gemini

### Workflow Warnings
1. The `_fill_missing_fields_in_dict()` function is critical for handling malformed LLM output. Refactor carefully.
2. Image selection logic affects user workflows - test thoroughly after changes.
3. Session storage patterns affect data persistence between page loads.
4. Error handling changes should maintain consistent user-facing messages.
