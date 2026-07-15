"""LLM provider factory."""

import time
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from loguru import logger

from app.config.settings import Settings, get_settings
from app.llm.provider import BaseLLMProvider, LLMResponse


class LangChainLLMProvider(BaseLLMProvider):
    """LangChain-backed LLM provider supporting multiple backends."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._chat_model = self._build_chat_model()
        self._current_groq_key_index = 0  # Track which Groq key is currently in use

    def _build_chat_model(self) -> BaseChatModel:
        provider = self.settings.llm_provider
        model = self.settings.llm_model
        temperature = self.settings.llm_temperature
        max_tokens = self.settings.llm_max_tokens

        if provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.settings.openai_api_key,
                timeout=self.settings.llm_timeout_seconds,
            )

        if provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.settings.anthropic_api_key,
                timeout=self.settings.llm_timeout_seconds,
            )

        if provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens,
                google_api_key=self.settings.google_api_key,
            )

        if provider == "ollama":
            from langchain_community.chat_models import ChatOllama

            return ChatOllama(
                model=model,
                temperature=temperature,
                base_url=self.settings.ollama_base_url,
            )

        if provider == "groq":
            from langchain_groq import ChatGroq

            # Use primary key initially
            api_key = self.settings.groq_api_key
            if not api_key and self.settings.groq_api_key_fallback:
                # If primary is not set, use fallback
                api_key = self.settings.groq_api_key_fallback
                self._current_groq_key_index = 1

            return ChatGroq(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                timeout=self.settings.llm_timeout_seconds,
            )

        raise ValueError(f"Unsupported LLM provider: {provider}")

    def get_chat_model(self) -> BaseChatModel:
        return self._chat_model

    @property
    def model_name(self) -> str:
        return self.settings.llm_model

    def _switch_groq_key(self) -> bool:
        """Switch to fallback Groq API key if available.
        
        Returns:
            bool: True if successfully switched to fallback key, False otherwise
        """
        if self.settings.llm_provider != "groq":
            return False
        
        # Check if we have a fallback key and haven't used it yet
        if self._current_groq_key_index == 0 and self.settings.groq_api_key_fallback:
            logger.warning("Primary Groq API key failed, switching to fallback key")
            self._current_groq_key_index = 1
            
            # Rebuild chat model with fallback key
            from langchain_groq import ChatGroq
            
            self._chat_model = ChatGroq(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                api_key=self.settings.groq_api_key_fallback,
                timeout=self.settings.llm_timeout_seconds,
            )
            return True
        
        # Check if we can switch back to primary key
        if self._current_groq_key_index == 1 and self.settings.groq_api_key:
            logger.warning("Fallback Groq API key failed, switching back to primary key")
            self._current_groq_key_index = 0
            
            # Rebuild chat model with primary key
            from langchain_groq import ChatGroq
            
            self._chat_model = ChatGroq(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                api_key=self.settings.groq_api_key,
                timeout=self.settings.llm_timeout_seconds,
            )
            return True
        
        return False

    async def invoke(self, messages: list[BaseMessage], **kwargs: Any) -> LLMResponse:
        start = time.perf_counter()
        
        try:
            response: AIMessage = await self._chat_model.ainvoke(messages, **kwargs)
        except Exception as e:
            # If Groq provider fails, try switching to fallback key
            if self.settings.llm_provider == "groq" and self._switch_groq_key():
                logger.info("Retrying with alternative Groq API key")
                try:
                    response: AIMessage = await self._chat_model.ainvoke(messages, **kwargs)
                except Exception as retry_error:
                    logger.error("Both Groq API keys failed: {}", retry_error)
                    raise
            else:
                # Not a Groq provider or no fallback available
                raise

        latency_ms = int((time.perf_counter() - start) * 1000)

        tokens_used = None
        if response.response_metadata:
            usage = response.response_metadata.get("token_usage", {})
            tokens_used = usage.get("total_tokens")

        key_info = ""
        if self.settings.llm_provider == "groq":
            key_info = f" key={self._current_groq_key_index + 1}"

        logger.debug(
            "LLM invoke provider={} model={} latency={}ms tokens={}{}",
            self.settings.llm_provider,
            self.model_name,
            latency_ms,
            tokens_used,
            key_info,
        )

        return LLMResponse(
            content=str(response.content),
            model=self.model_name,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
        )


class FallbackLLMProvider(BaseLLMProvider):
    """Deterministic safety provider used when an optional LLM package is missing."""

    def __init__(self, reason: str, settings: Settings | None = None) -> None:
        self.reason = reason
        self.settings = settings or get_settings()

    def get_chat_model(self) -> BaseChatModel:
        raise RuntimeError(f"No chat model available: {self.reason}")

    @property
    def model_name(self) -> str:
        return f"fallback:{self.settings.llm_provider}"

    async def invoke(self, messages: list[BaseMessage], **kwargs: Any) -> LLMResponse:
        start = time.perf_counter()
        text = "\n".join(str(message.content) for message in messages).lower()
        if "planner" in text:
            content = (
                '{"execution_order":["audit","technical","performance","content","reporting","monitoring"],'
                '"merge_strategy":"Safe fallback plan: analyze first and require approval before writes",'
                '"retry_policy":"retry failed read-only steps once"}'
            )
        elif "performance" in text:
            content = '{"score":70,"opportunities":["Review theme scripts","Compress oversized media","Watch Core Web Vitals"],"risk":"read_only"}'
        elif "monitoring" in text:
            content = '{"status":"checked","regressions":[],"next_check_recommendation":"Continue monitoring after the next sync"}'
        else:
            content = '{"status":"fallback","message":"LLM provider package missing; returned deterministic safe response"}'
        return LLMResponse(
            content=content,
            model=self.model_name,
            tokens_used=0,
            latency_ms=int((time.perf_counter() - start) * 1000),
            raw={"fallback_reason": self.reason},
        )


def get_llm_provider(settings: Settings | None = None) -> BaseLLMProvider:
    """Factory function - returns configured LLM provider.

    Optional provider packages may be absent in local development. Do not crash
    API dependency construction; use a deterministic fallback so agent endpoints
    still return useful workflow output instead of HTTP 500.
    """
    try:
        return LangChainLLMProvider(settings)
    except ModuleNotFoundError as exc:
        logger.warning("LLM provider package missing: {}. Using fallback provider.", exc.name)
        return FallbackLLMProvider(f"Missing optional package: {exc.name}", settings)
