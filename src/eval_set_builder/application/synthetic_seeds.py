"""The seeds for synthetic hard cases: each names a gap that real traffic has too little of."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import zip_longest

from eval_set_builder.domain.synthetic import Seed

_WRITE_ONLY = "Write only the customer's message, one to three sentences, in the customer's voice."
RARE = (
    ("gift_receipt", "asks for a gift receipt that does not show the price"),
    ("warranty_transfer", "asks to move the warranty to a friend who received the item as a gift"),
    ("accessibility_request", "asks whether the packaging can be opened without strong hands"),
    ("business_invoice_change", "asks to change the company name on an invoice that was already issued"),
    ("recall_notice", "asks whether a product they own is part of a recall"),
    ("subscription_pause", "asks to pause a monthly delivery for two months"),
    ("wholesale_account", "asks how to open a wholesale account"),
    ("workplace_redelivery", "asks the carrier to redeliver to a workplace reception desk"),
    ("allergy_question", "asks whether a scented candle contains nut oil"),
    ("repair_service", "asks whether the shop repairs a broken zipper for a fee"),
)
TWO_ORDER_TOPICS = (
    ("order_status", "the status"),
    ("refund_status", "a refund"),
    ("delivery_delay", "a late delivery"),
    ("return_label", "a return label"),
    ("cancel_order", "cancelling"),
)
POLICY = (
    ("start_return", "wants to return an item 45 days after delivery", 1),
    ("partial_refund", "wants a refund for one item of a bundle", 1),
    ("refund_method", "wants the refund sent to another person's card", 0),
    ("restocking_fee", "asks whether an opened hygiene product can be returned", 0),
    ("price_adjustment", "asks for the price difference on a sale item bought 20 days ago", 1),
)
LANGUAGES = (("es", "Spanish"), ("fr", "French"), ("de", "German"), ("pt", "Portuguese"))
LANGUAGE_INTENTS = (
    ("order_status", "asks where the order is"),
    ("refund_status", "asks when the refund will arrive"),
    ("cancel_order", "asks to cancel the order"),
    ("start_return", "asks how to return the order"),
    ("delivery_delay", "complains the order is late"),
    ("damaged_item", "says the item arrived broken"),
    ("tracking_link", "asks for the tracking link again"),
)
AMBIGUOUS = (
    ("order_status", "asks where their last order is without giving a number"),
    ("delivery_delay", "says the package they are waiting for is late without giving a number"),
    ("cancel_order", "asks to cancel the thing they bought yesterday without giving a number"),
)
ANGRY = (
    ("damaged_item", "is angry that the item arrived broken and also that nobody answered the first email"),
    ("missing_item", "is angry that an item is missing and also that the tracking page was wrong"),
    ("double_charge", "is angry about being charged twice and also about a delayed parcel"),
)


def _two_orders() -> list[Seed]:
    seeds = []
    for index in range(20):
        first, second = 1100 + 37 * index, 2400 + 53 * index
        intent, topic = TWO_ORDER_TOPICS[index % len(TWO_ORDER_TOPICS)]
        instruction = (
            f"Write a customer message that asks about {topic} for two different orders, {first} and {second}, "
            f"in the same message. {_WRITE_ONLY}"
        )
        seeds.append(Seed(f"two-orders-{index:02d}", "two_order_numbers", intent, "en", instruction, 2))
    return seeds


def _rare() -> list[Seed]:
    seeds = []
    for index in range(20):
        name, what = RARE[index % len(RARE)]
        instruction = (
            f"Write a customer message from someone who {what}. Variant {index // len(RARE) + 1}. {_WRITE_ONLY}"
        )
        seeds.append(Seed(f"rare-{index:02d}", "rare_intent", f"rare_{name}", "en", instruction, 0))
    return seeds


def _policy() -> list[Seed]:
    seeds = []
    for index in range(25):
        intent, what, orders = POLICY[index % len(POLICY)]
        number = f" for order {3100 + 41 * index}" if orders else " and gives no order number"
        instruction = f"Write a customer message from someone who {what}{number}. Variant {index // len(POLICY) + 1}. {_WRITE_ONLY}"
        seeds.append(Seed(f"policy-{index:02d}", "policy_edge", intent, "en", instruction, orders))
    return seeds


def _languages() -> list[Seed]:
    seeds = []
    for index in range(25):
        code, name = LANGUAGES[index % len(LANGUAGES)]
        intent, what = LANGUAGE_INTENTS[index % len(LANGUAGE_INTENTS)]
        instruction = (
            f"Write a customer message in {name} from someone who {what} for order {4200 + 29 * index}. {_WRITE_ONLY}"
        )
        seeds.append(Seed(f"language-{index:02d}", "other_language", intent, code, instruction, 1))
    return seeds


def _ambiguous() -> list[Seed]:
    seeds = []
    for index in range(15):
        intent, what = AMBIGUOUS[index % len(AMBIGUOUS)]
        instruction = (
            f"Write a customer message from someone who {what}. Variant {index // len(AMBIGUOUS) + 1}. {_WRITE_ONLY}"
        )
        seeds.append(Seed(f"ambiguous-{index:02d}", "ambiguous_order", intent, "en", instruction, 0))
    return seeds


def _angry() -> list[Seed]:
    seeds = []
    for index in range(15):
        intent, what = ANGRY[index % len(ANGRY)]
        instruction = f"Write a customer message from someone who {what}, for order {5300 + 17 * index}. {_WRITE_ONLY}"
        seeds.append(Seed(f"angry-{index:02d}", "angry_multi_issue", intent, "en", instruction, 1))
    return seeds


def build_seeds() -> tuple[Seed, ...]:
    """Each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100."""
    groups: Sequence[list[Seed]] = (_two_orders(), _rare(), _policy(), _languages(), _ambiguous(), _angry())
    interleaved = [seed for row in zip_longest(*groups) for seed in row if seed is not None]
    return tuple(interleaved)
