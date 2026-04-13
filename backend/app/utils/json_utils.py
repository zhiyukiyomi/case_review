from __future__ import annotations

import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.utils.exceptions import LLMInvalidJSONError


_T = TypeVar("_T", bound=BaseModel)


def _strip_code_fences(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.replace("\ufeff", "").strip()


def _remove_invalid_control_chars(text: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)


def _extract_json_slice(text: str) -> str:
    if not text:
        raise LLMInvalidJSONError("LLM returned an empty response.")

    start_candidates = [idx for idx in (text.find("{"), text.find("[")) if idx != -1]
    if not start_candidates:
        raise LLMInvalidJSONError("LLM response does not contain JSON data.")

    start = min(start_candidates)
    end_object = text.rfind("}")
    end_array = text.rfind("]")
    end = max(end_object, end_array)
    if end == -1 or end < start:
        raise LLMInvalidJSONError("Unable to identify a complete JSON payload.")
    return text[start : end + 1]


def parse_json_text(raw_text: str) -> Any:
    text = _remove_invalid_control_chars(_strip_code_fences(raw_text))
    candidate = _extract_json_slice(text)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise LLMInvalidJSONError(f"LLM returned invalid JSON: {exc}") from exc


def parse_json_model(raw_text: str, model_type: type[_T]) -> _T:
    payload = parse_json_text(raw_text)
    try:
        return model_type.model_validate(payload)
    except ValidationError as exc:
        raise LLMInvalidJSONError(f"JSON validation failed: {exc}") from exc
