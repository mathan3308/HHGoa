import uuid
import time
from typing import Dict, Any, Optional

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.models.response_models import VoiceQueryResponse, LatencyBreakdown, SourceChunk, GroundingResult
from backend.app.utils.timers import LatencyTimer
from backend.app.guardrails.input_guard import InputGuard
from backend.app.guardrails.relevance_guard import RelevanceGuard
from backend.app.guardrails.safety_guard import SafetyGuard
from backend.app.guardrails.grounding_guard import GroundingGuard
from backend.app.services.speech_service import SpeechService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.generation_service import GenerationService
from backend.app.services.reranking_service import RerankingService
from backend.app.services.benchmark_service import BenchmarkService

class VoiceRAGPipeline:
    """
    Main Orchestrator pipeline for Voice-Enabled RAG System.
    Flow:
    Audio -> STT -> Input Guard -> Embedding -> Hybrid RRF Retrieval -> Reranking -> Relevance Guard -> Prompt -> LLM Gen -> Grounding Guard -> Response
    """
    def __init__(self):
        self.speech_service = SpeechService()
        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService()
        self.generation_service = GenerationService()
        self.reranking_service = RerankingService()
        self.input_guard = InputGuard()
        self.relevance_guard = RelevanceGuard(threshold=settings.RETRIEVAL_THRESHOLD)
        self.safety_guard = SafetyGuard()
        self.grounding_guard = GroundingGuard(threshold=settings.GROUNDING_THRESHOLD)
        self.benchmark_service = BenchmarkService()

    async def process_voice_query(self, audio_bytes: bytes, filename: str = "audio.wav", request_id: str = None) -> VoiceQueryResponse:
        request_id = request_id or str(uuid.uuid4())
        logger.info("Starting voice query pipeline", request_id=request_id)

        latency = LatencyBreakdown()
        start_e2e = time.perf_counter()

        # 1. Speech-to-Text
        t_stt = LatencyTimer().start()
        stt_res = await self.speech_service.transcribe_audio(audio_bytes, filename)
        latency.stt_ms = t_stt.stop()
        logger.info(f"STT completed: {latency.stt_ms}ms | text='{stt_res.text}'", request_id=request_id)

        transcript = stt_res.text
        language = stt_res.language

        # 2. Run pure text RAG pipeline
        response = await self.process_text_query(
            query=transcript,
            language=language,
            request_id=request_id,
            stt_latency_ms=latency.stt_ms
        )

        response.latency.total_end_to_end_ms = round((time.perf_counter() - start_e2e) * 1000.0, 2)
        return response

    async def process_text_query(
        self,
        query: str,
        language: str = "en",
        request_id: str = None,
        stt_latency_ms: float = 0.0
    ) -> VoiceQueryResponse:
        request_id = request_id or str(uuid.uuid4())
        logger.info(f"Processing text query: '{query}'", request_id=request_id)

        latency = LatencyBreakdown(stt_ms=stt_latency_ms)
        start_rag = time.perf_counter()

        # 1. Tier 1 Input Safety Guard
        t_guard = LatencyTimer().start()
        valid_input, msg = self.input_guard.validate(query)
        if not valid_input:
            latency.guardrail_ms = t_guard.stop()
            latency.total_rag_ms = latency.guardrail_ms
            latency.total_end_to_end_ms = round(stt_latency_ms + latency.total_rag_ms, 2)
            return VoiceQueryResponse(
                request_id=request_id,
                transcript=query,
                language=language,
                answer=f"Refusal: {msg}",
                grounded=False,
                grounding_details=GroundingResult(grounded=False, reason=msg),
                sources=[],
                latency=latency,
                status="rejected",
                error=msg,
                mock_mode=settings.MOCK_EXTERNAL_SERVICES
            )

        # 2. Embedding Generation
        t_emb = LatencyTimer().start()
        _ = self.embedding_service.embed_query(query)
        latency.embedding_ms = t_emb.stop()
        logger.info(f"Embedding completed: {latency.embedding_ms}ms", request_id=request_id)

        # 3. Dense + Sparse + RRF Retrieval
        t_ret = LatencyTimer().start()
        retrieved_docs = self.retrieval_service.hybrid_retrieve(
            query=query,
            top_k=settings.TOP_K,
            filter_strategy=None
        )
        latency.retrieval_ms = t_ret.stop()
        logger.info(f"Retrieval completed: {latency.retrieval_ms}ms | docs={len(retrieved_docs)}", request_id=request_id)

        # 4. Optional Reranking
        t_rerank = LatencyTimer().start()
        top_passages = self.reranking_service.rerank(query, retrieved_docs, top_k=settings.MAX_CONTEXT_CHUNKS)
        latency.reranking_ms = t_rerank.stop()

        # 5. Tier 2 Relevance Guard
        has_context, rel_msg = self.relevance_guard.validate(top_passages)
        if not has_context:
            guard_extra = t_guard.stop()
            latency.guardrail_ms = round(latency.guardrail_ms + guard_extra, 2)
            latency.total_rag_ms = round((time.perf_counter() - start_rag) * 1000.0, 2)
            latency.total_end_to_end_ms = round(stt_latency_ms + latency.total_rag_ms, 2)
            refusal_text = "I couldn't find relevant information in the provided dataset."
            return VoiceQueryResponse(
                request_id=request_id,
                transcript=query,
                language=language,
                answer=refusal_text,
                grounded=False,
                grounding_details=GroundingResult(grounded=False, reason="insufficient_retrieval_context"),
                sources=[],
                latency=latency,
                status="completed",
                mock_mode=settings.MOCK_EXTERNAL_SERVICES
            )

        # 6. LLM Answer Generation
        t_gen = LatencyTimer().start()
        answer_text = await self.generation_service.generate(query, top_passages)
        latency.generation_ms = t_gen.stop()
        logger.info(f"Generation completed: {latency.generation_ms}ms", request_id=request_id)

        # 7. Tier 4 Grounding Validator
        grounding_res = self.grounding_guard.validate(answer_text, top_passages)
        guard_extra = t_guard.stop()
        latency.guardrail_ms = round(guard_extra, 2)

        # 8. Final Latency Calculation
        latency.total_rag_ms = round((time.perf_counter() - start_rag) * 1000.0, 2)
        latency.total_end_to_end_ms = round(stt_latency_ms + latency.total_rag_ms, 2)

        # Convert top passages to SourceChunk list
        sources = [
            SourceChunk(
                chunk_id=doc.get("chunk_id", f"c_{i}"),
                source_id=doc.get("source_id", "dataset_source"),
                passage_id=doc.get("passage_id"),
                query_id=doc.get("query_id"),
                language=doc.get("language", language),
                text=doc.get("text", ""),
                relevance_score=float(doc.get("relevance_score", doc.get("score", 0.0))),
                chunk_strategy=doc.get("chunk_strategy", settings.CHUNK_STRATEGY)
            ) for i, doc in enumerate(top_passages)
        ]

        response = VoiceQueryResponse(
            request_id=request_id,
            transcript=query,
            language=language,
            answer=answer_text,
            grounded=grounding_res.grounded,
            grounding_details=grounding_res,
            sources=sources,
            latency=latency,
            status="completed",
            mock_mode=settings.MOCK_EXTERNAL_SERVICES
        )

        # Record benchmark record
        self.benchmark_service.add_record(response.model_dump())
        logger.info(f"RAG pipeline completed: {latency.total_rag_ms}ms (Total E2E: {latency.total_end_to_end_ms}ms)", request_id=request_id)

        return response
