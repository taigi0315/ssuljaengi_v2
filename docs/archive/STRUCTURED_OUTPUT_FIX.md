# Structured Output Implementation Fix

## Problem
The webtoon writer and story evaluator were experiencing JSON parsing errors because:
1. LLM responses were being truncated mid-JSON
2. Manual JSON parsing was fragile and error-prone
3. No schema enforcement for LLM outputs
4. **NEW:** `with_structured_output()` incompatible with nested Pydantic models in Gemini

## Solution
Implemented `JsonOutputParser` with Pydantic schema validation for all services that need structured data.

## Changes Made

### 1. Webtoon Writer Service (`backend/app/services/webtoon_writer.py`)

**Before:**
- Used `StrOutputParser()` to get raw text
- Manually parsed JSON with `json.loads()`
- Manually created Pydantic models from parsed data
- Prone to truncation and parsing errors

**After:**
```python
self.parser = JsonOutputParser(pydantic_object=WebtoonScript)
chain = prompt | self.llm | self.parser
result = await chain.ainvoke({
    "web_novel_story": story,
    "format_instructions": self.parser.get_format_instructions()
})
webtoon_script = WebtoonScript(**result)
```

**Benefits:**
- LLM receives JSON schema in prompt via `format_instructions`
- Parser validates JSON structure
- Automatic conversion to Pydantic model
- Better error handling for malformed JSON

### 2. Story Evaluator Service (`backend/app/services/story_evaluator.py`)

**Before:**
- Attempted to use `with_structured_output()` which failed with nested models
- Caused Pydantic v1/v2 compatibility issues

**After:**
```python
self.parser = JsonOutputParser(pydantic_object=EvaluationResult)
chain = self.prompt | self.llm | self.parser
result = await chain.ainvoke({
    "story": story,
    "format_instructions": self.parser.get_format_instructions()
})
evaluation = EvaluationResult(**result)
```

**Benefits:**
- Returns valid `EvaluationResult` Pydantic model
- No Pydantic version conflicts
- Type-safe and validated output
- Cleaner, more maintainable code

## Why JsonOutputParser Instead of with_structured_output?

### Issue with `with_structured_output()`
- Gemini's LangChain integration has issues with nested Pydantic models
- Causes `ValueError: Value not declarable with JSON Schema` errors
- Incompatible with Pydantic v2 field definitions
- Internal schema conversion uses Pydantic v1

### Benefits of `JsonOutputParser`
- ✅ Works with nested Pydantic models (`Character`, `WebtoonPanel`)
- ✅ Compatible with both Pydantic v1 and v2
- ✅ Provides schema via `format_instructions` in prompt
- ✅ Validates JSON structure before model creation
- ✅ Better error messages for debugging

## How JsonOutputParser Works

```python
# 1. Create parser with Pydantic model
parser = JsonOutputParser(pydantic_object=WebtoonScript)

# 2. Get format instructions (JSON schema)
format_instructions = parser.get_format_instructions()

# 3. Include in prompt
prompt = f"{your_prompt}\n\n{format_instructions}\n\nReturn ONLY valid JSON."

# 4. Parse response
result = await (prompt | llm | parser).ainvoke(input)

# 5. Convert to Pydantic model
model_instance = WebtoonScript(**result)
```

## Services Updated

✅ **WebtoonWriter** - Now uses `JsonOutputParser` with `WebtoonScript`
✅ **StoryEvaluator** - Now uses `JsonOutputParser` with `EvaluationResult`
✅ **StoryWriter** - Already correct (returns plain text)
✅ **StoryRewriter** - Already correct (returns plain text)

## Testing

To verify the fix works:
1. Restart backend server
2. Generate a story from a Reddit post
3. Click "Generate Webtoon" 
4. Should now successfully create webtoon script without errors
5. Check logs - should see "Webtoon script created with X characters and Y panels"

## Related Files

- `backend/app/models/story.py` - Contains all Pydantic models
- `backend/app/services/llm_config.py` - LLM configuration
- `backend/app/prompt/webtoon_writer.py` - Webtoon writer prompt

## Future Improvements

Consider using `JsonOutputParser` for any services that:
- Need structured JSON output
- Use nested Pydantic models
- Require schema validation
- Want better error handling
