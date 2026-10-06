import pytest
from fastapi.testclient import TestClient

from rag_studio.api.dependencies import get_generator, get_run_store
from rag_studio.api.main import app
from rag_studio.core.config import Settings, get_settings
from rag_studio.pipelines.mock_generator import MockGenerator

CRITERIA = """Story: login
AC1: Given I am on /login, when I enter valid credentials, then I see /dashboard.
AC2: Given I am on /login, when I enter a wrong password, then I see an error.
AC3: Given I failed 5 times, when I retry, then the account is locked."""


def make_payload(criteria_text: str = CRITERIA) -> dict:
    return {
        "criteria_text": criteria_text,
        "techniques": ["Boundary value analysis", "Equivalence partitioning"],
        "test_types": ["Functional", "Negative"],
        "context_sources": ["Existing tests"],
        "model": "Fast and cheap (OpenRouter)",
    }


@pytest.fixture
def client() -> TestClient:
    get_run_store.cache_clear()
    app.dependency_overrides[get_generator] = lambda: MockGenerator()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_run_generates_two_cases_per_criterion(client):
    response = client.post("/runs", json=make_payload())
    body = response.json()
    assert response.status_code == 201
    assert body["criteria_count"] == 3
    assert len(body["test_cases"]) == 6
    assert body["test_cases"][0]["id"] == "TC-001"


def test_create_run_without_criteria_returns_422(client):
    response = client.post("/runs", json=make_payload("just some text"))
    assert response.status_code == 422
    assert "No acceptance criteria" in response.json()["detail"]


def test_create_run_without_techniques_returns_422(client):
    payload = make_payload() | {"techniques": []}
    assert client.post("/runs", json=payload).status_code == 422


def test_get_run_and_list_runs(client):
    run_id = client.post("/runs", json=make_payload()).json()["id"]
    assert client.get(f"/runs/{run_id}").json()["id"] == run_id
    summaries = client.get("/runs").json()
    assert summaries[0]["id"] == run_id
    assert summaries[0]["test_case_count"] == 6


def test_get_unknown_run_returns_404(client):
    assert client.get("/runs/nope").status_code == 404


def test_missing_api_key_returns_503():
    get_run_store.cache_clear()
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, generator="llm", openrouter_api_key="")
    try:
        response = TestClient(app).post("/runs", json=make_payload())
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert "OPENROUTER_API_KEY" in response.json()["detail"]