"""Turn a model's text reply into a validated Pydantic object."""
import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from rag_studio.domain.errors import InvalidLlmOutputError

T = TypeVar("T", bound=BaseModel)
_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)


def extract_json(text: str):
    """Parse JSON, tolerating code fences and text around the object."""
    cleaned = _FENCE.sub("", text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            pass
    raise InvalidLlmOutputError("The reply was not valid JSON.")


def _summarize(error: ValidationError) -> str:
    parts = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in error.errors()[:3]]
    return "The JSON did not match the expected shape (" + "; ".join(parts) + ")."


def parse_model(text: str, model_class: type[T]) -> T:
    data = extract_json(text)
    try:
        return model_class.model_validate(data)
    except ValidationError as error:
        raise InvalidLlmOutputError(_summarize(error)) from error