"""
Shared pytest fixtures for the RogueGPT test suite.
"""
import json

import pytest


# ---------------------------------------------------------------------------
# Minimal prompt_engine.json fixture
# ---------------------------------------------------------------------------

MINIMAL_CONFIG = {
    "PromptTemplate": "Write a [[Style]] article about [[Topic]] in [[Language]].",
    "GeneratorURL": "https://api.openai.com/v1",
    "GeneratorAPIKey": "PLACEHOLDER",
    "GeneratorAPIType": ["OpenAI"],
    "GeneratorAPIVersion": ["2024-02-01"],
    "GeneratorModel": [
        "openai_gpt-4o_2024-08-06",
        "anthropic_claude-3.5-sonnet",
        "meta_llama-3.3-70b",
    ],
    "Components": {
        "Language": {
            "English": {"ISOLanguage": ["en"]},
            "German":  {"ISOLanguage": ["de"]},
            "French":  {"ISOLanguage": ["fr"]},
            "Spanish": {"ISOLanguage": ["es"]},
        }
    },
}


@pytest.fixture
def config_file(tmp_path):
    """Write a minimal prompt_engine.json to a temp directory and return its path."""
    path = tmp_path / "prompt_engine.json"
    path.write_text(json.dumps(MINIMAL_CONFIG))
    return str(path)


@pytest.fixture(autouse=True)
def reset_config_cache():
    """
    Reset core's in-process config cache between tests so each test that
    patches the config file path sees fresh data.
    """
    import core as _core
    _core._config_cache = None
    yield
    _core._config_cache = None


# ---------------------------------------------------------------------------
# Canonical valid fragment dict
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_machine_fragment():
    return {
        "Content": "Scientists discover water on Mars.",
        "Origin": "Machine",
        "IsFake": True,
        "ISOLanguage": "en",
        "MachineModel": "openai_gpt-4o_2024-08-06",
        "MachinePrompt": "Write a fake news article about Mars.",
    }


@pytest.fixture
def valid_human_fragment():
    return {
        "Content": "Scientists discover water on Mars.",
        "Origin": "Human",
        "IsFake": False,
        "ISOLanguage": "en",
        "HumanOutlet": "BBC",
        "HumanURL": "https://www.bbc.com/news/science-mars",
    }
