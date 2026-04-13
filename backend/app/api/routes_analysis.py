from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from app.api.schemas import AnalysisJobStatusResponse, CreateAnalysisJobResponse, ErrorResponse
from app.config import settings
from app.services.analysis_service import analysis_service
from app.services.task_service import task_service


router = APIRouter(prefix="/analysis", tags=["analysis"])


async def _save_upload(upload: UploadFile, destination: Path) -> Path:
    data = await upload.read()
    destination.write_bytes(data)
    return destination


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/jobs",
    response_model=CreateAnalysisJobResponse,
    responses={400: {"model": ErrorResponse}},
)
async def create_analysis_job(
    prd_file: UploadFile = File(description="PRD file: txt, md, or pdf"),
    test_case_file: UploadFile = File(description="Test case file: xlsx"),
    sheet_name: str | None = Form(default=None),
    generate_missing_cases: bool = Form(default=True),
) -> CreateAnalysisJobResponse:
    if not prd_file.filename or not test_case_file.filename:
        raise HTTPException(status_code=400, detail="请同时上传需求文档和测试用例文件。")

    job_dir = settings.temp_dir / uuid.uuid4().hex
    job_dir.mkdir(parents=True, exist_ok=True)

    prd_path = job_dir / prd_file.filename
    test_case_path = job_dir / test_case_file.filename
    await _save_upload(prd_file, prd_path)
    await _save_upload(test_case_file, test_case_path)

    task = task_service.submit(
        lambda: analysis_service.run(
            prd_path=prd_path,
            test_case_path=test_case_path,
            sheet_name=sheet_name,
            generate_missing_cases=generate_missing_cases,
        )
    )
    return CreateAnalysisJobResponse(task_id=task.task_id, status=task.status)


@router.get(
    "/jobs/{task_id}",
    response_model=AnalysisJobStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_analysis_job(task_id: str) -> AnalysisJobStatusResponse:
    task = task_service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="分析任务不存在。")
    return AnalysisJobStatusResponse(
        task_id=task.task_id,
        status=task.status,
        result=task.result,
        error=task.error,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get(
    "/jobs/{task_id}/report",
    response_class=PlainTextResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_analysis_report(task_id: str) -> PlainTextResponse:
    task = task_service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="分析任务不存在。")
    if task.status != "completed" or not task.result:
        raise HTTPException(status_code=404, detail="分析报告尚未生成。")
    report = task.result.get("markdown_report", "")
    return PlainTextResponse(content=report, media_type="text/markdown; charset=utf-8")

