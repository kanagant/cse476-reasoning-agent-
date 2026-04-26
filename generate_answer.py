#!/usr/bin/env python3
"""
Generate a placeholder answer file that matches the expected auto-grader format.

Replace the placeholder logic inside `build_answers()` with your own agent loop
before submitting so the ``output`` fields contain your real predictions.

Reads the input questions from cse_476_final_project_test_data.json and writes
an answers JSON file where each entry contains a string under the "output" key.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Tuple

from src.agent import (
    LLM,
    agent_loop,
    load_questions,
    load_answers,
    save_answers_atomic,
    validate_results,
)

INPUT_PATH = Path("cse_476_final_project_test_data.json")
OUTPUT_PATH = Path("cse_476_final_project_answers.json")

CHECKPOINT_EVERY = 10
MAX_CALLS_PER_QUESTION = 20

def get_config() -> Tuple[str, str, str]:
    """Read API credentials from env; prompt for the key if missing."""
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except ImportError:
        pass

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = getpass("Enter SOL/Voyager API key: ").strip()
    if not api_key:
        raise SystemExit("No API key provided.")

    api_base = os.getenv("API_BASE", "https://openai.rc.asu.edu/v1")
    model = os.getenv("MODEL_NAME", "qwen3-30b-a3b-instruct-2507")
    return api_key, api_base, model


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the reasoning agent on the test set.")
    p.add_argument("--input", type=Path, default=INPUT_PATH)
    p.add_argument("--output", type=Path, default=OUTPUT_PATH)
    p.add_argument("--limit", type=int, default=None,
                   help="Only run the first N questions (smoke tests).")
    p.add_argument("--restart", action="store_true",
                   help="Ignore any existing answers file and start over.")
    p.add_argument("--max-calls", type=int, default=MAX_CALLS_PER_QUESTION)
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    api_key, api_base, model = get_config()
    llm = LLM(api_key=api_key, api_base=api_base, model=model)

    questions = load_questions(args.input)
    if args.limit is not None:
        questions = questions[: args.limit]
    print(f"Loaded {len(questions)} questions from {args.input}")

    # Resume support: pick up where the last run left off.
    if args.restart or not args.output.exists():
        answers: list = []
    else:
        answers = load_answers(args.output)[: len(questions)]
        if answers:
            print(f"Resuming from checkpoint: {len(answers)} already saved.")

    try:
        for idx in range(len(answers), len(questions)):
            q = str(questions[idx].get("input", ""))
            answers.append({"output": agent_loop(q, llm, max_calls=args.max_calls)})

            if (idx + 1) % CHECKPOINT_EVERY == 0:
                save_answers_atomic(args.output, answers)
                if args.verbose:
                    print(f"[{idx + 1}/{len(questions)}] checkpoint | {llm.stats.summary()}")

    except KeyboardInterrupt:
        save_answers_atomic(args.output, answers)
        print(f"\nInterrupted. Saved {len(answers)} answers to {args.output}. "
              "Re-run to resume.", file=sys.stderr)
        raise

    save_answers_atomic(args.output, answers)
    validate_results(questions, load_answers(args.output))

    print(f"\nWrote {len(answers)} answers to {args.output}.")
    print(f"Final usage: {llm.stats.summary()}")


if __name__ == "__main__":
    main()