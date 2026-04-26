import re

from src.prompts import build_baseline_prompt

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


def solve_baseline(question, llm, budget):
    prompt = build_baseline_prompt(question)
    response = response = llm.call(prompt, budget, temperature=0.0, max_tokens=48)
    if not response:
        return "unknown"
    lines = [ln.strip() for ln in response.splitlines() if ln.strip()]
    chunk = lines[-1] if lines else response.strip()
    return clean_local_answer(chunk) or "unknown"
