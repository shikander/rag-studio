"""Stand-in for the backend. Replace generate_test_cases with a call to the FastAPI service."""
import re

from models import GenerationRequest, TestCase

AC_PATTERN = re.compile(r"^(AC\d+):\s*(.+)$", re.MULTILINE)


def parse_criteria(text: str) -> list[tuple[str, str]]:
    return AC_PATTERN.findall(text)


def count_criteria(text: str) -> int:
    return len(parse_criteria(text))


def _build_case(number: int, ac_id: str, kind: str, text: str) -> TestCase:
    negative = kind == "Negative"
    return TestCase(
        id=f"TC-{number:03d}",
        criterion=ac_id,
        test_type=kind,
        scenario=f"{kind}: {text}",
        steps=f"1. Open the page\n2. Enter {'invalid' if negative else 'valid'} data\n3. Submit",
        data="[TEST DATA]",
        expected=(
            "The system rejects the input and shows an error."
            if negative
            else "The outcome described in the criterion is observed."
        ),
    )


def generate_test_cases(request: GenerationRequest) -> list[TestCase]:
    cases: list[TestCase] = []
    for ac_id, text in parse_criteria(request.criteria_text):
        for kind in ("Positive", "Negative"):
            cases.append(_build_case(len(cases) + 1, ac_id, kind, text))
    return cases