# CSE 476 Final Project: General-Purpose Reasoning Agent

GitHub Repository: [https://github.com/kanagant/cse476-reasoning-agent](https://github.com/kanagant/cse476-reasoning-agent-)

## Project Overview

This project builds a general-purpose reasoning agent using only the provided SOL LLM API.

The agent is designed to answer a large test set while staying within the project rule of at most 20 LLM calls per question.

The system includes these inference-time reasoning techniques:

* Chain of Thought (CoT)
* Self-Consistency
* Self-Refine
* Decomposition
* Tree of Thought
* ReAct
* Tool-Augmented Reasoning
* Plan-and-Solve

## Requirements

* Python 3.10 or newer
* Access to ASU SOL / Research Compute
* Cisco VPN if you are off campus
* A valid SOL API key

## Installation

Clone the repository:

```bash
git clone https://github.com/kanagant/cse476-reasoning-agent.git
cd cse476-reasoning-agent
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the project root and add:

```env
OPENAI_API_KEY=your_key_here
API_BASE=https://openai.rc.asu.edu/v1
MODEL_NAME=qwen3-30b-a3b-instruct-2507
```

Important:

* Do not upload your real `.env` file to GitHub
* Connect to Cisco VPN if needed before running the code

## Main Files

* `generate_answer.py` - runs the full pipeline and creates final answers
* `src/agent.py` - main LLM wrapper and agent loop
* `src/router.py` - method selection logic
* `src/prompts.py` - prompts used by the reasoning methods
* `src/methods/` - reasoning technique implementations
* `dev_eval.py` - small development evaluation script

## How to Run

Small test run:

```bash
python3 generate_answer.py --limit 25 --restart --verbose
```

Full run:

```bash
python3 generate_answer.py --restart --verbose
```

## Output

The final output file is:

```text
cse_476_final_project_answers.json
```

This file contains one `"output"` entry for each question in the test set.

## Reproducing Results

To reproduce the results:

1. Install dependencies
2. Add your SOL API key to `.env`
3. Connect to VPN if needed
4. Run the project using the commands above

## Individual Contributions

### Member 1: Aishwarya

* Set up SOL API integration
* Built the shared pipeline and agent wrapper
* Added budget tracking and final JSON output handling
* Integrated all team code into the final project structure

### Member 2: Krutika Anaganti

* Implemented baseline prompting
* Implemented Chain of Thought (CoT)
* Implemented Self-Refine
* Implemented Self-Consistency
* Helped with prompt formatting and answer cleaning
* Ran small development tests to compare reasoning methods

### Member 3: Siri Poluri

* Implemented Decomposition
* Implemented Tree of Thought
* Implemented ReAct
* Implemented Tool-Augmented Reasoning
* Worked on routing logic and evaluation support

## Notes

* The project uses only the provided SOL API
* The code is written to stay within the call budget limit
* Runtime may vary depending on SOL availability and network speed
