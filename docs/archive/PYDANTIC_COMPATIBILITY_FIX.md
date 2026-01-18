# Pydantic Compatibility Fix

## Error
```
ValueError: Value not declarable with JSON Schema, field: name='_characters' type=Character required=True
```

## Root Cause
The `with_structured_output()` method in LangChain's Gemini integration has compatibility issues with:
1. Nested Pydantic models (e.g., `List[Character]` inside `WebtoonScript`)
2. Pydantic v2 field definitions
3. Internal schema conversion using Pydantic v1

## Solution
Switched from `with_structured_output()` to `JsonOutputParser` which:
- ✅ Works with nested Pydantic models
- ✅ Compatible with both Pydantic v1 and v2
- ✅ Provides JSON schema via `format_instructions`
- ✅ Better error handling and validation

## Implementation

### Before (Broken)
```python
self.structured_llm = self.llm.with_structured_output(WebtoonScript)
chain = prompt | self.structured_llm
result = await chain.ainvoke({"web_novel_story": story})
```

### After (Fixed)
```python
self.parser = JsonOutputParser(pydantic_object=WebtoonScript)
prompt = ChatPromptTemplate.from_template(
    WEBTOON_WRITER_PROMPT + "\n\n{format_instructions}\n\nReturn ONLY valid JSON."
)
chain = prompt | self.llm | self.parser
result = await chain.ainvoke({
    "web_novel_story": story,
    "format_instructions": self.parser.get_format_instructions()
})
webtoon_script = WebtoonScript(**result)
```

## Files Fixed
1. `backend/app/services/webtoon_writer.py` - Uses `JsonOutputParser`
2. `backend/app/services/story_evaluator.py` - Uses `JsonOutputParser`

## Testing
Server should now start without errors. Test by:
1. Starting backend: `cd backend && ./run.sh`
2. Should see no Pydantic schema errors
3. Generate story and webtoon script
4. Should complete successfully

## Key Differences

| Feature | with_structured_output | JsonOutputParser |
|---------|----------------------|------------------|
| Nested models | ❌ Fails | ✅ Works |
| Pydantic v2 | ❌ Issues | ✅ Compatible |
| Schema injection | Automatic | Via format_instructions |
| Error messages | Cryptic | Clear |
| Validation | Built-in | Manual conversion |
