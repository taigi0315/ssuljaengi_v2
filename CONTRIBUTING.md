# Contributing to Gossiptoon V2

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Accept feedback graciously

---

## Getting Started

### Prerequisites

1. Python 3.10 or higher
2. Node.js 18 or higher
3. Git

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/<your-username>/gossiptoon_v2_2.git
cd gossiptoon_v2_2

# Set up upstream
git remote add upstream https://github.com/taigi0315/ssuljaengi_v2.git

# Install dependencies
npm install
cd backend && pip install -r requirements.txt && cd ..
cd viral-story-search && npm install && cd ..
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create a new branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the code style guidelines below
- Write tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd viral-story-search
npm test
```

### 4. Submit a Pull Request

See [Pull Request Process](#pull-request-process) below.

---

## Code Style Guidelines

### Python (Backend)

| Aspect     | Standard                           |
| ---------- | ---------------------------------- |
| Formatter  | Black                              |
| Linter     | Flake8, Ruff                       |
| Type Hints | Required for all functions         |
| Docstrings | Google style                       |
| Language   | **English only** for code/comments |

```bash
# Format code
black app/

# Lint code
flake8 app/
```

Example function:

```python
def calculate_viral_score(upvotes: int, comments: int, age_hours: float) -> float:
    """
    Calculate the viral score for a Reddit post.

    Args:
        upvotes: Number of upvotes on the post.
        comments: Number of comments on the post.
        age_hours: Age of the post in hours.

    Returns:
        Calculated viral score as a float.
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)

| Aspect    | Standard                           |
| --------- | ---------------------------------- |
| Formatter | Prettier                           |
| Linter    | ESLint                             |
| Types     | Strict TypeScript                  |
| Language  | **English only** for code/comments |

```bash
# Format code
npm run format

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type       | Description                     |
| ---------- | ------------------------------- |
| `feat`     | New feature                     |
| `fix`      | Bug fix                         |
| `docs`     | Documentation changes           |
| `style`    | Code style changes (formatting) |
| `refactor` | Code refactoring                |
| `test`     | Adding or updating tests        |
| `chore`    | Maintenance tasks               |

### Examples

```bash
feat(webtoon): add character library support

fix(api): resolve 404 error on story generation restart

docs(readme): update installation instructions
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe how you tested the changes

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
```

### Review Process

1. Submit your PR
2. Wait for automated checks to pass
3. Address any review feedback
4. Once approved, your PR will be merged

---

## Questions?

If you have questions, please open an issue with the label `question`.

Thank you for contributing! 🎉
