"""Stage 6: have a model write hard cases from seeds, filter them, and attach the current assistant's reply."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.application.dedupe_stage import DedupSettings
from eval_set_builder.application.ports import ModelRequest, TextModel
from eval_set_builder.application.prompts import PromptFile
from eval_set_builder.application.reference_assistant import judge_reply, reply_to
from eval_set_builder.domain.dedup import jaccard, numbers_in, shingles
from eval_set_builder.domain.errors import SyntheticGenerationError
from eval_set_builder.domain.synthetic import Rejection, Seed, check_message


@dataclass(frozen=True, slots=True)
class SyntheticCase:
    """An accepted synthetic case: the message, the current assistant's reply and the rubric's true label."""

    case_id: str
    seed: Seed
    message: str
    reply: str
    true_label: str
    model: str


@dataclass(frozen=True, slots=True)
class SyntheticResult:
    """Accepted cases, every rejection with its rule, and what the calls used."""

    cases: tuple[SyntheticCase, ...]
    rejections: tuple[Rejection, ...]
    calls: int
    input_tokens: int
    output_tokens: int


def clean_message(text: str) -> str:
    """One paragraph, surrounding quotes removed."""
    return " ".join(text.split()).strip("\"'\u201c\u201d\u2018\u2019 ")


class _KnownMessages:
    """The messages a candidate must stay clear of, with their shingle sets computed once."""

    def __init__(self, messages: Mapping[str, str], settings: DedupSettings) -> None:
        self._settings = settings
        self._texts = dict(messages)
        self._sets = {key: shingles(text, settings.size) for key, text in messages.items()}

    def add(self, key: str, text: str) -> None:
        self._texts[key] = text
        self._sets[key] = shingles(text, self._settings.size)

    def closest(self, message: str) -> tuple[str, float] | None:
        """The known message at or above the threshold with the highest overlap, if any."""
        own = shingles(message, self._settings.size)
        best: tuple[str, float] | None = None
        for key, other in self._sets.items():
            score = jaccard(own, other)
            if score < self._settings.threshold or (best is not None and score <= best[1]):
                continue
            if not self._settings.same_numbers or numbers_in(message) == numbers_in(self._texts[key]):
                best = (key, score)
        return best


def synthesize(
    model: TextModel,
    prompt: PromptFile,
    seeds: Sequence[Seed],
    real_messages: Mapping[str, str],
    target: int,
    settings: DedupSettings,
) -> SyntheticResult:
    """Ask for one message per seed until `target` pass the guide's rules and sit outside the near-duplicate threshold."""
    accepted: list[SyntheticCase] = []
    rejections: list[Rejection] = []
    known = _KnownMessages(real_messages, settings)
    calls = input_tokens = output_tokens = 0
    for seed in seeds:
        if len(accepted) == target:
            break
        reply = model.complete(ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instruction))
        calls += 1
        input_tokens += reply.input_tokens
        output_tokens += reply.output_tokens
        message = clean_message(reply.text)
        rejection = check_message(seed, message)
        if rejection is None:
            twin = known.closest(message)
            if twin is not None:
                rejection = Rejection(seed.seed_id, "near_duplicate", f"{twin[1]:.2f} to {twin[0]}", message)
        if rejection is not None:
            rejections.append(rejection)
            continue
        case_id = f"s-{len(accepted) + 1:03d}"
        answer = reply_to(message)
        accepted.append(SyntheticCase(case_id, seed, message, answer, judge_reply(seed, message, answer), reply.model))
        known.add(case_id, message)
    if len(accepted) < target:
        raise SyntheticGenerationError(f"only {len(accepted)} of {target} synthetic cases passed after {calls} calls")
    return SyntheticResult(tuple(accepted), tuple(rejections), calls, input_tokens, output_tokens)
