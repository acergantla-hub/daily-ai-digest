#!/usr/bin/env python3
"""
Daily AI Digest — Main Pipeline Script (Fast Version)
Only searches high-signal sources with short timeouts.
"""

import os
import sys
import re
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"
DIST_DIR = BASE_DIR / "dist"
IG_DIR = BASE_DIR / "instagram_posts"

# Only high-signal sources with fast responses
NEWS_SOURCES = {
    "Hacker News": "https://hacker-news.firebaseio.com/v0/topstories.json",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/",
    "ArsTechnica AI": "https://arstechnica.com/ai/",
    "The Verge AI": "https://www.theverge.com/ai-artificial-intelligence",
    "VentureBeat AI": "https://venturebeat.com/category/ai/",
    "Simon Willison": "https://simonwillison.net/",
    "Anthropic": "https://www.anthropic.com/news",
    "OpenAI": "https://openai.com/news",
    "Google AI": "https://blog.google/technology/ai/",
}
# URL patterns that are NEVER signal
NOISE_URL_PATTERNS = [
    r"/category/", r"/tag/", r"/author/", r"/page/\d+", r"\.pdf$",
    r"news\.ycombinator\.com/item\?id=", r"hacker-news\.firebaseio\.com",
    r"platform\.claude\.com/cookbook", r"axios\.com",
]
AI_KEYWORDS = [
    'ai', 'gpt', 'claude', 'llm', 'openai', 'anthropic', 'gemini', 'mistral',
    'agent', 'machine learning', 'deepmind', 'neural', 'copilot', 'chatgpt',
    'llama', 'artificial intelligence', 'nvidia', 'ai chip', 'sora',
    'diffusion', 'transformer', 'cursor', 'windsurf', 'codex', 'devin',
    'agentic', 'orchestrat', 'mcp', 'context protocol', 'rag', 'retrieval',
    'nouscoder', 'qwen', 'kimi', 'open weight', 'open-weight', 'local model',
    'vulnerability', 'exploit', 'injection', 'phishing', 'aegisai',
    'credential', 'secret leak', 'supply chain', 'starlette', 'badhost',
    'rogue agent', 'smuggle', 'memory poison', 'guardrail', 'red team',
    'benchmark', 'eval', 'scarfbench', 'itbench', 'agentx', 'unslop',
    'slackbot', 'salesforce', 'workspace', 'enterprise', 'robinhood',
    'sierra', 'takeoff', 'presence', 'cowork', 'managed agent',
]


