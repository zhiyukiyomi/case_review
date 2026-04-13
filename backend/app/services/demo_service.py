from __future__ import annotations

from pathlib import Path

from app.agent.models import CoverageMapping, CoverageResult, DimensionScore, RequirementPoint, TestCase
from app.utils.report_generator import generate_markdown_report


def build_demo_result(
    *,
    prd_path: Path,
    test_case_path: Path,
    sheet_name: str | None = None,
    generate_missing_cases: bool = True,
) -> dict:
    requirement_points = [
        RequirementPoint(
            id="REQ-001",
            module="登录",
            type="functional",
            description="用户可以使用手机号和密码登录系统。",
            priority="high",
            source_text="支持手机号和密码登录。",
        ),
        RequirementPoint(
            id="REQ-002",
            module="登录",
            type="business_rule",
            description="密码连续错误 5 次后，账号锁定 10 分钟。",
            priority="high",
            source_text="密码连续输错 5 次后限制登录 10 分钟。",
        ),
        RequirementPoint(
            id="REQ-003",
            module="登录",
            type="boundary_condition",
            description="密码长度上限为 20 位，达到上限后仍允许提交校验。",
            priority="medium",
            source_text="密码最长支持 20 位。",
        ),
        RequirementPoint(
            id="REQ-004",
            module="登录",
            type="non_functional",
            description="登录接口在正常流量下 2 秒内返回。",
            priority="medium",
            source_text="登录接口响应时间不超过 2 秒。",
        ),
    ]

    test_cases = [
        TestCase(
            case_id="TC-001",
            title="手机号密码登录成功",
            preconditions="用户已注册且账号状态正常",
            steps="输入正确手机号和密码，点击登录按钮。",
            expected_result="登录成功并跳转到首页。",
            tags=["登录", "正向"],
        ),
        TestCase(
            case_id="TC-002",
            title="登录接口性能验证",
            preconditions="接口服务可用",
            steps="模拟正常流量发起登录请求并记录响应时间。",
            expected_result="接口响应时间不超过 2 秒。",
            tags=["登录", "性能"],
        ),
    ]

    generated_cases = (
        [
            TestCase(
                case_id="GEN-001",
                title="连续输错密码 5 次后账号锁定",
                preconditions="账号状态正常，已知正确密码",
                steps="连续 5 次输入错误密码后再次尝试登录。",
                expected_result="系统提示账号锁定 10 分钟，期间禁止继续登录。",
                tags=["登录", "异常", "锁定"],
            ),
            TestCase(
                case_id="GEN-002",
                title="20 位密码边界提交校验",
                preconditions="账号状态正常",
                steps="输入长度为 20 位的合法密码并提交登录。",
                expected_result="系统允许提交，并按密码正确性返回结果。",
                tags=["登录", "边界"],
            ),
        ]
        if generate_missing_cases
        else []
    )

    coverage_mappings = [
        CoverageMapping(
            requirement_id="REQ-001",
            covered=True,
            matched_case_ids=["TC-001"],
            rationale="TC-001 覆盖了登录成功主流程。",
        ),
        CoverageMapping(
            requirement_id="REQ-002",
            covered=False,
            missing_reason="当前缺少连续输错密码后的锁定验证用例。",
            suggested_case=generated_cases[0] if generated_cases else None,
        ),
        CoverageMapping(
            requirement_id="REQ-003",
            covered=False,
            missing_reason="当前未覆盖 20 位密码的边界提交行为。",
            suggested_case=generated_cases[1] if len(generated_cases) > 1 else None,
        ),
        CoverageMapping(
            requirement_id="REQ-004",
            covered=True,
            matched_case_ids=["TC-002"],
            rationale="TC-002 覆盖了登录接口性能要求。",
        ),
    ]

    missing_points = [requirement_points[1], requirement_points[2]]
    covered_points = [requirement_points[0], requirement_points[3]]

    coverage_result = CoverageResult(
        score=72,
        level="存在遗漏，需补充",
        dimension_scores={
            "core_function": DimensionScore(score=50, full_score=50, reason="核心登录主流程已覆盖。"),
            "business_rules_and_boundaries": DimensionScore(
                score=12,
                full_score=25,
                reason="缺少密码错误锁定规则与 20 位密码边界测试。",
            ),
            "exception_flows": DimensionScore(
                score=0,
                full_score=15,
                reason="未覆盖密码连续输错后的异常与逆向流程。",
            ),
            "non_functional": DimensionScore(score=10, full_score=10, reason="已覆盖登录接口性能要求。"),
        },
        covered_points=covered_points,
        missing_points=missing_points,
        suggestions=[
            "补充密码连续输错 5 次后的锁定与解锁测试。",
            "补充 20 位密码的边界提交与校验测试。",
        ],
        generated_cases=generated_cases,
        requirement_points=requirement_points,
        test_cases=test_cases,
        coverage_mappings=coverage_mappings,
    )
    coverage_result.markdown_report = generate_markdown_report(coverage_result)

    payload = coverage_result.model_dump()
    payload["metadata"] = {
        "mode": "demo",
        "sheet_name": sheet_name or "first_sheet",
        "prd_file_name": prd_path.name,
        "test_case_file_name": test_case_path.name,
        "note": "Demo mode returns a built-in sample result without calling DeepSeek.",
    }
    return payload
