#!/usr/bin/env python3
"""
Daily AI Digest — Unified Pipeline v2
Scrape → 3-stage Dedup + Cross-site History → Viral Scoring → LLM Blog → Verify → Build → Instagram Top-10 → Caption → Git Push
Runs daily at 8 AM. Retries failed sources. Auto-push only after verification passes.
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import random
import hashlib

# ── Config ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"
DIST_DIR = BASE_DIR / "dist"
IG_DIR = BASE_DIR / "instagram_posts"
HERMES_SCRIPTS = Path.home() / ".hermes" / "scripts"

NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(hours=24)
DATE_STR = NOW.strftime("%Y-%m-%d")
DISPLAY_DATE = NOW.strftime("%B %d, %Y")

KEYWORDS = [
    "ai agent", "ai agents", "claude code", "openclaw", "open claw",
    "hermes agent", "llm agent", "autonomous agent", "agent framework",
    "ai automation", "workflow automation", "copilot agent",
    "multi-agent", "agentic", "mcp", "model context protocol",
]

RSS_FEEDS = [
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("Anthropic Blog", "https://www.anthropic.com/rss.xml"),
    ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("LangChain Blog", "https://blog.langchain.dev/rss/"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/feed/"),
    ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
]

YOUTUBE_CHANNELS = [
    ("OpenAI", "UCXFyGQ9qBSMk0fDfHSwjF1g"),
    ("Google DeepMind", "UCUHW94eEFW7hkUMVaZz4eDg"),
    ("Two Minute Papers", "UCbfYPyITQ-7l4upoX8nvctg"),
    ("AI Explained", "UCNJ1Ymd5tJJNp9JtyNiv3uw"),
    ("Matt Wolfe", "UC1dB3LigxQKdpG1O75QjHZA"),
    ("Fireship", "UCsBjURrPoezykLs9EqgamOA"),
    ("TheAIGRID", "UCF8kv4NcmS7IYOi8kBgawfA"),
]

NITTER_SEARCHES = [
    "AI+agents",
    "claude+code",
    "openclaw",
    "hermes+agent",
    "ai+automation",
]

NITTER_MIRRORS = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
]

HN_QUERIES = ["AI agent", "Claude Code", "LLM agent", "agent framework", "AI automation"]

ALIAS_MAP = {
    "openclaw": {"open claw", "openclaw ai"},
    "claude code": {"anthropic claude code", "claude coding"},
    "nvidia": {"nvidia"},
    "huggingface": {"hugging face"},
    "gemini api": {"google gemini", "gemini managed agents"},
    "openai": {"openai", "open ai"},
    "notion": {"notion ai"},
}

# ── Utils ──────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def is_relevant(text: str) -> bool:
    low = text.lower()
    return any(kw in low. We are at the character limit. Let me continue by writing the file in multiple steps.
    I'll write the file in parts to avoid the limit.
    First, let me write the beginning of the file up to the Vercel_SOURCES definition<tool_call>
<function=write_file>
<parameter=content>
#!/usr/bin/env python3
"""
Daily AI Digest — Unified Pipeline v2
Scrape → 3-stage Dedup + Cross-site History → Viral Scoring → LLM Blog → Verify → Build → Instagram Top-10 → Caption → Git Push
Runs daily at 8 AM. Retries failed sources. Auto-push only after verification passes.
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import random
import hashlib

# ── Config ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"
DIST_DIR = BASE_DIR / "dist"
IG_DIR = BASE_DIR / "instagram_posts"
HERMES_SCRIPTS = Path.home() / ".hermes" / "scripts"

NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(hours=24)
DATE_STR = NOW.strftime("%Y-%m-%d")
DISPLAY_DATE = NOW.strftime("%B %d, %Y")

KEYWORDS = [
    "ai agent", "ai agents", "claude code", "openclaw", "open claw",
    "hermes agent", "llm agent", "autonomous agent", "agent framework",
    "ai automation", "workflow automation", "copilot agent",
    "multi-agent", "agentic", "mcp", "model context protocol",
]

