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

    if not budget.can_call():
        return "unknown"

    decide_prompt = (
        f"Question:\n{question}\n\n"
        "If this question can be helped by a calculator, extract a single valid Python arithmetic expression. "
        "Otherwise return NONE.\n\n"
        "Reply exactly as:\nEXPR: <expression or NONE>"
    )
    decide_text = llm.call(decide_prompt, budget, temperature=0.0, max_tokens=64)

    expr = None
    for line in decide_text.splitlines():
        if line.lower().startswith("expr:"):
            expr = line.split(":", 1)[1].strip()
            break

    tool_result = None
    if expr and expr.upper() != "NONE":
        tool_result = _try_eval_expression(expr)

    if tool_result is None:
        return "unknown"

    if not budget.can_call():
        return str(tool_result)[:4999]

    final_prompt = (
        f"Question:\n{question}\n\n"
        f"Tool result:\n{tool_result}\n\n"
        "Use the tool result to answer the question. "
        "Return only the final answer."
    )
    final_text = llm.call(final_prompt, budget, temperature=0.0, max_tokens=96)
    return extract_final_answer(final_text) or str(tool_result)[:4999]