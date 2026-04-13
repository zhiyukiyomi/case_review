from app.agent.coverage_agent import CoverageAgent
from app.agent.models import CoverageAssessmentPayload, CoverageMapping, RequirementPoint
from app.config import settings


class FakeLLMClient:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def invoke_json(self, *, system_prompt: str, user_prompt: str, response_model):  # type: ignore[override]
        self.calls.append(user_prompt)
        batch_number = len(self.calls)
        if batch_number == 1:
            return CoverageAssessmentPayload(
                mappings=[
                    CoverageMapping(requirement_id="REQ-001", covered=True, matched_case_ids=["TC-001"]),
                    CoverageMapping(requirement_id="REQ-002", covered=False, missing_reason="缺少边界用例"),
                ],
                suggestions=["补充边界值测试"],
            )
        return CoverageAssessmentPayload(
            mappings=[
                CoverageMapping(requirement_id="REQ-003", covered=False, missing_reason="缺少异常用例"),
            ],
            suggestions=["补充异常流程测试"],
        )


def test_evaluate_coverage_batches_and_fills_missing_requirements() -> None:
    original_batch_size = settings.coverage_batch_size
    settings.coverage_batch_size = 2
    try:
        agent = CoverageAgent(llm_client=FakeLLMClient())  # type: ignore[arg-type]
        requirements = [
            RequirementPoint(
                id="REQ-001",
                module="A",
                type="functional",
                description="d1",
                priority="high",
                source_text="s1",
            ),
            RequirementPoint(
                id="REQ-002",
                module="A",
                type="functional",
                description="d2",
                priority="high",
                source_text="s2",
            ),
            RequirementPoint(
                id="REQ-003",
                module="A",
                type="functional",
                description="d3",
                priority="high",
                source_text="s3",
            ),
            RequirementPoint(
                id="REQ-004",
                module="A",
                type="functional",
                description="d4",
                priority="high",
                source_text="s4",
            ),
        ]

        payload = agent._evaluate_coverage(requirements, test_cases=[], generate_missing_cases=True)

        assert len(agent.llm_client.calls) == 2
        assert [item.requirement_id for item in payload.mappings] == ["REQ-001", "REQ-002", "REQ-003", "REQ-004"]
        assert payload.mappings[-1].covered is False
        assert payload.mappings[-1].missing_reason == "模型未返回该需求点的覆盖判断，请人工复核。"
        assert payload.suggestions == ["补充边界值测试", "补充异常流程测试"]
    finally:
        settings.coverage_batch_size = original_batch_size
