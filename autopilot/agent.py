"""Core runner: natural-language task -> browser actions."""
import os
from dataclasses import dataclass, field

from browser_use import Agent, Browser

from .llm import get_llm, resolve_provider, supports_vision


@dataclass
class RunResult:
    success: bool
    result: str
    urls: list[str] = field(default_factory=list)
    steps: int = 0
    errors: list[str] = field(default_factory=list)


def make_browser(headless: bool = True) -> Browser:
    return Browser(
        headless=headless,
        chromium_sandbox=False,  # required when running as root / in containers
        executable_path=os.getenv("CHROME_PATH") or None,
        keep_alive=False,
    )


async def run_task(task: str, headless: bool = True, max_steps: int = 25,
                   provider: str | None = None, model: str | None = None) -> RunResult:
    provider = resolve_provider(provider)
    llm = get_llm(provider, model)
    browser = make_browser(headless)
    local = provider == "ollama"
    extra = dict(
        llm_timeout=600, step_timeout=900,   # local models are slow
        flash_mode=True, use_thinking=False,  # short outputs = faster, fewer format errors
        max_actions_per_step=2, max_clickable_elements_length=8000,
    ) if local else {}
    agent = Agent(task=task, llm=llm, browser=browser, use_judge=False,
                  enable_planning=False, use_vision=supports_vision(provider), **extra)
    history = await agent.run(max_steps=max_steps)
    return RunResult(
        success=bool(history.is_successful()),
        result=history.final_result() or "",
        urls=[u for u in history.urls() if u],
        steps=history.number_of_steps(),
        errors=[str(e) for e in history.errors() if e],
    )
