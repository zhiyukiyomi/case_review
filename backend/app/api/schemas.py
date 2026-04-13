from __future__ import annotations

from pydantic import BaseModel, Field


class CreateAnalysisJobResponse(BaseModel):
    task_id: str
    status: str


class AnalysisJobStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")

