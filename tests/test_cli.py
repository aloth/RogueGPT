"""
Smoke tests for cli.py — verify argument parsing and command dispatch.

All tests mock core.* so no MongoDB connection is required.
"""
import json
import os
import sys
from io import StringIO
from unittest.mock import patch


# Ensure flat-layout root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_cli(monkeypatch, *argv):
    """
    Invoke cli.main() with a given argv and capture stdout/stderr.
    Returns (stdout_str, exit_code).
    """
    monkeypatch.setattr(sys, "argv", ["roguegpt", *argv])

    captured_out = StringIO()
    captured_err = StringIO()

    exit_code = 0
    try:
        with patch("sys.stdout", captured_out), patch("sys.stderr", captured_err):
            cli.main()
    except SystemExit as e:
        exit_code = e.code if e.code is not None else 0

    return captured_out.getvalue(), captured_err.getvalue(), exit_code


# ---------------------------------------------------------------------------
# --help smoke tests
# ---------------------------------------------------------------------------

class TestHelp:
    def test_top_level_help(self, monkeypatch):
        """roguegpt --help exits cleanly and mentions subcommands."""
        _, _, code = run_cli(monkeypatch, "--help")
        assert code == 0

    def test_ingest_help(self, monkeypatch):
        _, _, code = run_cli(monkeypatch, "ingest", "--help")
        assert code == 0

    def test_retrieve_help(self, monkeypatch):
        _, _, code = run_cli(monkeypatch, "retrieve", "--help")
        assert code == 0

    def test_stats_help(self, monkeypatch):
        _, _, code = run_cli(monkeypatch, "stats", "--help")
        assert code == 0

    def test_models_help(self, monkeypatch):
        _, _, code = run_cli(monkeypatch, "models", "--help")
        assert code == 0


# ---------------------------------------------------------------------------
# models command
# ---------------------------------------------------------------------------

class TestModelsCommand:
    def test_lists_models(self, monkeypatch):
        """models command should call core.get_valid_models and print each one."""
        model_list = ["openai_gpt-4o_2024-08-06", "anthropic_claude-3.5-sonnet"]
        with patch("core.get_valid_models", return_value=model_list):
            out, _, code = run_cli(monkeypatch, "models")
        assert code == 0
        for m in model_list:
            assert m in out

    def test_empty_model_list(self, monkeypatch):
        with patch("core.get_valid_models", return_value=[]):
            out, _, code = run_cli(monkeypatch, "models")
        assert code == 0
        assert out.strip() == ""


# ---------------------------------------------------------------------------
# stats command
# ---------------------------------------------------------------------------

class TestStatsCommand:
    def test_stats_json_output(self, monkeypatch):
        """stats outputs valid JSON with total/human/machine keys."""
        with patch("core.count_fragments", side_effect=[100, 20, 80]):
            out, _, code = run_cli(monkeypatch, "stats")
        assert code == 0
        data = json.loads(out)
        assert data == {"total": 100, "human": 20, "machine": 80}


# ---------------------------------------------------------------------------
# ingest command
# ---------------------------------------------------------------------------

