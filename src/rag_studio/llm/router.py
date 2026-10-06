"""Chooses the OpenRouter model id for a model label sent by the UI."""
from rag_studio.core.config import Settings


def resolve_model(label: str, settings: Settings) -> str:
    if "/" in label:  # already an OpenRouter id such as "vendor/model"
        return label
    if "strong" in label.lower():
        return settings.strong_model
    return settings.fast_model