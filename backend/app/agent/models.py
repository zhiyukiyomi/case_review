from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RequirementPoint(BaseModel):
    id: str
    module: str
    type: str
    description: str
    priority: str = "medium"
    source_text: str


class TestCase(BaseModel):
    case_id: str
    title: str
    preconditions: str = ""
    steps: str
    expected_result: str
    tags: list[str] = Field(default_factory=list)


class CoverageMapping(BaseModel):
    requirement_id: str
    covered: bool
    matched_case_ids: list[str] = Field(default_factory=list)
    rationale: str = ""
    missing_reason: str = ""
    suggested_case: TestCase | None = None


class DimensionScore(BaseModel):
    score: int
    full_score: int
    reason: str


class CoverageResult(BaseModel):
    score: int
    level: str
    dimension_scores: dict[str, DimensionScore]
    covered_points: list[RequirementPoint]
    missing_points: list[RequirementPoint]
    suggestions: list[str]
    generated_cases: list[TestCase]
    markdown_report: str = ""
    requirement_points: list[RequirementPoint] = Field(default_factory=list)
    test_cases: list[TestCase] = Field(default_factory=list)
    coverage_mappings: list[CoverageMapping] = Field(default_factory=list)


class RequirementExtractionPayload(BaseModel):
    requirements: list[RequirementPoint]


class CoverageAssessmentPayload(BaseModel):
    mappings: list[CoverageMapping]
    suggestions: list[str] = Field(default_factory=list)


class AnalysisArtifacts(BaseModel):
    prd_text: str
    requirement_points: list[RequirementPoint]
    test_cases: list[TestCase]
    coverage_result: CoverageResult
    metadata: dict[str, Any] = Field(default_factory=dict)
