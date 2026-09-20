import streamlit as st
from dotenv import load_dotenv
from src.task10_generation import generate_with_citation
import os
import base64
from pathlib import Path

load_dotenv()

# Sync st.secrets to os.environ for seamless Streamlit Cloud deployment
try:
    if hasattr(st, "secrets"):
        for key, val in st.secrets.items():
            if isinstance(val, str) and key not in os.environ:
                os.environ[key] = val
except Exception:
    pass

st.set_page_config(
    page_title="FPT Dormitory Assistant — KTX Hòa Lạc",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load media (video or image) as base64 for reliable rendering
def get_base64_media(file_path: str) -> str:
    if not file_path:
        return ""
    path = Path(file_path)
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

# Check if a background video exists, otherwise fallback to image
video_file = None
for candidate in ["background.mp4", "ghibli_background.mp4", "ghibli_wallpaper.mp4"]:
    if Path(candidate).exists():
        video_file = candidate
        break

video_b64 = get_base64_media(video_file) if video_file else ""
wallpaper_b64 = get_base64_media("ghibli_wallpaper.jpg")

# Video background HTML tag (if video is present)
video_html = (
    f"""
    <video autoplay loop muted playsinline id="bg-video">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    """
    if video_b64
    else ""
)

# Background styling for .stApp depending on media type
bg_style = (
    """
    .stApp {
        background: color-mix(in srgb, var(--background-color) 70%, transparent) !important;
    }
    #bg-video {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -999;
        pointer-events: none;
    }
    """
    if video_b64
    else f"""
    .stApp {{
        background: radial-gradient(ellipse at 50% 25%, color-mix(in srgb, var(--background-color) 72%, transparent) 0%, color-mix(in srgb, var(--background-color) 92%, transparent) 100%),
                    url("data:image/jpeg;base64,{wallpaper_b64}") no-repeat center bottom fixed !important;
        background-size: cover !important;
    }}
    """
)

# Inject Modern Clean Glassmorphism CSS with 100% Vietnamese Font (Be Vietnam Pro)
st.markdown(
    f"""
    {video_html}
    <style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap');

    {bg_style}

    /* Apply Be Vietnam Pro everywhere to prevent any Vietnamese font distortion and fix color contrast */
    html, body, [class*="css"], .stApp, .stMarkdown, p, div, span, input, button, textarea, [data-testid="stChatMessage"] {{
        font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.01em;
        color: var(--text-color) !important;
    }}

    /* Make header and bottom input container transparent */
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    [data-testid="stBottom"] {{
        background: transparent !important;
    }}

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {{
        background: color-mix(in srgb, var(--secondary-background-color) 88%, transparent) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent) !important;
        box-shadow: 4px 0 25px rgba(0, 0, 0, 0.1) !important;
    }}

    /* Chat Messages Glassmorphism */
    [data-testid="stChatMessage"] {{
        background: color-mix(in srgb, var(--background-color) 75%, transparent) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent) !important;
        border-radius: 18px !important;
        padding: 1.2rem 1.4rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15) !important;
        color: var(--text-color) !important;
        font-size: 1.02rem !important;
        line-height: 1.65 !important;
    }}

    [data-testid="stChatMessage"]:hover {{
        border-color: var(--primary-color) !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25) !important;
    }}

    /* Chat Input Glassmorphism */
    [data-testid="stChatInput"] {{
        background: color-mix(in srgb, var(--background-color) 88%, transparent) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid var(--primary-color) !important;
        border-radius: 18px !important;
        color: var(--text-color) !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2) !important;
    }}

    [data-testid="stChatInput"]:focus-within {{
        border-color: #38bdf8 !important;
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.6), 0 0 16px rgba(56, 189, 248, 0.35) !important;
    }}

    /* Expander Glassmorphism */
    [data-testid="stExpander"] {{
        background: color-mix(in srgb, var(--background-color) 65%, transparent) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent) !important;
        border-radius: 14px !important;
        margin-top: 0.6rem !important;
        color: var(--text-color) !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: color-mix(in srgb, var(--text-color) 8%, transparent) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid color-mix(in srgb, var(--text-color) 15%, transparent) !important;
        border-radius: 12px !important;
        color: var(--text-color) !important;
        font-weight: 500 !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        padding: 0.6rem 0.9rem !important;
        font-size: 0.92rem !important;
    }}

    .stButton > button:hover {{
        background: color-mix(in srgb, var(--primary-color) 20%, transparent) !important;
        border-color: var(--primary-color) !important;
        transform: translateY(-1px) !important;
        color: var(--primary-color) !important;
    }}

    /* Title & Subtitle styling */
    .app-title {{
        font-family: 'Be Vietnam Pro', sans-serif;
        font-weight: 700;
        font-size: 2.1rem;
        background: linear-gradient(135deg, var(--text-color) 30%, var(--primary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }}

    .app-sub {{
        font-size: 0.95rem;
        color: color-mix(in srgb, var(--text-color) 75%, transparent);
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }}

    .rag-badge {{
        display: inline-block;
        background: color-mix(in srgb, var(--primary-color) 15%, transparent);
        color: var(--primary-color);
        border: 1px solid color-mix(in srgb, var(--primary-color) 35%, transparent);
        border-radius: 8px;
        padding: 0.25rem 0.6rem;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar configuration
with st.sidebar:
    st.markdown('<div class="rag-badge"><i class="fa-solid fa-bolt" style="color: #fbbf24;"></i> RAG Pipeline Active</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="font-size: 2.2rem; font-weight: 700; margin-bottom: 0;"><i class="fa-solid fa-building" style="color: var(--primary-color);"></i> KTX FPT Assistant</h1>', unsafe_allow_html=True)
    st.markdown("**Hệ thống tư vấn Ký túc xá FPT University (Hòa Lạc)**")
    st.markdown("---")

    llm_provider = os.getenv("LLM_PROVIDER", "nvidia").upper()
    llm_model = os.getenv("LLM_MODEL", "z-ai/glm-5.3-flash")
    st.info(f"**LLM Engine:** {llm_provider}\n\n**Model:** `{llm_model}`\n\n**Chế độ:** Full Chunks Hybrid RAG", icon=":material/memory:")

    if st.button("Xóa lịch sử trò chuyện", icon=":material/delete:", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown('<h3><i class="fa-solid fa-lightbulb" style="color: #fbbf24;"></i> Câu hỏi thường gặp:</h3>', unsafe_allow_html=True)
    sample_queries = [
        "Giờ giới nghiêm của KTX FPT là mấy giờ?",
        "Định mức điện nước miễn phí mỗi kỳ là bao nhiêu?",
        "Khi thiết bị trong phòng hỏng thì báo ở đâu?",
        "Quy định trừ điểm uy tín CFD khi vi phạm?",
        "Trường ĐH Bách Khoa có mấy cơ sở? (Test từ chối)",
    ]
    for q in sample_queries:
        if st.button(q, key=f"btn_{q}", use_container_width=True):
            st.session_state.suggested_query = q

# Main app header
st.markdown('<div class="app-title"><i class="fa-solid fa-building-user"></i> Trợ lý Ảo Ký túc xá FPT University Hà Nội</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-sub">Tra cứu chính xác nội quy, thủ tục nhận phòng, chi phí điện nước, điểm uy tín CFD và quy trình hỗ trợ sinh viên tại Campus Hòa Lạc.</div>',
    unsafe_allow_html=True,
)

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"Nguồn tham khảo ({len(message['sources'])} chunks) — Phương thức: {message.get('retrieval_source', 'hybrid')}", icon=":material/menu_book:"):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    st.markdown(
                        f"**[{idx}] {meta.get('title', 'Tài liệu')}** (`{meta.get('source', '')}`) | "
                        f"Độ tương quan: `{src.get('score', 0):.4f}` | "
                        f"Phương thức: `{src.get('retrieval_method', '')}`"
                    )
                    st.caption(src.get("content", "")[:350] + "...")

# Handle query from input or sample buttons
query = st.chat_input("Nhập câu hỏi về KTX FPT (ví dụ: giờ giới nghiêm, phí điện nước, báo hỏng thiết bị)...")
if getattr(st.session_state, "suggested_query", None):
    query = st.session_state.suggested_query
    st.session_state.suggested_query = None

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu dữ liệu và tổng hợp câu trả lời..."):
            # Chạy full chunks tối ưu (top_k=5) tự động
            result = generate_with_citation(query, top_k=5)
            answer = result["answer"]
            sources = result["sources"]
            retrieval_source = result["retrieval_source"]

            st.markdown(answer)

            if sources:
                with st.expander(f"Nguồn tham khảo ({len(sources)} chunks) — Phương thức: {retrieval_source}", icon=":material/menu_book:"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        st.markdown(
                            f"**[{idx}] {meta.get('title', 'Tài liệu')}** (`{meta.get('source', '')}`) | "
                            f"Độ tương quan: `{src.get('score', 0):.4f}` | "
                            f"Phương thức: `{src.get('retrieval_method', '')}`"
                        )
                        st.caption(src.get("content", "")[:350] + "...")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
