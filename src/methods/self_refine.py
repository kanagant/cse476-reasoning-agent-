import re

from src.prompts import (
    build_self_refine_draft_prompt,
    build_self_refine_revision_prompt,
)

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


def solve_self_refine(question, llm, budget):
    draft_prompt = build_self_refine_draft_prompt(question)
    draft = llm.call(draft_prompt, budget, temperature=0.0, max_tokens=512)

    if not draft:
        return "unknown"

    revise_prompt = build_self_refine_revision_prompt(question, draft)
    revised = llm.call(revise_prompt, budget, temperature=0.0, max_tokens=512)

    out = extract_final_answer(revised) if revised else ""
    if not out:
        out = extract_final_answer(draft)
    return out or "unknown"
