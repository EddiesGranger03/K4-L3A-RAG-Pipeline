"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation. Nếu thiếu evidence, hãy từ chối xác minh."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (Lost in the middle mitigation)."""
    copied = [dict(c) for c in chunks]
    if len(copied) <= 2:
        return copied
    front = copied[::2]
    back = copied[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Unknown")
        source = metadata.get("source", "Unknown")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi NVIDIA NIM, OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = os.getenv("LLM_PROVIDER", "nvidia").lower()

    if provider in {"nvidia", "openai"}:
        from openai import OpenAI

        if provider == "nvidia":
            api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv(
                "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
            )
            model = (
                os.getenv("LLM_MODEL")
                or "meta/llama-3.1-70b-instruct"
            )
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL")
            model = os.getenv("LLM_MODEL") or "gpt-4o-mini"

        if not api_key:
            return (
                "Chưa cấu hình API Key trong file .env. "
                "Vui lòng điền NVIDIA_API_KEY hoặc OPENAI_API_KEY để kích hoạt tính năng trả lời tự động."
            )

        client = OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=1024,
        )
        msg = response.choices[0].message
        content = msg.content
        if not content and hasattr(msg, "reasoning_content") and msg.reasoning_content:
            content = msg.reasoning_content
        return content or ""

    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "Chưa cấu hình GEMINI_API_KEY trong file .env."
        from google import genai

        client = genai.Client(api_key=api_key)
        model = os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        response = client.models.generate_content(
            model=model,
            contents=f"{system_prompt}\n\n{user_message}",
        )
        return response.text or ""

    elif provider == "anthropic":
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "Chưa cấu hình ANTHROPIC_API_KEY trong file .env."
        client = anthropic.Anthropic(api_key=api_key)
        model = os.getenv("LLM_MODEL") or "claude-3-5-sonnet-20241022"
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
        )
        return response.content[0].text

    return "Không xác định được LLM_PROVIDER hợp lệ."


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult kèm citation và safe refusal."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as error:
        answer = f"Lỗi khi kết nối tới LLM ({error}). Dưới đây là các trích dẫn liên quan tìm thấy được trong tài liệu."

    retrieval_source = chunks[0].get("retrieval_method", "hybrid")
    if retrieval_source not in {"hybrid", "pageindex", "none"}:
        retrieval_source = "hybrid"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(generate_with_citation("Quy định giờ giới nghiêm của KTX FPT là mấy giờ?"))