RSS_FEEDS = [
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("Anthropic Blog", "https://www.anthropic.com/rss.xml"),
    ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("LangChain Blog", "https://blog.langchain.dev/rss/"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/feed/"),
    ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
]

YOUTUBE_CHANNELS = [
    ("OpenAI", "UCXFyGQ9qBSMk0fDfHSwjF1g"),
    ("Google DeepMind", "UCUHW94eEFW7hkUMVaZz4eDg"),
    ("Two Minute Papers", "UCbfYPyITQ-7l4upoX8nvctg"),
    ("AI Explained", "UCNJ1Ymd5tJJNp9JtyNiv3uw"),
    ("Matt Wolfe", "UC1dB3LigxQKdpG1O75QjHZA"),
    ("Fireship", "UCsBjURrPoezykLs9EqgamOA"),
    ("TheAIGRID", "UCF8kv4NcmS7IYOi8kBgawfA"),
]

NITTER_SEARCHES = [
    "AI+agents",
    "claude+code",
    "openclaw",
    "hermes+agent",
    "ai+automation",
]

NITTER_MIRRORS = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
]

HN_QUERIES = ["AI agent", "Claude Code", "LLM agent", "agent framework", "AI automation"]

ALIAS_MAP = {
    "openclaw": {"open claw", "openclaw ai"},
    "claude code": {"anthropic claude code", "claude coding"},
    "nvidia": {"nvidia"},
    "huggingface": {"hugging face"},
    "gemini api": {"google gemini", "gemini managed agents"},
    "openai": {"openai", "open ai"},
    "notion": {"notion ai"},
}

# ── Utils ──────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def is_relevant(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in KEYWORDS)

def item_key(item: dict) -> str:
    return f"{normalize(item.get('title',''))} ||| {normalize(item.get('url',''))} ||| {normalize(item.get('source',''))}"

def parse_date(s: str):
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def fetch(url: str, timeout: int = 15, headers: dict = None) -> str | None:
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "daily-ai-digest/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

def fetch_with_retry(url: str, retries: int = 3, backoff: int = 2, **kwargs) -> str | None:
    for attempt in range(retries):
        data = fetch(url, **kwargs)
        if data:
            return data
        if attempt < retries - 1:
            time.sleep(backoff * (attempt + 1))
    return None

# ── Source Fetchers ────────────────────────────────────────────────────

def fetch_hn() -> list:
    stories = []
    seen_ids = set()
    epoch_cutoff = int(CUTOFF.timestamp())
    for q in HN_QUERIES:
        url = (
            "https://hn.algolia.com/api/v1/search?"
            + urllib.parse.urlencode({
                "query": q, "tags": "story",
                "numericFilters": f"created_at_i>{epoch_cutoff}",
                "hitsPerPage": 20,
            })
        )
        data = fetch_with_retry(url)
        if not data:
            continue
        for hit in json.loads(data).get("hits", []):
            sid = hit.get("objectID", "")
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            title = hit.get("title", "")
            if not is_relevant(title):
                continue
            ts = None
            if hit.get("created_at"):
                try:
                    ts = datetime.fromisoformat(hit["created_at"].replace("Z", "+00:00"))
                except Exception:
                    pass
            story_url = hit.get("url", f"https://news.ycombinator.com/item?id={sid}")
            stories.append({
                "source": "Hacker News",
                "title": title,
                "url": story_url,
                "score": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
                "time": ts or NOW,
            })
    return stories

