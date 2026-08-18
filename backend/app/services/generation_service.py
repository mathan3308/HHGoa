import httpx
import re
from typing import List, Dict, Any
from backend.app.config import settings
from backend.app.core.exceptions import LLMException
from backend.app.core.logging import logger
from backend.app.rag.prompts.answer_prompt import STRICT_GROUNDED_ANSWER_PROMPT

class BaseLLMProvider:
    async def generate_answer(self, query: str, context_passages: List[Dict[str, Any]]) -> str:
        raise NotImplementedError

class SarvamLLMProvider(BaseLLMProvider):
    """Sarvam AI LLM provider using sarvam-105b-conversations model."""
    def __init__(self, api_key: str, model: str = "sarvam-105b-conversations"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.sarvam.ai/v1/chat/completions"

    async def generate_answer(self, query: str, context_passages: List[Dict[str, Any]]) -> str:
        if not self.api_key:
            raise LLMException("SARVAM_API_KEY is not configured.")

        # Build formatted context text from retrieved passages
        formatted_passages = ""
        for idx, doc in enumerate(context_passages, start=1):
            source = doc.get("source_id", f"Passage_{idx}")
            text = doc.get("text", "").strip()
            formatted_passages += f"[{source}]: {text}\n\n"

        prompt = STRICT_GROUNDED_ANSWER_PROMPT.format(
            context_passages=formatted_passages.strip(),
            user_query=query
        )

        headers = {
            "api-subscription-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Answer the user query strictly and accurately based on the provided context passages."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 256
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(self.url, headers=headers, json=payload)
                if response.status_code == 200:
                    res_json = response.json()
                    answer = res_json["choices"][0]["message"]["content"].strip()
                    return answer
                else:
                    logger.warning(f"Sarvam LLM API error {response.status_code}: {response.text}")
                    # Fallback to local context synthesis provider
                    mock = MockLLMProvider()
                    return await mock.generate_answer(query, context_passages)
            except Exception as e:
                logger.error(f"HTTP request to Sarvam LLM failed: {str(e)}")
                mock = MockLLMProvider()
                return await mock.generate_answer(query, context_passages)

class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider generating query-specific grounded responses from retrieved context."""
    async def generate_answer(self, query: str, context_passages: List[Dict[str, Any]]) -> str:
        if not context_passages:
            return "I couldn't find enough information in the provided dataset to answer that question."

        query_clean = query.lower()
        query_words = set(re.findall(r'\w+', query_clean))

        # Find best matching sentence across context passages
        best_sentence = ""
        best_overlap = -1

        for doc in context_passages:
            text = doc.get("text", "")
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for s in sentences:
                s_words = set(re.findall(r'\w+', s.lower()))
                overlap = len(query_words.intersection(s_words))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_sentence = s.strip()

        if best_sentence and best_overlap > 0:
            return f"Based on the dataset: {best_sentence}"

        # Default summary from top doc
        first_doc = context_passages[0].get("text", "").strip()
        if len(first_doc) > 180:
            first_doc = first_doc[:180] + "..."
        return f"Based on the dataset: {first_doc}"

class GenerationService:
    def __init__(self):
        if settings.MOCK_EXTERNAL_SERVICES or not settings.SARVAM_API_KEY:
            self.provider = MockLLMProvider()
        else:
            self.provider = SarvamLLMProvider(
                api_key=settings.SARVAM_API_KEY,
                model=settings.SARVAM_LLM_MODEL
            )

    async def generate(self, query: str, context_passages: List[Dict[str, Any]]) -> str:
        return await self.provider.generate_answer(query, context_passages)
