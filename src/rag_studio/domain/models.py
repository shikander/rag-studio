"""Core business objects. Also used as API request and response schemas."""
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    COMPLETED = "completed"


class TestCase(BaseModel):
    __test__ = False  # stop pytest from trying to collect this class

    id: str
    criterion: str
    test_type: str
    technique: str
    scenario: str
    steps: list[str]
    data: str
    expected: str


class RunRequest(BaseModel):
    criteria_text: str = Field(min_length=1)
    techniques: list[str] = Field(min_length=1)
    test_types: list[str] = Field(min_length=1)
    context_sources: list[str] = Field(default_factory=list)
    model: str = "default"


class Run(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    status: RunStatus = RunStatus.COMPLETED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request: RunRequest
    criteria_count: int
    test_cases: list[TestCase]