"""
RogueGPT Core — Data layer for fragment ingestion and retrieval.

Handles MongoDB operations, schema validation, and config loading.
No UI dependencies. Used by both app.py (Streamlit) and mcp_server.py.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "prompt_engine.json")

# ─── Config ───────────────────────────────────────────────────────────

_config_cache: Optional[dict] = None


def load_config(path: str = CONFIG_FILE) -> dict:
    """Load and cache prompt_engine.json."""
    global _config_cache
    if _config_cache is None:
        with open(path, "r") as f:
            _config_cache = json.load(f)
    return _config_cache


def get_valid_models() -> List[str]:
    """Return the list of recognised model identifiers from config."""
    return load_config()["GeneratorModel"]


def get_valid_languages() -> List[str]:
    """Return all ISO language codes defined in the config."""
    langs: set = set()
    components = load_config().get("Components", {})
    for lang_block in components.get("Language", {}).values():
        for code in lang_block.get("ISOLanguage", []):
            langs.add(code)
    return sorted(langs)


# ─── MongoDB ──────────────────────────────────────────────────────────

def _get_mongo_uri() -> str:
    """
    Resolve MongoDB URI from (in order):
      1. ROGUEGPT_MONGO_URI env var
      2. Streamlit secrets (if available)
    """
    uri = os.environ.get("ROGUEGPT_MONGO_URI")
    if uri:
        return uri
    try:
        import streamlit as st
        return st.secrets["mongo"]["connection"]
    except Exception:
        pass
    raise RuntimeError(
        "No MongoDB URI found. Set ROGUEGPT_MONGO_URI or configure Streamlit secrets."
    )


def _get_collection():
    """Return the fragments collection handle."""
    client = MongoClient(_get_mongo_uri(), server_api=ServerApi("1"))
    return client.realorfake.fragments


# ─── Validation ───────────────────────────────────────────────────────

class ValidationError(Exception):
    """Raised when a fragment fails schema validation."""
    pass


def validate_fragment(fragment: dict, strict_model: bool = True) -> List[str]:
    """
    Validate a fragment dict.  Returns a list of warnings (empty = OK).
    Raises ValidationError on hard failures.
    """
    warnings: List[str] = []

    # Required fields
    if not fragment.get("Content"):
        raise ValidationError("Content is required and must not be empty.")

    origin = fragment.get("Origin")
    if origin not in ("Human", "Machine"):
        raise ValidationError(f"Origin must be 'Human' or 'Machine', got '{origin}'.")

    if origin == "Human":
        if not fragment.get("HumanOutlet"):
            raise ValidationError("HumanOutlet is required for Human-origin fragments.")
        if not fragment.get("HumanURL"):
            warnings.append("HumanURL is missing (recommended for provenance).")
    else:
        model = fragment.get("MachineModel")
        if not model:
            raise ValidationError("MachineModel is required for Machine-origin fragments.")
        valid_models = get_valid_models()
        if model not in valid_models:
            msg = f"MachineModel '{model}' is not in prompt_engine.json."
            if strict_model:
                raise ValidationError(msg + " Use strict_model=False to allow it.")
            warnings.append(msg)
        if not fragment.get("MachinePrompt"):
            warnings.append("MachinePrompt is missing (recommended for reproducibility).")

    lang = fragment.get("ISOLanguage")
    valid_langs = get_valid_languages()
    if lang and lang not in valid_langs:
        warnings.append(f"ISOLanguage '{lang}' is not in config (known: {valid_langs}).")

    if "IsFake" not in fragment:
        raise ValidationError("IsFake (bool) is required.")

    return warnings


def normalize_fragment(fragment: dict) -> dict:
    """
    Fill in defaults and ensure consistent types.
    Does NOT validate — call validate_fragment first.
    """
    out = dict(fragment)
    out.setdefault("FragmentID", uuid.uuid4().hex)
    out.setdefault("CreationDate", datetime.now(timezone.utc))
    out.setdefault("IngestedVia", "unknown")

    # Ensure optional fields exist
    for field in ("HumanOutlet", "HumanURL", "MachineModel", "MachinePrompt"):
        out.setdefault(field, "")

    return out


# ─── CRUD ─────────────────────────────────────────────────────────────

def save_fragment(fragment: dict, strict_model: bool = True) -> Dict[str, Any]:
    """
    Validate, normalize, and persist a fragment.
    Returns {"fragment_id": ..., "warnings": [...]}.
    """
    warnings = validate_fragment(fragment, strict_model=strict_model)
    doc = normalize_fragment(fragment)
    _get_collection().insert_one(doc)
    return {"fragment_id": doc["FragmentID"], "warnings": warnings}


def get_random_fragments(
    n: int = 1,
    origin: Optional[str] = None,
    model: Optional[str] = None,
    language: Optional[str] = None,
    is_fake: Optional[bool] = None,
) -> List[dict]:
    """
    Retrieve random fragments from the database.
    """
    match: Dict[str, Any] = {}
    if origin:
        match["Origin"] = origin
    if model:
        match["MachineModel"] = model
    if language:
        match["ISOLanguage"] = language
    if is_fake is not None:
        match["IsFake"] = is_fake

    pipeline: list = []
    if match:
        pipeline.append({"$match": match})
    pipeline.append({"$sample": {"size": n}})
    pipeline.append({"$project": {"_id": 0}})

    return list(_get_collection().aggregate(pipeline))


def count_fragments(
    origin: Optional[str] = None,
    model: Optional[str] = None,
) -> int:
    """Count fragments matching the given filters."""
    match: Dict[str, Any] = {}
    if origin:
        match["Origin"] = origin
    if model:
        match["MachineModel"] = model
    return _get_collection().count_documents(match)
