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

    page_title="FPT Dormitory RAG Assistant — Ghibli Live",
    page_icon="✨",
    layout="wide",
)

# Load wallpaper as base64 for reliable rendering
def get_base64_image(image_path: str) -> str:
    path = Path(image_path)
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

wallpaper_b64 = get_base64_image("ghibli_wallpaper.jpg")

# Inject dynamic Ghibli Live Wallpaper, drifting clouds, canvas particles, and glassmorphism
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

    /* Background image & gradient overlay */
    .stApp {{
        background: radial-gradient(circle at 50% 30%, rgba(20, 35, 70, 0.4) 0%, rgba(5, 10, 25, 0.85) 100%),
                    url("data:image/jpeg;base64,{wallpaper_b64}") no-repeat center bottom fixed !important;
        background-size: cover !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #f8fafc !important;
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
        background: rgba(8, 14, 32, 0.72) !important;
        backdrop-filter: blur(22px) !important;
        -webkit-backdrop-filter: blur(22px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 4px 0 25px rgba(0, 0, 0, 0.4) !important;
    }}

    /* Chat Messages Glassmorphism */
    [data-testid="stChatMessage"] {{
        background: rgba(14, 22, 46, 0.58) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 20px !important;
        padding: 1.25rem 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.35) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }}

    [data-testid="stChatMessage"]:hover {{
        border-color: rgba(137, 180, 250, 0.45) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45), 0 0 15px rgba(137, 180, 250, 0.2) !important;
    }}

    /* Chat Input Glassmorphism */
    [data-testid="stChatInput"] {{
        background: rgba(12, 18, 40, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(137, 180, 250, 0.35) !important;
        border-radius: 18px !important;
        color: #ffffff !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5) !important;
    }}

    [data-testid="stChatInput"]:focus-within {{
        border-color: #89b4fa !important;
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.6), 0 0 18px rgba(137, 180, 250, 0.4) !important;
    }}

    /* Expander Glassmorphism */
    [data-testid="stExpander"] {{
        background: rgba(10, 16, 35, 0.5) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        margin-top: 0.6rem !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }}

    .stButton > button:hover {{
        background: rgba(137, 180, 250, 0.25) !important;
        border-color: #89b4fa !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
    }}

    /* Title & Badge styling */
    .ghibli-title {{
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 2.2rem;
        background: linear-gradient(135deg, #ffffff 40%, #89b4fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }}

    .ghibli-sub {{
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-bottom: 1.5rem;
    }}

    /* Drifting Clouds Animation Layer */
    .cloud-drift {{
        position: fixed;
        top: 0;
        left: 0;
        width: 200%;
        height: 50%;
        background-image: radial-gradient(ellipse 60% 40% at 50% 20%, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
        animation: drift 100s linear infinite;
        pointer-events: none;
        z-index: 0;
    }}

    @keyframes drift {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}
    </style>

    <!-- Drifting clouds background element -->
    <div class="cloud-drift"></div>

    <!-- Live Interactive Canvas: Stars, Dandelions, Fireflies -->
    <canvas id="liveGhibliCanvas" style="position: fixed; inset: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none;"></canvas>

    <script>
    (function() {{
        const canvas = document.getElementById('liveGhibliCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let w = canvas.width = window.innerWidth;
        let h = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {{
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }});

        // Stars
        const stars = [];
        for (let i = 0; i < 90; i++) {{
            stars.push({{
                x: Math.random() * w,
                y: Math.random() * (h * 0.6),
                r: Math.random() * 1.5 + 0.4,
                a: Math.random(),
                speed: Math.random() * 0.03 + 0.01
            }});
        }}

        // Dandelion seeds
        const dandelions = [];
        for (let i = 0; i < 45; i++) {{
            dandelions.push({{
                x: Math.random() * w,
                y: Math.random() * h,
                vx: Math.random() * 0.9 + 0.3,
                vy: Math.random() * 0.3 - 0.15,
                r: Math.random() * 3 + 2,
                a: Math.random() * 0.45 + 0.35,
                wobble: Math.random() * Math.PI * 2
            }});
        }}

        // Fireflies
        const fireflies = [];
        for (let i = 0; i < 25; i++) {{
            fireflies.push({{
                x: Math.random() * w,
                y: h * 0.4 + Math.random() * (h * 0.55),
                vx: (Math.random() - 0.5) * 0.6,
                vy: (Math.random() - 0.5) * 0.5,
                r: Math.random() * 2 + 1.5,
                pulse: Math.random() * Math.PI * 2
            }});
        }}

        function loop() {{
            ctx.clearRect(0, 0, w, h);

            // Draw Stars
            for (let s of stars) {{
                s.a += s.speed;
                const alpha = (Math.sin(s.a) + 1) / 2 * 0.8;
                ctx.fillStyle = `rgba(240, 245, 255, ${{alpha}})`;
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
                ctx.fill();
            }}

            // Draw Dandelions
            for (let d of dandelions) {{
                d.wobble += 0.03;
                d.x += d.vx + Math.sin(d.wobble) * 0.8;
                d.y += d.vy + Math.cos(d.wobble) * 0.2;
                if (d.x > w + 20) d.x = -20;
                if (d.y > h + 20) d.y = -20;
                if (d.y < -20) d.y = h + 20;

                ctx.fillStyle = `rgba(255, 255, 255, ${{d.a}})`;
                ctx.beginPath();
                ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = `rgba(200, 230, 255, ${{d.a * 0.3}})`;
                ctx.beginPath();
                ctx.arc(d.x, d.y, d.r * 2.2, 0, Math.PI * 2);
                ctx.fill();
            }}

            // Draw Fireflies
            for (let f of fireflies) {{
                f.pulse += 0.04;
                f.x += f.vx;
                f.y += f.vy;
                if (f.x < 0 || f.x > w) f.vx *= -1;
                if (f.y < h * 0.35 || f.y > h * 0.95) f.vy *= -1;

                const glow = (Math.sin(f.pulse) + 1) / 2;
                const radius = f.r * (2.5 + glow * 2);
                const grad = ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, radius);
                grad.addColorStop(0, 'rgba(168, 255, 120, 0.9)');
                grad.addColorStop(0.5, 'rgba(120, 240, 180, 0.3)');
                grad.addColorStop(1, 'rgba(120, 240, 180, 0)');

                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(f.x, f.y, radius, 0, Math.PI * 2);
                ctx.fill();
            }}

            requestAnimationFrame(loop);
        }}
        requestAnimationFrame(loop);
    }})();
    </script>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🏢 KTX FPT Assistant")
    st.markdown("**Chủ đề:** Dịch vụ đại học — Ký túc xá FPT University (Hòa Lạc)")
    st.markdown("---")

    llm_provider = os.getenv("LLM_PROVIDER", "nvidia").upper()
    llm_model = os.getenv("LLM_MODEL", "z-ai/glm-5.3-flash")
    st.info(f"🤖 **LLM Engine:** {llm_provider}\n\n📦 **Model:** `{llm_model}`")

    top_k = st.slider("Số lượng Chunks truy xuất (top_k)", min_value=3, max_value=10, value=5)

    st.markdown("---")
    st.subheader("💡 Câu hỏi gợi ý:")
    sample_queries = [
        "Giờ giới nghiêm của KTX FPT là mấy giờ?",
        "Định mức điện nước miễn phí mỗi kỳ là bao nhiêu?",
        "Khi thiết bị trong phòng hỏng thì báo ở đâu?",
        "Quy định trừ điểm uy tín CFD khi nấu ăn trong phòng?",
        "Trường ĐH Bách Khoa có bao nhiêu cơ sở? (Test từ chối)",
    ]
    for q in sample_queries:
        if st.button(q, key=f"btn_{q}"):
            st.session_state.suggested_query = q

st.markdown('<div class="ghibli-title">🏢 Trợ lý Ảo Ký túc xá FPT University Hà Nội</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ghibli-sub">Hệ thống RAG tra cứu nội quy, biểu phí, điểm uy tín và thủ tục lưu trú KTX FPT (Hòa Lạc) — Phong cách Ghibli Live Wallpaper</div>',
    unsafe_allow_html=True,
)

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📚 Nguồn tham khảo ({len(message['sources'])} chunks) — Phương thức: {message.get('retrieval_source', 'hybrid')}"):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    st.markdown(
                        f"**[{idx}] {meta.get('title', 'Tài liệu')}** (`{meta.get('source', '')}`) | "
                        f"Điểm số: `{src.get('score', 0):.4f}` | "
                        f"Method: `{src.get('retrieval_method', '')}`"
                    )
                    st.caption(src.get("content", "")[:300] + "...")

# Handle query from input or sample buttons
query = st.chat_input("Nhập câu hỏi về KTX FPT...")
if getattr(st.session_state, "suggested_query", None):
    query = st.session_state.suggested_query
    st.session_state.suggested_query = None

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu tài liệu và tổng hợp câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result["sources"]
            retrieval_source = result["retrieval_source"]

            st.markdown(answer)

            if sources:
                with st.expander(f"📚 Nguồn tham khảo ({len(sources)} chunks) — Phương thức: {retrieval_source}"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        st.markdown(
                            f"**[{idx}] {meta.get('title', 'Tài liệu')}** (`{meta.get('source', '')}`) | "
                            f"Điểm số: `{src.get('score', 0):.4f}` | "
                            f"Method: `{src.get('retrieval_method', '')}`"
                        )
                        st.caption(src.get("content", "")[:300] + "...")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
