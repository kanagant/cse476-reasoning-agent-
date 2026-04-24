def build_baseline_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Give only the final answer."
    )


def build_cot_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Think step by step, then end with:\n"
        "Final Answer: <answer>"
    )


def build_self_refine_draft_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Solve carefully and give your best answer."
    )


def build_self_refine_revision_prompt(question: str, draft: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        f"Draft Answer:\n{draft}\n\n"
        "Check the draft for mistakes and return an improved final answer only."
    )
