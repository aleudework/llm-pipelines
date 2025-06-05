from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from readability import Document


def search_web(query, num_results=5):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=num_results))

def extract_text_from_url(url, max_chars=5000):
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        doc = Document(response.text)
        html = doc.summary()
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:max_chars]
    except Exception as e:
        return f"[Fejl ved hentning af {url}]: {e}"


def find_relevant_pages(query, max_pages=3):
    results = search_web(query, num_results=10)
    pages = []

    for r in results:
        url = r.get("href") or r.get("url")
        title = r.get("title", "Ingen titel")

        if not url:
            continue

        text = extract_text_from_url(url)
        pages.append({
            "title": title,
            "url": url,
            "text": text
        })

        if len(pages) >= max_pages:
            break

    return pages

# 🧠 Dette er "LLM tool-funktionen"
def web_tool(query: str) -> str:
    pages = find_relevant_pages(query)
    response = []

    for i, page in enumerate(pages):
        response.append(
            f"SIDE {i+1}:\nTitel: {page['title']}\nURL: {page['url']}\nUddrag:\n{page['text'][:1000]}\n"
        )

    return "\n\n".join(response)

query = 'VKK60311HV'
output = web_tool(query)

print(output)