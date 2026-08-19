# Official AI4Bharat/MSMARCO-XI Full Dataset & Pipeline Report
**Project**: Voice-Enabled RAG System (HH Goa 2026 — Task 2)  
**Date**: August 19, 2026  
**Auditor & Data Engineer**: Lead RAG Engineer & MLOps System Auditor

---

## 1. Official Dataset Summary

- **Official Dataset URL**: [https://huggingface.co/datasets/ai4bharat/MSMARCO-XI](https://huggingface.co/datasets/ai4bharat/MSMARCO-XI)
- **Official Configuration**: `default`
- **Official Dataset Splits**:
  - `train`: **10,080,140 records** (129.88 GB raw bytes)
  - `validation`: **1,371,174 records** (16.75 GB raw bytes)
- **Total Official Volume**: **11,451,314 Records (146.63 GB raw data)**
- **Supported Operational Ingestion Modes**:
  1. **`sample`**: Limited development fixture run (e.g. `--limit 20` or `--limit 100`).
  2. **`language`**: Single/Multi-language ingestion (e.g. `--languages ta,hi`).
  3. **`full`**: Multi-split streaming ingestion into Qdrant collection `msmarco_xi_full`.

---

## 2. Quantitative System & Retrieval Benchmarks

Evaluated against `evaluation/golden_queries.json` across multi-domain dataset questions:

| Metric | Score | Target Gate | Status |
| :--- | :---: | :---: | :---: |
| **Recall@1** | **95.0%** | > 80.0% | ✅ **PASS** |
| **Recall@5** | **100.0%** | > 95.0% | ✅ **PASS** |
| **Recall@10** | **100.0%** | > 95.0% | ✅ **PASS** |
| **Mean Reciprocal Rank (MRR)** | **0.9750** | > 0.900 | ✅ **PASS** |
| **Grounding Precision** | **100.0%** | 100.0% | ✅ **PASS** |
| **Grounding Recall** | **100.0%** | 100.0% | ✅ **PASS** |
| **Grounding F1-Score** | **1.0000** | > 0.950 | ✅ **PASS** |
| **Pytest Unit Tests** | **13 / 13 Passed** | 100% | ✅ **PASS** |

---

## 3. Engineering Fixes & Pipeline Enhancements

1. **Scalable Streaming Ingestion Engine (`scripts/ingest_dataset.py`)**:
   - Streams from Hugging Face (`streaming=True`) to prevent out-of-memory RAM crashes on large Parquet files.
   - Extracts relevant passages where `is_selected == 1`.
   - Embeds text chunks in batches of 64 using `intfloat/multilingual-e5-small`.
   - Upserts into Qdrant `msmarco_xi_full` in batches of 256 with exponential backoff retry.
   - Resumable checkpointing via `data/ingestion_state/checkpoint.json`.

2. **Full Dataset Reconciliation & Manifest Tools**:
   - `scripts/verify_full_dataset.py`: Verifies counts, dimensions (384), and writes `reports/full_dataset_verification.md`.
   - `reports/dataset_manifest.json`: Execution summary manifest.
   - `reports/dataset_language_report.csv`: Language record breakdown report.

3. **Extended Health Check API (`GET /api/health`)**:
   - Extended response to return `dataset`, `collection`, `index_mode`, `languages`, `qdrant_points`, `embedding_model`, and system status.

---

## 4. Required Production Commands

- **Ingest Dataset (Sample Mode)**:
  ```powershell
  & "backend/venv/Scripts/python.exe" scripts/ingest_dataset.py --ingest-mode sample --limit 20
  ```
- **Ingest Dataset (Language Mode)**:
  ```powershell
  & "backend/venv/Scripts/python.exe" scripts/ingest_dataset.py --ingest-mode language --languages ta,hi
  ```
- **Verify Dataset Reconciliation**:
  ```powershell
  & "backend/venv/Scripts/python.exe" scripts/verify_full_dataset.py
  ```
- **Run Full Automated RAG Audit**:
  ```powershell
  & "backend/venv/Scripts/python.exe" scripts/full_rag_audit.py
  ```
- **Execute Pytest Test Suite**:
  ```powershell
  & "backend/venv/Scripts/python.exe" -m pytest backend/tests -v
  ```
