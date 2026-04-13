from __future__ import annotations

from pathlib import Path

from app.utils.exceptions import FileMissingError, UnsupportedFileTypeError


SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md"}


def read_text_file(file_path: Path) -> str:
    if not file_path.exists():
        raise FileMissingError(f"文件不存在: {file_path}")
    if file_path.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
        raise UnsupportedFileTypeError(f"不支持的文本文件类型: {file_path.suffix}")
    return file_path.read_text(encoding="utf-8")

