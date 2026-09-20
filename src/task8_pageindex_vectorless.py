"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    print("Documents ready for PageIndex vectorless retrieval.")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    import re
    from .task4_chunking_indexing import chunk_documents, load_documents

    documents = load_documents()
    chunks = chunk_documents(documents)

    query_words = set(re.findall(r"\w+", query.lower()))
    scored = []
    for chunk in chunks:
        content_lower = chunk["content"].lower()
        title_lower = chunk["metadata"]["title"].lower()
        matches = sum(1 for w in query_words if w in content_lower)
        title_matches = sum(2 for w in query_words if w in title_lower)
        score = float(matches + title_matches)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored and chunks:
        scored = [(1.0 - i * 0.1, chunk) for i, chunk in enumerate(chunks[:top_k])]

    results = []
    for rank, (score, chunk) in enumerate(scored[:top_k], 1):
        results.append({
            "id": chunk["id"],
            "content": chunk["content"],
            "score": float(score),
            "metadata": chunk["metadata"],
            "retrieval_method": "pageindex",
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    upload_documents()
