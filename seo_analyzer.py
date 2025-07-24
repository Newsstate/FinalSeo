import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re


def is_valid_link(href):
    return href and not href.startswith('#') and not href.lower().startswith('javascript:')


def extract_seo_data(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return {"error": f"Failed to fetch URL: {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        # Meta tags
        title = soup.title.string.strip() if soup.title else ''
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        meta_robots = soup.find("meta", attrs={"name": "robots"})
        canonical_tag = soup.find("link", rel="canonical")
        lang_tag = soup.html.get("lang") if soup.html else None

        # Breadcrumb detection
        breadcrumb = soup.select('[itemtype*="BreadcrumbList"]')

        # Date detection
        date_published = soup.find("meta", attrs={"property": "article:published_time"}) or \
                         soup.find("meta", attrs={"name": "date"})
        date_modified = soup.find("meta", attrs={"property": "article:modified_time"})

        # Author detection
        author = soup.find("meta", attrs={"name": "author"})
        author_link = soup.find("a", href=True, text=re.compile("author", re.IGNORECASE))

        # Robots.txt
        robots_txt_url = urljoin(base_url, "/robots.txt")
        robots_txt = requests.get(robots_txt_url).text if "robots.txt" in robots_txt_url else ""

        # max-image-preview
        max_preview = "large" in (meta_robots["content"].lower() if meta_robots and meta_robots.has_attr("content") else "")

        # Schema
        schemas = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "@type" in data:
                    schemas.append(data["@type"])
                elif isinstance(data, list):
                    schemas.extend([item.get("@type") for item in data if "@type" in item])
            except Exception:
                continue

       # Broken links
links = soup.find_all("a", href=True)
broken_links = 0
nofollow_links = 0
external_links = 0

for i, link in enumerate(links[:5]):  # Limit to 5 links for performance
    href = link.get("href")
    rel = link.get("rel")
    if not is_valid_link(href):
        continue
    full_url = urljoin(url, href)
    if "nofollow" in (rel or []):
        nofollow_links += 1
    if urlparse(full_url).netloc != urlparse(url).netloc:
        external_links += 1
    try:
        res = requests.head(full_url, allow_redirects=True, timeout=3)
        if res.status_code >= 400:
            broken_links += 1
    except Exception:
        broken_links += 1


        # Score calculation
        score = {
            "Metadata": int(bool(title) and bool(meta_desc)) * 100,
            "Links": max(100 - broken_links * 2, 0),
            "Schema": min(len(schemas) * 10, 100),
            "Technical": 75 if robots_txt else 50
        }
        overall_score = int(sum(score.values()) / len(score))

        return {
            "meta_title": title,
            "meta_description": meta_desc["content"] if meta_desc and meta_desc.has_attr("content") else "",
            "meta_keywords_length": len(meta_keywords["content"]) if meta_keywords and meta_keywords.has_attr("content") else 0,
            "canonical": canonical_tag["href"] if canonical_tag and canonical_tag.has_attr("href") else None,
            "canonical_self": canonical_tag and canonical_tag["href"] == url,
            "robots_tag": meta_robots["content"] if meta_robots and meta_robots.has_attr("content") else "",
            "lang_tag": lang_tag,
            "breadcrumb_present": bool(breadcrumb),
            "date_published": date_published["content"] if date_published and date_published.has_attr("content") else "",
            "date_modified": date_modified["content"] if date_modified and date_modified.has_attr("content") else "",
            "author_profile_clickable": bool(author_link),
            "broken_links": broken_links,
            "external_links_nofollow": nofollow_links,
            "schema_types": schemas,
            "robots_txt_contains": robots_txt[:300],
            "max_image_preview_large": max_preview,
            "score_breakdown": score,
            "overall_score": overall_score,
            "url": url
        }

    except Exception as e:
        return {"error": str(e), "url": url}

