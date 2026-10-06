from functools import lru_cache

from fastapi import Depends

from rag_studio.services.run_service import RunService
from rag_studio.storage.run_store import InMemoryRunStore


@lru_cache
def get_run_store() -> InMemoryRunStore:
    return InMemoryRunStore()


def get_run_service(store: InMemoryRunStore = Depends(get_run_store)) -> RunService:
    return RunService(store)