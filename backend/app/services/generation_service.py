import httpx
from typing import List, Dict, Any
from backend.app.config import settings
from backend.app.core.exceptions import LLMException
from backend.app.core.logging import logger
from backend.app.rag.prompts.answer_prompt import STRICT_GROUNDED_ANSWER_PROMPT

class BaseLLMProvider:
    async def generate_answer(self, query: str, context_passages: List[Dict[str, Any]]) -> str:
        raise NotImplementedError

class SarvamLLMProvider(BaseLLMProvider):
    """Sarvam AI LLM provider using sarvam-30b model."""
    def __init__(self, api_key: str, model: str = "sarvam-30b"):
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You answer strictly from retrieved passages."},
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
                    raise LLMException(f"Sarvam LLM API error {response.status_code}: {response.text}")
            except httpx.HTTPError as e:
                raise LLMException(f"HTTP request to Sarvam LLM failed: {str(e)}")

class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider generating grounded mock responses from context."""
    async def generate_answer(self, query: str, context_passages: List[Dict[str, Any]]) -> str:
        if not context_passages:
            return "I couldn't find enough information in the provided dataset to answer that question."
        
        first_doc = context_passages[0].get("text", "")
        if not first_doc:
            return "I couldn't find enough information in the provided dataset to answer that question."

        # Synthesize a concise response based on retrieved passage text
        summary = first_doc.strip()
        if len(summary) > 200:
            summary = summary[:200] + "..."

        return f"Based on the dataset: {summary}"

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
