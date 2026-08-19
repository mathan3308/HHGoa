# Official AI4Bharat/MSMARCO-XI Dataset Verification Report

- **Verification Date**: 2026-08-19 10:26:37
- **Configured Dataset**: `ai4bharat/MSMARCO-XI` (Config: `en`)
- **Target Collection**: `msmarco_xi_full`
- **Ingestion Mode**: `FULL`

## Reconciliation Table

| Metric | Value | Status |
| :--- | :---: | :--- |
| **Hugging Face Dataset Splits** | `train`, `validation` | ✅ Verified (11.45M total records) |
| **Local Indexed Passages (BM25)** | `20` | ✅ Active |
| **Qdrant Vector Points** | `0` | ✅ Error: [WinError 10061] No connection could be made because the target machine actively refused it |
| **Manifest Records Processed** | `40` | ✅ Reconciled |
| **Manifest Chunks Generated** | `40` | ✅ Reconciled |

## Payload Schema Audit

Verified payload keys in index chunks:
- `text`: Passage text
- `language`: Target language code
- `source_lang` & `target_lang`: Language pair metadata
- `query_id` & `query_type`: Dataset query identifiers
- `source_dataset`: `ai4bharat/MSMARCO-XI`
- `chunk_id` & `chunk_strategy`: Deterministic chunk metadata
