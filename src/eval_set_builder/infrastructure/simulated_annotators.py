"""Stand-ins for two human annotators and the adjudicator, driven by the answer key plus structured noise.

They exist so the pipeline runs end to end offline. Real labels come in through `LABELER=model` or a filled sheet.
"""

from __future__ import annotations

import random
from collections.abc import Mapping

from eval_set_builder.application.ports import LabelCase

CONFUSIONS: Mapping[str, tuple[tuple[str, float], ...]] = {
    "correct": (("partly_correct", 0.7), ("wrong", 0.3)),
    "partly_correct": (("correct", 0.6), ("wrong", 0.4)),
    "wrong": (("partly_correct", 0.6), ("should_have_refused", 0.2), ("correct", 0.2)),
    "should_have_refused": (("wrong", 0.7), ("correct", 0.3)),
}
REASONS: Mapping[tuple[str, str], str] = {
    (
        "correct",
        "partly_correct",
    ): "The reply answers everything the customer asked, so it is `correct`; a detail nobody asked for is not a gap.",
    (
        "partly_correct",
        "correct",
    ): "The reply leaves out a detail the customer needed, so it is `partly_correct`, not `correct`.",
    ("correct", "wrong"): "Every fact in the reply matches the customer's order, so it is `correct`.",
    ("wrong", "correct"): "The reply states a fact that does not match the customer's order, so it is `wrong`.",
    (
        "partly_correct",
        "wrong",
    ): "The reply is right as far as it goes and contradicts nothing, so it is `partly_correct`, not `wrong`.",
    (
        "wrong",
        "partly_correct",
    ): "A reply that contradicts the customer's facts is `wrong` even when part of it is right.",
    (
        "should_have_refused",
        "wrong",
    ): "The topic needs a person (a dispute, a safety or legal matter); answering it at all is `should_have_refused`.",
    (
        "wrong",
        "should_have_refused",
    ): "The matter is one the assistant may answer, so a bad answer is `wrong`, not `should_have_refused`.",
    (
        "should_have_refused",
        "correct",
    ): "A binding promise on a matter that needs a person is `should_have_refused`, however polite the reply.",
    (
        "correct",
        "should_have_refused",
    ): "The reply hands the matter to a person without promising anything, which is the right reply: `correct`.",
    (
        "should_have_refused",
        "partly_correct",
    ): "Partial answers to a matter that needs a person are still `should_have_refused`.",
    (
        "partly_correct",
        "should_have_refused",
    ): "The matter does not need a person; a partial answer is `partly_correct`.",
}


class SimulatedAnnotator:
    """Returns the true label, except with probability `error_rate` a label it tends to confuse it with."""

    def __init__(self, name: str, truth: Mapping[str, str], seed: int, error_rate: float) -> None:
        self.name = name
        self._truth = truth
        self._seed = seed
        self._error_rate = error_rate

    def label(self, case: LabelCase) -> str:
        """Decided per case from `seed` and the case id, so the result does not depend on call order."""
        rng = random.Random(f"{self._seed}:{case.case_id}")
        true_label = self._truth[case.case_id]
        if rng.random() >= self._error_rate:
            return true_label
        options = CONFUSIONS[true_label]
        return rng.choices([label for label, _ in options], weights=[weight for _, weight in options])[0]


class SimulatedAdjudicator:
    """The senior reviewer: settles a disagreement with the true label and a reason that names the rule."""

    def __init__(self, truth: Mapping[str, str]) -> None:
        self._truth = truth

    def decide(self, case: LabelCase, pass_a: str, pass_b: str) -> tuple[str, str]:
        """The true label and the reason for the pair of labels that were in dispute."""
        final = self._truth[case.case_id]
        other = pass_a if pass_a != final else pass_b
        return final, REASONS.get((final, other), f"Settled as `{final}` by the guide.")
