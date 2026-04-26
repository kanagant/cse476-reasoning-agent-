from collections import Counter

from src.prompts import build_cot_prompt
from src.methods.cot import extract_final_answer


def normalize_answer(text: str) -> str:
    return extract_final_answer(text).strip().lower()


def solve_self_consistency(question, llm, budget, num_samples=3):
    responses = []

    for _ in range(num_samples):
        if not budget.can_call():
            break
        prompt = build_cot_prompt(question)
        response = llm.call(prompt, budget, temperature=0.5, max_tokens=192)
        if response:
            responses.append(response)

    if not responses:
        return "unknown"

    keys = [normalize_answer(r) for r in responses]
    keys = [k for k in keys if k]

    if not keys:
        return extract_final_answer(responses[0]) or "unknown"

    winner = Counter(keys).most_common(1)[0][0]

    for r in responses:
        if normalize_answer(r) == winner:
            return extract_final_answer(r) or "unknown"

    return extract_final_answer(responses[0]) or "unknown"