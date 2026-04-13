from __future__ import annotations

from pathlib import Path

from app.agent.models import (
    AnalysisArtifacts,
    CoverageAssessmentPayload,
    RequirementExtractionPayload,
    RequirementPoint,
)
from app.agent.prompts import (
    COVERAGE_ASSESSMENT_SYSTEM_PROMPT,
    REQUIREMENT_EXTRACTION_SYSTEM_PROMPT,
    build_coverage_assessment_prompt,
    build_requirement_extraction_prompt,
)
from app.agent.models import CoverageMapping
from app.agent.scorer import calculate_coverage_result
from app.config import settings
from app.llm.deepseek_client import DeepSeekClient
from app.readers.excel_reader import read_test_cases
from app.readers.pdf_reader import read_pdf_file
from app.readers.text_reader import read_text_file
from app.utils.chunking import chunk_text
from app.utils.exceptions import ChunkProcessingError, UnsupportedFileTypeError
from app.utils.report_generator import generate_markdown_report


class CoverageAgent:
    def __init__(self, llm_client: DeepSeekClient | None = None) -> None:
        self.llm_client = llm_client or DeepSeekClient()

    def analyze(
        self,
        *,
        prd_path: Path,
        test_case_path: Path,
        sheet_name: str | None = None,
        generate_missing_cases: bool = True,
    ) -> AnalysisArtifacts:
        prd_text = self._read_prd(prd_path)
        test_cases = read_test_cases(test_case_path, sheet_name=sheet_name)
        requirements = self._extract_requirements(prd_text)
        assessment = self._evaluate_coverage(requirements, test_cases, generate_missing_cases)
        coverage_result = calculate_coverage_result(
            requirement_points=requirements,
            test_cases=test_cases,
            mappings=assessment.mappings,
            suggestions=assessment.suggestions,
        )
        coverage_result.markdown_report = generate_markdown_report(coverage_result)

        return AnalysisArtifacts(
            prd_text=prd_text,
            requirement_points=requirements,
            test_cases=test_cases,
            coverage_result=coverage_result,
            metadata={
                "prd_file": str(prd_path),
                "test_case_file": str(test_case_path),
                "sheet_name": sheet_name,
                "model": settings.deepseek_model,
            },
        )

    def _read_prd(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md"}:
            return read_text_file(file_path)
        if suffix == ".pdf":
            return read_pdf_file(file_path)
        raise UnsupportedFileTypeError(f"不支持的需求文档类型: {suffix}")

    def _extract_requirements(self, prd_text: str) -> list[RequirementPoint]:
        chunks = chunk_text(prd_text, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            raise ChunkProcessingError("需求文档为空，无法进行需求点提取。")

        extracted: list[RequirementPoint] = []
        for index, chunk in enumerate(chunks, start=1):
            payload = self.llm_client.invoke_json(
                system_prompt=REQUIREMENT_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=build_requirement_extraction_prompt(chunk, index if len(chunks) > 1 else None),
                response_model=RequirementExtractionPayload,
            )
            extracted.extend(payload.requirements)

        if not extracted:
            raise ChunkProcessingError("需求文档分段处理完成，但未抽取出任何需求点。")

        deduplicated: list[RequirementPoint] = []
        seen: set[tuple[str, str]] = set()
        for item in extracted:
            key = (item.type.strip().lower(), item.description.strip())
            if key in seen:
                continue
            seen.add(key)
            deduplicated.append(item)

        for index, item in enumerate(deduplicated, start=1):
            item.id = f"REQ-{index:03d}"
        return deduplicated

    def _evaluate_coverage(
        self,
        requirements: list[RequirementPoint],
        test_cases: list,
        generate_missing_cases: bool,
    ) -> CoverageAssessmentPayload:
        if not requirements:
            return CoverageAssessmentPayload(mappings=[], suggestions=[])

        requirement_batches = [
            requirements[index : index + settings.coverage_batch_size]
            for index in range(0, len(requirements), settings.coverage_batch_size)
        ]

        merged_mappings: dict[str, CoverageMapping] = {}
        merged_suggestions: list[str] = []

        for batch_index, requirement_batch in enumerate(requirement_batches, start=1):
            payload = self.llm_client.invoke_json(
                system_prompt=COVERAGE_ASSESSMENT_SYSTEM_PROMPT,
                user_prompt=build_coverage_assessment_prompt(
                    requirement_points=requirement_batch,
                    test_cases=test_cases,
                    generate_missing_cases=generate_missing_cases,
                    batch_index=batch_index,
                    total_batches=len(requirement_batches),
                ),
                response_model=CoverageAssessmentPayload,
            )
            for mapping in payload.mappings:
                merged_mappings[mapping.requirement_id] = mapping
            for suggestion in payload.suggestions:
                if suggestion not in merged_suggestions:
                    merged_suggestions.append(suggestion)

        for requirement in requirements:
            if requirement.id not in merged_mappings:
                merged_mappings[requirement.id] = CoverageMapping(
                    requirement_id=requirement.id,
                    covered=False,
                    missing_reason="模型未返回该需求点的覆盖判断，请人工复核。",
                )

        ordered_mappings = [merged_mappings[requirement.id] for requirement in requirements]
        return CoverageAssessmentPayload(mappings=ordered_mappings, suggestions=merged_suggestions)
