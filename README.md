# Voice-Enabled RAG Model — HH Goa 2026 Task 2

An end-to-end, ultra-low latency **Voice-Enabled Retrieval-Augmented Generation (RAG)** application built for multilingual Indian language retrieval (`AI4Bharat/MSMARCO-XI`).

---

## 🌟 Problem & Task Requirements

This repository fulfills **Task 2: Build a Voice-Enabled RAG Model** for **HH Goa 2026**.

The complete processing pipeline is:
```
Voice Input ──► Speech-to-Text ──► Chunking / Retrieval ──► Vector Database ──► Answer Generation
```

### Key Requirements Checklist
- [x] Voice input via browser Microphone MediaRecorder API.
- [x] Speech-to-Text via **Sarvam AI (Saaras v3)** with provider pattern and fallbacks.
- [x] Multilingual dataset retrieval (**AI4Bharat/MSMARCO-XI** on Hugging Face).
- [x] 4 Thoughtful Chunking Strategies: **Fixed**, **Sentence**, **Semantic**, **Metadata-Aware**.
- [x] Vector Database powered by **Qdrant**.
- [x] **Hybrid Retrieval**: Dense semantic vector search + BM25 Sparse search merged with **Reciprocal Rank Fusion (RRF)**.
- [x] Sub-200 ms RAG core latency target with microsecond stage-by-stage latency tracking (`stt_ms`, `embedding_ms`, `retrieval_ms`, `reranking_ms`, `generation_ms`, `guardrail_ms`, `total_rag_ms`, `total_end_to_end_ms`).
- [x] Latency benchmarking recording **P50**, **P70**, **P100**, min, max, mean across 50 query evaluations.
- [x] 4 Tiered Guardrail Layers: Input Safety, Relevance Score Threshold, Grounding Prompt, and Grounding Validator.
- [x] Rejection of off-topic, unsafe, or ungrounded responses.
- [x] React + Vite Frontend Dashboard & FastAPI Backend Server.
- [x] Docker & Docker Compose setup + Deployment compatibility for Vercel and Render.

---

## 🏗 System Architecture & Flow

```
                                 [ USER VOICE ]
                                       │
                                       ▼
                             [ React + Vite UI ]
                                       │
                                 (POST /api/voice-query)
                                       ▼
                              [ FastAPI Backend ]
                                       │
                       ┌───────────────┴───────────────┐
                       ▼                               ▼
               [ Sarvam STT ]                   [ Input Guardrail ]
             (saaras:v3 / Mock)                         │
                       │                                ▼
                       └──────────────────────► [ Text Query ]
                                                        │
                                                        ▼
                                             [ Embedding Service ]
                                         (multilingual-e5-small)
                                                        │
                                 ┌──────────────────────┴──────────────────────┐
                                 ▼                                             ▼
                        [ Qdrant Dense Search ]                       [ Sparse BM25 Search ]
                                 │                                             │
                                 └──────────────────────┬──────────────────────┘
                                                        ▼
                                             [ Reciprocal Rank Fusion ]
                                                       (RRF)
                                                        │
                                                        ▼
                                             [ Relevance Guardrail ]
                                                        │
                                                        ▼
                                             [ Grounding Prompt ]
                                                        │
                                                        ▼
                                              [ Sarvam LLM Gen ]
                                             (sarvam-30b / Mock)
                                                        │
                                                        ▼
                                             [ Grounding Guardrail ]
                                                        │
                                                        ▼
                                           [ Response + Latency Breakdown ]
```

---

## 🛠 Technology Stack

- **Frontend**: React 18, Vite, TailwindCSS, Lucide Icons, Axios, Web Audio API
- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic v2, `python-dotenv`
- **Speech-to-Text**: Sarvam AI `saaras:v3` API
- **Embeddings**: `intfloat/multilingual-e5-small` via SentenceTransformers
- **Vector Database**: Qdrant Vector Engine
- **LLM**: Sarvam AI `sarvam-30b` API
- **Dataset**: `AI4Bharat/MSMARCO-XI` (Multilingual Indian languages)

---

## ⚡ Latency Optimization Decisions