def run_cmd(cmd, cwd=None, timeout=15):
    """Run a shell command with timeout."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd or str(BASE_DIR),
            capture_output=True, text=True, timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, -1, "", "Timeout")
    except Exception as e:
        return subprocess.CompletedProcess(cmd, -1, "", str(e))


def is_ai_relevant(title: str, url: str = "") -> bool:
    """Check if story is AI-relevant."""
    for pat in NOISE_URL_PATTERNS:
        if re.search(pat, url, re.IGNORECASE):
            return False
    title_lower = title.lower()
    return any(kw in title_lower for kw in AI_KEYWORDS)


def extract_article_links(html: str, base_url: str) -> list[tuple[str, str]]:
    """Extract article title + URL from listing page."""
    links = []
    patterns = [
        r'<a[^>]*href="([^"]*/20\d\d/\d\d/\d\d/[^"]*)"[^>]*>([^<]{20,200})</a>',
        r'<h[23][^>]*><a[^>]*href="([^"]*)"[^>]*>([^<]{20,200})</a></h[23]>',
        r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*[Hh]eadline[^"]*"[^>]*>([^<]{20,200})</a>',
        r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*[Pp]ost[^"]*"[^>]*>([^<]{20,200})</a>',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for url, title in matches:
            title = title.strip()
            if len(title) < 20 or len(title) > 200:
                continue
            if not url.startswith('http'):
                if url.startswith('/'):
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    url = f"{parsed.scheme}://{parsed.netloc}{url}"
                else:
                    continue
            links.append((url, title))
    return links


def fetch_content(url: str) -> str:
    """Fetch and extract main content - fast."""
    result = run_cmd(f"curl -sL --max-time 8 '{url}' 2>/dev/null")
    if result.returncode != 0 or not result.stdout:
        return ""
    html = result.stdout
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Try article/main content areas
    for pattern in [r'<article[^>]*>(.*?)</article>', r'<main[^>]*>(.*?)</main>', 
                    r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>']:
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        if matches:
            text = ' '.join(matches)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000]
    
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:2000]


def search_ai_news():
    """Search for today's top AI news."""
    print("\n🔍 Searching for today's AI news...")
    all_stories = []

    # 1. Hacker News - fast API
    result = run_cmd("curl -sL 'https://hacker-news.firebaseio.com/v0/topstories.json' 2>/dev/null", timeout=8)
    if result.returncode == 0 and result.stdout.strip():
        ids = json.loads(result.stdout[:5000])
        for story_id in ids[:30]:  # Reduced from 40
            story_result = run_cmd(f"curl -sL 'https://hacker-news.firebaseio.com/v0/item/{story_id}.json' 2>/dev/null", timeout=3)
            if story_result.returncode == 0 and story_result.stdout.strip():
                try:
                    story = json.loads(story_result.stdout)
                    if story and 'title' in story:
                        title = story.get('title', '')
                        url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                        if is_ai_relevant(title, url):
                            all_stories.append({
                                'title': title, 'url': url, 'source': 'Hacker News', 'score': story.get('score', 0)
                            })
                except:
                    pass

    # 2. Other sources - fetch listing pages with 8s timeout
    for source_name, source_url in NEWS_SOURCES.items():
        if source_name == "Hacker News":
            continue
        result = run_cmd(f"curl -sL --max-time 8 '{source_url}' 2>/dev/null", timeout=8)
        if result.returncode == 0 and result.stdout:
            links = extract_article_links(result.stdout, source_url)
            for url, title in links[:6]:  # Reduced from 8
                if is_ai_relevant(title, url):
                    all_stories.append({
                        'title': title, 'url': url, 'source': source_name, 'score': 0
                    })

    # Deduplicate - by URL (canonical) + fuzzy title
    seen_urls = set()
    seen_titles = set()
    unique = []
    
    def normalize_url(url: str) -> str:
        """Normalize URL for deduplication."""
        # Remove query params, fragments, trailing slash
        url = url.split('?')[0].split('#')[0].rstrip('/')
        # Normalize www
        url = url.replace('://www.', '://')
        return url.lower()
    
    def normalize_title(title: str) -> str:
        """Normalize title for fuzzy matching."""
        # Lowercase, remove punctuation, collapse whitespace
        t = title.lower()
        t = re.sub(r'[^\w\s]', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        # Remove common prefix/suffix words that vary
        t = re.sub(r'^(exclusive|breaking|analysis|opinion|review)\s+', '', t)
        t = re.sub(r'\s+(exclusive|breaking|analysis|opinion|review)$', '', t)
        return t
    
    for s in all_stories:
        norm_url = normalize_url(s['url'])
        norm_title = normalize_title(s['title'])
        
        # Check URL first (strongest signal)
        if norm_url in seen_urls:
            continue
        
        # Check fuzzy title (last 50 chars of normalized title)
        title_key = norm_title[-50:] if len(norm_title) > 50 else norm_title
        # Also check if very similar title exists (substring match)
        is_dup = False
        for existing in seen_titles:
            if title_key in existing or existing in title_key:
                # High overlap - likely same story
                if len(title_key) > 20 and len(existing) > 20:
                    is_dup = True
                    break
        
        if is_dup:
            continue
            
        seen_urls.add(norm_url)
        seen_titles.add(norm_title)
        unique.append(s)

    # Priority sort
    priority = {'TechCrunch AI': 10, 'ArsTechnica AI': 9, 'The Verge AI': 8, 
                'VentureBeat AI': 7, 'Simon Willison': 6, 'Anthropic': 5,
                'OpenAI': 5, 'Google AI': 5, 'Hacker News': 3}
    unique.sort(key=lambda x: (priority.get(x['source'], 0), x['score']), reverse=True)

    print(f"  Found {len(unique)} unique AI stories")
    for i, s in enumerate(unique[:12]):
        print(f"    {i+1}. {s['title'][:70]} ({s['source']})")
    return unique[:12]


def generate_blog_post_data(stories: list, date_str: str):
    """Generate blog post data JSON."""
    print("\n✍️  Generating blog post data...")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    display_date = dt.strftime("%B %d, %Y")

    stories_context = []
    for i, story in enumerate(stories):
        content = fetch_content(story['url'])
        stories_context.append({
            'index': i + 1,
            'title': story['title'],
            'url': story['url'],
            'source': story['source'],
            'content': content,
        })

    stories_json = BASE_DIR / ".current_stories.json"
    stories_json.write_text(json.dumps({
        'date': date_str,
        'display_date': display_date,
        'stories': stories_context,
    }, indent=2))

    print(f"  Saved {len(stories_context)} stories to {stories_json}")
    return stories_json


def build_site():
    """Build the static site."""
    print("\n🔨 Building site...")
    result = run_cmd("python3 build.py", timeout=60)
    print(result.stdout)
    return result.returncode == 0


def deploy_to_github():
    """Push to GitHub."""
    print("\n📤 Deploying to GitHub...")
    run_cmd("git config user.email 'hermes@termux' 2>/dev/null")
    run_cmd("git config user.name 'Hermes' 2>/dev/null")
    run_cmd("git add -A")
    status = run_cmd("git status --porcelain")
    if not status.stdout.strip():
        print("  No changes to commit")
        return True
    date_str = datetime.now().strftime("%Y-%m-%d")
    run_cmd(f'git commit -m "Add Daily AI Digest for {date_str}"', check=False)
    result = run_cmd("git push origin main", check=False, timeout=60)
    if result.returncode == 0:
        print("  ✓ Pushed to GitHub → Cloudflare Pages will auto-deploy")
    else:
        print(f"  ⚠ Push failed: {result.stderr[:200]}")
        return False
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    date_str = datetime.now().strftime("%Y-%m-%d")

    print("=" * 60)
    print(f"🤖 Daily AI Digest Pipeline — {date_str}")
    print("=" * 60)

    stories = search_ai_news()
    if not stories:
        print("\n⚠ No AI stories found. Exiting.")
        sys.exit(1)

    stories_json = generate_blog_post_data(stories, date_str)

    print(f"\n📝 Stories data ready at: {stories_json}")
    data = json.loads(stories_json.read_text())
    print(f"\n--- STORIES DATA FOR LLM ({len(data['stories'])} stories) ---")
    for s in data['stories']:
        print(f"\n{s['index']}. {s['title']}")
        print(f"   Source: {s['source']}")
        print(f"   URL: {s['url']}")
        print(f"   Content: {s['content'][:150]}...")
    print(f"\n--- END STORIES DATA ---")
    print(f"\n✅ Pipeline ready. Run: python3 generate_post.py")


if __name__ == '__main__':
    main()