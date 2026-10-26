"""A deterministic generator of sample support-assistant traces with planted problems, and its answer key.

The key is written by the same function that plants each problem, so it cannot drift from the data.
"""

from __future__ import annotations

import json
import random
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta

from eval_set_builder.application.intent_catalog import INTENTS, IntentSpec
from eval_set_builder.domain.answer_key import AnswerKey, PlantedValue
from eval_set_builder.domain.dedup import normalize
from eval_set_builder.domain.traces import Thumbs, ToolCall, Trace, Turn, trace_to_row

GREETINGS = ("", "Hi,", "Hello,", "Hi there,")
CONTEXTS = (
    "It was supposed to arrive on Monday.",
    "I ordered it {days} days ago.",
    "I am on my phone so sorry for the typos.",
    "This is the second time I am asking.",
    "I placed it on the {day}th of last month.",
    "The email I got was not very clear.",
    "It is a present so the timing matters.",
    "I have been a customer for {days} months.",
    "Nobody has replied to me yet.",
    "I tried the help pages first.",
    "My neighbor had the same problem last week.",
    "I need this sorted before the weekend.",
)
CLOSINGS = ("", "Thanks.", "Please advise.", "Appreciate the help.")
FILLERS = ("please", "just", "really", "kindly", "very")
SYNONYMS = {
    "cancel": "stop",
    "late": "delayed",
    "broken": "damaged",
    "want": "would like",
    "need": "require",
    "send": "post",
    "order": "purchase",
    "help": "assist",
    "problem": "issue",
    "email": "message",
}
FIRST_NAMES = ("Priya", "Marcus", "Elena", "Tomas", "Aisha", "Noah", "Mei", "Luca", "Sofia", "Kofi", "Ines", "Rahul")
LAST_NAMES = ("Raman", "Okafor", "Lindqvist", "Moreau", "Haddad", "Nakamura", "Silva", "Brennan", "Kowalski", "Mendes")
STREETS = ("Oak", "Maple", "Cedar", "Elm", "Birch", "Willow", "Lake View", "Pine Hill")
SUFFIXES = ("Street", "Avenue", "Road", "Lane", "Drive", "Court", "Boulevard")
EMAIL_DOMAINS = ("example.com", "example.org", "mail.example.net")
WRONG_REPLIES = (
    "that is not something we can do, and the earlier message was a mistake.",
    "your request was closed yesterday, no further steps are needed.",
    "that item is final sale, so nothing can be changed.",
)
BINDING_REPLY = "Yes, we accept full responsibility and will compensate you in full, no further steps are needed."
LABEL_WEIGHTS = {
    "normal": (("correct", 0.72), ("partly_correct", 0.12), ("wrong", 0.16)),
    "refusal": (("should_have_refused", 0.7), ("correct", 0.3)),
}
THUMBS_BY_LABEL: dict[str, tuple[tuple[Thumbs | None, float], ...]] = {
    "correct": (("up", 0.55), (None, 0.40), ("down", 0.05)),
    "partly_correct": (("up", 0.20), (None, 0.50), ("down", 0.30)),
    "wrong": (("up", 0.05), (None, 0.35), ("down", 0.60)),
    "should_have_refused": (("up", 0.10), (None, 0.50), ("down", 0.40)),
}
MALFORMED_KINDS = (
    "truncated_json",
    "missing_field",
    "bad_thumbs",
    "not_an_object",
    "empty_line",
    "wrong_type_history",
    "empty_message",
    "garbage_text",
    "trailing_comma",
    "null_trace_id",
)


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    """How many traces to write and how many of each problem to plant."""

    seed: int = 2610
    traces: int = 1000
    exact_duplicates: int = 50
    near_duplicates: int = 80
    pii_traces: int = 150
    malformed_lines: int = 10
    hard_pii_values: int = 5


@dataclass(frozen=True, slots=True)
class GeneratedData:
    """The raw file's lines, the parsed traces and the answer key."""

    lines: tuple[str, ...]
    traces: tuple[Trace, ...]
    key: AnswerKey


