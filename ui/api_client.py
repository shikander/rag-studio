"""HTTP client for the RAG Studio API."""
import os
from dataclasses import asdict

import requests

from models import GenerationRequest, TestCase

API_URL = os.getenv("RAG_STUDIO_API_URL", "http://localhost:8000")
TIMEOUT_SECONDS = 120


class ApiError(Exception):
    """Raised with a message that is safe to show to the user."""


def _error_message(response: requests.Response) -> str:
    try:
        return str(response.json().get("detail", response.text))
    except ValueError:
        return response.text or f"API returned status {response.status_code}"


def _post(path: str, payload: dict) -> dict:
    try:
        response = requests.post(f"{API_URL}{path}", json=payload, timeout=TIMEOUT_SECONDS)
    except requests.ConnectionError as error:
        raise ApiError(f"Cannot reach the API at {API_URL}. Is it running?") from error
    except requests.Timeout as error:
        raise ApiError("The API took too long to respond.") from error
    if not response.ok:
        raise ApiError(_error_message(response))
    return response.json()


def _to_test_case(item: dict) -> TestCase:
    steps = "\n".join(f"{number}. {step}" for number, step in enumerate(item["steps"], start=1))
    return TestCase(
        id=item["id"],
        criterion=item["criterion"],
        test_type=item["test_type"],
        scenario=item["scenario"],
        steps=steps,
        data=item["data"],
        expected=item["expected"],
    )


def generate_test_cases(request: GenerationRequest) -> list[TestCase]:
    run = _post("/runs", asdict(request))
    return [_to_test_case(item) for item in run["test_cases"]]