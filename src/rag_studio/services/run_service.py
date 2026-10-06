from rag_studio.domain.errors import RunNotFoundError
from rag_studio.domain.models import Run, RunRequest
from rag_studio.pipelines.generate_test_cases import generate_test_cases
from rag_studio.storage.run_store import InMemoryRunStore


class RunService:
    def __init__(self, store: InMemoryRunStore) -> None:
        self._store = store

    def create_run(self, request: RunRequest) -> Run:
        cases = generate_test_cases(request.criteria_text, request.techniques)
        run = Run(
            request=request,
            criteria_count=len({case.criterion for case in cases}),
            test_cases=cases,
        )
        self._store.save(run)
        return run

    def get_run(self, run_id: str) -> Run:
        run = self._store.get(run_id)
        if run is None:
            raise RunNotFoundError(f"Run {run_id} not found")
        return run

    def list_runs(self) -> list[Run]:
        return self._store.list()