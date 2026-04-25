import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from src.agent import LLM, CallBudget
from src.methods.baseline import solve_baseline
from src.methods.cot import solve_cot
from src.methods.self_refine import solve_self_refine
from src.methods.self_consistency import solve_self_consistency

DEV_PATH = Path("cse476_final_project_dev_data.json")

_MC_START = re.compile(r"^(?:\([A-Da-d]\)|[A-Da-d][\.\)])\s*")


def normalize(text: str) -> str:
    if text is None:
        return ""
    s = str(text).strip()
    s = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s).strip()

    s = s.lower()
    while True:
        t = s.strip()
        if t.startswith("final answer:"):
            s = t[len("final answer:"):].strip()
        elif t.startswith("answer:"):
            s = t[len("answer:"):].strip()
        else:
            break

    s = _MC_START.sub("", s).strip()
    s = s.replace(",", "")
    while len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()

    s = " ".join(s.split())
    if len(s) > 1 and s.endswith("."):
        s = s[:-1].rstrip()

    return s


def load_dev_data():
    with DEV_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_method(method_name, method_fn, data, llm):
    correct = 0
    total_calls = 0

    for i, item in enumerate(data, start=1):
        question = str(item.get("input", ""))
        gold = str(item.get("output", ""))

        budget = CallBudget(max_calls=20)
        pred = method_fn(question, llm, budget)

        total_calls += budget.used

        if normalize(pred) == normalize(gold):
            correct += 1

    total = len(data)
    acc = correct / total if total else 0.0
    avg_calls = total_calls / total if total else 0.0

    print(f"{method_name}:")
    print(f"  Correct: {correct}/{total}")
    print(f"  Accuracy: {acc:.3f}")
    print(f"  Avg calls/question: {avg_calls:.2f}")
    print()


def main():
    load_dotenv(dotenv_path=".env")

    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("API_BASE", "https://openai.rc.asu.edu/v1")
    model = os.getenv("MODEL_NAME", "qwen3-30b-a3b-instruct-2507")

    if not api_key:
        raise SystemExit("OPENAI_API_KEY not found in .env")

    llm = LLM(api_key=api_key, api_base=api_base, model=model)

    data = load_dev_data()[:10]

    methods = [
        ("baseline", solve_baseline),
        ("cot", solve_cot),
        ("self_refine", solve_self_refine),
        ("self_consistency", solve_self_consistency),
    ]

    print("Running dev comparison...\n")

    for name, fn in methods:
        evaluate_method(name, fn, data, llm)


if __name__ == "__main__":
    main()
