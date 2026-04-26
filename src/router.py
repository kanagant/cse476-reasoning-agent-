import re

from src.methods.baseline import solve_baseline
from src.methods.cot import solve_cot
from src.methods.self_consistency import solve_self_consistency
from src.methods.self_refine import solve_self_refine
from src.methods.decomposition import solve_decomposition
from src.methods.react import solve_react
from src.methods.tot import solve_tot
from src.methods.tool_augmented import solve_tool_augmented
from src.methods.plan_and_solve import solve_plan_and_solve


def looks_like_arithmetic(question: str) -> bool:
    q = question.strip().lower()

    if q.startswith("what is ") or q.startswith("what's "):
        return True

    arithmetic_pattern = r"^[\s\d\+\-\*/%\.\(\)\^=]+$"
    if re.fullmatch(arithmetic_pattern, q):
        return True

    symbol_count = sum(ch in "+-*/%^=" for ch in q)
    digit_count = sum(ch.isdigit() for ch in q)
    return digit_count >= 2 and symbol_count >= 1


def is_multiple_choice(question: str) -> bool:
    q = question.lower()
    return (
        "(a)" in q or "(b)" in q or "(c)" in q or "(d)" in q
        or "\na." in q or "\nb." in q or "\nc." in q or "\nd." in q
    )


def classify_question(question: str) -> str:
    q = question.lower()
    words = len(question.split())

    planning_keywords = ["plan", "steps", "procedure", "how should", "approach"]
    strategy_keywords = ["best approach", "best strategy", "compare approaches", "which approach"]
    multi_step_keywords = ["first", "then", "after", "before", "compare", "analyze", "infer", "determine"]
    action_keywords = ["simulate", "trace", "sequence", "action", "follow", "state transition"]
    ambiguity_keywords = ["most likely", "best supported", "which of the following"]

    if looks_like_arithmetic(question):
        return "tool_augmented"

    if any(k in q for k in strategy_keywords):
        return "tot"

    if any(k in q for k in planning_keywords):
        return "plan_and_solve"

    if any(k in q for k in action_keywords):
        return "react"

    if (any(k in q for k in multi_step_keywords) and words > 18) or words > 45:
        return "decomposition"

    if is_multiple_choice(question) or any(k in q for k in ambiguity_keywords):
        return "self_consistency"

    if words < 10:
        return "baseline"

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
        if budget.can_call(2):
            return solve_self_refine(question, llm, budget)
        return "unknown"

    if route == "plan_and_solve":
        answer = solve_plan_and_solve(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call():
            return solve_cot(question, llm, budget)
        return "unknown"

    if route == "react":
        answer = solve_react(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call():
            return solve_cot(question, llm, budget)
        return "unknown"

    if route == "decomposition":
        answer = solve_decomposition(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call(2):
            return solve_self_refine(question, llm, budget)
        return "unknown"

    if route == "self_consistency":
        answer = solve_self_consistency(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call():
            return solve_cot(question, llm, budget)
        return "unknown"

    if route == "baseline":
        answer = solve_baseline(question, llm, budget)
        if answer and answer != "unknown":
            return answer
        if budget.can_call():
            return solve_cot(question, llm, budget)
        return "unknown"

    answer = solve_cot(question, llm, budget)
    if answer and answer != "unknown":
        return answer

    if budget.can_call(2):
        return solve_self_refine(question, llm, budget)

    return "unknown"