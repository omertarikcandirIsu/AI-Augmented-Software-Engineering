"""RAG — policy-grounded answers.

Task: answer a customer question using ONLY the retrieved help-center text. If the
answer isn't in the docs, the model must say it doesn't know (don't hallucinate).

Fill in YOUR_SYSTEM_PROMPT and YOUR_RETRIEVER.
Run:  python rag.py
"""
import os

from ollama import chat

MODEL = "llama3.1:8b"
DATA = os.path.join(os.path.dirname(__file__), "data", "help_center.txt")


def load_chunks() -> list[str]:
    with open(DATA, encoding="utf-8") as f:
        # one chunk per non-empty line
        return [line.strip() for line in f if line.strip()]


def YOUR_RETRIEVER(question: str, chunks: list[str]) -> list[str]:
    stop_words = {
        "a", "an", "and", "are", "do", "does", "for", "how", "i", "in",
        "is", "it", "me", "my", "of", "the", "to", "we", "what", "you", "your",
    }
    variants = {
        "internationally": "international",
        "items": "item",
        "returns": "return",
        "shipping": "ship",
        "shipped": "ship",
    }

    def terms(text: str) -> set[str]:
        words = (word.strip(".,?!:;()[]{}\"'").lower() for word in text.split())
        return {
            variants.get(word, word)
            for word in words
            if word and word not in stop_words
        }

    question_terms = terms(question)
    ranked = []
    for index, chunk in enumerate(chunks):
        score = len(question_terms & terms(chunk))
        if score:
            ranked.append((score, index, chunk))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [chunk for _, _, chunk in ranked]


YOUR_SYSTEM_PROMPT = """Answer the customer's question using only the supplied help-center context. Do not add outside facts or guesses. If the context does not contain the answer, politely say exactly: I don't know based on the available information. Keep the answer concise and faithful to the context."""

CASES = [
    ("How long do I have to return an item?", ["30 days"]),
    ("Do you ship internationally?", ["international"]),
    ("What's your CEO's home address?", ["don't know", "do not know", "not sure", "cannot"]),
]


def answer(question: str) -> str:
    context = "\n".join(YOUR_RETRIEVER(question, load_chunks()))
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": YOUR_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        options={"temperature": 0.0},
    )
    return resp.message.content.strip().lower()


def run() -> bool:
    passed = 0
    for question, needles in CASES:
        got = answer(question)
        ok = any(n.lower() in got for n in needles)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {question!r} -> {got[:80]!r}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
