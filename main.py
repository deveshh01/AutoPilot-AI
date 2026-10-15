"""AutoPilot AI CLI.

  python main.py "Go to news.ycombinator.com and list the top 5 stories"
  python main.py --doctor         # verify browser setup (no API key needed)
  python main.py --serve          # web UI at http://localhost:5000
"""
import argparse
import asyncio
import sys

from dotenv import load_dotenv

import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
load_dotenv()


def main() -> int:
    ap = argparse.ArgumentParser(description="AI browser agent")
    ap.add_argument("task", nargs="?", help="what the agent should do, in plain English")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    ap.add_argument("--max-steps", type=int, default=25)
    ap.add_argument("--provider", choices=["ollama", "openai", "anthropic", "google"])
    ap.add_argument("--model")
    ap.add_argument("--doctor", action="store_true", help="self-test the browser setup")
    ap.add_argument("--serve", action="store_true", help="start the web UI")
    ap.add_argument("--port", type=int, default=5000)
    a = ap.parse_args()

    if a.doctor:
        from autopilot.doctor import main as doctor
        return doctor()
    if a.serve:
        from autopilot.web import app
        app.run(host="0.0.0.0", port=a.port)
        return 0
    if not a.task:
        ap.print_help()
        return 2

    from autopilot.agent import run_task
    try:
        r = asyncio.run(run_task(a.task, not a.headed, a.max_steps, a.provider, a.model))
    except Exception as e:
        if 'connect' in str(e).lower() or 'ollama' in str(e).lower():
            e = f"{e}\nIs Ollama running? Start it and run: ollama pull qwen2.5:7b"
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(f"\n=== Result (success={r.success}, steps={r.steps}) ===\n{r.result}")
    return 0 if r.success else 1


if __name__ == "__main__":
    sys.exit(main())