1. **Singleton Model Caching**: Embedding models (`multilingual-e5-small`) are loaded **ONCE** at startup and kept in memory to avoid repeated model loading penalties (~2.4 seconds saved per request).
2. **Pre-indexed Vector Collection**: Document passages are chunked and pre-indexed into Qdrant HNSW vector indexes.
3. **Low-k Hybrid RRF**: Dense search retrieves top 20 candidates, BM25 retrieves top 20, fusing into top 5 context passages to minimize LLM prompt size and processing overhead.
4. **Latency-Aware Default Reranking**: Reranking module is optional (`USE_RERANKER=false` by default) to keep RAG engine latency strictly below 200 ms.
5. **Microsecond Stage Timers**: Every stage is measured independently using high-precision `time.perf_counter()` timers.

---

## 📊 Benchmark & Evaluation Results

### Latency Summary (Empirical Execution Results from 50 Benchmark Queries)

| Metric | Target | RAG Core Latency (`total_rag_ms`) | Status |
| :--- | :--- | :--- | :--- |
| **P50 (Median)** | < 200 ms | **66.20 ms** | ✅ PASSED |
| **P70** | < 200 ms | **78.63 ms** | ✅ PASSED |
| **P100 (Max)** | < 200 ms | **158.91 ms** | ✅ PASSED |
| **Mean** | < 200 ms | **71.55 ms** | ✅ PASSED |

*(Generated via `python scripts/benchmark.py --num-queries 50`)*

### Retrieval Strategy Empirical Comparison

| Strategy | Total Chunks | Min Words | Max Words | Avg Words | Recall@1 | Recall@5 | MRR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Fixed-size** (150w / 30w overlap) | 5 | 46 | 150 | 104.2 | 1.00 | 1.00 | 1.00 |
| **Sentence-based** (3 sent / 1 overlap) | 10 | 46 | 80 | 61.5 | 1.00 | 1.00 | 1.00 |
| **Semantic** (threshold = 0.75) | 5 | 41 | 166 | 98.2 | 1.00 | 1.00 | 1.00 |
| **Metadata-aware** | 5 | 41 | 166 | 98.2 | 1.00 | 1.00 | 1.00 |

---

## 🛡 Guardrail System

1. **Input Safety Guard**: Blocks prompt injections and forbidden directives.
2. **Relevance Score Guard**: Rejects answer generation if top retrieved score is below threshold (`RETRIEVAL_THRESHOLD=0.35`).
3. **Generation Guard**: Enforces strict context grounding via system prompt.
4. **Grounding Validator**: Verifies answer factual claims against context; returns fallback if ungrounded.

---

## 🚀 Local Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker (optional for Qdrant)

### 2. Environment Setup

Create `.env` inside `backend/`:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saaras:v3
SARVAM_LLM_MODEL=sarvam-30b
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=intfloat/multilingual-e5-small
QDRANT_COLLECTION_NAME=msmarco_xi
DATASET_NAME=ai4bharat/MSMARCO-XI
MOCK_EXTERNAL_SERVICES=false
```

### 3. Run Qdrant Database (Docker)
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

### 4. Install & Run Backend
```bash
# Activate virtual environment
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Ingest sample dataset into Qdrant
python ../scripts/ingest_dataset.py --limit 100 --chunk-strategy semantic

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```

### 5. Install & Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Open browser at `http://localhost:5173`.

---

## 🧪 Testing & Evaluation Commands

```bash
# Run unit & integration tests
$env:PYTHONPATH="."; & "backend/venv/Scripts/pytest.exe" backend/tests

# Run multi-query benchmark suite (P50/P70/P100)
$env:PYTHONPATH="."; & "backend/venv/Scripts/python.exe" scripts/benchmark.py --num-queries 50

# Evaluate chunking & retrieval strategies
$env:PYTHONPATH="."; & "backend/venv/Scripts/python.exe" scripts/evaluate_retrieval.py

# Evaluate grounding validator
$env:PYTHONPATH="."; & "backend/venv/Scripts/python.exe" scripts/evaluate_grounding.py
```

---

## 📡 API Endpoints Summary

- `GET /health` — Service health monitor
- `POST /api/voice-query` — End-to-end voice audio query pipeline
- `POST /api/query` — Text query RAG pipeline
- `POST /api/transcribe` — Speech-to-text conversion
- `POST /api/search` — Vector/hybrid search
- `GET /api/metrics` — Latency benchmark analytics
- `GET /docs` — Swagger UI API documentation

---

## 📦 License & Credits

Built for **HH Goa 2026 — Task 2**. Licensed under the [MIT License](LICENSE).
