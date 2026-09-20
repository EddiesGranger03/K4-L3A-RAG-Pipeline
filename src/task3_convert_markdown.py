"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

import csv
import json
import shutil
from pathlib import Path
from docx import Document
import pypdf

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
KYTUCXA_DIR = Path(__file__).parent.parent / "data" / "kytucxa"
ROOT_DIR = Path(__file__).parent.parent



def extract_pdf_text(pdf_path: Path) -> str:
    """Trích xuất text từ file PDF."""
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        texts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texts.append(t.strip())
        return "\n\n".join(texts)
    except Exception as e:
        print(f"Lỗi đọc PDF {pdf_path}: {e}")
        return ""


def extract_docx_text(docx_path: Path) -> str:
    """Trích xuất text từ file DOCX."""
    try:
        doc = Document(docx_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"Lỗi đọc DOCX {docx_path}: {e}")
        return ""


def convert_legal_docs() -> None:
    """Convert PDF/DOCX vào standardized/legal kèm title và source ở đầu file."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(legal_dir.iterdir()):
        if path.is_file() and not path.name.startswith("."):
            content = ""
            if path.suffix.lower() == ".pdf":
                content = extract_pdf_text(path)
            elif path.suffix.lower() in {".doc", ".docx"}:
                content = extract_docx_text(path)

            if content:
                header = (
                    f"# {path.stem}\n\n"
                    f"**Source:** {path.name}\n\n"
                    f"**Document Type:** legal\n\n---\n\n"
                )
                (output_dir / f"{path.stem}.md").write_text(header + content, encoding="utf-8")


def convert_news_articles() -> None:
    """Convert JSON vào standardized/news kèm title và source ở đầu file."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(news_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            header = (
                f"# {data['title']}\n\n"
                f"**Source:** {data['url']}\n\n"
                f"**Crawled:** {data.get('date_crawled', '2026-09-20')}\n\n"
                f"**Document Type:** news\n\n---\n\n"
            )
            (output_dir / f"{path.stem}.md").write_text(
                header + data.get("content_markdown", ""), encoding="utf-8"
            )
        except Exception as e:
            print(f"Lỗi đọc JSON {path}: {e}")


def sync_kytucxa_metadata() -> None:
    """Tạo bộ dữ liệu data/kytucxa với frontmatter chuẩn theo sources.csv."""
    KYTUCXA_DIR.mkdir(parents=True, exist_ok=True)
    sources_file = KYTUCXA_DIR / "sources.csv"
    if not sources_file.exists() and (ROOT_DIR / "sources.csv").exists():
        shutil.copy(ROOT_DIR / "sources.csv", sources_file)

    if not sources_file.exists():
        print(f"Lưu ý: Không tìm thấy {sources_file}, bỏ qua bước sync metadata.")
        return

    rows = list(csv.DictReader(open(sources_file, encoding="utf-8")))
    
    # Mapping doc_id to content
    content_map = {}
    
    # Từ legal
    for path in (OUTPUT_DIR / "legal").glob("*.md"):
        if "KTX-HL" in path.name:
            content_map["fpt-noi-quy-ktx-hl"] = path.read_text(encoding="utf-8")
        elif "fpt-quy-dinh-bql" in path.name:
            content_map["fpt-quy-dinh-bql"] = path.read_text(encoding="utf-8")
        elif "SLIDE_KTX_K21" in path.name:
            content_map["slide-ktx-k21"] = path.read_text(encoding="utf-8")

    # Từ news JSON
    news_id_map = {
        "article_01.json": "fpt-ocd-portal",
        "article_02.json": "fpt-huong-dan-nhan-phong",
        "article_03.json": "fpt-tien-ich-ktx",
        "article_04.json": "fpt-kinh-nghiem-ktx",
        "article_05.json": "fpt-faq-ktx",
    }
    for json_file in (LANDING_DIR / "news").glob("*.json"):
        doc_id = news_id_map.get(json_file.name)
        if doc_id:
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                content_map[doc_id] = data.get("content_markdown", "")
            except Exception:
                pass

    for row in rows:
        doc_id = row.get("doc_id", "")
        title = row.get("title", "")
        url = row.get("url", "")
        aud = row.get("audience", "student")
        ver = row.get("document_version", "1.0")
        body = content_map.get(doc_id, f"# {title}\n\nNội dung chi tiết tài liệu {title}.")
        
        md_content = (
            f"---\n"
            f"doc_id: {doc_id}\n"
            f"title: {title}\n"
            f"source_url: {url}\n"
            f"retrieved_at: 2026-09-20\n"
            f"document_version: {ver}\n"
            f"audience: {aud}\n"
            f"---\n\n"
            f"{body}\n"
        )
        (KYTUCXA_DIR / f"{doc_id}.md").write_text(md_content, encoding="utf-8")
    print(f"Synced {len(rows)} files in {KYTUCXA_DIR}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    sync_kytucxa_metadata()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()

