# Task: Debug Webtoon Script Conversion TypeError

## Status

- [x] Investigate `WebtoonWriter._fill_missing_fields_in_dict`
- [x] Determine why `result` is a list instead of a dict
- [x] Fix the type error

## Context

User reported `TypeError: list indices must be integers or slices, not str` in `backend/app/services/webtoon_writer.py`.
Traceback indicates:

```python
[0]   File "/Users/changikchoi/Documents/Github/gossiptoon_v2_2/backend/app/services/webtoon_writer.py", line 473, in convert_story_to_script
[0]     result = self._fill_missing_fields_in_dict(result)
[0]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[0]   File "/Users/changikchoi/Documents/Github/gossiptoon_v2_2/backend/app/services/webtoon_writer.py", line 91, in _fill_missing_fields_in_dict
[0]     result["characters"] = []
[0]     ~~~~~~^^^^^^^^^^^^^^
[0] TypeError: list indices must be integers or slices, not str
```

## Investigation Findings

- The LLM sometimes returns a JSON list `[...]` instead of a root JSON object `{...}`.
- `WebtoonWriter._fill_missing_fields_in_dict` expects a `dict` as input.
- When `result` is a list, `result["characters"]` fails with `TypeError`.

## Resolution

- Added a check in `convert_story_to_script` to detect if `result` is a list.
- If it is a list, we now unwrap the first element (assuming it's the intended dict) or fall back to an empty dict to allow `_fill_missing_fields_in_dict` to handle the defaults safely.
