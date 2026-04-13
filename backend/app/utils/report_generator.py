from __future__ import annotations

from app.agent.models import CoverageResult, RequirementPoint, TestCase


def _render_points(points: list[RequirementPoint]) -> str:
    if not points:
        return "- 无\n"
    lines = []
    for point in points:
        lines.append(
            f"- [{point.id}] {point.module} / {point.type} / {point.priority}: {point.description}"
        )
    return "\n".join(lines) + "\n"


def _render_cases(cases: list[TestCase]) -> str:
    if not cases:
        return "- 无\n"
    lines = []
    for case in cases:
        lines.append(
            "\n".join(
                [
                    f"- 用例ID: {case.case_id}",
                    f"  标题: {case.title}",
                    f"  前置条件: {case.preconditions or '无'}",
                    f"  步骤: {case.steps}",
                    f"  预期结果: {case.expected_result}",
                    f"  标签: {', '.join(case.tags) if case.tags else '无'}",
                ]
            )
        )
    return "\n".join(lines) + "\n"


def generate_markdown_report(result: CoverageResult) -> str:
    dimension_lines = []
    for key, value in result.dimension_scores.items():
        dimension_lines.append(
            f"- {key}: {value.score}/{value.full_score}，说明：{value.reason or '无'}"
        )

    suggestions = [f"- {item}" for item in result.suggestions] or ["- 无"]

    return "\n".join(
        [
            "# 测试用例覆盖度评估报告",
            "",
            "## 综合评分",
            f"- 总分：{result.score}",
            f"- 等级：{result.level}",
            "",
            "## 维度得分",
            *dimension_lines,
            "",
            "## 已覆盖需求点",
            _render_points(result.covered_points),
            "## 未覆盖需求点",
            _render_points(result.missing_points),
            "## 补充建议",
            *suggestions,
            "",
            "## 建议新增测试用例",
            _render_cases(result.generated_cases),
        ]
    ).strip() + "\n"
