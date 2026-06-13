"""
Unit tests for core.py — pure logic tests that require no live MongoDB.

MongoDB-dependent tests (save_fragment, get_random_fragments, count_fragments)
are marked with @pytest.mark.requires_db and skipped in CI.
"""
import json
import os
import sys
import uuid
from unittest.mock import MagicMock, patch

import pytest

# Ensure the flat-layout root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import core


# ============================================================================
# load_config / config helpers
# ============================================================================

class TestLoadConfig:
    def test_loads_minimal_config(self, config_file):
        """load_config() returns a dict with expected top-level keys."""
        cfg = core.load_config(config_file)
        assert isinstance(cfg, dict)
        assert "GeneratorModel" in cfg
        assert "Components" in cfg

    def test_caches_result(self, config_file):
        """Second call returns the same object (cached)."""
        first  = core.load_config(config_file)
        second = core.load_config(config_file)
        assert first is second

    def test_missing_file_raises(self, tmp_path):
        """FileNotFoundError when path does not exist."""
        core._config_cache = None
        with pytest.raises(FileNotFoundError):
            core.load_config(str(tmp_path / "no_such_file.json"))

    def test_invalid_json_raises(self, tmp_path):
        """JSONDecodeError on malformed JSON."""
        bad = tmp_path / "bad.json"
        bad.write_text("{ not valid json }")
        core._config_cache = None
        with pytest.raises(json.JSONDecodeError):
            core.load_config(str(bad))


class TestGetValidModels:
    def test_returns_list_of_strings(self, config_file):
        with patch("core.CONFIG_FILE", config_file):
            models = core.get_valid_models()
        assert isinstance(models, list)
        assert all(isinstance(m, str) for m in models)
        assert len(models) > 0

    def test_contains_known_model(self, config_file):
        with patch("core.CONFIG_FILE", config_file):
            models = core.get_valid_models()
        assert "openai_gpt-4o_2024-08-06" in models


class TestGetValidLanguages:
    def test_returns_sorted_list(self, config_file):
        with patch("core.CONFIG_FILE", config_file):
            langs = core.get_valid_languages()
        assert langs == sorted(langs)

    def test_contains_standard_codes(self, config_file):
        with patch("core.CONFIG_FILE", config_file):
            langs = core.get_valid_languages()
        for code in ("en", "de", "fr", "es"):
            assert code in langs

    def test_no_duplicates(self, config_file):
        with patch("core.CONFIG_FILE", config_file):
            langs = core.get_valid_languages()
        assert len(langs) == len(set(langs))


# ============================================================================
# ValidationError
# ============================================================================

class TestValidationError:
    def test_is_exception_subclass(self):
        assert issubclass(core.ValidationError, Exception)

    def test_message_preserved(self):
        err = core.ValidationError("bad field")
        assert str(err) == "bad field"

    def test_raise_and_catch(self):
        with pytest.raises(core.ValidationError, match="bad field"):
            raise core.ValidationError("bad field")


# ============================================================================
# validate_fragment
# ============================================================================

