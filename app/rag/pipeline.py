"""RAG indexing and retrieval pipeline."""

import uuid
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.rag.chunker import chunk_text
from app.rag.embedder import BaseEmbeddingProvider
from app.rag.embedding_factory import get_embedding_provider
from app.rag.loader import LoadedDocument
from app.rag.qdrant_store import get_vector_store
from app.rag.vector_store import BaseVectorStore, VectorPoint


class RAGPipeline:
    """Complete RAG pipeline: chunk → embed → store → retrieve."""

    KNOWLEDGE_COLLECTION = "knowledge"
    MEMORY_COLLECTION = "memory"

    def __init__(
        self,
        session: AsyncSession | None = None,
        settings: Settings | None = None,
        embedder: BaseEmbeddingProvider | None = None,
        vector_store: BaseVectorStore | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.embedder = embedder or get_embedding_provider(self.settings)
        self.vector_store = vector_store or get_vector_store(self.settings)

    async def initialize(self) -> None:
        """Ensure required collections exist."""
        # Skip initialization if embeddings are disabled
        if self.settings.embedding_provider == "none":
            logger.info("Embeddings disabled - skipping RAG initialization")
            return
            
        dims = self.embedder.dimensions
        await self.vector_store.ensure_collection(self.KNOWLEDGE_COLLECTION, dims)
        await self.vector_store.ensure_collection(self.MEMORY_COLLECTION, dims)
        logger.info("RAG collections initialized (dims={})", dims)

    async def index_document(
        self,
        document: LoadedDocument,
        collection: str = KNOWLEDGE_COLLECTION,
    ) -> dict[str, Any]:
        """Chunk, embed, and store a document."""
        chunks = chunk_text(document.content, self.settings)
        if not chunks:
            return {"indexed": 0, "document_hash": document.content_hash}

        embeddings = await self.embedder.embed_batch(chunks)
        doc_id = str(uuid.uuid4())

        points = [
            VectorPoint(
                id=str(uuid.uuid4()),
                vector=emb.vector,
                payload={
                    "document_id": doc_id,
                    "title": document.title,
                    "source": document.source,
                    "chunk_index": i,
                    "text": emb.text,
                    "content_hash": document.content_hash,
                    **document.metadata,
                },
            )
            for i, emb in enumerate(embeddings)
        ]

        count = await self.vector_store.upsert(collection, points)
        logger.info("Indexed {} chunks for document '{}'", count, document.title)
        return {
            "indexed": count,
            "document_id": doc_id,
            "document_hash": document.content_hash,
            "collection": collection,
        }

    async def retrieve(
        self,
        query: str,
        collection: str = KNOWLEDGE_COLLECTION,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic search over indexed documents.

        Retrieval is advisory context for agents. If the vector store is not
        ready, return an empty context instead of failing the workflow.
        """
        if self.settings.embedding_provider == "none":
            return []
        top_k = top_k or self.settings.rag_top_k
        try:
            await self.initialize()
            query_embedding = await self.embedder.embed_text(query)

            results = await self.vector_store.search(
                collection=collection,
                query_vector=query_embedding.vector,
                limit=top_k,
                filters=filters,
            )
        except Exception as exc:
            logger.warning("RAG retrieval skipped for collection={}: {}", collection, exc)
            return []

        return [
            {
                "score": r.score,
                "text": r.payload.get("text", ""),
                "title": r.payload.get("title", ""),
                "source": r.payload.get("source", ""),
                "metadata": r.payload,
            }
            for r in results
        ]

    async def index_memory(
        self,
        key: str,
        content: str,
        memory_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Index a memory entry for semantic retrieval."""
        if self.settings.embedding_provider == "none":
            return str(uuid.uuid4())
        await self.initialize()
        embedding = await self.embedder.embed_text(content)
        point_id = str(uuid.uuid4())

        point = VectorPoint(
            id=point_id,
            vector=embedding.vector,
            payload={
                "key": key,
                "content": content,
                "memory_type": memory_type,
                **(metadata or {}),
            },
        )

        await self.vector_store.upsert(self.MEMORY_COLLECTION, [point])
        return point_id

    async def retrieve_memory(
        self,
        query: str,
        memory_type: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic memory retrieval."""
        filters = {"memory_type": memory_type} if memory_type else None
        return await self.retrieve(
            query,
            collection=self.MEMORY_COLLECTION,
            top_k=top_k,
            filters=filters,
        )
