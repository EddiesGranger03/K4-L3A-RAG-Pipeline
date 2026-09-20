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
    layout="wide",
    initial_sidebar_state="expanded",
)

# Video background HTML tag
video_html = """
    <video autoplay loop muted playsinline id="bg-video">
        <source src="https://strvid.nyc3.cdn.digitaloceanspaces.com/motionsite/nature-sunset.mp4" type="video/mp4">
    </video>
"""

# Inject external fonts safely
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# Inject Modern Clean Glassmorphism CSS with 100% Vietnamese Font (Be Vietnam Pro)
st.markdown(
    f"""
    {video_html}
    <style>

    #bg-video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -999;
        pointer-events: none;
        filter: brightness(0.6) sepia(0.2) hue-rotate(-20deg); /* VERDE nature vibe overlay */
    }}

    /* Brutal transparency for Streamlit core elements */
    :root {{
        --background-color: transparent !important;
        --secondary-background-color: transparent !important;
    }}

    .stApp, .stAppViewContainer, .stAppViewBlockContainer, .main, [data-testid="stHeader"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    /* Brutal transparency for all bottom container wrappers EXCEPT the actual chat input box */
    [data-testid="stBottom"], 
    [data-testid="stBottom"] div:not([data-testid="stChatInput"]):not([data-testid="stChatInput"] *) {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    /* Apply Be Vietnam Pro everywhere to prevent any Vietnamese font distortion and fix color contrast */
    html, body, [class*="css"], .stApp, .stMarkdown, p, input, button, textarea, [data-testid="stChatMessage"] {{
        font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.01em;
        color: #ffffff !important;
    }}

    /* Restore Icon Fonts */
    .fa, .fas, .fa-solid, .fa-regular, .fa-light, .fa-brands, i[class*="fa-"] {{
        font-family: "Font Awesome 6 Free", "Font Awesome 6 Brands" !important;
        font-weight: 900 !important;
    }}
    .material-symbols-rounded, .stIcon, span[class*="icon"] {{
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
    }}

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(27, 48, 34, 0.35) !important;
        background-color: rgba(27, 48, 34, 0.35) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 4px 0 25px rgba(0, 0, 0, 0.1) !important;
    }}

    /* Alerts and Info boxes Glassmorphism */
    [data-testid="stAlert"] {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }}
    [data-testid="stAlert"] * {{
        color: #ffffff !important;
    }}

    /* Chat Messages Glassmorphism */
    [data-testid="stChatMessage"] {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 18px !important;
        padding: 1.2rem 1.4rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
        font-size: 1.02rem !important;
        line-height: 1.65 !important;
        color: #ffffff !important;
    }}

    [data-testid="stChatMessage"]:hover {{
        border-color: #4a7c59 !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25) !important;
    }}

    /* Chat Input Glassmorphism */
    [data-testid="stChatInput"] {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 18px !important;
        color: #ffffff !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2) !important;
    }}

    [data-testid="stChatInput"]:focus-within {{
        border-color: #38bdf8 !important;
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.6), 0 0 16px rgba(56, 189, 248, 0.35) !important;
    }}

    /* Expander Glassmorphism */
    [data-testid="stExpander"] {{
        background: rgba(27, 48, 34, 0.6) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        margin-top: 0.6rem !important;
        color: #ffffff !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        padding: 0.6rem 0.9rem !important;
        font-size: 0.92rem !important;
    }}

    .stButton > button:hover {{
        background: rgba(74, 124, 89, 0.4) !important;
        border-color: #4a7c59 !important;
        transform: translateY(-1px) !important;
        color: #ffffff !important;
    }}

    /* Title & Subtitle styling */
    .app-title {{
        font-family: 'Be Vietnam Pro', sans-serif;
        font-weight: 700;
        font-size: 2.1rem;
        background: linear-gradient(135deg, #ffffff 30%, #4a7c59 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }}

    .app-sub {{
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.85);
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }}

    .rag-badge {{
        display: inline-block;
        background: rgba(74, 124, 89, 0.2);
        color: #4a7c59;
        border: 1px solid rgba(74, 124, 89, 0.4);
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

# SVG Avatars for Chat
USER_AVATAR = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIiBmaWxsPSIjMzhiZGY4Ij48cGF0aCBkPSJNMjI0IDI1NkExMjggMTI4IDAgMSAwIDIyNCAwYTEyOCAxMjggMCAxIDAgMCAyNTZ6bS00NS43IDQ4Qzc5LjggMzA0IDAgMzgzLjggMCA0ODIuM0MwIDQ5OC43IDEzLjMgNTEyIDI5LjcgNTEySDQxOC4zYzE2LjQgMCAyOS43LTEzLjMgMjkuNy0yOS43QzQ0OCAzODMuOCAzNjguMiAzMDQgMjY5LjcgMzA0SDE3OC4zeiIvPjwvc3ZnPg=="
BOT_AVATAR = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIiBmaWxsPSIjZmJiZjI0Ij48cGF0aCBkPSJNMjU2IDBjLTE3LjcgMC0zMiAxNC4zLTMyIDMyVjY2LjdDMTUwLjMgNzIuNSA5NiAxMzYuNSA5NiAyMTMuM1YzODRjMCA1MyA0MyA5NiA5NiA5NkgzMjBjNTMgMCA5Ni00MyA5Ni05NlYyMTMuM2MwLTc2LjgtNTQuMy0xNDAuOC0xMjgtMTQ2LjdWMzJjMC0xNy43LTE0LjMtMzItMzItMzJ6TTIxNSAyNTZhNDEgNDEgMCAxIDEgLTgyIDAgNDEgNDEgMCAxIDEgODIgMHptMTY0IDBhNDEgNDEgMCAxIDEgLTgyIDAgNDEgNDEgMCAxIDEgODIgMHoiLz48L3N2Zz4="

def get_avatar(role):
    return USER_AVATAR if role == "user" else BOT_AVATAR

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=get_avatar(message["role"])):
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

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(query)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
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
