from __future__ import annotations


def chunk_text(text: str, chunk_size: int, overlap: int = 0) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    if len(cleaned) <= chunk_size:
        return [cleaned]

    paragraphs = [segment.strip() for segment in cleaned.split("\n\n") if segment.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        addition = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(addition) <= chunk_size:
            current = addition
            continue

        if current:
            chunks.append(current)
            tail = current[-overlap:] if overlap > 0 else ""
            current = f"{tail}\n{paragraph}".strip()
        else:
            for index in range(0, len(paragraph), chunk_size):
                step = paragraph[index : index + chunk_size]
                if chunks and overlap > 0:
                    step = f"{chunks[-1][-overlap:]}\n{step}".strip()
                chunks.append(step)
            current = ""

    if current:
        chunks.append(current)

    return chunks

