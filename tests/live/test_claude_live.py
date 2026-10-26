"""Opt-in: calls the real model. Run with `make test-live` (RUN_LIVE=1 and ANTHROPIC_API_KEY set)."""

import os

import pytest

from eval_set_builder.application.ports import ModelRequest
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE") != "1" or not os.environ.get("ANTHROPIC_API_KEY"),
        reason="set RUN_LIVE=1 and ANTHROPIC_API_KEY to call the real model",
    ),
]


def test_the_real_model_writes_a_customer_message_for_a_seed():
    model = ClaudeTextModel(os.environ.get("MODEL_ID", "claude-sonnet-5-5"), os.environ["ANTHROPIC_API_KEY"])
    reply = model.complete(
        ModelRequest(
            "synthesize@v1",
            "You write test messages as a customer of a small online shop. Reply with the message only.",
            "Write a customer message that asks where order 4417 is. One sentence.",
            120,
        )
    )
    assert "4417" in reply.text
    assert reply.input_tokens > 0 and reply.output_tokens > 0
