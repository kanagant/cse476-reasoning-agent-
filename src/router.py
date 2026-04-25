from src.methods.baseline import solve_baseline
from src.methods.cot import solve_cot
from src.methods.self_consistency import solve_self_consistency
from src.methods.self_refine import solve_self_refine
from src.methods.decomposition import solve_decomposition
from src.methods.react import solve_react
from src.methods.tot import solve_tot
from src.methods.tool_augmented import solve_tool_augmented
import re


def looks_like_arithmetic(question: str) -> bool:
    q = question.strip().lower()

    if q.startswith("what is ") or q.startswith("what's "):
        return True

    arithmetic_pattern = r"^[\s\d\+\-\*/%\.\(\)\^=]+$"
    if re.fullmatch(arithmetic_pattern, q):
        return True

    symbol_count = sum(ch in "+-*/%^=" for ch in q)
    digit_count = sum(ch.isdigit() for ch in q)
    if digit_count >= 2 and symbol_count >= 1:
        return True

    return False


def classify_question(question: str) -> str:
    q = question.lower()

    math_keywords = [
        "calculate", "compute", "evaluate", "equation", "probability",
        "percent", "percentage", "sum", "difference", "product", "average",
        "ratio", "fraction", "multiply", "divide", "subtract", "add"
    ]
    multi_step_keywords = [
        "first", "then", "after", "before", "explain", "analyze",
        "compare", "determine", "infer", "why"
    ]
    planning_keywords = [
        "best approach", "strategy", "plan", "steps"
    ]

    if any(k in q for k in math_keywords) or looks_like_arithmetic(question):
        return "tool_augmented"

    if any(k in q for k in planning_keywords):
        return "tot"

    if len(question.split()) > 35 or any(k in q for k in multi_step_keywords):
        return "decomposition"

    return "cot"


def solve_with_router(question, llm, budget):
    route = classify_question(question)

    if route == "tool_augmented":
        answer = solve_tool_augmented(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call():
            return solve_cot(question, llm, budget)
        return "unknown"

    if route == "tot":
        answer = solve_tot(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call():
            return solve_react(question, llm, budget)
        return "unknown"

    if route == "decomposition":
        answer = solve_decomposition(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call():
            return solve_self_refine(question, llm, budget)
        return "unknown"

    answer = solve_cot(question, llm, budget)
    if answer and answer != "unknown":
        return answer

    if budget.can_call(2):
        return solve_self_consistency(question, llm, budget)

    if budget.can_call():
        return solve_baseline(question, llm, budget)

    return "unknown"