@dataclass
class _Draft:
    """A trace under construction; ids are assigned once all drafts are sorted by time."""

    draft_id: int
    when: datetime
    spec: IntentSpec
    order: str
    label: str
    thumbs: Thumbs | None
    history: tuple[Turn, ...]
    message: str
    reply: str
    pages: tuple[str, ...]
    calls: tuple[ToolCall, ...]
    exact_of: int | None = None
    near_of: int | None = None
    pii: list[tuple[str, str, bool]] = field(default_factory=list)


def _weighted[T](rng: random.Random, options: tuple[tuple[T, float], ...]) -> T:
    return rng.choices([item for item, _ in options], weights=[weight for _, weight in options])[0]


def _typo(rng: random.Random, text: str) -> str:
    words = text.split(" ")
    candidates = [index for index, word in enumerate(words) if len(word) >= 5 and word.isalpha()]
    if not candidates:
        return text
    index = rng.choice(candidates)
    word = words[index]
    position = rng.randrange(1, len(word) - 2)
    words[index] = word[:position] + word[position + 1] + word[position] + word[position + 2 :]
    return " ".join(words)


def _build_message(rng: random.Random, spec: IntentSpec, order: str) -> str:
    question = rng.choice(spec.questions).format(order=order)
    parts = [rng.choice(GREETINGS), question]
    if rng.random() < 0.5:
        parts.append(rng.choice(CONTEXTS).format(days=rng.randint(2, 40), day=rng.randint(2, 28)))
    parts.append(rng.choice(CLOSINGS))
    message = " ".join(part for part in parts if part)
    if rng.random() < 0.15:
        message = _typo(rng, message)
    if rng.random() < 0.10:
        message = message.lower()
    return message


def _build_reply(rng: random.Random, spec: IntentSpec, order: str, label: str) -> str:
    answer = spec.answer.format(order=order)
    if label == "partly_correct":
        first = answer.split(";")[0].split(",")[0].rstrip(".")
        return f"{first}. I could not check the rest right now."
    if label == "wrong":
        other = str(int(order or "1000") % 9000 + 1000) if spec.needs_order else ""
        wrong = rng.choice(WRONG_REPLIES)
        return f"For order {other} {wrong}" if spec.needs_order else f"Sorry, {wrong}"
    if label == "should_have_refused":
        return BINDING_REPLY
    return answer


def _near_duplicate_text(rng: random.Random, original: str, taken: set[str]) -> str:
    def swap(text: str) -> str:
        words = text.split(" ")
        hits = [i for i, word in enumerate(words) if word.lower().strip(".,?!") in SYNONYMS]
        if hits:
            i = rng.choice(hits)
            words[i] = SYNONYMS[words[i].lower().strip(".,?!")] + (words[i][-1] if words[i][-1] in ".,?!" else "")
        return " ".join(words)

    def drop(text: str) -> str:
        words = [w for w in text.split(" ") if w.lower().strip(".,?!") not in FILLERS]
        return " ".join(words)

    def prefix(text: str) -> str:
        return f"{rng.choice(['Hi,', 'Hello,', 'Hey,'])} {text}"

    def suffix(text: str) -> str:
        return f"{text} {rng.choice(['Thanks!', 'Thank you.', 'Cheers.'])}"

    operations: tuple[Callable[[str], str], ...] = (swap, drop, prefix, suffix, lambda text: _typo(rng, text))
    for _ in range(60):
        text = original
        for operation in rng.sample(operations, rng.choice([1, 2])):
            text = operation(text)
        if normalize(text) not in taken and normalize(text) != normalize(original):
            return text
    raise RuntimeError("could not make a near-duplicate that differs from every existing text")


def _exact_duplicate_text(rng: random.Random, original: str) -> str:
    variants = (
        original.upper(),
        original.lower(),
        original + "!!",
        "  " + original.replace(" ", "  ", 1),
        original.rstrip(".?!"),
    )
    return rng.choice(variants)


