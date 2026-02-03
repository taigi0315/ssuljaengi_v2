# Task: Clean Project State and Fix Makefile for macOS

## Status

- [x] Fix `clean` target in `Makefile` (currently uses Windows commands)
- [x] Fix `kill` target in `Makefile`
- [x] Run `make clean` to remove cached data
- [x] Verify fresh start

## Context

User wants a "fresh start" because the app keeps loading previous data.
The `clean` button/command isn't working.
Investigation shows `Makefile` uses Windows-specific commands (`del`, `if exist`, `taskkill`) which fail on macOS.

## Findings

- `Makefile` updated to use `rm` and `pkill` which work on macOS.
- `make clean` executed successfully.
- Data files in `backend/data/*.json` have been removed.

## Resolution

- Makefile is now compatible with macOS.
- Project state has been cleaned.
