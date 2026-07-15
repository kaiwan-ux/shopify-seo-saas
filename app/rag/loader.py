"""Document loading utilities for RAG."""

import hashlib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class LoadedDocument(BaseModel):
    """A loaded document ready for chunking."""

    title: str
    content: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()


def load_text_file(path: str | Path, source: str = "internal") -> LoadedDocument:
    """Load a plain text or markdown file."""
    path = Path(path)
    content = path.read_text(encoding="utf-8")
    return LoadedDocument(
        title=path.stem,
        content=content,
        source=source,
        metadata={"file_path": str(path)},
    )


def load_text_content(
    title: str,
    content: str,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> LoadedDocument:
    """Create a LoadedDocument from raw text."""
    return LoadedDocument(
        title=title,
        content=content,
        source=source,
        metadata=metadata or {},
    )
