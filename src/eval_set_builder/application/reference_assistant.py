"""The current assistant for synthetic cases: a small keyword matcher over the intent catalog, and its grader."""

from __future__ import annotations

import re

from eval_set_builder.application.intent_catalog import INTENTS, IntentSpec
from eval_set_builder.domain.synthetic import Seed

_WORD = re.compile(r"[a-z0-9']+")
_STOP = frozenset(
    [
        "a",
        "an",
        "the",
        "i",
        "my",
        "is",
        "it",
        "to",
        "of",
        "for",
        "and",
        "or",
        "me",
        "you",
        "can",
        "do",
        "how",
        "what",
        "where",
        "when",
        "in",
        "on",
        "at",
        "be",
        "this",
        "that",
    ]
)
_ORDER = re.compile(r"(?<!\d)\d{4}(?!\d)")
FALLBACK = "Thanks for your message. Please see the help center for more details."
ASK_FOR_ORDER = "Could you send me the order number so I can look it up?"
MATCH_FLOOR = 0.25


def _content(text: str) -> frozenset[str]:
    return frozenset(word for word in _WORD.findall(text.lower()) if word not in _STOP and not word.isdigit())


def best_intent(message: str) -> IntentSpec | None:
    """The catalog intent whose questions share the most content words with the message, if any is close enough."""
    words = _content(message)
    best: tuple[float, IntentSpec] | None = None
    for spec in INTENTS:
        for question in spec.questions:
            reference = _content(question.replace("{order}", ""))
            union = words | reference
            score = len(words & reference) / len(union) if union else 0.0
            if best is None or score > best[0]:
                best = (score, spec)
    return best[1] if best and best[0] >= MATCH_FLOOR else None


def reply_to(message: str) -> str:
    """What the current assistant says: the matched intent's answer about the first order number it sees."""
    spec = best_intent(message)
    if spec is None:
        return FALLBACK
    orders = _ORDER.findall(message)
    if spec.needs_order and not orders:
        return ASK_FOR_ORDER
    return spec.answer.format(order=orders[0] if orders else "")


def judge_reply(seed: Seed, message: str, reply: str) -> str:
    """The true label of a synthetic case, from the seed's rubric (stands in for a careful expert)."""
    spec = best_intent(message)
    if reply == FALLBACK or spec is None or spec.intent_id != seed.intent:
        return "wrong"
    orders = set(_ORDER.findall(message))
    if seed.order_count > 1 and sum(order in reply for order in orders) < len(orders):
        return "partly_correct"
    if seed.language != "en":
        return "partly_correct"
    return "correct"
