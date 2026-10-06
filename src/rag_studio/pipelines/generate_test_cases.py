"""Test case generation. MOCK for now: replace with retrieval + LLM later."""
import re

from rag_studio.domain.errors import NoCriteriaFoundError
from rag_studio.domain.models import TestCase

AC_PATTERN = re.compile(r"^(AC\d+):\s*(.+)$", re.MULTILINE)


def parse_criteria(text: str) -> list[tuple[str, str]]:
    return AC_PATTERN.findall(text)


def _build_case(number: int, criterion: str, kind: str, text: str, technique: str) -> TestCase:
    negative = kind == "Negative"
    return TestCase(
        id=f"TC-{number:03d}",
        criterion=criterion,
        test_type=kind,
        technique=technique,
        scenario=f"{kind}: {text}",
        steps=["Open the page", f"Enter {'invalid' if negative else 'valid'} data", "Submit"],
        data="[TEST DATA]",
        expected=(
            "The system rejects the input and shows an error."
            if negative
            else "The outcome described in the criterion is observed."
        ),
    )


def generate_test_cases(criteria_text: str, techniques: list[str]) -> list[TestCase]:
    criteria = parse_criteria(criteria_text)
    if not criteria:
        raise NoCriteriaFoundError("No acceptance criteria found. Start each one with AC1:, AC2: and so on.")
    cases: list[TestCase] = []
    for criterion, text in criteria:
        for kind in ("Positive", "Negative"):
            technique = techniques[len(cases) % len(techniques)]
            cases.append(_build_case(len(cases) + 1, criterion, kind, text, technique))
    return cases