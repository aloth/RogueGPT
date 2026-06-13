# Contributing to RogueGPT

Thank you for your interest in contributing to RogueGPT! This document guides you through setting up your development environment, running tests, and submitting changes.

---

## Table of Contents

1. [Development Environment](#development-environment)
2. [Running Tests](#running-tests)
3. [Code Style](#code-style)
4. [Extending the Model Configuration](#extending-the-model-configuration)
5. [PR Process](#pr-process)
6. [Reporting Issues](#reporting-issues)

---

## Development Environment

### Prerequisites

- Python 3.10 or higher
- A MongoDB instance (local or Atlas) — only needed for DB-dependent tests and actual use
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/<your-username>/RogueGPT.git
cd RogueGPT

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

# Install in editable mode with all dev extras
pip install -e ".[dev,mcp,app]"
```

The `[dev]` extra installs `pytest`, `pytest-cov`, and `pytest-mock`.
The `[mcp]` extra installs the MCP SDK for `mcp_server.py`.
The `[app]` extra installs `streamlit` and `openai` for `app.py`.

### Configuration

For tests or runtime use, set the MongoDB URI:

```bash
export ROGUEGPT_MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority"
```

Alternatively, for the Streamlit app, create `.streamlit/secrets.toml`:

```toml
[mongo]
connection = "mongodb+srv://user:pass@cluster.mongodb.net/..."
```

---

## Running Tests

```bash
# Run all tests that do NOT require MongoDB (safe in any environment)
pytest -m "not requires_db"

# Run all tests including DB-dependent ones (requires ROGUEGPT_MONGO_URI)
pytest

# Run with coverage
pytest -m "not requires_db" --cov --cov-report=term-missing

# Run a specific test file
pytest tests/test_core.py -v

# Run a single test
pytest tests/test_core.py::TestValidateFragment::test_missing_content_raises -v
```

### Test Markers

| Marker | Meaning |
|:---|:---|
| `requires_db` | Test needs a live MongoDB connection. Skip in CI with `-m "not requires_db"`. |

When writing tests for MongoDB-dependent functionality, mark them:

```python
@pytest.mark.requires_db
def test_something_with_db():
    ...
```

---

## Code Style

RogueGPT uses [Ruff](https://docs.astral.sh/ruff/) for linting:

```bash
pip install ruff
ruff check .           # lint
ruff check . --fix     # auto-fix safe issues
```

Key conventions:

- **Flat module layout** — do not restructure into a `src/` or nested package layout; all top-level `.py` modules are importable directly.
- **Type hints** — new functions should include type annotations compatible with Python 3.10+.
- **Docstrings** — public functions must have docstrings (one-line summary is fine for simple helpers).
- **No UI imports in `core.py`** — `core.py` is the pure data layer; keep it free of Streamlit, CLI, or MCP dependencies.
- **Line length** — 100 characters (Ruff default; long lines in docstrings/strings are fine).

---

## Extending the Model Configuration

To add a new LLM to the corpus:

1. Open `prompt_engine.json` and append the identifier to `GeneratorModel`:
   ```json
   "GeneratorModel": [
       "openai_gpt-4o_2024-08-06",
       "your-provider_model-variant",
       ...
   ]
   ```
2. Follow the naming convention `provider_model-variant` (e.g., `openai_gpt-4.1`, `anthropic_claude-3.5-sonnet`).
3. Update the existing tests or add new ones if the change affects validation logic.

---

## PR Process

1. **Fork** the repository on GitHub.
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-description
   ```
3. **Make your changes**, keeping commits focused and descriptive.
4. **Run the test suite** (`pytest -m "not requires_db"`) and ensure it passes.
5. **Run the linter** (`ruff check .`) and fix any issues.
6. **Push** your branch and **open a Pull Request** against `main`.
7. Describe *what* changed and *why* in the PR description. Reference any related issues.

For substantial changes (new features, schema changes, breaking changes), please **open an issue first** to discuss the approach before writing code.

---

## Reporting Issues

Please use [GitHub Issues](https://github.com/aloth/RogueGPT/issues) to report bugs or request features. Include:

- Python version and OS
- Steps to reproduce
- Expected vs actual behaviour
- Relevant error messages or stack traces

For security issues, please email the authors directly rather than opening a public issue.

---

## Acknowledgements

We appreciate all contributions, large and small. Thank you for helping make AI news authenticity research more reproducible and accessible.
