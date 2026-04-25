# TODO
from __future__ import annotations
 
import json
import logging
import os
import re
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union
from src.methods.baseline import solve_baseline
from src.methods.cot import solve_cot 
from src.methods.self_consistency import solve_self_consistency
from src.router import solve_with_router
import requests
 
log = logging.getLogger(__name__)
 
PathLike = Union[str, os.PathLike]
 
@dataclass
class CallBudget:
    
    max_calls: int = 20
    used: int = 0
 
    def can_call(self, n: int = 1) -> bool:
        return self.used + n <= self.max_calls
 
    def consume(self, n: int = 1) -> None:
        self.used += n
 
 
@dataclass
class UsageStats:
   
    total_calls: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_errors: int = 0
    per_question_calls: List[int] = field(default_factory=list)
 
    def summary(self) -> str:
        n = len(self.per_question_calls) or 1
        avg = sum(self.per_question_calls) / n
        mx = max(self.per_question_calls, default=0)
        return (f"Questions: {n} | Calls: {self.total_calls} | "
                f"Avg/q: {avg:.2f} | Max/q: {mx} | "
                f"Errors: {self.total_errors} | "
                f"Tokens: {self.total_prompt_tokens}+{self.total_completion_tokens}")
 
 
DEFAULT_SYSTEM = (
    "You solve questions carefully. "
    "When you reply, give only the final answer unless the user asks for steps."
)
 
 
class LLM:
   
 
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://openai.rc.asu.edu/v1",
        model: str = "qwen3-30b-a3b-instruct-2507",
        timeout: int = 60,
        max_retries: int = 3,
        backoff_base: float = 1.5,
    ):
        self.api_key = api_key
        self.api_base = api_base.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.stats = UsageStats()
 
    def call(
        self,
        prompt: str,
        budget: CallBudget,
        *,
        system: str = DEFAULT_SYSTEM,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str:
        
        if not budget.can_call():
            return ""
 
        url = f"{self.api_base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
 
        budget.consume(1)
 
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(url, headers=headers, json=payload,
                                     timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    self.stats.total_calls += 1
                    self.stats.total_prompt_tokens += usage.get("prompt_tokens", 0)
                    self.stats.total_completion_tokens += usage.get("completion_tokens", 0)
                    return (text or "").strip()
 
                
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_base ** attempt)
                        continue
 
                log.warning("HTTP %s: %s", resp.status_code, resp.text[:200])
                self.stats.total_errors += 1
                return ""
 
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt < self.max_retries:
                    time.sleep(self.backoff_base ** attempt)
                    continue
                log.warning("Network error: %s", e)
            except (KeyError, json.JSONDecodeError) as e:
                log.warning("Malformed response: %s", e)
                self.stats.total_errors += 1
                return ""
 
        self.stats.total_errors += 1
        return ""
  
def clean_answer(text: str) -> str:
    if not text:
        return ""
    s = text.strip()
    s = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s).strip()
    low = s.lower()
    for prefix in ("final answer:", "answer:"):
        if low.startswith(prefix):
            s = s[len(prefix):].strip()
            low = s.lower()
    s = re.sub(r"^(?:\([A-Da-d]\)|[A-Da-d][\.\)])\s*", "", s).strip()
    while len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()
    s = " ".join(s.split())
    if len(s) > 1 and s.endswith("."):
        s = s[:-1].rstrip()
    return s[:4999]
 
 
def _mathish(q: str) -> bool:
    ql = q.lower()
    if any(x in ql for x in ("$", "\\", "sqrt", "frac", "^", "triangle", "equation")):
        return True
    if sum(c.isdigit() for c in q) >= 4:
        return True
    if sum(q.count(c) for c in "+-*/=") >= 3:
        return True
    return False


def agent_loop(question: str, llm: LLM, max_calls: int = 20) -> str:
    budget = CallBudget(max_calls=max_calls)

    if _mathish(question):
        answer = solve_self_consistency(question, llm, budget, num_samples=3)
    else:
        answer = solve_cot(question, llm, budget)
    answer = solve_with_router(question, llm, budget)

    llm.stats.per_question_calls.append(budget.used)
    return answer or "unknown"
 
def load_questions(path: PathLike) -> List[Dict[str, Any]]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list.")
    for i, item in enumerate(data):
        if not isinstance(item, dict) or "input" not in item:
            raise ValueError(f"Item {i} missing 'input' field.")
    return data
 
 
def load_answers(path: PathLike) -> List[Dict[str, str]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list.")
    return data
 
 
def save_answers_atomic(path: PathLike, answers: List[Dict[str, str]]) -> None:
   
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fp:
            json.dump(answers, fp, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
 
def validate_results(questions: List[Dict[str, Any]],
                     answers: List[Dict[str, Any]]) -> None:
    if len(questions) != len(answers):
        raise ValueError(f"Mismatched lengths: {len(questions)} vs {len(answers)}.")
    for idx, a in enumerate(answers):
        if "output" not in a:
            raise ValueError(f"Missing 'output' field at index {idx}.")
        out = a["output"]
        if not isinstance(out, str):
            raise TypeError(f"Non-string output at index {idx}: {type(out)}")
        if len(out) >= 5000:
            raise ValueError(f"Answer {idx} exceeds 5000 chars ({len(out)}).")
        if len(out) == 0:
            raise ValueError(f"Answer {idx} is empty.")
