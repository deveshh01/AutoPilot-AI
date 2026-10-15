# AutoPilot AI

An AI browser agent: describe a task in plain English and an LLM drives a real
browser (open pages, click, fill forms, extract data) via the
[Browser Use](https://github.com/browser-use/browser-use) framework.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add one API key (OpenAI / Anthropic / Google)
```
If Chromium isn't installed, run `uvx playwright install chromium` or set `CHROME_PATH`.

## Usage
```bash
python main.py --doctor                     # verify browser works (no key needed)
python main.py "Go to news.ycombinator.com and list the top 5 stories"
python main.py --headed "Search Wikipedia for Alan Turing and summarize"
python main.py --serve                      # web UI on http://localhost:5000
```