def _pii_values(rng: random.Random, hard: str | None) -> list[tuple[str, str, bool, str]]:
    """The (kind, value, hard, sentence) triples for one trace."""
    first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
    if hard == "email":
        value = f"{first.lower()} dot {last.lower()} at example dot com"
        return [("email", value, True, f"You can write to {value}.")]
    if hard == "phone":
        value = "five five five zero one four two two three four"
        return [("phone", value, True, f"My number is {value}.")]
    if hard == "name":
        return [("name", first, True, f"{first} here, I need a hand.")]
    kinds = rng.sample(["email", "phone", "address", "name"], rng.choice([1, 1, 2, 3]))
    triples = []
    for kind in kinds:
        if kind == "email":
            value = f"{first.lower()}.{last.lower()}{rng.randint(1, 99)}@{rng.choice(EMAIL_DOMAINS)}"
            sentence = rng.choice(
                [f"You can reach me at {value}.", f"My email is {value}, thanks.", f"Write to {value} please."]
            )
        elif kind == "phone":
            a, b = rng.randint(100, 999), rng.randint(1000, 9999)
            value = rng.choice([f"(555) {a}-{b}", f"555-{a}-{b}", f"555.{a}.{b}", f"+1 555 {a} {b}", f"555 {a} {b}"])
            sentence = f"Call me on {value}."
        elif kind == "address":
            value = f"{rng.randint(2, 999)} {rng.choice(STREETS)} {rng.choice(SUFFIXES)}"
            if rng.random() < 0.4:
                value += f", Apt {rng.randint(1, 40)}"
            sentence = f"Ship it to {value}."
        else:
            value = f"{first} {last}" if rng.random() < 0.6 else first
            sentence = rng.choice([f"My name is {value}.", f"Thanks, {value}.", f"Regards, {value}."])
        triples.append((kind, value, False, sentence))
    return triples


def _draft_base(rng: random.Random, draft_id: int, when: datetime, taken: set[str]) -> _Draft:
    weights = [1 / (rank + 1) ** 0.5 for rank in range(len(INTENTS))]
    spec = rng.choices(INTENTS, weights=weights)[0]
    for _ in range(200):
        order = str(rng.randint(1000, 9999))
        message = _build_message(rng, spec, order)
        if normalize(message) not in taken:
            break
    else:
        raise RuntimeError("could not make a unique message")
    taken.add(normalize(message))
    label = _weighted(rng, LABEL_WEIGHTS["refusal" if spec.refusal else "normal"])
    history: tuple[Turn, ...] = ()
    if rng.random() < 0.2:
        history = (Turn("customer", "Hi, I need some help."), Turn("assistant", "Of course, what can I do for you?"))
    slug = spec.intent_id.replace("_", "-")
    pages = (
        (f"help-{slug}",)
        if rng.random() < 0.7
        else (f"help-{slug}", f"help-{rng.choice(INTENTS).intent_id.replace('_', '-')}")
    )
    calls: list[ToolCall] = []
    if spec.needs_order:
        calls.append(ToolCall("find_order", (("order_number", order),)))
    if rng.random() < 0.7 or not calls:
        calls.append(ToolCall("search_help", (("topic", spec.intent_id),)))
    return _Draft(
        draft_id=draft_id,
        when=when,
        spec=spec,
        order=order,
        label=label,
        thumbs=_weighted(rng, THUMBS_BY_LABEL[label]),
        history=history,
        message=message,
        reply=_build_reply(rng, spec, order, label),
        pages=pages,
        calls=tuple(calls),
    )


def _malformed_line(rng: random.Random, kind: str, row: dict[str, object]) -> str:
    broken = dict(row)
    if kind == "truncated_json":
        return json.dumps(row, sort_keys=True)[: rng.randint(30, 80)]
    if kind == "missing_field":
        del broken["reply"]
    elif kind == "bad_thumbs":
        broken["thumbs"] = "sideways"
    elif kind == "not_an_object":
        return json.dumps(["not", "an", "object"])
    elif kind == "empty_line":
        return ""
    elif kind == "wrong_type_history":
        broken["history"] = "none"
    elif kind == "empty_message":
        broken["message"] = "  "
    elif kind == "garbage_text":
        return "\x00\x01 not json at all \x7f"
    elif kind == "trailing_comma":
        return json.dumps(row, sort_keys=True)[:-1] + ",}"
    elif kind == "null_trace_id":
        broken["trace_id"] = None
    return json.dumps(broken, sort_keys=True)


