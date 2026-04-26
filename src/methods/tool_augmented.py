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

    return "unknown"