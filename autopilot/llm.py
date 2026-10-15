"""LLM provider selection. Picks a provider from env vars or an explicit name."""
import os

from browser_use import ChatAnthropic, ChatGoogle, ChatOpenAI

PROVIDERS = {
    "openai": ("OPENAI_API_KEY", "gpt-4.1", ChatOpenAI),
    "anthropic": ("ANTHROPIC_API_KEY", "claude-sonnet-4-5", ChatAnthropic),
    "google": ("GOOGLE_API_KEY", "gemini-2.5-flash", ChatGoogle),
}


def detect_provider() -> str | None:
    for name, (key, _, _) in PROVIDERS.items():
        if os.getenv(key):
            return name
    return None


def get_llm(provider: str | None = None, model: str | None = None):
    provider = (provider or os.getenv("LLM_PROVIDER") or detect_provider() or "").lower()
    if provider not in PROVIDERS:
        raise RuntimeError(
            "No LLM configured. Set one of OPENAI_API_KEY, ANTHROPIC_API_KEY or "
            "GOOGLE_API_KEY in .env (see .env.example)."
        )
    key_var, default_model, cls = PROVIDERS[provider]
    if not os.getenv(key_var):
        raise RuntimeError(f"{key_var} is not set for provider '{provider}'.")
    return cls(model=model or os.getenv("LLM_MODEL") or default_model)
