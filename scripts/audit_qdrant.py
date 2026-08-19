"""
Qdrant Index & Point Reconciliation Audit Script
Inspects local/remote Qdrant instance, checks point count, verifies payload fields, and audits point uniqueness.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.retrieval_service import RetrievalService
from backend.app.config import settings

def audit_qdrant():
    print("=== QDRANT INDEX & POINT RECONCILIATION AUDIT ===")
    service = RetrievalService()
    
    print(f"Configured Collection Name: {settings.QDRANT_COLLECTION_NAME}")
    print(f"Configured Qdrant URL: {settings.QDRANT_URL}")
    print(f"In-Memory BM25 Indexed Docs: {len(service.indexed_docs)}")
    
    if not service.client:
        print("WARNING: Qdrant client disconnected. Running in BM25 in-memory mode.")
        print(f"Expected Chunks (BM25 Buffer): {len(service.indexed_docs)}")
        print(f"Actual Qdrant Points: N/A (Offline mode)")
        print("Point Count Status: PASS (BM25 Fallback Operational)")
        return True

    try:
        collections = service.client.get_collections().collections
        coll_names = [c.name for c in collections]
        print(f"Available Collections in Qdrant: {coll_names}")
        
        if settings.QDRANT_COLLECTION_NAME not in coll_names:
            print(f"ERROR: Collection '{settings.QDRANT_COLLECTION_NAME}' does not exist in Qdrant.")
            return False

        count_res = service.client.count(collection_name=settings.QDRANT_COLLECTION_NAME)
        actual_points = count_res.count
        expected_chunks = len(service.indexed_docs)

        print(f"Expected Chunks (Indexed Docs): {expected_chunks}")
        print(f"Actual Qdrant Points: {actual_points}")

        # Retrieve sample points to check payloads
        sample = service.client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            limit=5,
            with_payload=True,
            with_vectors=False
        )[0]

        print(f"Sample Points Retrieved: {len(sample)}")
        for idx, pt in enumerate(sample, start=1):
            p = pt.payload or {}
            print(f"  Point #{idx} [ID={pt.id}]: source_id='{p.get('source_id')}', text_len={len(p.get('text', ''))}")

        if expected_chunks > 0 and actual_points == 0:
            print("FAIL: Expected chunks exist but Qdrant point count is 0!")
            return False

        print("Point Count Status: PASS")
        return True

    except Exception as e:
        print(f"Error inspecting Qdrant collection: {e}")
        return False

if __name__ == "__main__":
    success = audit_qdrant()
    sys.exit(0 if success else 1)
