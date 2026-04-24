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


def solve_cot(question, llm, budget):
    prompt = build_cot_prompt(question)
    response = llm.call(prompt, budget, temperature=0.0, max_tokens=512)
    answer = extract_final_answer(response)
    return answer or "unknown"
