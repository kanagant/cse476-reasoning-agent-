from src.prompts import (
    build_self_refine_draft_prompt,
    build_self_refine_revision_prompt,
)
from src.methods.cot import extract_final_answer


def solve_self_refine(question, llm, budget):
    draft_prompt = build_self_refine_draft_prompt(question)
    draft = llm.call(draft_prompt, budget, temperature=0.0, max_tokens=160)

    if not draft:
        return "unknown"

    if not budget.can_call():
        return extract_final_answer(draft) or "unknown"

    revise_prompt = build_self_refine_revision_prompt(question, draft)
    revised = llm.call(revise_prompt, budget, temperature=0.0, max_tokens=160)

    out = extract_final_answer(revised) if revised else ""
    if not out:
        out = extract_final_answer(draft)
    return out or "unknown"