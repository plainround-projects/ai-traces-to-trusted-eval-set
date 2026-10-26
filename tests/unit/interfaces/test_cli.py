import json
import shutil

import pytest

from eval_set_builder.interfaces.cli import main
from tests.unit.application.fakes import REPO


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    for name in ("data", "prompts", "fewshot", "finetune", "tests/fixtures", "eval-set"):
        shutil.copytree(REPO / name, tmp_path / name)
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("CASSETTE", str(tmp_path / "tests/fixtures/cassettes/synthetic-v1.json"))
    return tmp_path


def test_generate_writes_the_raw_file_and_its_key(workspace, monkeypatch):
    (workspace / "data/raw/traces.jsonl").unlink()
    assert main(["generate"]) == 0
    assert (workspace / "data/raw/traces.jsonl").read_text().count("\n") == 1010
    assert json.loads((workspace / "data/raw/answer_key.json").read_text())["seed"] == 2610


def test_a_single_stage_runs_and_writes_its_report(workspace):
    assert main(["load"]) == 0
    assert "Stage 1" in (workspace / "reports/01-load.md").read_text()
    assert main(["scrub"]) == 0
    assert (workspace / "work/scrubbed.jsonl").exists()


def test_run_all_prints_the_manifest_summary(workspace, capsys):
    assert main(["run-all"]) == 0
    assert "eval set v1: 400 cases" in capsys.readouterr().out


def test_rebuild_check_passes_on_the_committed_set_and_fails_when_it_was_edited(workspace, capsys):
    assert main(["rebuild-check"]) == 0
    assert "identical" in capsys.readouterr().out
    manifest = workspace / "eval-set/v1/manifest.json"
    manifest.write_text(manifest.read_text().replace('"kappa"', '"kappa_edited"'))
    assert main(["rebuild-check"]) == 1


def test_a_missing_recording_is_reported_not_raised(workspace, monkeypatch):
    prompt = workspace / "prompts/synthesize.v1.md"
    prompt.write_text(prompt.read_text() + "\nChanged text.\n")
    assert main(["load"]) == 0 and main(["scrub"]) == 0 and main(["dedup"]) == 0
    assert main(["sample-and-guide"]) == 0 and main(["label"]) == 0
    assert main(["synthesize"]) == 1


def test_a_bad_environment_value_stops_the_program_with_exit_code_two(monkeypatch, capsys):
    monkeypatch.setenv("MODEL_ADAPTER", "gpt")
    assert main(["load"]) == 2
    assert "MODEL_ADAPTER" in capsys.readouterr().err


def test_the_claude_adapter_without_a_key_is_a_configuration_error(workspace, monkeypatch, capsys):
    monkeypatch.setenv("MODEL_ADAPTER", "claude")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert main(["record-synthetic"]) == 1