class TestIngestCommand:
    def test_ingest_machine_fragment(self, monkeypatch):
        """Ingest a Machine-origin fragment and check JSON output."""
        fake_result = {"fragment_id": "abc123", "warnings": []}
        with patch("core.save_fragment", return_value=fake_result) as mock_save:
            out, _, code = run_cli(
                monkeypatch,
                "ingest",
                "--origin", "Machine",
                "--content", "Scientists find life on Mars.",
                "--model", "openai_gpt-4o_2024-08-06",
                "--is-fake",
                "--lang", "en",
            )
        assert code == 0
        data = json.loads(out)
        assert data["fragment_id"] == "abc123"
        assert mock_save.called

    def test_ingest_human_fragment(self, monkeypatch):
        fake_result = {"fragment_id": "def456", "warnings": []}
        with patch("core.save_fragment", return_value=fake_result):
            out, _, code = run_cli(
                monkeypatch,
                "ingest",
                "--origin", "Human",
                "--content", "Real news article text.",
                "--outlet", "BBC",
                "--url", "https://bbc.com/news/example",
                "--lang", "en",
            )
        assert code == 0
        data = json.loads(out)
        assert data["fragment_id"] == "def456"

    def test_ingest_validation_error_exits_1(self, monkeypatch):
        """When core raises ValidationError, exit code should be 1."""
        from core import ValidationError
        with patch("core.save_fragment", side_effect=ValidationError("bad input")):
            _, err, code = run_cli(
                monkeypatch,
                "ingest",
                "--origin", "Machine",
                "--content", "Text.",
                "--model", "openai_gpt-4o_2024-08-06",
            )
        assert code == 1
        assert "bad input" in err

    def test_ingest_content_required(self, monkeypatch):
        """Missing --content should cause argparse to fail (exit 2)."""
        _, _, code = run_cli(
            monkeypatch,
            "ingest",
            "--origin", "Machine",
            "--model", "openai_gpt-4o_2024-08-06",
        )
        assert code == 2

    def test_ingest_origin_required(self, monkeypatch):
        """Missing --origin should cause argparse to fail (exit 2)."""
        _, _, code = run_cli(
            monkeypatch,
            "ingest",
            "--content", "Some text.",
        )
        assert code == 2

    def test_ingest_invalid_origin_choice(self, monkeypatch):
        """Invalid origin value not in choices should fail."""
        _, _, code = run_cli(
            monkeypatch,
            "ingest",
            "--origin", "Alien",
            "--content", "Text.",
        )
        assert code == 2

    def test_ingest_lenient_flag_passed(self, monkeypatch):
        """--lenient should cause strict_model=False to be passed to save_fragment."""
        fake_result = {"fragment_id": "ghi789", "warnings": ["unknown model"]}
        with patch("core.save_fragment", return_value=fake_result) as mock_save:
            run_cli(
                monkeypatch,
                "ingest",
                "--origin", "Machine",
                "--content", "Text.",
                "--model", "unknown_vendor_xyz",
                "--lenient",
            )
        # strict_model=False when --lenient is set
        _, kwargs = mock_save.call_args
        assert kwargs.get("strict_model") is False or mock_save.call_args[0][1] is False


# ---------------------------------------------------------------------------
# retrieve command
# ---------------------------------------------------------------------------

class TestRetrieveCommand:
    def test_retrieve_default(self, monkeypatch):
        """retrieve with no args calls get_random_fragments(n=1) and outputs JSON."""
        from datetime import datetime, timezone
        frag = {
            "FragmentID": "aaa",
            "Content": "Test.",
            "Origin": "Machine",
            "IsFake": True,
            "ISOLanguage": "en",
            "MachineModel": "openai_gpt-4o_2024-08-06",
            "CreationDate": datetime(2024, 6, 1, tzinfo=timezone.utc),
        }
        with patch("core.get_random_fragments", return_value=[frag]):
            out, _, code = run_cli(monkeypatch, "retrieve")
        assert code == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert data[0]["FragmentID"] == "aaa"

    def test_retrieve_n_param(self, monkeypatch):
        with patch("core.get_random_fragments", return_value=[]) as mock_get:
            run_cli(monkeypatch, "retrieve", "--n", "5")
        mock_get.assert_called_once()
        assert mock_get.call_args[1].get("n") == 5 or mock_get.call_args[0][0] == 5

    def test_retrieve_datetime_serialized(self, monkeypatch):
        """CreationDate (datetime) must be JSON-serializable in output."""
        from datetime import datetime, timezone
        frag = {
            "FragmentID": "bbb",
            "Content": "Test.",
            "Origin": "Human",
            "IsFake": False,
            "CreationDate": datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc),
        }
        with patch("core.get_random_fragments", return_value=[frag]):
            out, _, code = run_cli(monkeypatch, "retrieve")
        assert code == 0
        data = json.loads(out)
        assert "2025-01-15" in data[0]["CreationDate"]


# ---------------------------------------------------------------------------
# No-command behaviour
# ---------------------------------------------------------------------------

class TestNoCommand:
    def test_no_subcommand_exits_nonzero(self, monkeypatch):
        """Calling roguegpt with no subcommand should exit non-zero."""
        _, _, code = run_cli(monkeypatch)
        assert code != 0
