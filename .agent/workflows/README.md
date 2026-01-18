# Agent Workflows Documentation

This directory contains agent-ready documentation for the Gossiptoon V2 codebase. All documentation follows the "Agent Handoff Protocol" to enable seamless knowledge transfer between AI agents and human developers.

## Directory Structure

```
.agent/workflows/
├── README.md                          # This file
├── architecture-overview.md           # System architecture with Mermaid diagrams
├── story-generation-workflow.md       # Story generation pipeline documentation
├── webtoon-generation-workflow.md     # Webtoon creation pipeline documentation
├── code-health-audit.md               # Current audit findings and technical debt
└── module-index.md                    # Quick reference for all modules
```

## For AI Agents

### Quick Context Loading

1. **Start here**: Read `architecture-overview.md` for system understanding
2. **For story tasks**: Reference `story-generation-workflow.md`
3. **For webtoon tasks**: Reference `webtoon-generation-workflow.md`
4. **For refactoring**: Check `code-health-audit.md` for known issues

### Entry Points

| Task Type | Entry File | Router |
|-----------|------------|--------|
| Reddit Search | `backend/app/routers/search.py` | `/api/v1/search/` |
| Story Generation | `backend/app/routers/story.py` | `/api/v1/story/` |
| Webtoon Creation | `backend/app/routers/webtoon.py` | `/api/v1/webtoon/` |
| Character Library | `backend/app/routers/character_library.py` | `/api/v1/characters/` |

### Critical Files for Common Tasks

| Task | Files |
|------|-------|
| Modify AI prompts | `backend/app/prompt/*.py` |
| Change story logic | `backend/app/services/story_writer.py`, `story_evaluator.py` |
| Modify image generation | `backend/app/services/image_generator.py` |
| Update frontend UI | `viral-story-search/src/components/` |
| Change API contracts | `backend/app/models/`, `viral-story-search/src/types/` |

## Documentation Standards

All workflow documents follow this structure:

1. **Intent**: What this workflow/module accomplishes
2. **Logic Flow**: Step-by-step execution path (with Mermaid diagrams)
3. **Entry/Exit Points**: API endpoints, function signatures
4. **Dependencies**: External services, internal modules
5. **Gotchas**: Edge cases, known issues, warnings

## Last Updated

- **Date**: 2026-01-18
- **By**: Code Health Audit Agent
- **Status**: Initial documentation created
