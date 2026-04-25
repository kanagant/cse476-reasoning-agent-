def build_baseline_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Reply with only the final answer. No explanation. "
        "For multiple choice write the answer text only, not the letter. "
        "For numbers write only the number or expression."
    )


def build_cot_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Think step by step, then on the last line write only the final answer. "
        "That line must have nothing else on it. No explanation on that line. "
        "For multiple choice write only the answer text, not A/B/C/D. "
        "For numbers write only the number or expression. No quotes or labels."
    )


def build_self_refine_draft_prompt(question: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        "Solve it and end with one line that is only your answer guess. "
        "No labels on that line."
    )


def build_self_refine_revision_prompt(question: str, draft: str) -> str:
    return (
        f"Question:\n{question}\n\n"
        f"Draft:\n{draft}\n\n"
        "If the draft is wrong or incomplete, solve again from scratch. "
        "Then reply with only the final answer. No explanation. "
        "For multiple choice write only the answer text, not the letter. "
        "For numbers write only the number or expression. "
        "Put it on the last line with nothing else on that line."
    )
