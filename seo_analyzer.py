
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

def extract_seo_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.title.string.strip() if soup.title else ""
        meta_description = ""
        robots_tag = ""
        canonical = ""
        lang_tag = soup.html.get("lang") if soup.html and soup.html.get("lang") else ""

        # Meta tags
        for tag in soup.find_all("meta"):
            if tag.get("name") == "description":
                meta_description = tag.get("content", "")
            if tag.get("name") == "robots":
                robots_tag = tag.get("content", "")

        # Canonical
        link_tag = soup.find("link", rel="canonical")
        if link_tag:
            canonical = link_tag.get("href", "")

        # Published/Modified dates
        date_published = ""
        date_modified = ""
        for tag in soup.find_all("meta"):
            if tag.get("property") == "article:published_time":
                date_published = tag.get("content", "")
            if tag.get("property") == "article:modified_time":
                date_modified = tag.get("content", "")

        # Alt tag check
        images = soup.find_all("img")
        images_missing_alt = sum(1 for img in images if not img.get("alt"))

        # Heading structure
        headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}

        # Schema types
        schema_types = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                parsed = json.loads(script.string)
                if isinstance(parsed, dict):
                    types = [parsed.get("@type")]
                elif isinstance(parsed, list):
                    types = [item.get("@type") for item in parsed if "@type" in item]
                else:
                    types = []
                schema_types.extend(types)
            except Exception:
                continue

        # Link analysis
        total_links = soup.find_all("a")
        broken_links = 0
        nofollow_links = 0
        for link in total_links:
            href = link.get("href")
            if href:
                if "nofollow" in link.get("rel", []):
                    nofollow_links += 1
                full_url = urljoin(url, href)
                try:
                    link_response = requests.head(full_url, timeout=5)
                    if link_response.status_code >= 400:
                        broken_links += 1
                except:
                    broken_links += 1

        # Performance (basic)
        load_time_ms = round(response.elapsed.total_seconds() * 1000)
        page_size_kb = round(len(response.content) / 1024, 2)

        return {
            "meta_title": meta_title,
            "meta_description": meta_description,
            "robots_tag": robots_tag,
            "canonical": canonical,
            "lang_tag": lang_tag,
            "date_published": date_published,
            "date_modified": date_modified,
            "image_alt_missing": images_missing_alt,
            "headings": headings,
            "schema_types": schema_types,
            "total_links": len(total_links),
            "broken_links": broken_links,
            "external_links_nofollow": nofollow_links,
            "load_time_ms": load_time_ms,
            "page_size_kb": page_size_kb,
            "overall_score": 85  # Placeholder logic
        }

    except Exception as e:
        return {
            "error": str(e)
        }
