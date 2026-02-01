# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-17

### Added

- **Reddit Story Search**
  - Multi-subreddit search capability
  - Time range filtering (1h, 1d, 10d, 100d)
  - Viral score calculation (upvotes + comments + recency)
- **Story Generation**

  - AI-powered story rewriting using Google Gemini
  - Story evaluation and quality scoring
  - Mood-based story customization

- **Webtoon Generation**

  - Webtoon script generation from stories
  - Character design and image generation
  - Scene image generation with Gemini 2.5 Flash
  - Character library for reusable character designs

- **Video Generation**

  - Video assembly from generated assets
  - Video preview and download functionality

- **Infrastructure**
  - FastAPI backend with async support
  - Next.js 16 frontend with React 19
  - LangChain and LangGraph integration
  - File-based persistence for workflows and assets
  - Comprehensive error handling and logging

### Technical Stack

- **Backend**: Python 3.10+, FastAPI 0.109, Pydantic V2
- **Frontend**: Next.js 16.1, React 19, TypeScript 5
- **AI**: LangChain, LangGraph, Google Gemini
- **Cache**: In-memory caching with file persistence

---

## [Unreleased]

### Planned

- Enhanced LangGraph workflow orchestration
- Multiple AI provider support for image generation
- Advanced story customization options
- Performance optimizations

---

## Template for Future Releases

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added

- New features

### Changed

- Changes to existing functionality

### Deprecated

- Features that will be removed in future versions

### Removed

- Features that were removed

### Fixed

- Bug fixes

### Security

- Security-related changes
```

---

## Version History

| Version | Date       | Highlights                            |
| ------- | ---------- | ------------------------------------- |
| 1.0.0   | 2026-01-17 | Initial release with full feature set |
