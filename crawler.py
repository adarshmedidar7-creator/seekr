import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

visited = set()
pages = {}

def crawl(url, depth=1):
    if depth == 0 or url in visited:
        return

    try:
        r = requests.get(url, timeout=5, headers={
            "User-Agent": "MiniSearchBot/1.0"
        })
        soup = BeautifulSoup(r.text, "html.parser")
        visited.add(url)

        # ✅ ONLY PARAGRAPHS
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)

        if len(text) > 300:  # ignore junk pages
            pages[url] = text[:8000]

        for link in soup.find_all("a", href=True):
            next_url = urljoin(url, link["href"])
            if next_url.startswith("http") and "wiki" in next_url:
                crawl(next_url, depth - 1)

    except Exception as e:
        print("Error:", e)
start_urls = [
    "https://en.wikipedia.org/wiki/Science",
    "https://en.wikipedia.org/wiki/Mathematics",
    "https://en.wikipedia.org/wiki/Physics",
    "https://en.wikipedia.org/wiki/Chemistry",
    "https://en.wikipedia.org/wiki/Biology",
    "https://en.wikipedia.org/wiki/Computer_science"
]

for u in start_urls:
    crawl(u, depth=1)

with open("pages.json", "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=2)

print("Crawling done. Pages:", len(pages))
