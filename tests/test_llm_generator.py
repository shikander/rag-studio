import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from rag_studio.core.config import Settings
from rag_studio.domain.errors import InvalidLlmOutputError, LlmError, NoCriteriaFoundError
from rag_studio.domain.models import RunRequest
from rag_studio.llm.client import OpenRouterClient
from rag_studio.llm.router import resolve_model
from rag_studio.llm.structured import extract_json
from rag_studio.pipelines.llm_generator import LlmGenerator

CRITERIA = "Story: login\nAC1: Valid login opens /dashboard.\nAC2: Wrong password shows an error."

GOOD_REPLY = json.dumps({
    "test_cases": [
        {"criterion": "AC1", "test_type": "Functional", "technique": "Equivalence partitioning",
         "scenario": "Valid login", "steps": ["1. Open /login", "2) Submit valid credentials"],
         "data": {"Email": "[VALID EMAIL]", "Password": "[VALID PASSWORD]"}, "expected": "Dashboard is shown"},
        {"criterion": "ac2", "test_type": "Negative", "technique": "Error guessing",
         "scenario": "Wrong password", "steps": ["Open /login", "Submit a wrong password"],
         "data": "Password: wrong", "expected": "Inline error is shown"},
    ]
})


class FakeClient:
    def __init__(self, *replies: str) -> None:
        self.replies = list(replies)
        self.calls: list[tuple[str, str, str]] = []

    def complete(self, system: str, user: str, model: str) -> str:
        self.calls.append((system, user, model))
        return self.replies.pop(0)


def make_request(criteria: str = CRITERIA) -> RunRequest:
    return RunRequest(
        criteria_text=criteria,
        techniques=["Equivalence partitioning", "Error guessing"],
        test_types=["Functional", "Negative"],
        model="Fast and cheap (OpenRouter)",
    )


def make_generator(*replies: str) -> tuple[LlmGenerator, FakeClient]:
    client = FakeClient(*replies)
    return LlmGenerator(client, Settings(_env_file=None, fast_model="vendor/fast")), client


def test_valid_reply_becomes_test_cases():
    generator, client = make_generator(GOOD_REPLY)
    cases = generator.generate(make_request())
    assert [c.id for c in cases] == ["TC-001", "TC-002"]
    assert cases[0].steps == ["Open /login", "Submit valid credentials"]  # numbering stripped
    assert cases[0].data == "Email: [VALID EMAIL]\nPassword: [VALID PASSWORD]"  # dict flattened
    assert cases[1].criterion == "AC2"  # normalised
    assert client.calls[0][2] == "vendor/fast"


def test_prompt_contains_requirement_techniques_and_types():
    generator, client = make_generator(GOOD_REPLY)
    generator.generate(make_request())
    user_prompt = client.calls[0][1]
    assert "AC1: Valid login opens /dashboard." in user_prompt
    assert "Equivalence partitioning, Error guessing" in user_prompt
    assert "Functional, Negative" in user_prompt
    assert "AC1, AC2" in user_prompt


def test_fenced_json_with_surrounding_text_is_accepted():
    generator, _ = make_generator("Here you go:\n```json\n" + GOOD_REPLY + "\n```\nHope it helps!")
    assert len(generator.generate(make_request())) == 2


def test_invalid_reply_is_retried_once_with_the_problem_described():
    generator, client = make_generator("not json at all", GOOD_REPLY)
    assert len(generator.generate(make_request())) == 2
    assert len(client.calls) == 2
    assert "previous reply was invalid" in client.calls[1][1]


def test_two_invalid_replies_raise():
    generator, client = make_generator("nope", '{"test_cases": []}')
    with pytest.raises(InvalidLlmOutputError):
        generator.generate(make_request())
    assert len(client.calls) == 2


def test_cases_for_unknown_criteria_are_dropped():
    reply = json.dumps({"test_cases": [
        {"criterion": "AC9", "test_type": "Functional", "technique": "x", "scenario": "s",
         "steps": ["a"], "data": "", "expected": "e"},
        {"criterion": "AC1", "test_type": "Functional", "technique": "x", "scenario": "s",
         "steps": ["a"], "data": "", "expected": "e"},
    ]})
    generator, _ = make_generator(reply)
    cases = generator.generate(make_request())
    assert [c.criterion for c in cases] == ["AC1"]
    assert cases[0].id == "TC-001"


def test_no_criteria_raises_before_calling_the_llm():
    generator, client = make_generator(GOOD_REPLY)
    with pytest.raises(NoCriteriaFoundError):
        generator.generate(make_request("just some text"))
    assert client.calls == []


def test_resolve_model():
    settings = Settings(_env_file=None, fast_model="a/fast", strong_model="b/strong")
    assert resolve_model("Fast and cheap (OpenRouter)", settings) == "a/fast"
    assert resolve_model("Strong coder (OpenRouter)", settings) == "b/strong"
    assert resolve_model("custom/model", settings) == "custom/model"


def test_extract_json_rejects_garbage():
    with pytest.raises(InvalidLlmOutputError):
        extract_json("no braces here")


# ---- real HTTP round trip against a stub that imitates OpenRouter ----

class StubHandler(BaseHTTPRequestHandler):
    status = 200
    seen: dict = {}

    def do_POST(self):  # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        StubHandler.seen = {"path": self.path, "model": body["model"], "auth": self.headers.get("Authorization")}
        payload = {"choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": GOOD_REPLY}}]}
        if StubHandler.status != 200:
            payload = {"error": {"message": "nope"}}
        data = json.dumps(payload).encode()
        self.send_response(StubHandler.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture
def stub_url():
    server = HTTPServer(("127.0.0.1", 0), StubHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    StubHandler.status = 200
    yield f"http://127.0.0.1:{server.server_port}/api/v1"
    server.shutdown()


def test_openrouter_client_round_trip(stub_url):
    settings = Settings(_env_file=None, fast_model="vendor/fast")
    client = OpenRouterClient("sk-test", stub_url, timeout=10)
    cases = LlmGenerator(client, settings).generate(make_request())
    assert len(cases) == 2
    assert StubHandler.seen["path"].endswith("/chat/completions")
    assert StubHandler.seen["model"] == "vendor/fast"
    assert StubHandler.seen["auth"] == "Bearer sk-test"


@pytest.mark.parametrize("status,fragment", [(401, "API key"), (404, "not found"), (402, "credits"), (429, "rate limit")])
def test_openrouter_errors_become_friendly_messages(stub_url, status, fragment):
    StubHandler.status = status
    client = OpenRouterClient("sk-test", stub_url, timeout=10)
    with pytest.raises(LlmError) as error:
        client.complete("s", "u", "vendor/fast")
    assert fragment.lower() in str(error.value).lower()