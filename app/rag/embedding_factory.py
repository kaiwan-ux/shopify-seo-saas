"""Embedding provider factory."""

from app.config.settings import Settings, get_settings
from app.rag.embedder import BaseEmbeddingProvider, EmbeddingResult


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, settings: Settings) -> None:
        from langchain_openai import OpenAIEmbeddings

        self._embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
        self._model = settings.embedding_model
        self._dims = settings.embedding_dimensions

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dims

    async def embed_text(self, text: str) -> EmbeddingResult:
        vector = await self._embeddings.aembed_query(text)
        return EmbeddingResult(text=text, vector=vector, model=self._model, dimensions=len(vector))

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        vectors = await self._embeddings.aembed_documents(texts)
        return [
            EmbeddingResult(text=t, vector=v, model=self._model, dimensions=len(v))
            for t, v in zip(texts, vectors, strict=True)
        ]


class NomicEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, settings: Settings) -> None:
        from langchain_community.embeddings import OllamaEmbeddings

        self._embeddings = OllamaEmbeddings(
            model=settings.embedding_model or "nomic-embed-text",
            base_url=settings.ollama_base_url,
        )
        self._model = settings.embedding_model or "nomic-embed-text"
        self._dims = settings.embedding_dimensions

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dims

    async def embed_text(self, text: str) -> EmbeddingResult:
        vector = await self._embeddings.aembed_query(text)
        return EmbeddingResult(text=text, vector=vector, model=self._model, dimensions=len(vector))

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        vectors = await self._embeddings.aembed_documents(texts)
        return [
            EmbeddingResult(text=t, vector=v, model=self._model, dimensions=len(v))
            for t, v in zip(texts, vectors, strict=True)
        ]


class BGEEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, settings: Settings) -> None:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        model_name = settings.embedding_model or "BAAI/bge-small-en-v1.5"
        self._embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self._model = model_name
        self._dims = settings.embedding_dimensions

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dims

    async def embed_text(self, text: str) -> EmbeddingResult:
        vector = await self._embeddings.aembed_query(text)
        return EmbeddingResult(text=text, vector=vector, model=self._model, dimensions=len(vector))

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        vectors = await self._embeddings.aembed_documents(texts)
        return [
            EmbeddingResult(text=t, vector=v, model=self._model, dimensions=len(v))
            for t, v in zip(texts, vectors, strict=True)
        ]


class NoOpEmbeddingProvider(BaseEmbeddingProvider):
    """No-op embedding provider that returns empty vectors when embeddings are disabled."""
    
    def __init__(self, settings: Settings) -> None:
        self._model = "none"
        self._dims = 0

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dims

    async def embed_text(self, text: str) -> EmbeddingResult:
        # Return empty vector when embeddings are disabled
        return EmbeddingResult(text=text, vector=[], model=self._model, dimensions=0)

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        # Return empty vectors when embeddings are disabled
        return [
            EmbeddingResult(text=t, vector=[], model=self._model, dimensions=0)
            for t in texts
        ]


def get_embedding_provider(settings: Settings | None = None) -> BaseEmbeddingProvider:
    settings = settings or get_settings()
    providers = {
        "openai": OpenAIEmbeddingProvider,
        "nomic": NomicEmbeddingProvider,
        "bge": BGEEmbeddingProvider,
        "none": NoOpEmbeddingProvider,
    }
    cls = providers.get(settings.embedding_provider)
    if cls is None:
        raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
    return cls(settings)
