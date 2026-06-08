from abc import ABC, abstractmethod

from app.core.config import Settings
from app.core.exceptions import LLMConfigurationError, LLMProviderError, LLMQuotaError
from app.models.schemas import ChatMessage, Source


class LLMClient(ABC):
    @abstractmethod
    async def answer(self, question: str, sources: list[Source], history: list[ChatMessage]) -> str:
        raise NotImplementedError


class OpenAIClient(LLMClient):
    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Create backend/.env and add OPENAI_API_KEY=your_key, then restart FastAPI."
            )
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def answer(self, question: str, sources: list[Source], history: list[ChatMessage]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=build_messages(question, sources, history),
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise map_openai_error(exc) from exc


class GeminiClient(LLMClient):
    def __init__(self, settings: Settings):
        if not settings.gemini_api_key:
            raise LLMConfigurationError(
                "GEMINI_API_KEY is required when LLM_PROVIDER=gemini. "
                "Create backend/.env and add GEMINI_API_KEY=your_key, then restart FastAPI."
            )
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        self.genai = genai
        self.model_names = gemini_model_candidates(settings.gemini_model)

    async def answer(self, question: str, sources: list[Source], history: list[ChatMessage]) -> str:
        prompt = "\n".join(message["content"] for message in build_messages(question, sources, history))
        last_error: LLMProviderError | None = None
        for model_name in self.model_names:
            try:
                model = self.genai.GenerativeModel(model_name)
                response = await model.generate_content_async(prompt)
                return response.text or ""
            except Exception as exc:
                mapped_error = map_gemini_error(exc, model_name)
                last_error = mapped_error
                if isinstance(mapped_error, LLMQuotaError):
                    continue
                raise mapped_error from exc
        raise last_error or LLMProviderError("Gemini request failed for all configured models.")


def get_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "gemini":
        return GeminiClient(settings)
    return OpenAIClient(settings)


def normalize_gemini_model(model_name: str) -> str:
    normalized = model_name.strip()
    if normalized.startswith("models/"):
        normalized = normalized.removeprefix("models/")
    stale_aliases = {
        "gemini-1.5-flash": "gemini-2.0-flash-lite",
        "gemini-1.5-flash-latest": "gemini-2.0-flash-lite",
    }
    return stale_aliases.get(normalized, normalized)


def gemini_model_candidates(model_name: str) -> list[str]:
    preferred = normalize_gemini_model(model_name)
    fallbacks = [
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
    ]
    candidates = [preferred, *fallbacks]
    return list(dict.fromkeys(candidates))


def map_gemini_error(exc: Exception, model_name: str) -> LLMProviderError:
    message = str(exc)
    lower_message = message.lower()
    if "404" in message and ("not found" in message.lower() or "not supported" in message.lower()):
        return LLMConfigurationError(
            f"Gemini model '{model_name}' is not available for generateContent. "
            "Set GEMINI_MODEL=gemini-2.0-flash in backend/.env, or run the Gemini ListModels API "
            "and choose a model that supports generateContent. Restart FastAPI after changing .env."
        )
    if "429" in message or "quota exceeded" in lower_message or "rate-limits" in lower_message:
        return LLMQuotaError(
            f"Gemini quota is exhausted for model '{model_name}' on this API key/project. "
            "The app can still return retrieved document sources, but Gemini cannot generate an answer until quota is available."
        )
    return LLMProviderError(f"Gemini request failed: {exc}")


def map_openai_error(exc: Exception) -> LLMProviderError:
    status_code = getattr(exc, "status_code", None)
    body = getattr(exc, "body", None) or {}
    error = body.get("error", {}) if isinstance(body, dict) else {}
    code = error.get("code")

    if status_code == 429 and code == "insufficient_quota":
        return LLMQuotaError(
            "OpenAI rejected the request because this API key has insufficient quota. "
            "Add billing/credits to the OpenAI account, use another key, or switch LLM_PROVIDER to gemini."
        )
    if status_code == 429:
        return LLMQuotaError("OpenAI rate limit reached. Wait a moment and try again, or use another provider.")
    if status_code in {401, 403}:
        return LLMConfigurationError("OpenAI rejected the API key. Check OPENAI_API_KEY in backend/.env and restart FastAPI.")
    return LLMProviderError(f"OpenAI request failed: {exc}")


def build_messages(question: str, sources: list[Source], history: list[ChatMessage]) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"[{idx}] {source.filename}, page {source.page}, score {source.score:.3f}\n{source.text}"
        for idx, source in enumerate(sources, start=1)
    )
    system = (
        "You are a careful document question-answering assistant. "
        "Answer only from the provided context. If the context is insufficient, say so. "
        "Cite sources inline using [1], [2], etc. Keep answers concise and factual."
    )
    trimmed_history = history[-8:]
    messages = [{"role": "system", "content": system}]
    messages.extend({"role": item.role, "content": item.content} for item in trimmed_history)
    messages.append(
        {
            "role": "user",
            "content": f"Context:\n{context or 'No relevant context found.'}\n\nQuestion: {question}",
        }
    )
    return messages
