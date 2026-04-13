from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.utils.exceptions import FileMissingError, ScannedPdfNotSupportedError, UnsupportedFileTypeError


def read_pdf_file(file_path: Path) -> str:
    if not file_path.exists():
        raise FileMissingError(f"文件不存在: {file_path}")
    if file_path.suffix.lower() != ".pdf":
        raise UnsupportedFileTypeError(f"不支持的 PDF 文件类型: {file_path.suffix}")

    reader = PdfReader(str(file_path))
    page_texts: list[str] = []

    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        page_texts.append(text)

    merged = "\n\n".join(text for text in page_texts if text)
    if not merged.strip():
        raise ScannedPdfNotSupportedError(
            "PDF 未提取到可用文本，当前版本仅支持文本型 PDF，不支持扫描件 OCR。"
        )
    return merged

