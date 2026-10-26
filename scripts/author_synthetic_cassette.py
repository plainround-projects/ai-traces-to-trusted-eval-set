"""Author the sample cassette of synthetic replies used for offline runs.

These are NOT model recordings: a script writes plausible customer messages from templates so the pipeline
and its filters can run without a key. `make record-synthetic` replaces the file with real recordings.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

from eval_set_builder.application.ports import ModelRequest
from eval_set_builder.application.prompts import parse_prompt_file
from eval_set_builder.application.synthetic_seeds import RARE, build_seeds
from eval_set_builder.domain.synthetic import Seed
from eval_set_builder.infrastructure.cassette import request_key

MODEL = "authored-sample-v1"
ROOT = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r"(?<!\d)\d{4}(?!\d)")

TWO_TOPIC = {
    "order_status": "where each one is right now",
    "refund_status": "when the refunds for both will arrive",
    "delivery_delay": "why both of them are late",
    "return_label": "how I can get a return label for each",
    "cancel_order": "how to cancel both before they ship",
}
TWO_FRAME = (
    "Hello, I am writing about two orders, {a} and {b}. Could you tell me {topic}?",
    "Hi team, orders {a} and {b} are both on my mind today. I would like to know {topic}.",
    "Good afternoon. I have two open orders, {b} and {a}, and I need to know {topic}.",
    "Quick question about {a} together with {b}: {topic}?",
)
RARE_TEXT = {
    "gift_receipt": (
        "I bought a present from your shop and the slip in the box shows the price. Can I get a gift receipt without it?",
        "The scarf was a gift for my sister and I do not want her to see what it cost. Is there a receipt that hides the price?",
    ),
    "warranty_transfer": (
        "A friend gave me one of your lamps as a birthday present. Can the warranty be moved to my name?",
        "My brother gave me his kettle as a gift and it still has warranty left. Can I take over the warranty?",
    ),
    "accessibility_request": (
        "Is the packaging of the water bottle easy to open? I have weak hands and cannot cut thick tape.",
        "Do you offer packaging that can be opened without scissors? My hands are arthritic.",
    ),
    "business_invoice_change": (
        "My company name was spelled wrong on the invoice you sent. Can you issue a corrected one with the right name?",
        "We need the invoice to show our registered company name instead of my own. Can it be reissued?",
    ),
    "recall_notice": (
        "I heard some heaters were recalled. How can I check whether mine is one of them?",
        "Is the baby gate I bought last spring part of any safety recall?",
    ),
    "subscription_pause": (
        "I get a monthly coffee delivery and I am away for two months. Can you pause it and restart it later?",
        "Can my monthly box skip the next two months without cancelling the subscription?",
    ),
    "wholesale_account": (
        "I run a small gift shop and would like to buy your products at wholesale prices. How do I open an account?",
        "Do you sell wholesale to shops, and if so who do I talk to about setting that up?",
    ),
    "workplace_redelivery": (
        "The carrier tried to deliver to my house while I was at work. Can it be sent to the reception desk of my office?",
        "Can you ask the carrier to leave my parcel with the front desk at my workplace instead?",
    ),
    "allergy_question": (
        "My son is allergic to nuts. Does the vanilla candle contain any nut oil?",
        "Before I buy the lavender soap, I need to know if it is made with almond or other nut oils.",
    ),
    "repair_service": (
        "The zipper on my backpack broke after a year. Do you repair them for a fee?",
        "Do you offer a repair service for broken zips, or do I have to go to a tailor?",
    ),
}
POLICY_TEXT = {
    "start_return": "I got order {n} about 45 days ago and only now noticed the stitching is coming apart. I know the return window is shorter, can I still send it back?",
    "partial_refund": "Order {n} was a bundle of three items and one of them is faulty. Can I get money back for just that one?",
    "refund_method": "I paid with my friend's card but I would like the refund to go to my own account. Is that possible?",
    "restocking_fee": "I opened a hygiene product and it does not suit my skin. Can it still be returned, and is there a fee?",
    "price_adjustment": "The jacket in order {n} was on sale 20 days after I bought it at full price. Can I get the difference back?",
}
POLICY_TAIL = (
    "",
    " Thanks for your help.",
    " Please let me know what my options are.",
    " I would appreciate a quick answer.",
    " I kept the receipt.",
)
LANGUAGE_TEXT = {
    "es": {
        "order_status": "Hola, ¿dónde está mi pedido {n}? Todavía no ha llegado.",
        "refund_status": "Hola, ¿cuándo llegará el reembolso de mi pedido {n}? Lo devolví hace una semana.",
        "cancel_order": "Hola, quiero cancelar mi pedido {n} antes de que lo envíen, por favor.",
        "start_return": "Hola, ¿cómo puedo devolver el pedido {n}? No me queda bien.",
        "delivery_delay": "Hola, mi pedido {n} llega tarde y no tengo noticias. ¿Qué ha pasado?",
        "damaged_item": "Hola, el artículo del pedido {n} llegó roto. ¿Qué puedo hacer?",
        "tracking_link": "Hola, ¿pueden enviarme otra vez el enlace de seguimiento del pedido {n}?",
    },
    "fr": {
        "order_status": "Bonjour, où est ma commande {n} ? Elle n'est toujours pas arrivée.",
        "refund_status": "Bonjour, quand le remboursement de ma commande {n} va-t-il arriver ? Je l'ai renvoyée la semaine dernière.",
        "cancel_order": "Bonjour, je voudrais annuler ma commande {n} avant l'expédition, s'il vous plaît.",
        "start_return": "Bonjour, comment puis-je retourner la commande {n} ? Elle ne me va pas.",
        "delivery_delay": "Bonjour, ma commande {n} a du retard et je n'ai aucune nouvelle. Que se passe-t-il ?",
        "damaged_item": "Bonjour, l'article de la commande {n} est arrivé cassé. Que dois-je faire ?",
        "tracking_link": "Bonjour, pouvez-vous me renvoyer le lien de suivi de la commande {n} ?",
    },
    "de": {
        "order_status": "Hallo, wo ist meine Bestellung {n}? Sie ist noch nicht angekommen.",
        "refund_status": "Hallo, wann kommt die Rückerstattung für meine Bestellung {n}? Ich habe sie letzte Woche zurückgeschickt.",
        "cancel_order": "Hallo, ich möchte meine Bestellung {n} stornieren, bevor sie versendet wird.",
        "start_return": "Hallo, wie kann ich die Bestellung {n} zurückgeben? Sie passt mir nicht.",
        "delivery_delay": "Hallo, meine Bestellung {n} ist verspätet und ich habe keine Nachricht. Was ist passiert?",
        "damaged_item": "Hallo, der Artikel aus Bestellung {n} ist kaputt angekommen. Was kann ich tun?",
        "tracking_link": "Hallo, können Sie mir den Sendungslink für die Bestellung {n} noch einmal schicken?",
    },
    "pt": {
        "order_status": "Olá, onde está o meu pedido {n}? Ainda não chegou.",
        "refund_status": "Olá, quando chega o reembolso do meu pedido {n}? Devolvi há uma semana.",
        "cancel_order": "Olá, quero cancelar o meu pedido {n} antes do envio, por favor.",
        "start_return": "Olá, como posso devolver o pedido {n}? Não serviu.",
        "delivery_delay": "Olá, o meu pedido {n} está atrasado e não tenho notícias. O que aconteceu?",
        "damaged_item": "Olá, o artigo do pedido {n} chegou partido. O que posso fazer?",
        "tracking_link": "Olá, podem enviar outra vez o link de rastreio do pedido {n}?",
    },
}
AMBIGUOUS_TEXT = {
    "order_status": (
        "Hi, where is the thing I bought last week? I cannot find the email with the number.",
        "Hello, I ordered a lamp recently and have heard nothing. Where is it?",
        "Hey, my last order has not shown up and I do not know the order number. Can you look it up?",
        "Hi, I am waiting for a parcel from your shop and the tracking email got deleted. Where is it now?",
        "Hello, can you tell me where my most recent order is? I lost the confirmation.",
    ),
    "delivery_delay": (
        "The package I am waiting for is late and I have no idea what the number was.",
        "My delivery should have been here days ago, and I do not have the order number at hand.",
        "Still nothing from my last purchase, it is well past the date you gave me.",
        "The parcel I expected this week is not here and I cannot find any number for it.",
        "My recent order is overdue. Please check it for me, I do not have the number.",
    ),
    "cancel_order": (
        "I want to cancel what I bought yesterday, I do not have the number but it was a backpack.",
        "Please cancel my latest order, I ordered by mistake and cannot find the confirmation.",
        "Can you cancel the order I placed this morning? I do not know the number.",
        "I need to cancel the thing I bought last night before it ships.",
        "Please stop my most recent order, I do not have the order number.",
    ),
}
ANGRY_TEXT = {
    "damaged_item": "This is unacceptable. The item in order {n} arrived broken and nobody answered my first email about it.",
    "missing_item": "I am furious. An item is missing from order {n} and the tracking page told me it was complete.",
    "double_charge": "I was charged twice for order {n} and the parcel is late as well. Fix this now.",
}
AGENT_VOICE = "I noticed that you have placed more than one order. Could you please confirm which one you mean?"


def _estimate(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def _message(seed: Seed, index: int, numbers: list[str]) -> str:
    gap, intent = seed.gap, seed.intent
    if gap == "two_order_numbers":
        return TWO_FRAME[index % len(TWO_FRAME)].format(a=numbers[0], b=numbers[1], topic=TWO_TOPIC[intent])
    if gap == "rare_intent":
        name = intent.removeprefix("rare_")
        variant = 0 if int(seed.seed_id.split("-")[1]) < len(RARE) else 1
        return RARE_TEXT[name][variant]
    if gap == "policy_edge":
        number = f"{numbers[0]}" if numbers else ""
        tail = POLICY_TAIL[(index // 5) % len(POLICY_TAIL)]
        return POLICY_TEXT[intent].format(n=number) + tail
    if gap == "other_language":
        return LANGUAGE_TEXT[seed.language][intent].format(n=numbers[0])
    if gap == "ambiguous_order":
        return AMBIGUOUS_TEXT[intent][(int(seed.seed_id.split("-")[1]) // 3) % 5]
    return ANGRY_TEXT[intent].format(n=numbers[0])


def main() -> int:
    """Write tests/fixtures/cassettes/synthetic-v1.json."""
    prompt = parse_prompt_file("synthesize", (ROOT / "prompts/synthesize.v1.md").read_text(encoding="utf-8"))
    seeds = build_seeds()
    real = []
    for line in (ROOT / "data/raw/traces.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and isinstance(row.get("message"), str):
            real.append(row)
    reusable = [
        row["message"]
        for row in real
        if len(NUMBER.findall(row["message"])) == 1 and "@" not in row["message"] and row["message"].isascii()
    ]
    voice_slots = {6, 31, 52, 77, 98}
    twin_slots = [i for i, s in enumerate(seeds) if s.language == "en" and s.order_count == 1][2:80:30]
    entries: dict[str, dict[str, int | str]] = {}
    for index, seed in enumerate(seeds):
        numbers = NUMBER.findall(seed.instruction)
        if index in voice_slots:
            text = AGENT_VOICE
        elif index in twin_slots:
            text = reusable[index] + " Thanks!"
        else:
            text = _message(seed, index, numbers)
        request = ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instruction)
        entries[request_key(MODEL, request)] = {
            "text": text,
            "input_tokens": _estimate(prompt.text + seed.instruction),
            "output_tokens": _estimate(text),
        }
    document = {
        "provenance": "authored by scripts/author_synthetic_cassette.py from templates; not a model recording. "
        "Token counts are estimates (characters / 4). Replace with `make record-synthetic`.",
        "model": MODEL,
        "entries": entries,
    }
    target = ROOT / "tests/fixtures/cassettes/synthetic-v1.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} replies to {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
