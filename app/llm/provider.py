"""LLM provider abstraction — configurable without code changes."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """Structured LLM response."""

    content: str
    model: str
    tokens_used: int | None = None
    latency_ms: int | None = None
    raw: dict[str, Any] | None = None


class BaseLLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        """Return the underlying LangChain chat model."""

    @abstractmethod
    async def invoke(
        self,
        messages: list[BaseMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Send messages and return structured response."""

    async def invoke_prompt(
        self,
        system: str,
        user: str,
        **kwargs: Any,
    ) -> LLMResponse:
        """Convenience method for system + user messages."""
        messages = [SystemMessage(content=system), HumanMessage(content=user)]
        return await self.invoke(messages, **kwargs)

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the configured model name."""
