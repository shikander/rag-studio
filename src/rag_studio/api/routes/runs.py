from fastapi import APIRouter, Depends

from rag_studio.api.dependencies import get_run_service
from rag_studio.api.schemas import RunSummary
from rag_studio.domain.models import Run, RunRequest
from rag_studio.services.run_service import RunService

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=Run, status_code=201)
def create_run(request: RunRequest, service: RunService = Depends(get_run_service)) -> Run:
    """Generate test cases from acceptance criteria and store the run."""
    return service.create_run(request)


@router.get("", response_model=list[RunSummary])
def list_runs(service: RunService = Depends(get_run_service)) -> list[RunSummary]:
    return [RunSummary.from_run(run) for run in service.list_runs()]


@router.get("/{run_id}", response_model=Run)
def get_run(run_id: str, service: RunService = Depends(get_run_service)) -> Run:
    return service.get_run(run_id)