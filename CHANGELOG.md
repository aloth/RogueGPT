# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-07-29

### Added
- `CHANGELOG.md` (this file).
- Research-context section at the top of the README, stating intended use,
  corpus scale, and the safeguards that constrain how the framework is applied.
- `Software design`, `Research impact statement`, and `AI usage disclosure`
  sections in `paper/paper.md`, as required by the JOSS submission checklist.
- CI status badge in the README.

### Changed
- The package version is now declared once, in `pyproject.toml`. `core.py`
  resolves it at runtime via `importlib.metadata`; `app.py` and `mcp_server.py`
  read it from `core`.
- `requirements.txt` now carries upper bounds and points to
  `pip install ".[app,mcp]"` as the authoritative install path.
- `CITATION.cff` version corrected from `0.1.0` to the actual release version.

### Fixed
- Version strings no longer disagree across `pyproject.toml` (1.2.0),
  `app.py` (1.1.0), `mcp_server.py` (1.1.0), and `CITATION.cff` (0.1.0).
- Citation month for the WWW '26 Companion papers (see 609c71b).

## [1.2.0] - 2026-06-13

### Added
- JOSS submission preparation: `paper/paper.md`, `paper/paper.bib`,
  test suite, CI workflow, and packaging metadata.

## [1.1.0] - 2026-02-23

### Added
- Command-line interface, MCP server, and multi-provider expansion.

## [1.0.1] - 2026-02-14

### Added
- Expanded model support.

## [1.0.0] - 2025-02-25

### Added
- Initial stable release: controlled AI news stimulus generation for JudgeGPT.

[1.3.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.3.0
[1.2.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.2.0
[1.1.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.1.0
[1.0.1]: https://github.com/aloth/RogueGPT/releases/tag/v1.0.1
[1.0.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.0.0
