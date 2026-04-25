import re
from src.methods.cot import extract_final_answer


def _try_eval_expression(expr: str):
    try:
        expr = expr.replace("^", "**")
        allowed = {"__builtins__": {}}
        value = eval(expr, allowed, {})
        return str(value)
    except Exception:
        return None


def _maybe_extract_math_expression(question: str):
    q = question.strip()
    patterns = [
        r"what is (.+)",
        r"calculate (.+)",
        r"compute (.+)",
        r"evaluate (.+)",
    ]
    for pat in patterns:
        m = re.search(pat, q, flags=re.IGNORECASE)
        if m:
            expr = m.group(1).strip().rstrip("?.!")
            return expr
    return None


def solve_tool_augmented(question, llm, budget):
    expr = _maybe_extract_math_expression(question)
    if expr:
        result = _try_eval_expression(expr)
        if result is not None:
            return result[:4999]

    decide_prompt = (
        f"Question:\n{question}\n\n"
        "Would a calculator help?\n"
        "Return exactly:\n"
        "TOOL: yes/no\n"
        "EXPR: <expression or NONE>"
    )
    decide_text = llm.call(decide_prompt, budget, temperature=0.0, max_tokens=128)

    use_tool = False
    expr = None

    for line in decide_text.splitlines():
        low = line.lower().strip()
        if low.startswith("tool:"):
            use_tool = low.split(":", 1)[1].strip() == "yes"
        elif low.startswith("expr:"):
            expr = line.split(":", 1)[1].strip()

    tool_result = None
    if use_tool and expr and expr.upper() != "NONE":
        tool_result = _try_eval_expression(expr)

    if tool_result is not None:
        if not budget.can_call():
            return tool_result[:4999]

        final_prompt = (
            f"Question:\n{question}\n\n"
            f"Tool Result:\n{tool_result}\n\n"
            "Use the tool result to answer the question.\n"
            "Return only the final answer."
        )
        final_text = llm.call(final_prompt, budget, temperature=0.0, max_tokens=128)
        return extract_final_answer(final_text) or tool_result[:4999]

    if not budget.can_call():
        return "unknown"

    fallback_prompt = (
        f"Question:\n{question}\n\n"
        "Solve it carefully.\n"
        "Return only the final answer."
    )
    fallback_text = llm.call(fallback_prompt, budget, temperature=0.0, max_tokens=256)
    return extract_final_answer(fallback_text) or "unknown"