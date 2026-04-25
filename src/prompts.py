def build_baseline_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Give only the final answer."
    )


def build_cot_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Think through the problem carefully, but in your final response output only one line in exactly this format:\n"
        "Final Answer: <answer>\n"
        "Do not include any extra explanation."
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
