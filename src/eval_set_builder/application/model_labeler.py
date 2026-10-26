"""A labeler that asks a text model to apply the guide to one case."""

from __future__ import annotations

from eval_set_builder.application.ports import LabelCase, ModelRequest, TextModel
from eval_set_builder.application.prompts import PromptFile
from eval_set_builder.domain.errors import LabelingError
from eval_set_builder.domain.labels import LABELS


class ModelLabeler:
    """Labels a case by sending the guide-bearing prompt and the exchange to a model; the reply must name a label."""

    def __init__(self, name: str, model: TextModel, prompt: PromptFile, guide: str) -> None:
        self.name = name
        self._model = model
        self._prompt = prompt
        self._guide = guide

    def label(self, case: LabelCase) -> str:
        """The first label the model's reply names; anything else is a `LabelingError`."""
        user = f"Customer: {case.message}\nAssistant: {case.reply}"
        system = f"{self._prompt.text}\n\n{self._guide}"
        reply = self._model.complete(ModelRequest(f"{self._prompt.name}@{self._prompt.version}", system, user, 20))
        words = reply.text.lower().replace("`", " ").split()
        for word in words:
            cleaned = word.strip(".,:;\"'")
            if cleaned in LABELS:
                return cleaned
        raise LabelingError(f"the model's reply names none of {', '.join(LABELS)}")
