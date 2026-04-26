from src.prompts import (
    build_plan_and_solve_plan_prompt,
    build_plan_and_solve_solve_prompt,
)
from src.methods.cot import extract_final_answer


def solve_plan_and_solve(question, llm, budget):
    plan_prompt = build_plan_and_solve_plan_prompt(question)
    plan = llm.call(plan_prompt, budget, temperature=0.0, max_tokens=128)

    if not plan:
        return "unknown"

    if not budget.can_call():
        return "unknown"

    solve_prompt = build_plan_and_solve_solve_prompt(question, plan)
    response = llm.call(solve_prompt, budget, temperature=0.0, max_tokens=192)
    answer = extract_final_answer(response)

    return answer or "unknown"