"""Checks server.json against the MCP registry limits and the package metadata.

The 1.5.0 release reached PyPI but not the MCP registry because the description
was 103 characters long; the registry rejects anything over 100.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
# tomllib needs Python 3.11; the package supports 3.10, so read the two fields
# from the [project] table directly.
_PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
_PROJECT_TABLE = _PYPROJECT.split("[project]", 1)[1].split("\n[", 1)[0]
PROJECT = {
    key: re.search(rf'^{key}\s*=\s*"([^"]+)"', _PROJECT_TABLE, re.M).group(1)
    for key in ("name", "version")
}


def test_description_fits_the_registry_limit():
    assert 0 < len(SERVER["description"]) <= 100, len(SERVER["description"])


def test_versions_match_pyproject():
    assert SERVER["version"] == PROJECT["version"]
    assert SERVER["packages"][0]["version"] == PROJECT["version"]
    assert SERVER["packages"][0]["identifier"] == PROJECT["name"]


def test_readme_carries_the_mcp_name_the_registry_checks_on_pypi():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    match = re.search(r"<!--\s*mcp-name:\s*(\S+)\s*-->", readme)
    assert match and match.group(1) == SERVER["name"]
