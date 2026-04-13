from app.agent.models import CoverageMapping, RequirementPoint, TestCase
from app.agent.scorer import calculate_coverage_result


def test_calculate_coverage_result() -> None:
    requirements = [
        RequirementPoint(
            id="REQ-001",
            module="登录",
            type="functional",
            description="用户可以使用手机号登录",
            priority="high",
            source_text="支持手机号登录",
        ),
        RequirementPoint(
            id="REQ-002",
            module="登录",
            type="exception_scenario",
            description="密码错误时提示失败",
            priority="medium",
            source_text="密码错误时提示失败",
        ),
    ]
    mappings = [
        CoverageMapping(
            requirement_id="REQ-001",
            covered=True,
            matched_case_ids=["TC-001"],
            rationale="已覆盖",
        ),
        CoverageMapping(
            requirement_id="REQ-002",
            covered=False,
            missing_reason="无异常用例",
        ),
    ]
    cases = [
        TestCase(
            case_id="TC-001",
            title="手机号登录",
            steps="输入手机号和密码",
            expected_result="登录成功",
            tags=["登录"],
        )
    ]
    result = calculate_coverage_result(requirements, cases, mappings, ["补齐异常场景"])
    assert result.score == 85
    assert result.dimension_scores["core_function"].score == 50
    assert result.dimension_scores["exception_flows"].score == 0

