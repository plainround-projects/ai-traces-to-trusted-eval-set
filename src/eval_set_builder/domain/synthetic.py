"""Synthetic hard cases: the seeds that ask for them and the filters every generated message must pass."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

AGENT_VOICE = (
    "i noticed that you",
    "thank you for contacting",
    "thanks for contacting",
    "could you please confirm",
    "can you confirm that",
    "how can i help",
    "how may i assist",
    "i can help you",
    "let me look into",
    "we apologize",
    "i understand your frustration",
    "please provide your",
    "i see that you",
    "i would be happy to",
)
STOPWORDS: Mapping[str, frozenset[str]] = {
    "es": frozenset({"mi", "pedido", "el", "la", "no", "que", "por", "favor", "hola", "mis", "una"}),
    "fr": frozenset({"ma", "commande", "le", "la", "pas", "que", "bonjour", "mon", "une", "pour"}),
    "de": frozenset({"meine", "bestellung", "der", "die", "nicht", "ich", "hallo", "und", "mein", "ist"}),
    "pt": frozenset({"meu", "pedido", "o", "a", "não", "que", "olá", "minha", "uma", "por"}),
}
_ORDER_NUMBER = re.compile(r"(?<!\d)\d{4}(?!\d)")
_WORDS = re.compile(r"[\w']+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class Seed:
    """A gap in real traffic and the instruction that asks the model to fill it."""

    seed_id: str
    gap: str
    intent: str
    language: str
    instruction: str
    order_count: int


@dataclass(frozen=True, slots=True)
class Rejection:
    """A generated message that was filtered out, with the rule that caught it."""

    seed_id: str
    rule: str
    detail: str
    message: str


def check_message(seed: Seed, message: str) -> Rejection | None:
    """Apply the guide's rules to one generated message; None means it passes.

    Rules: written in the customer's voice (a message from the agent is the wrong direction), 4 to 80 words,
    the number of distinct four-digit order numbers the seed asks for, and the seed's language.
    """
    lowered = message.lower()
    for phrase in AGENT_VOICE:
        if phrase in lowered:
            return Rejection(seed.seed_id, "voice", f"agent phrase {phrase!r}", message)
    words = _WORDS.findall(lowered)
    if not 4 <= len(words) <= 80:
        return Rejection(seed.seed_id, "length", f"{len(words)} words", message)
    found = len(set(_ORDER_NUMBER.findall(message)))
    if found != seed.order_count:
        return Rejection(
            seed.seed_id, "order_numbers", f"{found} order numbers, seed asks for {seed.order_count}", message
        )
    if seed.language != "en" and not STOPWORDS[seed.language] & set(words):
        return Rejection(seed.seed_id, "language", f"no {seed.language} stop words", message)
    return None
