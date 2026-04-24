from src.prompts import (
    build_self_refine_draft_prompt,
    build_self_refine_revision_prompt,
)


def clean_local_answer(text: str) -> str:
    if not text:
        return ""
    s = text.strip()

    if s.startswith("```") and s.endswith("```"):
        lines = s.splitlines()
        if len(lines) >= 3:
            s = "\n".join(lines[1:-1]).strip()

    lower = s.lower()
    if lower.startswith("final answer:"):
        s = s[len("final answer:"):].strip()
    elif lower.startswith("answer:"):
        s = s[len("answer:"):].strip()

    return s[:4999]


def solve_self_refine(question, llm, budget):
    draft_prompt = build_self_refine_draft_prompt(question)
    draft = llm.call(draft_prompt, budget, temperature=0.0, max_tokens=512)

    if not draft:
        return "unknown"

    revise_prompt = build_self_refine_revision_prompt(question, draft)
    revised = llm.call(revise_prompt, budget, temperature=0.0, max_tokens=512)

    return clean_local_answer(revised) or clean_local_answer(draft) or "unknown"
