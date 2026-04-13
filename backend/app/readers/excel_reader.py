from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.agent.models import TestCase
from app.utils.exceptions import ExcelColumnMissingError, FileMissingError, UnsupportedFileTypeError


COLUMN_ALIASES: dict[str, list[str]] = {
    "case_id": ["case_id", "id", "用例id", "测试用例id", "编号", "case id"],
    "title": ["title", "标题", "用例标题", "测试标题", "名称"],
    "preconditions": ["preconditions", "前置条件", "前提条件"],
    "steps": ["steps", "步骤", "测试步骤", "执行步骤", "操作步骤"],
    "expected_result": ["expected_result", "预期结果", "expected", "结果"],
    "tags": ["tags", "标签", "tag"],
}

REQUIRED_FIELDS = {"case_id", "title", "steps", "expected_result"}


def _normalize_column(value: str) -> str:
    return value.strip().lower().replace("\n", " ").replace("_", " ")


def _resolve_columns(columns: list[str]) -> dict[str, str]:
    normalized_mapping = {_normalize_column(column): column for column in columns}
    resolved: dict[str, str] = {}

    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            normalized = _normalize_column(alias)
            if normalized in normalized_mapping:
                resolved[canonical] = normalized_mapping[normalized]
                break

    missing = REQUIRED_FIELDS - resolved.keys()
    if missing:
        raise ExcelColumnMissingError(
            f"Excel 缺少必要列: {', '.join(sorted(missing))}。支持列名示例: {COLUMN_ALIASES}"
        )
    return resolved


def read_test_cases(file_path: Path, sheet_name: str | None = None) -> list[TestCase]:
    if not file_path.exists():
        raise FileMissingError(f"文件不存在: {file_path}")
    if file_path.suffix.lower() != ".xlsx":
        raise UnsupportedFileTypeError(f"不支持的测试用例文件类型: {file_path.suffix}")

    dataframe = pd.read_excel(file_path, sheet_name=sheet_name or 0)
    if dataframe.empty:
        return []

    dataframe = dataframe.fillna("")
    resolved = _resolve_columns(dataframe.columns.astype(str).tolist())

    cases: list[TestCase] = []
    for _, row in dataframe.iterrows():
        case_id = str(row.get(resolved["case_id"], "")).strip()
        title = str(row.get(resolved["title"], "")).strip()
        steps = str(row.get(resolved["steps"], "")).strip()
        expected = str(row.get(resolved["expected_result"], "")).strip()

        if not any([case_id, title, steps, expected]):
            continue

        tags_value = str(row.get(resolved.get("tags", ""), "")).strip() if "tags" in resolved else ""
        tags = [item.strip() for item in tags_value.replace("，", ",").split(",") if item.strip()]

        preconditions = ""
        if "preconditions" in resolved:
            preconditions = str(row.get(resolved["preconditions"], "")).strip()

        cases.append(
            TestCase(
                case_id=case_id or f"AUTO-{len(cases) + 1:03d}",
                title=title or "未命名测试用例",
                preconditions=preconditions,
                steps=steps,
                expected_result=expected,
                tags=tags,
            )
        )
    return cases
