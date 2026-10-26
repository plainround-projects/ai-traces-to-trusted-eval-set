"""The real adapter: Claude through the official SDK. The key comes from the environment, never from code."""

from __future__ import annotations

from typing import Any

import anthropic

from eval_set_builder.application.ports import ModelCallError, ModelReply, ModelRequest
from eval_set_builder.infrastructure.environment import ConfigurationError


class ClaudeTextModel:
    """Sends one user message with a system prompt and returns the text; failures become `ModelCallError`."""

    def __init__(
        self, model_id: str, api_key: str | None, *, timeout_seconds: float = 60.0, client: Any = None
    ) -> None:
        if client is None:
            if not api_key:
                raise ConfigurationError("ANTHROPIC_API_KEY must be set to use the Claude adapter")
            client = anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds, max_retries=3)
        self._client = client
        self._model_id = model_id

    def complete(self, request: ModelRequest) -> ModelReply:
        """Call the Messages API once (the SDK retries rate limits and server errors with backoff)."""
        try:
            message = self._client.messages.create(
                model=self._model_id,
                max_tokens=request.max_tokens,
                system=request.system,
                messages=[{"role": "user", "content": request.user}],
            )
        except anthropic.APIError as error:
            raise ModelCallError(f"{type(error).__name__}: {error}") from error
        if message.stop_reason == "refusal":
            raise ModelCallError("the model declined the request (stop_reason=refusal)")
        text = "".join(block.text for block in message.content if block.type == "text")
        return ModelReply(text, message.model, message.usage.input_tokens, message.usage.output_tokens)
