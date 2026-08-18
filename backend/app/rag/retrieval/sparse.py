import math
from typing import List, Dict, Any, Optional
from collections import Counter
from backend.app.utils.text import word_tokenize

class BM25SparseRetriever:
    """In-memory BM25 sparse keyword retriever for hybrid retrieval."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[Dict[str, Any]] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_freqs: List[Counter] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        self.df: Counter = Counter()

    def index(self, documents: List[Dict[str, Any]]) -> None:
        self.corpus = documents
        self.doc_tokens = []
        self.doc_freqs = []
        self.doc_lengths = []
        self.df = Counter()

        for doc in documents:
            tokens = word_tokenize(doc.get("text", ""))
            self.doc_tokens.append(tokens)
            freqs = Counter(tokens)
            self.doc_freqs.append(freqs)
            self.doc_lengths.append(len(tokens))
            for t in freqs.keys():
                self.df[t] += 1

        total_words = sum(self.doc_lengths)
        num_docs = len(documents)
        self.avg_doc_length = (total_words / num_docs) if num_docs > 0 else 1.0

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        if not self.corpus:
            return []

        query_tokens = word_tokenize(query)
        if not query_tokens:
            return []

        N = len(self.corpus)
        scores = [0.0] * N

        for token in query_tokens:
            if token not in self.df:
                continue
            df_val = self.df[token]
            # Standard BM25 IDF
            idf = math.log((N - df_val + 0.5) / (df_val + 0.5) + 1.0)

            for i in range(N):
                tf = self.doc_freqs[i][token]
                if tf == 0:
                    continue
                doc_len = self.doc_lengths[i]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_length))
                scores[i] += idf * (numerator / denominator)

        # Sort indices by score descending
        scored_indices = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for idx, score in scored_indices:
            if score > 0.0:
                doc = dict(self.corpus[idx])
                doc["score"] = float(score)
                results.append(doc)

        return results
