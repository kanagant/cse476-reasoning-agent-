from collections import Counter
from src.prompts import build_cot_prompt


def clean_local_answer(text: str) -> str:
    if not text:
        return ""
    s = text.strip()

    if s.startswith("```") and s.endswith("```"):
        lines = s.splitlines()
        if len(lines) >= 3:
            s = "\n".join(lines[1:-1]).strip()

    lower = s.lower()
    if lower.startswith("final answer:"):
        s = s[len("final answer:"):].strip()
    elif lower.startswith("answer:"):
        s = s[len("answer:"):].strip()

    return s[:4999]


def extract_final_answer(text: str) -> str:
    if not text:
        return ""
    marker = "Final Answer:"
    if marker in text:
        return clean_local_answer(text.split(marker)[-1].strip())
    return clean_local_answer(text)


def normalize_answer(text: str) -> str:
    return extract_final_answer(text).strip().lower()


def solve_self_consistency(question, llm, budget, num_samples=3):
    responses = []

    for _ in range(num_samples):
        prompt = build_cot_prompt(question)
        response = llm.call(prompt, budget, temperature=0.7, max_tokens=512)
        if response:
            responses.append(response)

    if not responses:
        return "unknown"

    normalized = [normalize_answer(r) for r in responses if normalize_answer(r)]
    if not normalized:
        return extract_final_answer(responses[0])

    winner = Counter(normalized).most_common(1)[0][0]

    for r in responses:
        if normalize_answer(r) == winner:
            return extract_final_answer(r)

    return extract_final_answer(responses[0])
