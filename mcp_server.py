"""
RogueGPT MCP Server — Expose fragment ingestion and retrieval as MCP tools.

Run:  python mcp_server.py
Env:  ROGUEGPT_MONGO_URI=mongodb+srv://...

Two tools:
  - ingest_fragment:  Validate and store a new fragment (human or machine).
  - retrieve_fragments: Fetch random fragments with optional filters.
"""

import json
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

# Ensure core.py is importable from the same directory
sys.path.insert(0, os.path.dirname(__file__))

import core

# ─── Server setup ─────────────────────────────────────────────────────

mcp = FastMCP(
    "RogueGPT",
    version="1.1.0",
    description=(
        "MCP server for the RogueGPT research dataset. "
        "Ingest human-sourced or LLM-generated news fragments and retrieve them for evaluation."
    ),
)


# ─── Tool: ingest ─────────────────────────────────────────────────────

@mcp.tool()
def ingest_fragment(
    content: str,
    origin: str,
    is_fake: bool,
    iso_language: str = "en",
    machine_model: str = "",
    machine_prompt: str = "",
    human_outlet: str = "",
    human_url: str = "",
    strict_model: bool = True,
) -> dict[str, Any]:
    """
    Ingest a news fragment into the RogueGPT dataset.

    Args:
        content: The news text (required).
        origin: "Human" or "Machine" (required).
        is_fake: Whether the fragment is fake news (required).
        iso_language: ISO 639-1 language code (default: "en").
        machine_model: Model identifier for Machine origin (must match prompt_engine.json, e.g. "openai_gpt-4o_2024-08-06").
        machine_prompt: The prompt used to generate the fragment (recommended for Machine origin).
        human_outlet: Publishing outlet name for Human origin (required if Human).
        human_url: Source URL for Human origin (recommended).
        strict_model: If True, reject unknown model names. If False, warn but allow.

    Returns:
        {"fragment_id": str, "warnings": list[str]} on success.
    """
    fragment = {
        "Content": content,
        "Origin": origin,
        "IsFake": is_fake,
        "ISOLanguage": iso_language,
        "MachineModel": machine_model,
        "MachinePrompt": machine_prompt,
        "HumanOutlet": human_outlet,
        "HumanURL": human_url,
        "IngestedVia": "mcp",
    }

    try:
        result = core.save_fragment(fragment, strict_model=strict_model)
        return {"status": "ok", **result}
    except core.ValidationError as e:
        return {"status": "error", "error": str(e)}


# ─── Tool: retrieve ───────────────────────────────────────────────────

@mcp.tool()
def retrieve_fragments(
    n: int = 1,
    origin: str | None = None,
    model: str | None = None,
    language: str | None = None,
    is_fake: bool | None = None,
) -> dict[str, Any]:
    """
    Retrieve random fragments from the RogueGPT dataset.

    Args:
        n: Number of fragments to return (default: 1, max: 50).
        origin: Filter by "Human" or "Machine" (optional).
        model: Filter by model identifier, e.g. "openai_gpt-4o_2024-08-06" (optional).
        language: Filter by ISO language code (optional).
        is_fake: Filter by fake news status (optional).

    Returns:
        {"fragments": [...], "count": int}
    """
    n = min(max(1, n), 50)
    fragments = core.get_random_fragments(
        n=n, origin=origin, model=model, language=language, is_fake=is_fake
    )
    # Serialize datetimes for JSON
    for f in fragments:
        for k, v in f.items():
            if hasattr(v, "isoformat"):
                f[k] = v.isoformat()
    return {"fragments": fragments, "count": len(fragments)}


# ─── Resource: config info ────────────────────────────────────────────

@mcp.resource("roguegpt://config/models")
def list_models() -> str:
    """List all recognised model identifiers from prompt_engine.json."""
    return json.dumps(core.get_valid_models(), indent=2)


@mcp.resource("roguegpt://config/languages")
def list_languages() -> str:
    """List all supported ISO language codes."""
    return json.dumps(core.get_valid_languages(), indent=2)


@mcp.resource("roguegpt://stats")
def dataset_stats() -> str:
    """Return basic dataset statistics."""
    total = core.count_fragments()
    human = core.count_fragments(origin="Human")
    machine = core.count_fragments(origin="Machine")
    models = core.get_valid_models()

    per_model = {}
    for m in models:
        c = core.count_fragments(model=m)
        if c > 0:
            per_model[m] = c

    return json.dumps(
        {
            "total": total,
            "human": human,
            "machine": machine,
            "by_model": per_model,
        },
        indent=2,
    )


# ─── Main ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
