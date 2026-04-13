from __future__ import annotations

from pathlib import Path

from app.agent.coverage_agent import CoverageAgent
from app.config import settings
from app.services.demo_service import build_demo_result


class AnalysisService:
    def __init__(self, agent: CoverageAgent | None = None) -> None:
        self.agent = agent

    def run(
        self,
        *,
        prd_path: Path,
        test_case_path: Path,
        sheet_name: str | None = None,
        generate_missing_cases: bool = True,
    ) -> dict:
        if settings.demo_mode:
            return build_demo_result(
                prd_path=prd_path,
                test_case_path=test_case_path,
                sheet_name=sheet_name,
                generate_missing_cases=generate_missing_cases,
            )

        agent = self.agent or CoverageAgent()
        artifacts = agent.analyze(
            prd_path=prd_path,
            test_case_path=test_case_path,
            sheet_name=sheet_name,
            generate_missing_cases=generate_missing_cases,
        )
        payload = artifacts.coverage_result.model_dump()
        payload["metadata"] = artifacts.metadata
        return payload


analysis_service = AnalysisService()
