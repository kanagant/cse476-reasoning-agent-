from src.prompts import build_baseline_prompt
from src.methods.cot import clean_local_answer


def solve_baseline(question, llm, budget):
    prompt = build_baseline_prompt(question)
    response = llm.call(prompt, budget, temperature=0.0, max_tokens=128)
    if not response:
        return "unknown"

    lines = [ln.strip() for ln in response.splitlines() if ln.strip()]
    chunk = lines[-1] if lines else response.strip()
    return clean_local_answer(chunk) or "unknown"