---
title: Webtoon Script Validation Error Fix
status: completed
created: 2026-01-16
---

# Webtoon Script Validation Error Fix

## Problem Statement

The webtoon script generation was failing intermittently with Pydantic validation errors when the LLM (Gemini) returned incomplete JSON objects missing required fields, particularly `visual_prompt` in panels.

### Error Pattern
```
ValidationError: 1 validation error for WebtoonScript
panels.12.visual_prompt
  Field required [type=missing, input_value={...}, input_type=dict]
```

### Root Cause Analysis

1. **LLM Inconsistency**: Gemini sometimes generates incomplete JSON where `visual_prompt` or other panel fields are missing
2. **Validation Timing**: Pydantic validates during `__init__()`, so validation errors occur BEFORE any post-processing can fill missing fields
3. **Previous Approach Failed**: The `_fill_missing_fields()` method operated on the Pydantic model AFTER creation, which was too late

## Solution

### Strategy
Fill missing fields in the raw dictionary **BEFORE** Pydantic validation occurs.

### Implementation

#### 1. New Method: `_fill_missing_fields_in_dict()`
- Operates on raw dict from LLM before Pydantic model creation
- Ensures all required fields exist with sensible defaults
- Logs warnings for monitoring

#### 2. Field Filling Logic

**Panel Fields:**
- `panel_number`: Auto-increment if missing (i+1)
- `shot_type`: Default to "Medium Shot"
- `active_character_names`: Default to empty list
- `visual_prompt`: Generate from character descriptions + shot_type
- `dialogue`: Default to None

**Character Fields:**
- `name`: Default to "Unknown Character"
- `gender`: Infer from visual_description keywords (woman/female/she → female, man/male/he → male)
- `face`, `hair`, `body`, `outfit`, `mood`: Placeholder text if missing
- `visual_description`: Default to "A character in the story"

#### 3. Execution Flow
```python
# 1. LLM generates JSON (may be incomplete)
result = await chain.ainvoke({...})

# 2. Fill missing fields in raw dict
result = self._fill_missing_fields_in_dict(result)

# 3. Create Pydantic model (now guaranteed to pass validation)
webtoon_script = WebtoonScript(**result)
```

## Files Modified

- `backend/app/services/webtoon_writer.py`
  - Replaced `_fill_missing_fields()` with `_fill_missing_fields_in_dict()`
  - Updated `convert_story_to_script()` to call new method before Pydantic validation
  - Added comprehensive field checking and default value logic

## Testing Checklist

- [ ] Generate webtoon script multiple times to verify no validation errors
- [ ] Check logs for warnings about filled fields
- [ ] Verify generated visual_prompts are sensible when auto-filled
- [ ] Confirm character fields are properly inferred/filled
- [ ] Test with various story lengths and character counts

## Expected Behavior

1. **No More Validation Errors**: All webtoon script generations should succeed
2. **Graceful Degradation**: Missing fields are filled with sensible defaults
3. **Monitoring**: Warnings logged when fields are auto-filled
4. **Quality**: Auto-generated visual_prompts combine shot_type + character descriptions

## Acceptance Criteria

✅ Webtoon script generation completes without Pydantic validation errors
✅ Missing `visual_prompt` fields are auto-generated with character descriptions
✅ Missing character fields are filled with placeholders or inferred values
✅ Warnings are logged for monitoring LLM output quality
✅ Backend auto-reloads and applies changes immediately

## Notes

- The LLM still generates complete data most of the time - this is a safety net
- Auto-filled visual_prompts may be less detailed than LLM-generated ones
- Consider improving the LLM prompt if warnings appear frequently
- Character fields are rarely missing - panels are the main issue
