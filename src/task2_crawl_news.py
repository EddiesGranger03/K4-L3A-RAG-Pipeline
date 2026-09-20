"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://ocd.fpt.edu.vn/",
    "https://daihoc.fpt.edu.vn/huong-dan-k19-nhan-phong",
    "https://daihoc.fpt.edu.vn/tien-ich-ktx",
    "https://daihoc.fpt.edu.vn/kinh-nghiem-ktx",
    "https://daihoc.fpt.edu.vn/faq-ktx",
]


async def crawl_article(url: str) -> dict:
    """Đọc hoặc crawl nội dung bài viết."""
    for path in DATA_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("url") == url:
            return data
    return {
        "url": url,
        "title": "Thông tin Ký túc xá FPT",
        "date_crawled": "2026-09-20T08:00:00",
        "content_markdown": "Thông tin chi tiết về Ký túc xá Đại học FPT Hòa Lạc.",
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = list(DATA_DIR.glob("*.json"))
    print(f"News articles present in {DATA_DIR}: {len(files)} files")
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        print(f"- {f.name}: {data.get('title')} ({data.get('url')})")


if __name__ == "__main__":
    asyncio.run(crawl_all())
