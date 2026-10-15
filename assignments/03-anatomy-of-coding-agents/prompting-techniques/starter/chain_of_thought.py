"""Chain-of-thought — refund eligibility.

Task: given the refund policy and an order, decide YES or NO. Use chain-of-thought
so the model reasons step by step, but make the FINAL line exactly `DECISION: YES`
or `DECISION: NO` so it can be graded.

Only edit YOUR_SYSTEM_PROMPT.
Run:  python chain_of_thought.py
"""
from ollama import chat

MODEL = "llama3.1:8b"

POLICY = """Refund policy:
- Refunds allowed within 30 days of purchase.
- Item must be unused / in original condition.
- Final-sale items are never refundable.
"""

# Evaluate the policy criteria in order and keep the required decision line machine-readable.
YOUR_SYSTEM_PROMPT = """Evaluate refund eligibility using every rule in the policy below.
Check whether the purchase is within 30 days, the item is unused and in original condition, and the item is not final sale. A refund is eligible only when all conditions pass.
Briefly state the result of each relevant check. End with exactly one final line: DECISION: YES or DECISION: NO. Do not put anything after that final line."""

CASES = [
    ("Bought 10 days ago, unused, not final sale.", "YES"),
    ("Bought 45 days ago, unused.", "NO"),
    ("Bought 5 days ago but it was a final-sale item.", "NO"),
]


def decide(system_prompt: str, order: str) -> str:
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt + "\n" + POLICY},
            {"role": "user", "content": order},
        ],
        options={"temperature": 0.0},
    )
    text = resp.message.content.strip()
    last = text.splitlines()[-1].upper() if text else ""
    return "YES" if "DECISION: YES" in last else "NO" if "DECISION: NO" in last else "?"


def run() -> bool:
    passed = 0
    for order, expected in CASES:
        got = decide(YOUR_SYSTEM_PROMPT, order)
        ok = got == expected
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {order!r} -> {got}, expected {expected}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
