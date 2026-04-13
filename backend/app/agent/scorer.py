from __future__ import annotations

from collections import defaultdict

from app.agent.models import CoverageMapping, CoverageResult, DimensionScore, RequirementPoint, TestCase


DIMENSION_RULES = {
    "core_function": {
        "full_score": 50,
        "types": {"functional"},
    },
    "business_rules_and_boundaries": {
        "full_score": 25,
        "types": {"business_rule", "boundary_condition"},
    },
    "exception_flows": {
        "full_score": 15,
        "types": {"exception_scenario"},
    },
    "non_functional": {
        "full_score": 10,
        "types": {"non_functional"},
    },
}


TYPE_NORMALIZATION = {
    "功能点": "functional",
    "functional": "functional",
    "core_function": "functional",
    "业务规则": "business_rule",
    "business_rule": "business_rule",
    "business_rules": "business_rule",
    "边界条件": "boundary_condition",
    "boundary": "boundary_condition",
    "boundary_condition": "boundary_condition",
    "异常场景": "exception_scenario",
    "exception": "exception_scenario",
    "exception_scenario": "exception_scenario",
    "reverse_flow": "exception_scenario",
    "negative_flow": "exception_scenario",
    "非功能需求": "non_functional",
    "non_functional": "non_functional",
    "performance": "non_functional",
    "security": "non_functional",
    "compatibility": "non_functional",
}


def _normalize_type(raw_type: str) -> str:
    normalized = raw_type.strip().lower()
    return TYPE_NORMALIZATION.get(raw_type, TYPE_NORMALIZATION.get(normalized, "functional"))


def _allocate_scores(full_score: int, count: int) -> list[int]:
    if count <= 0:
        return []
    base = full_score // count
    remainder = full_score % count
    return [base + (1 if index < remainder else 0) for index in range(count)]


def _level_from_score(score: int) -> str:
    if score >= 90:
        return "覆盖达标"
    if score >= 70:
        return "存在遗漏，需补充"
    return "不合格，需重新设计"


def calculate_coverage_result(
    requirement_points: list[RequirementPoint],
    test_cases: list[TestCase],
    mappings: list[CoverageMapping],
    suggestions: list[str],
) -> CoverageResult:
    mapping_lookup = {mapping.requirement_id: mapping for mapping in mappings}
    dimension_points: dict[str, list[RequirementPoint]] = defaultdict(list)

    for point in requirement_points:
        point.type = _normalize_type(point.type)
        for dimension, rule in DIMENSION_RULES.items():
            if point.type in rule["types"]:
                dimension_points[dimension].append(point)
                break

    covered_points: list[RequirementPoint] = []
    missing_points: list[RequirementPoint] = []
    dimension_scores: dict[str, DimensionScore] = {}
    total_score = 0

    for dimension, rule in DIMENSION_RULES.items():
        points = dimension_points.get(dimension, [])
        full_score = rule["full_score"]

        if not points:
            dimension_scores[dimension] = DimensionScore(
                score=full_score,
                full_score=full_score,
                reason="PRD 中未识别到该维度需求点，按无可评估项处理，不扣分。",
            )
            total_score += full_score
            continue

        point_scores = _allocate_scores(full_score, len(points))
        obtained_score = 0
        missing_descriptions: list[str] = []

        for index, point in enumerate(points):
            mapping = mapping_lookup.get(point.id)
            if mapping and mapping.covered:
                obtained_score += point_scores[index]
                covered_points.append(point)
            else:
                missing_points.append(point)
                missing_descriptions.append(f"[{point.id}] {point.description}")

        total_score += obtained_score
        deduction = full_score - obtained_score
        reason = (
            f"已覆盖 {len(points) - len(missing_descriptions)}/{len(points)} 个需求点。"
            if not missing_descriptions
            else f"扣分 {deduction} 分。未覆盖需求点：" + "；".join(missing_descriptions)
        )
        dimension_scores[dimension] = DimensionScore(
            score=obtained_score,
            full_score=full_score,
            reason=reason,
        )

    generated_cases = [
        mapping.suggested_case
        for mapping in mappings
        if mapping.suggested_case is not None and not mapping.covered
    ]

    deduplicated_cases: list[TestCase] = []
    seen_case_ids: set[str] = set()
    for case in generated_cases:
        if case.case_id in seen_case_ids:
            continue
        seen_case_ids.add(case.case_id)
        deduplicated_cases.append(case)

    return CoverageResult(
        score=total_score,
        level=_level_from_score(total_score),
        dimension_scores=dimension_scores,
        covered_points=covered_points,
        missing_points=missing_points,
        suggestions=suggestions,
        generated_cases=deduplicated_cases,
        requirement_points=requirement_points,
        test_cases=test_cases,
        coverage_mappings=mappings,
    )
