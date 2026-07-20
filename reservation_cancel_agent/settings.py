"""Runtime settings for the reservation cancellation agent."""

from __future__ import annotations

import os

DEFAULT_OLLAMA_API_BASE = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "gemma4:12b"
OLLAMA_PROVIDER = "ollama_chat"


def get_ollama_api_base() -> str:
    """Return the Ollama base URL used by LiteLLM."""
    return os.environ.get("OLLAMA_API_BASE", DEFAULT_OLLAMA_API_BASE)


def get_ollama_model_name() -> str:
    """Return the local Ollama model name, without the LiteLLM provider prefix."""
    return os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_litellm_model() -> str:
    """Return the LiteLLM model string ADK expects for Ollama chat models."""
    return f"{OLLAMA_PROVIDER}/{get_ollama_model_name()}"


def ensure_ollama_env() -> None:
    """Set a local default so LiteLLM routes auxiliary calls to Ollama."""
    os.environ.setdefault("OLLAMA_API_BASE", DEFAULT_OLLAMA_API_BASE)
