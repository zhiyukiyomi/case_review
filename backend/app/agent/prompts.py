from __future__ import annotations

import json

from app.config import settings
from app.agent.models import RequirementPoint, TestCase


REQUIREMENT_EXTRACTION_SYSTEM_PROMPT = """
你是一名资深测试架构师，负责从产品需求文档中抽取结构化需求点。

必须遵守：
1. 只输出合法 JSON。
2. 按要求把需求点归类到以下 type 之一：
   - functional
   - business_rule
   - boundary_condition
   - exception_scenario
   - non_functional
3. 每条需求必须尽量原子化，避免把多个需求混在一起。
4. source_text 必须保留对应原文摘要。
5. priority 只能是 high / medium / low。
6. 如果文档某类需求不存在，不要编造。
7. 返回格式：
{
  "requirements": [
    {
      "id": "TEMP-001",
      "module": "模块名",
      "type": "functional",
      "description": "需求描述",
      "priority": "high",
      "source_text": "原文片段"
    }
  ]
}
""".strip()


COVERAGE_ASSESSMENT_SYSTEM_PROMPT = """
你是一名测试覆盖度分析专家，需要根据结构化需求点和测试用例判断覆盖关系。

必须遵守：
1. 只输出合法 JSON。
2. 不要直接给总分。
3. 针对每个 requirement_id 判断是否被覆盖。
4. matched_case_ids 只填写真实存在的 case_id。
5. 如果未覆盖，需要给出 missing_reason。
6. 如果未覆盖且适合补齐，请生成 suggested_case。
7. suggested_case 必须包含：
   - case_id
   - title
   - preconditions
   - steps
   - expected_result
   - tags
8. rationale 和 missing_reason 控制在 80 个汉字以内。
9. suggested_case.steps 与 expected_result 保持简洁，不要写成长段落。
10. 只输出 JSON，不要输出任何额外文字。
11. 返回格式：
{
  "mappings": [
    {
      "requirement_id": "REQ-001",
      "covered": true,
      "matched_case_ids": ["TC-001"],
      "rationale": "说明为何判定已覆盖",
      "missing_reason": "",
      "suggested_case": null
    }
  ],
  "suggestions": [
    "补充建议1"
  ]
}
""".strip()


def _truncate_text(value: str, *, max_chars: int | None = None) -> str:
    limit = max_chars or settings.prompt_text_preview_chars
    cleaned = " ".join(value.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[:limit]}..."


def _compact_requirement(requirement: RequirementPoint) -> dict:
    return {
        "id": requirement.id,
        "module": _truncate_text(requirement.module, max_chars=80),
        "type": requirement.type,
        "description": _truncate_text(requirement.description),
        "priority": requirement.priority,
        "source_text": _truncate_text(requirement.source_text),
    }


def _compact_test_case(test_case: TestCase) -> dict:
    return {
        "case_id": test_case.case_id,
        "title": _truncate_text(test_case.title, max_chars=120),
        "preconditions": _truncate_text(test_case.preconditions, max_chars=180),
        "steps": _truncate_text(test_case.steps, max_chars=220),
        "expected_result": _truncate_text(test_case.expected_result, max_chars=180),
        "tags": test_case.tags[:8],
    }


def build_requirement_extraction_prompt(prd_text: str, chunk_index: int | None = None) -> str:
    prefix = f"这是需求文档分段 #{chunk_index}。\n" if chunk_index is not None else ""
    return (
        f"{prefix}"
        "请从以下 PRD 文本中抽取结构化需求点，并严格输出 JSON。\n\n"
        f"PRD 文本：\n{prd_text}"
    )


def build_coverage_assessment_prompt(
    requirement_points: list[RequirementPoint],
    test_cases: list[TestCase],
    generate_missing_cases: bool,
    batch_index: int | None = None,
    total_batches: int | None = None,
) -> str:
    compact_requirements = [_compact_requirement(item) for item in requirement_points]
    compact_cases = [_compact_test_case(item) for item in test_cases]
    batch_prefix = ""
    if batch_index is not None and total_batches is not None:
        batch_prefix = f"当前是覆盖评估分批任务 {batch_index}/{total_batches}。\n"
    return (
        f"{batch_prefix}"
        "请根据以下结构化需求点与测试用例进行覆盖判断，严格输出 JSON。\n"
        f"当 generate_missing_cases={str(generate_missing_cases).lower()} 时，"
        "对未覆盖需求点尽量输出 suggested_case，否则返回 null。\n\n"
        f"需求点：\n{json.dumps(compact_requirements, ensure_ascii=False, indent=2)}\n\n"
        f"测试用例：\n{json.dumps(compact_cases, ensure_ascii=False, indent=2)}"
    )
