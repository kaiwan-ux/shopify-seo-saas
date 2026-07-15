"""Document chunking for RAG indexing."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import Settings, get_settings


def get_text_splitter(settings: Settings | None = None) -> RecursiveCharacterTextSplitter:
    settings = settings or get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def chunk_text(text: str, settings: Settings | None = None) -> list[str]:
    """Split text into chunks for embedding."""
    splitter = get_text_splitter(settings)
    return splitter.split_text(text)
