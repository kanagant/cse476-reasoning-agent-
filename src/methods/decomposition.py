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


def solve_decomposition(question, llm, budget):
    plan_prompt = (
        f"Question:\n{question}\n\n"
        "Break this into 2 to 4 smaller subproblems that would help solve it.\n"
        "Return only the subproblems as a numbered list.\n"
        "Do not solve them yet."
    )
    plan_text = llm.call(plan_prompt, budget, temperature=0.0, max_tokens=160)
    steps = _clean_lines(plan_text)[:3]

    if not steps:
        return "unknown"

    solved_steps = []
    for step in steps:
        if not budget.can_call():
            break

        sub_prompt = (
            f"Original Question:\n{question}\n\n"
            f"Subproblem:\n{step}\n\n"
            "Solve this subproblem carefully.\n"
            "Return only the answer to this subproblem."
        )
        sub_answer = llm.call(sub_prompt, budget, temperature=0.0, max_tokens=160)
        sub_answer = extract_final_answer(sub_answer)
        solved_steps.append((step, sub_answer))

    if not solved_steps:
        return "unknown"

    if not budget.can_call():
        return solved_steps[-1][1] or "unknown"

    combine_prompt = (
        f"Question:\n{question}\n\n"
        f"Subproblem Answers:\n{solved_steps}\n\n"
        "Use the subproblem answers to solve the original question.\n"
        "Return only the final answer."
    )
    final_text = llm.call(combine_prompt, budget, temperature=0.0, max_tokens=160)
    return extract_final_answer(final_text) or "unknown"