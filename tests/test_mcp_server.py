"""Import-level smoke test for the MCP server.

Issue #3 (JOSS review): the server failed at import time, so importing the
module is enough to catch the regression. `FastMCP` rejected the `version` and
`description` kwargs from mcp 1.13 onwards, and `mcp.server.fastmcp` does not
exist before 1.2 at all.

Skipped when the optional `mcp` extra is absent, so the default `.[dev]` test
run stays green.
"""

import pytest

mcp_pkg = pytest.importorskip("mcp", reason="optional 'mcp' extra not installed")


def test_mcp_server_imports():
    """The module must import; construction of FastMCP happens at import time."""
    import mcp_server

    assert mcp_server.mcp is not None


def test_server_name_is_set():
    import mcp_server

    assert mcp_server.mcp.name == "RogueGPT"


def test_expected_tools_are_defined():
    import mcp_server

    assert callable(mcp_server.ingest_fragment)
    assert callable(mcp_server.retrieve_fragments)
