# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Generation now records its sampling parameters per fragment (`SamplingParams`), so the conditions under which a stimulus was produced can be reconstructed from the corpus rather than only from the source file. `validate_fragment` reports a warning when the field is absent, which keeps fragments ingested before this change identifiable as such instead of silently defaulting them.

### Changed
- `generate_batch.py` no longer hard-codes temperature and token limit in three separate provider calls; all three read from a single `SAMPLING` constant.
- `paper/paper.md` and `paper/paper.bib` now reference the corpus by its concept DOI (10.5281/zenodo.18703137), which always resolves to the current version, and `archive_doi` points at the software concept DOI (10.5281/zenodo.20681920) rather than a single version.
- The paper states the corpus access model explicitly: machine-generated fragments are CC BY 4.0, human-sourced fragments are third-party news excerpts that cannot be licensed onward and are shared under the research exception for text and data mining, and access is granted to researchers at academic or non-profit institutions on request. The README carries the same distinction where the corpus is introduced.
- The paper no longer claims that stored metadata reproduces experimental conditions "exactly". Exact regeneration is outside the framework's control because commercial APIs are non-deterministic and providers revise models behind stable identifiers.
- The research impact section states that all four cited uses originate from the authors' own research programme.

## [1.3.1] - 2026-08-28

### Fixed
- The MCP server could not be imported on a fresh install. `FastMCP` no longer accepts the `version` and `description` keyword arguments from mcp 1.13 onwards, so the call now passes only the server name. Reported in #3.
- The `mcp` extra declared `mcp[cli]>=1.0` in `pyproject.toml`, which resolved to mcp 2.x, where `FastMCP` has been renamed. `mcp.server.fastmcp` also does not exist before 1.2, so the floor was never valid. Both `pyproject.toml` and `requirements.txt` now declare `mcp[cli]>=1.2,<2`. Reported in #3.
- `generate_batch.py` exited 0 even when every generation failed. It now exits 1 when no fragment was produced and at least one attempt failed. A dry run attempts nothing and still exits 0. Reported in #4.

### Added
- Import-level smoke test for the MCP server (`tests/test_mcp_server.py`), skipped when the optional `mcp` extra is not installed. CI now installs `.[dev,mcp]` so the test runs there.

### Documentation
- Corpus composition and generator configuration are now reported as separate figures throughout the README and `paper/paper.md`. Corpus statistics cite the released snapshot (3,278 fragments from 10 models across 6 providers); the model registry count is labeled as configuration and carries the date it was measured (47 identifiers across 11 providers as of 2026-02-23).
- Added recount commands to the README so both figures can be reproduced from the repository.

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

[1.3.1]: https://github.com/aloth/RogueGPT/releases/tag/v1.3.1
[1.3.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.3.0
[1.2.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.2.0
[1.1.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.1.0
[1.0.1]: https://github.com/aloth/RogueGPT/releases/tag/v1.0.1
[1.0.0]: https://github.com/aloth/RogueGPT/releases/tag/v1.0.0
