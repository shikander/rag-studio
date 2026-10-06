from datetime import datetime

from pydantic import BaseModel

from rag_studio.domain.models import Run, RunStatus


class RunSummary(BaseModel):
    id: str
    status: RunStatus
    created_at: datetime
    criteria_count: int
    test_case_count: int

    @classmethod
    def from_run(cls, run: Run) -> "RunSummary":
        return cls(
            id=run.id,
            status=run.status,
            created_at=run.created_at,
            criteria_count=run.criteria_count,
            test_case_count=len(run.test_cases),
        )