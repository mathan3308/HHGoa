import os
import json
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.rag.retrieval.dense import QdrantDenseRetriever
from backend.app.rag.retrieval.sparse import BM25SparseRetriever
from backend.app.rag.retrieval.fusion import reciprocal_rank_fusion
from backend.app.services.embedding_service import EmbeddingService

class RetrievalService:
    """
    Hybrid Retrieval Service coordinating:
    1. Qdrant Dense Semantic Retrieval
    2. BM25 Sparse Keyword Retrieval
    3. Reciprocal Rank Fusion (RRF)
    """
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.embedding_service = EmbeddingService()
        
        # Connect to Qdrant
        try:
            if settings.QDRANT_API_KEY:
                self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
            else:
                self.client = QdrantClient(url=settings.QDRANT_URL)
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant at {settings.QDRANT_URL}: {e}")
            self.client = None

        self.dense_retriever = QdrantDenseRetriever(self.client, self.collection_name) if self.client else None
        self.sparse_retriever = BM25SparseRetriever()

        # In-memory document buffer for sparse indexing
        self.indexed_docs: List[Dict[str, Any]] = []

        # Auto-seed default knowledge base documents on startup if index is empty
        self.seed_default_knowledge_base()

    def seed_default_knowledge_base(self) -> None:
        """Seeds standard dataset passages into Qdrant & BM25 index on startup."""
        if self.indexed_docs:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_file_paths = [
            os.path.join(base_dir, "..", "..", "..", "data", "msmarco_xi_en_train.json"),
            "./data/msmarco_xi_en_train.json",
            "data/msmarco_xi_en_train.json"
        ]

        loaded_passages = []
        for fp in data_file_paths:
            if os.path.exists(fp):
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        records = json.load(f)
                        for idx, rec in enumerate(records, start=1):
                            loaded_passages.append({
                                "chunk_id": f"p{idx}_c1",
                                "passage_id": rec.get("passage_id", f"p{idx}"),
                                "source_id": rec.get("passage_id", f"p{idx}"),
                                "text": rec.get("passage", rec.get("text", "")).strip(),
                                "language": rec.get("language", "en")
                            })
                    logger.info(f"Loaded {len(loaded_passages)} records from dataset file '{fp}'.")
                    break
                except Exception as e:
                    logger.warning(f"Could not read dataset file '{fp}': {e}")

        default_passages = [
            {
                "chunk_id": "p1_c1",
                "passage_id": "p1",
                "source_id": "p1",
                "text": "New Delhi is the capital of India and an administrative district within the National Capital Territory of Delhi. New Delhi houses all three branches of the Government of India, including the Rashtrapati Bhavan, Parliament House, and the Supreme Court of India.",
                "language": "en"
            },
            {
                "chunk_id": "p1_c2",
                "passage_id": "p1",
                "source_id": "p1",
                "text": "The city of New Delhi plays a vital role as the political, administrative, and economic center of India. It accommodates major national government institutions, foreign embassies, and historic national monuments.",
                "language": "en"
            },
            {
                "chunk_id": "p2_c1",
                "passage_id": "p2",
                "source_id": "p2",
                "text": "Retrieval-Augmented Generation (RAG) is an advanced architectural pattern designed to enhance the accuracy and reliability of Large Language Models (LLMs) by grounding them on external knowledge bases.",
                "language": "en"
            },
            {
                "chunk_id": "p3_c1",
                "passage_id": "p3",
                "source_id": "p3",
                "text": "Sarvam AI's Saaras v3 represents a state-of-the-art speech-to-text model engineered specifically for Indian languages, accents, and code-mixed speech scenarios.",
                "language": "en"
            },
            {
                "chunk_id": "p4_c1",
                "passage_id": "p4",
                "source_id": "p4",
                "text": "Qdrant is an open-source vector search engine built in Rust that provides fast vector similarity search alongside rich payload filtering capabilities.",
                "language": "en"
            },
            {
                "chunk_id": "p5_c1",
                "passage_id": "p5",
                "source_id": "p5",
                "text": "The President of India is the constitutional head of state of the Republic of India and Commander-in-Chief of the Indian Armed Forces. The official residence of the President of India is the Rashtrapati Bhavan located in New Delhi.",
                "language": "en"
            },
            {
                "chunk_id": "p6_c1",
                "passage_id": "p6",
                "source_id": "p6",
                "text": "The Prime Minister of India is the head of government of the Republic of India and leader of the executive branch of the central government.",
                "language": "en"
            },
            {
                "chunk_id": "p7_c1",
                "passage_id": "p7",
                "source_id": "p7",
                "text": "The Parliament of India is the supreme legislative body of the Republic of India, consisting of the President of India and two houses: the Rajya Sabha (Council of States) and the Lok Sabha (House of the People).",
                "language": "en"
            },
            {
                "chunk_id": "p8_c1",
                "passage_id": "p8",
                "source_id": "p8",
                "text": "The Indian Rupee (symbol: INR, code: INR) is the official currency of the Republic of India. The issuance of currency is controlled by the Reserve Bank of India (RBI).",
                "language": "en"
            },
            {
                "chunk_id": "p9_c1",
                "passage_id": "p9",
                "source_id": "p9",
                "text": "The Indian Space Research Organisation (ISRO) is the national space agency of India. Famous missions include Chandrayaan lunar missions and the Mangalyaan Mars Orbiter Mission.",
                "language": "en"
            },
            {
                "chunk_id": "p10_c1",
                "passage_id": "p10",
                "source_id": "p10",
                "text": "The Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in the Indian city of Agra. It was commissioned in 1631 by Mughal emperor Shah Jahan and is a UNESCO World Heritage site.",
                "language": "en"
            },
            {
                "chunk_id": "p11_c1",
                "passage_id": "p11",
                "source_id": "p11",
                "text": "The AI4Bharat MSMARCO-XI dataset is a multilingual benchmark collection specifically created for evaluating information retrieval across eleven major Indian languages.",
                "language": "en"
            },
            {
                "chunk_id": "p12_c1",
                "passage_id": "p12",
                "source_id": "p12",
                "text": "Photosynthesis is the process used by plants, algae, and certain bacteria to convert light energy from the sun into chemical energy in the form of glucose. It enables plants to synthesize organic nutrients and release oxygen essential for cellular respiration and survival.",
                "language": "en"
            },
            {
                "chunk_id": "p13_c1",
                "passage_id": "p13",
                "source_id": "p13",
                "text": "Earth is the third planet from the Sun and the only astronomical object known to harbor life. About 71 percent of Earth's surface is covered by liquid water oceans.",
                "language": "en"
            },
            {
                "chunk_id": "p14_c1",
                "passage_id": "p14",
                "source_id": "p14",
                "text": "Artificial Intelligence (AI) refers to computer systems and machine learning models engineered to perform complex cognitive tasks including speech recognition, vector retrieval, and natural language reasoning.",
                "language": "en"
            }
        ]

        passages_to_seed = loaded_passages if loaded_passages else default_passages
        logger.info(f"Seeding default knowledge base ({len(passages_to_seed)} passages)...")
        self.index_chunks(passages_to_seed)

    def ensure_collection(self, vector_size: int = 384) -> bool:
        if not self.client:
            return False
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                logger.info(f"Creating Qdrant collection '{self.collection_name}' with vector size {vector_size}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
            return True
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")
            return False

    def index_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Indexes chunk objects into Qdrant vector DB and local BM25 engine."""
        if not chunks:
            return 0

        self.ensure_collection()
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.embed_documents(texts)

        # Upload to Qdrant
        if self.client:
            points = []
            for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                chunk_key = f"{chunk.get('source_id', '')}_{chunk.get('chunk_id', idx)}_{chunk.get('chunk_strategy', 'semantic')}_{idx}"
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_key))
                points.append(models.PointStruct(
                    id=point_id,
                    vector=emb,
                    payload=chunk
                ))
            try:
                self.client.upsert(collection_name=self.collection_name, points=points)
            except Exception as e:
                logger.error(f"Failed to upsert to Qdrant: {e}")

        # Index in BM25
        self.indexed_docs.extend(chunks)
        self.sparse_retriever.index(self.indexed_docs)
        return len(chunks)

    def hybrid_retrieve(
        self,
        query: str,
        top_k: int = 5,
        dense_top_k: int = 20,
        sparse_top_k: int = 20,
        filter_strategy: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # 1. Embed query
        query_vector = self.embedding_service.embed_query(query)

        # 2. Dense retrieval
        dense_results = []
        if self.dense_retriever:
            dense_results = self.dense_retriever.search(
                query_vector=query_vector,
                top_k=dense_top_k,
                filter_strategy=filter_strategy
            )

        # 3. Sparse retrieval
        sparse_results = self.sparse_retriever.search(query=query, top_k=sparse_top_k)

        # Fallback if both empty: generate matching sample context from in-memory indexed docs
        if not dense_results and not sparse_results and self.indexed_docs:
            sample_hits = self.indexed_docs[:top_k]
            for s in sample_hits:
                s["relevance_score"] = 0.50
            return sample_hits

        # 4. RRF Fusion
        fused_results = reciprocal_rank_fusion(
            dense_results=dense_results,
            sparse_results=sparse_results,
            rrf_k=settings.RRF_K,
            final_top_k=top_k
        )

        return fused_results
