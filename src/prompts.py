def build_baseline_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Reply with only the final answer. No explanation. "
        "For multiple choice, write the answer text only, not the letter. "
        "For numbers, write only the number or expression."
    )


def build_cot_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Think step by step. Then on the last line write only the final answer. "
        "That last line must contain nothing except the answer. "
        "For multiple choice, write the answer text only, not the letter. "
        "For numbers, write only the number or expression."
    )


def build_self_refine_draft_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Solve the question carefully. "
        "On the last line, write only your answer guess."
    )


def build_self_refine_revision_prompt(question: str, draft: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        f"Draft answer:\n{draft}\n\n"
        "Check whether the draft is wrong, incomplete, or inconsistent. "
        "If needed, solve again from scratch. "
        "Then write only the final answer on the last line."
    )


def build_plan_and_solve_plan_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Create a short plan with 2 to 4 steps for solving this question. "
        "Return only the plan as a numbered list. Do not solve it yet."
    )


def build_plan_and_solve_solve_prompt(question: str, plan: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        f"Plan:\n{plan}\n\n"
        "Now solve the question using the plan. "
        "Write only the final answer on the last line."
    )