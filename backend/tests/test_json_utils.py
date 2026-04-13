from app.agent.models import RequirementExtractionPayload
from app.utils.json_utils import parse_json_model, parse_json_text


def test_parse_json_model_from_code_fence() -> None:
    raw = """```json
    {"requirements": []}
    ```"""
    parsed = parse_json_model(raw, RequirementExtractionPayload)
    assert parsed.requirements == []


def test_parse_json_text_removes_control_chars() -> None:
    raw = '{"requirements": []}\x00\x01'
    parsed = parse_json_text(raw)
    assert parsed == {"requirements": []}

