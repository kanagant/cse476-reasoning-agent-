import re

from src.methods.cot import extract_final_answer


def _extract_action(text: str) -> str:
    if not text:
        return ""
    match = re.search(r"ACTION:\s*(.*)", text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _safe_calculate(expr: str):
    try:
        expr = expr.replace("^", "**")
        allowed = {"__builtins__": {}}
        value = eval(expr, allowed, {})
        return str(value)
    except Exception:
        return "ERROR"


def solve_react(question, llm, budget, max_steps=3):
    scratchpad = []

    for _ in range(max_steps):
        if not budget.can_call():
            break

        prompt = (
            "You are solving a question step by step.\n\n"
            "Allowed actions:\n"
            "1. CALCULATE[expression]\n"
            "2. FINISH[answer]\n\n"
            "Reply in exactly this format:\n"
            "THOUGHT: <short thought>\n"
            "ACTION: <one action>\n\n"
            f"Question:\n{question}\n\n"
            f"Scratchpad:\n{chr(10).join(scratchpad) if scratchpad else 'None'}"
        )

        response = llm.call(prompt, budget, temperature=0.0, max_tokens=160)
        action = _extract_action(response)
        scratchpad.append(response.strip())

        if action.upper().startswith("CALCULATE[") and action.endswith("]"):
            expr = action[len("CALCULATE["):-1].strip()
            obs = _safe_calculate(expr)
            scratchpad.append(f"OBSERVATION: {obs}")
            continue

        if action.upper().startswith("FINISH[") and action.endswith("]"):
            answer = action[len("FINISH["):-1].strip()
            return extract_final_answer(answer) or "unknown"

        scratchpad.append("OBSERVATION: Invalid action")

    if not budget.can_call():
        return "unknown"

    final_prompt = (
        f"Question:\n{question}\n\n"
        f"Reasoning Trace:\n{chr(10).join(scratchpad)}\n\n"
        "Give only the final answer."
    )
    final_text = llm.call(final_prompt, budget, temperature=0.0, max_tokens=160)
    return extract_final_answer(final_text) or "unknown"