class TestValidateFragment:

    # --- Hard failures (ValidationError) ------------------------------------

    def test_missing_content_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        del frag["Content"]
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="Content"):
                core.validate_fragment(frag)

    def test_empty_content_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment, Content="")
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="Content"):
                core.validate_fragment(frag)

    def test_invalid_origin_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment, Origin="Robot")
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="Origin"):
                core.validate_fragment(frag)

    def test_missing_origin_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        del frag["Origin"]
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="Origin"):
                core.validate_fragment(frag)

    def test_machine_missing_model_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        del frag["MachineModel"]
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="MachineModel"):
                core.validate_fragment(frag)

    def test_machine_empty_model_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment, MachineModel="")
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="MachineModel"):
                core.validate_fragment(frag)

    def test_human_missing_outlet_raises(self, config_file, valid_human_fragment):
        frag = dict(valid_human_fragment)
        del frag["HumanOutlet"]
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="HumanOutlet"):
                core.validate_fragment(frag)

    def test_missing_isfake_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        del frag["IsFake"]
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="IsFake"):
                core.validate_fragment(frag)

    # --- Strict model check -------------------------------------------------

    def test_unknown_model_strict_raises(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment, MachineModel="vendor_totally-unknown-3000")
        with patch("core.CONFIG_FILE", config_file):
            with pytest.raises(core.ValidationError, match="not in prompt_engine.json"):
                core.validate_fragment(frag, strict_model=True)

    def test_unknown_model_lenient_returns_warning(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment, MachineModel="vendor_totally-unknown-3000")
        with patch("core.CONFIG_FILE", config_file):
            warnings = core.validate_fragment(frag, strict_model=False)
        assert any("not in prompt_engine.json" in w for w in warnings)

    # --- Valid fragments (no errors, possible warnings) ---------------------

    def test_valid_machine_fragment_passes(self, config_file, valid_machine_fragment):
        with patch("core.CONFIG_FILE", config_file):
            warnings = core.validate_fragment(valid_machine_fragment)
        # warnings allowed (e.g., missing MachinePrompt), but no exception
        assert isinstance(warnings, list)

    def test_valid_human_fragment_passes(self, config_file, valid_human_fragment):
        with patch("core.CONFIG_FILE", config_file):
            warnings = core.validate_fragment(valid_human_fragment)
        assert isinstance(warnings, list)

    def test_human_missing_url_is_warning_not_error(self, config_file, valid_human_fragment):
        frag = dict(valid_human_fragment)
        frag.pop("HumanURL", None)
        with patch("core.CONFIG_FILE", config_file):
            warnings = core.validate_fragment(frag)
        assert any("HumanURL" in w for w in warnings)

    def test_machine_missing_prompt_is_warning(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        frag.pop("MachinePrompt", None)
        with patch("core.CONFIG_FILE", config_file):
            warnings = core.validate_fragment(frag)
        assert any("MachinePrompt" in w for w in warnings)

    def test_unknown_language_is_warning(self, config_file, valid_machine_fragment):
        frag = dict(valid_machine_fragment, ISOLanguage="xx")
        with patch("core.CONFIG_FILE", config_file):
            warnings = core.validate_fragment(frag)
        assert any("ISOLanguage" in w for w in warnings)

    def test_no_language_is_not_an_error(self, config_file, valid_machine_fragment):
        """ISOLanguage is optional — missing entirely should not raise."""
        frag = dict(valid_machine_fragment)
        frag.pop("ISOLanguage", None)
        with patch("core.CONFIG_FILE", config_file):
            # should not raise
            core.validate_fragment(frag)

    def test_returns_empty_list_for_perfect_fragment(self, config_file, valid_machine_fragment):
        """A fully-populated valid fragment should produce zero warnings."""
        with patch("core.CONFIG_FILE", config_file):
            warnings = core.validate_fragment(valid_machine_fragment)
        assert warnings == []


# ============================================================================
# normalize_fragment
# ============================================================================

class TestNormalizeFragment:

    def test_fills_fragment_id(self, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        frag.pop("FragmentID", None)
        out = core.normalize_fragment(frag)
        assert "FragmentID" in out
        assert len(out["FragmentID"]) == 32          # uuid4().hex

    def test_preserves_existing_fragment_id(self, valid_machine_fragment):
        frag = dict(valid_machine_fragment, FragmentID="custom-id-123")
        out = core.normalize_fragment(frag)
        assert out["FragmentID"] == "custom-id-123"

    def test_fills_creation_date(self, valid_machine_fragment):
        from datetime import datetime
        frag = dict(valid_machine_fragment)
        frag.pop("CreationDate", None)
        out = core.normalize_fragment(frag)
        assert isinstance(out["CreationDate"], datetime)

    def test_preserves_existing_creation_date(self, valid_machine_fragment):
        from datetime import datetime, timezone
        dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        frag = dict(valid_machine_fragment, CreationDate=dt)
        out = core.normalize_fragment(frag)
        assert out["CreationDate"] == dt

    def test_fills_ingested_via_unknown(self, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        frag.pop("IngestedVia", None)
        out = core.normalize_fragment(frag)
        assert out["IngestedVia"] == "unknown"

    def test_preserves_existing_ingested_via(self, valid_machine_fragment):
        frag = dict(valid_machine_fragment, IngestedVia="cli")
        out = core.normalize_fragment(frag)
        assert out["IngestedVia"] == "cli"

    def test_optional_fields_default_empty_string(self, valid_machine_fragment):
        """Fields that don't apply to the origin should default to empty string."""
        frag = {
            "Content": "Text.",
            "Origin": "Machine",
            "IsFake": False,
            "MachineModel": "openai_gpt-4o_2024-08-06",
        }
        out = core.normalize_fragment(frag)
        assert out.get("HumanOutlet") == ""
        assert out.get("HumanURL") == ""

    def test_does_not_mutate_input(self, valid_machine_fragment):
        """normalize_fragment must not modify the caller's dict."""
        original = dict(valid_machine_fragment)
        core.normalize_fragment(valid_machine_fragment)
        assert valid_machine_fragment == original

    def test_fragment_id_is_hex_string(self, valid_machine_fragment):
        frag = dict(valid_machine_fragment)
        frag.pop("FragmentID", None)
        out = core.normalize_fragment(frag)
        # Must be a valid hex string (UUID4 hex has exactly 32 chars, all hex digits)
        assert all(c in "0123456789abcdef" for c in out["FragmentID"])


# ============================================================================
# MongoDB-dependent tests (skipped in CI)
# ============================================================================

@pytest.mark.requires_db
class TestSaveFragment:
    def test_save_and_returns_fragment_id(self, config_file, valid_machine_fragment):
        """Requires a live ROGUEGPT_MONGO_URI in the environment."""
        with patch("core.CONFIG_FILE", config_file):
            result = core.save_fragment(valid_machine_fragment)
        assert "fragment_id" in result
        assert isinstance(result["fragment_id"], str)

    def test_save_returns_warnings_list(self, config_file, valid_machine_fragment):
        with patch("core.CONFIG_FILE", config_file):
            result = core.save_fragment(valid_machine_fragment)
        assert "warnings" in result
        assert isinstance(result["warnings"], list)


@pytest.mark.requires_db
class TestGetRandomFragments:
    def test_returns_list(self):
        fragments = core.get_random_fragments(n=1)
        assert isinstance(fragments, list)

    def test_respects_n_param(self):
        fragments = core.get_random_fragments(n=3)
        assert len(fragments) <= 3

    def test_no_underscore_id_field(self):
        fragments = core.get_random_fragments(n=1)
        for f in fragments:
            assert "_id" not in f


@pytest.mark.requires_db
class TestCountFragments:
    def test_returns_int(self):
        count = core.count_fragments()
        assert isinstance(count, int)
        assert count >= 0

    def test_origin_filter(self):
        total    = core.count_fragments()
        human    = core.count_fragments(origin="Human")
        machine  = core.count_fragments(origin="Machine")
        assert human + machine <= total
