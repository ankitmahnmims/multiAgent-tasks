import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def scrape_job(url: str) -> Dict[str, Any]:
    """
    Scrape job title and description text from a job posting URL.
    Returns dict with keys: 'url', 'title_raw', 'description', 'is_thin'.
    """
    url = (url or "").strip()
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return {
            "url": url,
            "title_raw": "Job Application",
            "description": "",
            "is_thin": True
        }

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"[Job Scraper Warning] Failed fetching {url}: {e}")
        return {
            "url": url,
            "title_raw": "Job Application",
            "description": "",
            "is_thin": True
        }

    soup = BeautifulSoup(html, "html.parser")

    # Clean up non-content elements
    for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        element.extract()

    # Extract Job Title
    title = ""
    title_tag = soup.find("h1") or soup.find("title")
    if title_tag:
        title = title_tag.get_text().strip()
    
    if not title:
        title = "Job Opportunity"

    # Try extracting main description block
    main_content = (
        soup.find("article") or
        soup.find("main") or
        soup.find("div", class_=re.compile(r"(job|description|content|details|posting)", re.I)) or
        soup.body
    )

    if main_content:
        # Extract text from paragraphs, list items, headings
        lines = []
        for tag in main_content.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            txt = tag.get_text().strip()
            if txt and len(txt) > 3:
                lines.append(txt)
        description = "\n".join(lines)
    else:
        description = soup.get_text()

    # Clean multi-whitespace
    description = re.sub(r"\n{3,}", "\n\n", description).strip()

    is_thin = len(description) < 200

    return {
        "url": url,
        "title_raw": title,
        "description": description,
        "is_thin": is_thin
    }
