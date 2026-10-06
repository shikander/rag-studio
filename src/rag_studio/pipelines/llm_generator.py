"""Generates test cases by asking an LLM, with one retry if the reply is not usable JSON."""
from rag_studio.core.config import Settings
from rag_studio.domain.errors import InvalidLlmOutputError
from rag_studio.domain.models import RunRequest, TestCase
from rag_studio.llm.client import LlmClient
from rag_studio.llm.router import resolve_model
from rag_studio.llm.structured import parse_model
from rag_studio.pipelines.criteria import parse_criteria
from rag_studio.pipelines.llm_output import GeneratedCases
from rag_studio.prompts.loader import render

MAX_ATTEMPTS = 2


class LlmGenerator:
    def __init__(self, client: LlmClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    def generate(self, request: RunRequest) -> list[TestCase]:
        criteria = parse_criteria(request.criteria_text)
        valid_ids = [criterion.id for criterion in criteria]
        system = render("test_case_system.jinja")
        user = render(
            "test_case_user.jinja",
            criteria_text=request.criteria_text,
            criterion_ids=valid_ids,
            techniques=request.techniques,
            test_types=request.test_types,
            context=[],  # filled by retrieval later
        )
        model = resolve_model(request.model, self._settings)
        generated = self._ask_with_retry(system, user, model)
        return self._to_test_cases(generated, valid_ids)

    def _ask_with_retry(self, system: str, user: str, model: str) -> GeneratedCases:
        problem = ""
        for _ in range(MAX_ATTEMPTS):
            prompt = user if not problem else self._with_correction(user, problem)
            reply = self._client.complete(system, prompt, model)
            try:
                return parse_model(reply, GeneratedCases)
            except InvalidLlmOutputError as error:
                problem = str(error)
        raise InvalidLlmOutputError(f"The model did not return usable test cases. {problem}")

    @staticmethod
    def _with_correction(user: str, problem: str) -> str:
        return f"{user}\n\nYour previous reply was invalid: {problem}\nReply again with valid JSON only."

    @staticmethod
    def _to_test_cases(generated: GeneratedCases, valid_ids: list[str]) -> list[TestCase]:
        cases: list[TestCase] = []
        for item in generated.test_cases:
            criterion = item.criterion.strip().upper()
            if criterion not in valid_ids:
                continue  # the model referred to a criterion that does not exist
            cases.append(
                TestCase(
                    id=f"TC-{len(cases) + 1:03d}",
                    criterion=criterion,
                    test_type=item.test_type,
                    technique=item.technique,
                    scenario=item.scenario,
                    steps=item.steps,
                    data=item.data,
                    expected=item.expected,
                )
            )
        if not cases:
            raise InvalidLlmOutputError("The model returned test cases for unknown criteria.")
        return cases