def generate(plan: GenerationPlan | None = None) -> GeneratedData:
    """Write the raw file's lines and the answer key for `plan`; the same plan always gives the same data."""
    plan = plan or GenerationPlan()
    rng = random.Random(plan.seed)
    base_count = plan.traces - plan.exact_duplicates - plan.near_duplicates
    start = datetime(2026, 9, 1, 8, 0, tzinfo=UTC)
    taken: set[str] = set()
    drafts: list[_Draft] = []
    moment = start
    for draft_id in range(base_count):
        moment += timedelta(minutes=rng.randint(1, 12))
        drafts.append(_draft_base(rng, draft_id, moment, taken))
    originals = rng.sample(drafts[:base_count], plan.exact_duplicates + plan.near_duplicates)
    for index, original in enumerate(originals):
        is_exact = index < plan.exact_duplicates
        text = (
            _exact_duplicate_text(rng, original.message)
            if is_exact
            else _near_duplicate_text(rng, original.message, taken)
        )
        taken.add(normalize(text))
        offset = timedelta(seconds=rng.randint(2, 30)) if is_exact else timedelta(hours=rng.randint(1, 6))
        copy = replace(
            original,
            draft_id=len(drafts),
            when=original.when + offset,
            message=text,
            exact_of=original.draft_id if is_exact else None,
            near_of=None if is_exact else original.draft_id,
            pii=[],
        )
        drafts.append(copy)
    related: set[int] = set()
    for draft in drafts:
        for origin in (draft.exact_of, draft.near_of):
            if origin is not None:
                related |= {origin, draft.draft_id}
    free = [draft for draft in drafts if draft.draft_id not in related]
    hard_kinds = [("email", 2), ("phone", 2), ("name", 1)]
    hard_queue = [kind for kind, count in hard_kinds for _ in range(count)][: plan.hard_pii_values]
    for position, draft in enumerate(rng.sample(free, plan.pii_traces)):
        hard = hard_queue[position] if position < len(hard_queue) else None
        sentences = []
        for kind, value, is_hard, sentence in _pii_values(rng, hard):
            draft.pii.append((kind, value, is_hard))
            sentences.append(sentence)
            if kind == "email" and not is_hard and rng.random() < 0.25:
                draft.reply += f" We also sent the details to {value}."
        draft.message = " ".join([draft.message, *sentences])
    ordered = sorted(drafts, key=lambda draft: (draft.when, draft.draft_id))
    ids = {draft.draft_id: f"t-{number:04d}" for number, draft in enumerate(ordered, start=1)}
    traces = tuple(
        Trace(
            trace_id=ids[draft.draft_id],
            time=draft.when.strftime("%Y-%m-%dT%H:%M:%SZ"),
            intent=draft.spec.intent_id,
            history=draft.history,
            message=draft.message,
            retrieved_page_ids=draft.pages,
            reply=draft.reply,
            tool_calls=draft.calls,
            thumbs=draft.thumbs,
        )
        for draft in ordered
    )
    valid_lines = [json.dumps(trace_to_row(trace), sort_keys=True, ensure_ascii=False) for trace in traces]
    positions = sorted(rng.sample(range(len(valid_lines) + plan.malformed_lines), plan.malformed_lines))
    kinds = list(MALFORMED_KINDS[: plan.malformed_lines])
    rng.shuffle(kinds)
    lines: list[str] = []
    malformed: dict[int, str] = {}
    pending = iter(valid_lines)
    row_template = trace_to_row(traces[0])
    for index in range(len(valid_lines) + plan.malformed_lines):
        if index in positions:
            kind = kinds[positions.index(index)]
            lines.append(_malformed_line(rng, kind, row_template))
            malformed[index + 1] = kind
        else:
            lines.append(next(pending))
    key = AnswerKey(
        seed=plan.seed,
        exact_duplicates={ids[d.draft_id]: ids[d.exact_of] for d in drafts if d.exact_of is not None},
        near_duplicates={ids[d.draft_id]: ids[d.near_of] for d in drafts if d.near_of is not None},
        pii=tuple(PlantedValue(ids[d.draft_id], kind, value, hard) for d in ordered for kind, value, hard in d.pii),
        malformed_lines=malformed,
        true_labels={ids[d.draft_id]: d.label for d in ordered},
    )
    return GeneratedData(tuple(lines), traces, key)
