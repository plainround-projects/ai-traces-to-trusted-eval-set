"""An adjudicator that asks a (stronger) model to settle a disagreement; used when no human reviewer is wired in."""

from __future__ import annotations

from eval_set_builder.application.ports import LabelCase, ModelRequest, TextModel
from eval_set_builder.application.prompts import PromptFile
from eval_set_builder.domain.errors import LabelingError
from eval_set_builder.domain.labels import LABELS


class ModelAdjudicator:
    """Sends the exchange and both labels; the reply is `label: reason`."""

    def __init__(self, model: TextModel, prompt: PromptFile, guide: str) -> None:
        self._model = model
        self._prompt = prompt
        self._guide = guide

    def decide(self, case: LabelCase, pass_a: str, pass_b: str) -> tuple[str, str]:
        """The final label and the reason the model gives."""
        user = f"Customer: {case.message}\nAssistant: {case.reply}\nPass A said {pass_a}. Pass B said {pass_b}."
        reply = self._model.complete(
            ModelRequest(
                f"{self._prompt.name}@{self._prompt.version}", f"{self._prompt.text}\n\n{self._guide}", user, 200
            )
        )
        label, _, reason = reply.text.strip().partition(":")
        label = label.strip().strip("`").lower()
        if label not in LABELS:
            raise LabelingError(f"the adjudicator's reply must start with one of {', '.join(LABELS)}")
        return label, reason.strip()
