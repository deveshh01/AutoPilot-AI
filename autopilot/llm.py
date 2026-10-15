"""LLM provider selection.

Default is Ollama (local, free, no API key). If a cloud key is set it is used instead,
unless LLM_PROVIDER says otherwise.
"""
import os

from browser_use import ChatAnthropic, ChatGoogle, ChatOllama, ChatOpenAI

DEFAULT_OLLAMA_MODEL = "qwen2.5:7b"

CLOUD = {
    "openai": ("OPENAI_API_KEY", "gpt-4.1", ChatOpenAI),
    "anthropic": ("ANTHROPIC_API_KEY", "claude-sonnet-4-5", ChatAnthropic),
    "google": ("GOOGLE_API_KEY", "gemini-2.5-flash", ChatGoogle),  # free tier available
}
PROVIDERS = ["ollama", *CLOUD]


def detect_provider() -> str:
    for name, (key, _, _) in CLOUD.items():
        if os.getenv(key):
            return name
    return "ollama"


def supports_vision(provider: str) -> bool:
    # Small local text models can't read screenshots.
    return provider != "ollama" or bool(os.getenv("OLLAMA_VISION"))


def resolve_provider(provider: str | None = None) -> str:
    p = (provider or os.getenv("LLM_PROVIDER") or detect_provider()).lower()
    if p not in PROVIDERS:
        raise RuntimeError(f"Unknown provider '{p}'. Choose from: {', '.join(PROVIDERS)}")
    return p


def get_llm(provider: str | None = None, model: str | None = None):
    p = resolve_provider(provider)
    model = model or os.getenv("LLM_MODEL")
    if p == "ollama":
        return ChatOllama(
            model=model or DEFAULT_OLLAMA_MODEL,
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            timeout=300,
        )
    key_var, default_model, cls = CLOUD[p]
    if not os.getenv(key_var):
        raise RuntimeError(f"{key_var} is not set for provider '{p}'.")
    return cls(model=model or default_model)
