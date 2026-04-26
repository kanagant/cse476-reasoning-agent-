from src.methods.baseline import solve_baseline
from src.methods.cot import solve_cot
from src.methods.decomposition import solve_decomposition
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
        "first", "then", "after", "before", "compare", "determine", "infer"
    ]
    planning_keywords = [
        "best approach", "strategy", "plan", "steps"
    ]

    if any(k in q for k in math_keywords) or looks_like_arithmetic(question):
        return "tool_augmented"

    if any(k in q for k in planning_keywords):
        return "tot"

    if any(k in q for k in multi_step_keywords) and len(question.split()) > 20:
        return "decomposition"

    if len(question.split()) < 10:
        return "baseline"

    return "cot"


def solve_with_router(question, llm, budget):
    route = classify_question(question)

    if route == "tool_augmented":
        answer = solve_tool_augmented(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        return solve_cot(question, llm, budget) if budget.can_call() else "unknown"

    if route == "tot":
        answer = solve_tot(question, llm, budget)
        return answer if answer and answer != "unknown" else "unknown"

    if route == "decomposition":
        answer = solve_decomposition(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        return solve_cot(question, llm, budget) if budget.can_call() else "unknown"

    if route == "baseline":
        answer = solve_baseline(question, llm, budget)
        if answer and answer != "unknown":
            return answer

    answer = solve_cot(question, llm, budget)
    return answer if answer and answer != "unknown" else "unknown"