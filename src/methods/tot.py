from src.methods.cot import extract_final_answer


def _clean_lines(text: str):
    if not text:
        return []
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("- "):
            s = s[2:].strip()
        elif s.startswith("* "):
            s = s[2:].strip()
        elif "." in s and s.split(".", 1)[0].isdigit():
            s = s.split(".", 1)[1].strip()
        if s:
            lines.append(s)
    return lines


def solve_tot(question, llm, budget, branches=3):
    branch_prompt = (
        f"Question:\n{question}\n\n"
        f"Generate {branches} different short reasoning approaches for solving this question.\n"
        "Do not fully solve it.\n"
        "Return them as a numbered list."
    )
    branch_text = llm.call(branch_prompt, budget, temperature=0.3, max_tokens=256)
    candidates = _clean_lines(branch_text)[:branches]

    if not candidates:
        return "unknown"

    if not budget.can_call():
        return candidates[0]

    select_prompt = (
        f"Question:\n{question}\n\n"
        f"Candidate Approaches:\n{candidates}\n\n"
        "Choose the best approach.\n"
        "Return exactly:\n"
        "BEST: <number>"
    )
    select_text = llm.call(select_prompt, budget, temperature=0.0, max_tokens=64)

    best_idx = 0
    for line in select_text.splitlines():
        if line.lower().startswith("best:"):
            val = line.split(":", 1)[1].strip()
            if val.isdigit():
                best_idx = max(0, min(len(candidates) - 1, int(val) - 1))
            break

    best_plan = candidates[best_idx]

    if not budget.can_call():
        return best_plan

    solve_prompt = (
        f"Question:\n{question}\n\n"
        f"Use this reasoning approach:\n{best_plan}\n\n"
        "Solve carefully.\n"
        "Return only the final answer."
    )
    final_text = llm.call(solve_prompt, budget, temperature=0.0, max_tokens=256)
    return extract_final_answer(final_text) or "unknown"