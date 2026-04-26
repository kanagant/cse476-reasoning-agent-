import re

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


def solve_cot(question, llm, budget):
    prompt = build_cot_prompt(question)
    response = llm.call(prompt, budget, temperature=0.0, max_tokens=64)
    answer = extract_final_answer(response)
    return answer or "unknown"
