"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


CORPUS: list[dict] = []


import math
import re

CORPUS: list[dict] = []


def tokenize(text: str) -> list[str]:
    """Tokenize đơn giản cho tiếng Việt và tiếng Anh."""
    return re.findall(r"\w+", text.lower())


class SimpleBM25:
    """Triển khai thuần Python BM25Okapi."""

    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(x) for x in corpus) / (self.corpus_size or 1)
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = [len(x) for x in corpus]

        df = {}
        for doc in corpus:
            frequencies = {}
            for word in doc:
                frequencies[word] = frequencies.get(word, 0) + 1
            self.doc_freqs.append(frequencies)
            for word in frequencies:
                df[word] = df.get(word, 0) + 1

        for word, freq in df.items():
            self.idf[word] = math.log(
                1 + (self.corpus_size - freq + 0.5) / (freq + 0.5)
            )

    def get_scores(self, query: list[str]) -> list[float]:
        scores = [0.0] * self.corpus_size
        for q in query:
            if q not in self.idf:
                continue
            idf = self.idf[q]
            for i in range(self.corpus_size):
                tf = self.doc_freqs[i].get(q, 0)
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * self.doc_len[i] / (self.avgdl or 1)
                )
                scores[i] += idf * (numerator / denominator)
        return scores


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    try:
        from rank_bm25 import BM25Okapi

        tokenized = [tokenize(item["content"]) for item in corpus]
        return BM25Okapi(tokenized)
    except Exception:
        tokenized = [tokenize(item["content"]) for item in corpus]
        return SimpleBM25(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    from .task4_chunking_indexing import chunk_documents, load_documents

    global CORPUS
    corpus = CORPUS
    if not corpus:
        documents = load_documents()
        corpus = chunk_documents(documents)

    if not corpus:
        return []

    bm25 = build_bm25_index(corpus)
    query_tokens = tokenize(query)
    scores = bm25.get_scores(query_tokens)

    indexed_scores = [(idx, score) for idx, score in enumerate(scores)]
    indexed_scores.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in indexed_scores[:top_k]:
        item = corpus[idx]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(score),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for result in lexical_search("test query", top_k=3):
        print(result)
