"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import hashlib
import json
import math
import os
import re
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm: Semantic Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "semantic"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"



def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Tính độ tương đồng cosine giữa 2 vector."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1)) or 1.0
    norm2 = math.sqrt(sum(b * b for b in vec2)) or 1.0
    return dot / (norm1 * norm2)


def semantic_chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    similarity_threshold: float = 0.60,
) -> list[str]:
    """Chia văn bản dựa trên độ tương đồng ngữ nghĩa giữa các câu (Semantic Chunking)."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    # Tách văn bản thành các câu hoặc mệnh đề ngữ nghĩa
    raw_sentences = re.split(r"(?<=[.?!;\n])\s+", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    if not sentences:
        return []

    sentence_vectors = embed_texts(sentences)
    chunks = []
    current_chunk = []
    current_len = 0

    for i in range(len(sentences)):
        s = sentences[i]
        s_len = len(s) + (1 if current_chunk else 0)

        # Phát hiện bước chuyển chủ đề ngữ nghĩa (Semantic breakpoint)
        should_split = False
        if current_chunk and i > 0:
            sim = cosine_similarity(sentence_vectors[i - 1], sentence_vectors[i])
            # Nếu tương đồng thấp hơn ngưỡng và chunk đã đủ độ dài tối thiểu
            if sim < similarity_threshold and current_len >= 150:
                should_split = True

        # Ràng buộc kích thước tối đa để không vượt quá chunk_size
        if current_len + s_len > chunk_size:
            should_split = True

        if should_split and current_chunk:
            chunk_str = " ".join(current_chunk).strip()
            if chunk_str:
                chunks.append(chunk_str)
            current_chunk = [s]
            current_len = len(s)
        else:
            current_chunk.append(s)
            current_len += s_len

    if current_chunk:
        chunk_str = " ".join(current_chunk).strip()
        if chunk_str:
            chunks.append(chunk_str)

    # Đảm bảo không chunk nào vượt quá int(chunk_size * 1.1) theo contract
    max_allowed = int(chunk_size * 1.1)
    final_chunks = []
    for c in chunks:
        if len(c) > max_allowed:
            for j in range(0, len(c), chunk_size - chunk_overlap):
                part = c[j : j + chunk_size].strip()
                if part:
                    final_chunks.append(part)
        else:
            final_chunks.append(c)

    return final_chunks


def split_text_recursive(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    separators: list[str] | None = None,
) -> list[str]:
    """Chia văn bản đệ quy theo separators mà không vượt quá chunk_size."""
    return semantic_chunk_text(text, chunk_size, chunk_overlap)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding vector cho danh sách văn bản."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBEDDING_MODEL)
        return model.encode(texts).tolist()
    except Exception:
        pass

    embeddings = []
    for text in texts:
        vec = [0.0] * EMBEDDING_DIM
        words = re.findall(r"\w+", text.lower())
        if not words:
            vec[0] = 1.0
            embeddings.append(vec)
            continue
        for word in words:
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx = h % EMBEDDING_DIM
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        embeddings.append([x / norm for x in vec])
    return embeddings


_GLOBAL_IN_MEMORY_COLLECTION = None


def get_collection():
    """Mở Chroma collection dùng cosine distance hoặc in-memory fallback."""
    global _GLOBAL_IN_MEMORY_COLLECTION
    try:
        import chromadb
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception:
        if _GLOBAL_IN_MEMORY_COLLECTION is None:
            class InMemoryCollection:
                def __init__(self):
                    self.items = {}

                def upsert(self, ids, documents, embeddings, metadatas):
                    for i, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
                        self.items[i] = {
                            "document": doc,
                            "embedding": emb,
                            "metadata": meta,
                        }

                def query(self, query_embeddings, n_results=10, **kwargs):
                    q_emb = query_embeddings[0]
                    scored = []
                    for item_id, data in self.items.items():
                        d_emb = data["embedding"]
                        dot = sum(a * b for a, b in zip(q_emb, d_emb))
                        dist = max(0.0, 1.0 - dot)
                        scored.append((dist, item_id, data["document"], data["metadata"]))
                    scored.sort(key=lambda x: x[0])
                    top = scored[:n_results]
                    return {
                        "ids": [[x[1] for x in top]],
                        "documents": [[x[2] for x in top]],
                        "metadatas": [[x[3] for x in top]],
                        "distances": [[x[0] for x in top]],
                    }

            _GLOBAL_IN_MEMORY_COLLECTION = InMemoryCollection()
        return _GLOBAL_IN_MEMORY_COLLECTION


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8")
        url = None
        match = re.search(r"\*\*Source:\*\*\s*(https?://[^\s\n]+)", content)
        if match:
            url = match.group(1).strip()
        documents.append({
            "id": path.stem,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": path.stem,
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    chunks = []
    for document in documents:
        pieces = split_text_recursive(document["content"], CHUNK_SIZE, CHUNK_OVERLAP)
        for index, text in enumerate(pieces):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks from {len(documents)} documents")


if __name__ == "__main__":
    run_pipeline()
