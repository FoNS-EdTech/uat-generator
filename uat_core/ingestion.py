# uat_core/ingestion.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import uuid
from typing import List
from.models import Document

def fetch_web_docs(base_url: str, max_pages: int = 20) -> List[Document]:
    visited = set()
    to_visit = [base_url]
    docs = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Very naive main content extraction; adjust selectors for your docs
        title = soup.title.string.strip() if soup.title else url
        main = soup.find("main") or soup.find("article") or soup.body
        content = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)

        doc_id = str(uuid.uuid4())
        role_hint = infer_role_from_title(title)
        docs.append(Document(
            doc_id=doc_id,
            source_type="web",
            source_location=url,
            role_hint=role_hint,
            title=title,
            content=content
        ))

        # Discover more links within same domain
        domain = urlparse(base_url).netloc
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            if urlparse(link).netloc == domain and link not in visited:
                to_visit.append(link)

    return docs

def infer_role_from_title(title: str) -> str:
    t = title.lower()
    if "admin" in t or "administrator" in t or "configuration" in t or "setup" in t:
        return "admin"
    if "user guide" in t or "end user" in t or "using" in t:
        return "end-user"
    return None