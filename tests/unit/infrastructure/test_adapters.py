import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import anthropic
import pytest

from eval_set_builder.application.ports import LabelCase, ModelCallError, ModelReply, ModelRequest
from eval_set_builder.infrastructure.cassette import (
    MissingRecordingError,
    RecordedTextModel,
    RecordingTextModel,
    request_key,
)
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel
from eval_set_builder.infrastructure.environment import ConfigurationError
from eval_set_builder.infrastructure.logging import configure_logging, fields
from eval_set_builder.infrastructure.retry import retry
from eval_set_builder.infrastructure.settings import Settings
from eval_set_builder.infrastructure.shutdown import ShutdownSignal
from eval_set_builder.infrastructure.simulated_annotators import SimulatedAdjudicator, SimulatedAnnotator
from eval_set_builder.infrastructure.workspace import DirectoryWorkspace

REQUEST = ModelRequest("synth@v1", "system", "user", 50)


def _message(text="hello", stop_reason="end_turn"):
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text), SimpleNamespace(type="thinking", text="ignored")],
        stop_reason=stop_reason,
        model="claude-sonnet-5-5",
        usage=SimpleNamespace(input_tokens=11, output_tokens=7),
    )


class StubClient:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def test_the_claude_adapter_sends_the_system_prompt_and_reads_text_blocks_and_usage():
    client = StubClient(_message("a reply"))
    reply = ClaudeTextModel("claude-sonnet-5-5", None, client=client).complete(REQUEST)
    assert reply == ModelReply("a reply", "claude-sonnet-5-5", 11, 7)
    assert client.calls == [
        {
            "model": "claude-sonnet-5-5",
            "max_tokens": 50,
            "system": "system",
            "messages": [{"role": "user", "content": "user"}],
        }
    ]


def test_the_claude_adapter_turns_sdk_failures_and_refusals_into_one_named_error():
    request = anthropic.APIConnectionError(request=SimpleNamespace(method="POST", url="x"))  # type: ignore[arg-type]
    with pytest.raises(ModelCallError, match="APIConnectionError"):
        ClaudeTextModel("m", None, client=StubClient(request)).complete(REQUEST)
    with pytest.raises(ModelCallError, match="declined"):
        ClaudeTextModel("m", None, client=StubClient(_message(stop_reason="refusal"))).complete(REQUEST)


def test_the_claude_adapter_needs_a_key_from_the_environment():
    with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY"):
        ClaudeTextModel("m", None)
    assert ClaudeTextModel("m", "sk-test-not-real") is not None


def test_a_recording_replays_by_the_hash_of_the_whole_request_and_a_changed_prompt_misses(tmp_path):
    path = tmp_path / "cassette.json"
    recorder = RecordingTextModel(StubModel("recorded text"), path, "model-x", "test")
    recorder.complete(REQUEST)
    replay = RecordedTextModel(path)
    assert replay.complete(REQUEST).text == "recorded text"
    assert replay.provenance == "test"
    with pytest.raises(MissingRecordingError, match="make record-synthetic"):
        replay.complete(ModelRequest("synth@v2", "system", "user", 50))
    assert request_key("a", REQUEST) != request_key("b", REQUEST)


class StubModel:
    def __init__(self, text):
        self.text = text

    def complete(self, request):
        return ModelReply(self.text, "stub", 3, 2)


def test_settings_have_safe_defaults_and_reject_bad_values():
    settings = Settings.from_environ({})
    assert (settings.model_adapter, settings.labeler, settings.sample_size) == ("recorded", "simulated", 300)
    assert settings.anthropic_api_key is None
    for bad in ({"MODEL_ADAPTER": "gpt"}, {"SEED": "x"}, {"SAMPLE_SIZE": "0"}, {"LOG_LEVEL": "LOUD"}):
        with pytest.raises(ConfigurationError):
            Settings.from_environ(bad)
    assert Settings.from_environ({"ANTHROPIC_API_KEY": " k "}).anthropic_api_key == "k"


def test_the_workspace_reads_writes_hashes_lists_and_refuses_to_leave_its_root(tmp_path):
    workspace = DirectoryWorkspace(tmp_path)
    assert not workspace.exists("a/b.txt")
    workspace.write_text("a/b.txt", "héllo\n")
    assert workspace.read_text("a/b.txt") == "héllo\n" and workspace.exists("a/b.txt")
    assert len(workspace.digest("a/b.txt")) == 64
    workspace.write_text("a/c.txt", "x")
    assert workspace.list_names("a/") == ["a/b.txt", "a/c.txt"]
    for name in ("../x", "/etc/passwd"):
        with pytest.raises(ValueError, match="relative"):
            workspace.read_text(name)


def test_simulated_annotators_are_deterministic_and_wrong_at_about_their_error_rate():
    truth = {f"c{n}": "correct" for n in range(400)}
    annotator = SimulatedAnnotator("a", truth, seed=1, error_rate=0.2)
    labels = [annotator.label(LabelCase(f"c{n}", "i", (), "m", "r")) for n in range(400)]
    assert labels == [annotator.label(LabelCase(f"c{n}", "i", (), "m", "r")) for n in range(400)]
    assert 0.1 < sum(label != "correct" for label in labels) / 400 < 0.3
    decided, reason = SimulatedAdjudicator(truth).decide(
        LabelCase("c1", "i", (), "m", "r"), "correct", "partly_correct"
    )
    assert decided == "correct"
    assert "`correct`" in reason


def test_log_lines_are_logfmt_with_fields_and_quoted_values():
    stream = io.StringIO()
    configure_logging("INFO", stream)
    logging.getLogger("x").info("two words", extra=fields(stage="scrub", note="a b"))
    line = stream.getvalue().strip()
    assert 'msg="two words"' in line and "stage=scrub" in line and 'note="a b"' in line
    configure_logging("INFO", stream)
    assert len(logging.getLogger().handlers) == 1


def test_retry_backs_off_with_jitter_and_raises_the_last_failure():
    pauses: list[float] = []
    attempts = []

    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("x")
        return "ok"

    assert retry(flaky, attempts=4, base_delay_seconds=1.0, retry_on=(ConnectionError,), sleep=pauses.append) == "ok"
    assert len(pauses) == 2 and 0 <= pauses[0] <= 1.0 and 0 <= pauses[1] <= 2.0
    with pytest.raises(ConnectionError):
        retry(
            lambda: (_ for _ in ()).throw(ConnectionError("y")),
            attempts=2,
            base_delay_seconds=0,
            retry_on=(ConnectionError,),
            sleep=lambda s: None,
        )
    with pytest.raises(ValueError, match="at least 1"):
        retry(lambda: 1, attempts=0, base_delay_seconds=0, retry_on=(ValueError,))


def test_a_shutdown_signal_is_a_flag_that_wakes_waiters():
    flag = ShutdownSignal()
    assert not flag.requested and not flag.wait(0.001)
    flag.request()
    assert flag.requested and flag.wait(0.001)
    flag.install()


def test_cassette_file_is_valid_json_with_provenance():
    data = json.loads(Path("tests/fixtures/cassettes/synthetic-v1.json").read_text(encoding="utf-8"))
    assert data["model"] == "authored-sample-v1" and "not a model recording" in data["provenance"]
