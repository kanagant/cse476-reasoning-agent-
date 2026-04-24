# cse476-reasoning-agent

## Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-sol-key"
```

## Run
```bash
python generate_answer.py --limit 3 --verbose   # smoke test
python generate_answer.py --verbose              # full run
```

## Files
- `agent.py` — LLM wrapper, budget, agent loop
- `generate_answer.py` — entrypoint, reads test data, writes answers JSON