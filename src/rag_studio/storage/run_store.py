"""In-memory run storage. Swap for SQLite/Postgres later with the same methods."""
from rag_studio.domain.models import Run


class InMemoryRunStore:
    def __init__(self) -> None:
        self._runs: dict[str, Run] = {}

    def save(self, run: Run) -> None:
        self._runs[run.id] = run

    def get(self, run_id: str) -> Run | None:
        return self._runs.get(run_id)

    def list(self) -> list[Run]:
        return sorted(self._runs.values(), key=lambda run: run.created_at, reverse=True)