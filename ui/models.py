"""Plain data classes shared by the UI. Swap for Pydantic models later."""
from dataclasses import dataclass


@dataclass
class TestCase:
    id: str
    criterion: str
    test_type: str
    scenario: str
    steps: str
    data: str
    expected: str


@dataclass
class GenerationRequest:
    criteria_text: str
    techniques: list[str]
    test_types: list[str]
    context_sources: list[str]
    model: str