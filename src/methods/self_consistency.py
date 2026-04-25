import re
from collections import Counter

from src.prompts import build_cot_prompt

_MC_START = re.compile(r"^(?:\([A-Da-d]\)|[A-Da-d][\.\)])\s*")


def clean_local_answer(text: str) -> str:
    if not text:
        return ""
    s = text.strip()
    s = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s).strip()

    low = s.lower()
    if low.startswith("final answer:"):
        s = s[len("final answer:"):].strip()
        low = s.lower()
    if low.startswith("answer:"):
        s = s[len("answer:"):].strip()

    s = _MC_START.sub("", s).strip()
    while len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()

    s = " ".join(s.split())
    if len(s) > 1 and s.endswith("."):
        s = s[:-1].rstrip()

    return s[:4999]


def extract_final_answer(text: str) -> str:
    if not text:
        return ""
    low = text.lower()
    key = "final answer:"
    if key in low:
        i = low.rfind(key)
        text = text[i + len(key):].strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    return clean_local_answer(lines[-1])


def normalize_answer(text: str) -> str:
    return extract_final_answer(text).strip().lower()


def solve_self_consistency(question, llm, budget, num_samples=3):
    responses = []

    for _ in range(num_samples):
        prompt = build_cot_prompt(question)
        response = llm.call(prompt, budget, temperature=0.7, max_tokens=512)
        if response:
            responses.append(response)

    if not responses:
        return "unknown"

    keys = [normalize_answer(r) for r in responses]
    keys = [k for k in keys if k]
    if not keys:
        return extract_final_answer(responses[0]) or "unknown"

    winner = Counter(keys).most_common(1)[0][0]

    for r in responses:
        if normalize_answer(r) == winner:
            return extract_final_answer(r) or "unknown"

    return extract_final_answer(responses[0]) or "unknown"