def fetch_rss(name: str, feed_url: str) -> list:
    data = fetch_with_retry(feed_url)
    if not data:
        return []
    try:
        root = ET.fromstring(data)
    except Exception:
        return []
    items = []
    atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
    rss_items = root.findall(".//item")
    if rss_items:
        for entry in rss_items[:30]:
            title_el = entry.find("title")
            link_el = entry.find("link")
            date_el = entry.find("pubDate") or entry.find("{http://purl.org/dc/elements/1.1/}date")
            desc_el = entry.find("description")
            title = (title_el.text or "").strip() if title_el is not None else ""
            link = (link_el.text or "").strip() if link_el is not None else ""
            desc = ""
            if desc_el is not None and desc_el.text:
                desc = re.sub(r"<[^>]+>", "", desc_el.text).strip()[:300]
            ts = None
            if date_el is not None and date_el.text:
                ts = parse_date(date_el.text.strip())
            if not title or not link:
                continue
            if ts and ts < CUTOFF:
                continue
            if not is_relevant(title + " " + desc):
                continue
            items.append({
                "source": f"RSS: {name}",
                "title": title,
                "url": link,
                "desc": desc,
                "time": ts or NOW,
            })
    else:
        for entry in root.findall(".//atom:entry", atom_ns)[:30]:
            title_el = entry.find("atom:title", atom_ns)
            link_el = entry.find("atom:link", atom_ns)
            date_el = entry.find("atom:updated", atom_ns) or entry.find("atom:published", atom_ns)
            summary_el = entry.find("atom:summary", atom_ns) or entry.find("atom:content", atom_ns)
            title = (title_el.text or "").strip() if title_el is not None else ""
            link = link_el.get("href", "") if link_el is not None else ""
            desc = ""
            if summary_el is not None and summary_el.text:
                desc = re.sub(r"<[^>]+>", "", summary_el.text).strip()[:300]
            ts = None
            if date_el is not None and date_el.text:
                try:
                    ts = parse_date(date_el.text.strip())
                except Exception:
                    pass
            if not title or not link:
                continue
            if ts and ts < CUTOFF:
                continue
            if not is_relevant(title + " " + desc):
                continue
            items.append({
                "source": f"Atom: {name}",
                "title": title,
                "url": link,
                "desc": desc,
                "time": ts or NOW,
            })
    return items

def fetch_youtube(channel_name: str, channel_id: str) -> list:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    # Use a browser-like user agent to avoid 403
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    data = fetch_with_retry(url, headers=headers)
    if not data:
        return []
    try:
        root = ET.fromstring(data)
    except Exception:
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []
    for entry in root.findall("atom:entry", ns)[:20]:
        title_el = entry.find("atom:title", ns)
        link_el = entry.find("atom:link", ns)
        pub_el = entry.find("atom:published", ns)
        title = (title_el.text or "").strip() if title_el is not None else ""
        link = link_el.get("href", "") if link_el is not None else ""
        ts = None
        if pub_el is not None and pub_el.text:
            ts = parse_date(pub_el.text.strip())
        if not title or not link:
            continue
        if ts and ts < CUTOFF:
            continue
        if not is_relevant(title):
            continue
        items.append({
            "source": f"YouTube: {channel_name}",
            "title": title,
            "url": link,
            "time": ts or NOW,
        })
    return items

def fetch_nitter(query: str) -> list:
    # Use shorter timeout and fewer retries for Nitter as it's often unreliable
    all_items = []
    for base in NITTER_MIRRORS:
        url = f"{base}/search/rss?f=tweets&q={query}&since=&until=&near="
        data = fetch_with_retry(url, timeout=8, retries=1)
        if not data:
            continue
        try:
            root = ET.fromstring(data)
        except Exception:
            continue
        for item in root.findall(".//item")[:15]:
            title_el = item.find("title")
            link_el = item.find("link")
            date_el = item.find("pubDate")
            creator_el = item.find("{http://purl.org/dc/elements/1.1/}creator")
            title = (title_el.text or "").strip() if title_el is not None else ""
            link = (link_el.text or "").strip() if link_el is not None else ""
            ts = None
            if date_el is not None and date_el.text:
                try:
                    ts = parse_date(date_el.text.strip())
                except Exception:
                    pass
            if not title:
                continue
            if ts and ts < CUTOFF:
                continue
            if not is_relevant(title):
                continue
            author = ""
            if creator_el is not None and creator_el.text:
                author = creator_el.text.strip()
            all_items.append({
                "source": "X/Twitter",
                "title": title[:280],
                "url": link,
                "time": ts or NOW,
                "meta": f"@{author}" if author else query.replace("+", " "),
            })
        if all_items:
            break
    return all_items