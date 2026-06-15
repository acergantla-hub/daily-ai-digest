#!/usr/bin/env python3
"""
Daily AI Digest — Main Pipeline Script
Runs daily to: search news, write blog post, build site, deploy to GitHub, generate Instagram images.

Usage: python daily_run.py [--dry-run]
"""

import os
import sys
import re
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

# ── config ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"
DIST_DIR = BASE_DIR / "dist"
IG_DIR = BASE_DIR / "instagram_posts"
GITHUB_REPO = "acergantla-hub/daily-ai-digest"

# AI news sources to search
NEWS_SOURCES = [
    "techcrunch.com/category/artificial-intelligence",
    "arstechnica.com/ai",
    "theverge.com/ai-artificial-intelligence",
    "venturebeat.com/ai",
    "hacker-news",
    "reuters.com/technology/artificial-intelligence",
    "bbc.com/news",
    "404media.co",
    "simonwillison.net",
    "anthropic.com/news",
    "openai.com/news",
    "blog.google/technology/ai",
    "economist.com",
]

def run_cmd(cmd, cwd=None, check=True):
    """Run a shell command and return output."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or str(BASE_DIR),
        capture_output=True, text=True
    )
    if check and result.returncode != 0:
        print(f"  ⚠ Command failed: {cmd}")
        print(f"    stderr: {result.stderr[:500]}")
    return result

# ── step 1: search for AI news ──────────────────────────────────────

def search_ai_news():
    """Search for today's top AI news from multiple sources."""
    print("\n🔍 Searching for today's AI news...")

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    all_stories = []

    # Search each source via curl
    for source in NEWS_SOURCES:
        if "hacker-news" in source:
            try:
                result = run_cmd(
                    "curl -sL 'https://hacker-news.firebaseio.com/v0/topstories.json' 2>/dev/null",
                    check=False
                )
                if result.returncode == 0 and result.stdout.strip():
                    ids = json.loads(result.stdout[:5000])
                    for story_id in ids[:30]:
                        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                        story_result = run_cmd(f"curl -sL '{story_url}' 2>/dev/null", check=False)
                        if story_result.returncode == 0 and story_result.stdout.strip():
                            try:
                                story = json.loads(story_result.stdout)
                                if story and 'title' in story:
                                    title = story.get('title', '')
                                    # AI-related keywords
                                    ai_keywords = ['ai', 'gpt', 'claude', 'llm', 'openai', 'anthropic',
                                                   'gemini', 'mistral', 'agent', 'machine learning',
                                                   'deepmind', 'neural', 'copilot', 'chatgpt', 'llama',
                                                   'artificial intelligence', 'nvidia', 'ai chip',
                                                   'sora', 'diffusion', 'transformer', 'cursor']
                                    if any(kw in title.lower() for kw in ai_keywords):
                                        url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                                        score = story.get('score', 0)
                                        all_stories.append({
                                            'title': title,
                                            'url': url,
                                            'source': 'Hacker News',
                                            'score': score,
                                        })
                            except:
                                pass
            except:
                pass
        else:
            # Try to fetch recent articles from the source
            try:
                search_url = f"https://{source}"
                result = run_cmd(f"curl -sL --max-time 10 '{search_url}' 2>/dev/null", check=False)
                if result.returncode == 0 and result.stdout:
                    # Extract article titles and links
                    titles = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*(?:AI|GPT|Claude|LLM|OpenAI|Anthropic|Gemini|Mistral|Agent|ChatGPT|Machine Learning|DeepMind|Neural|Copilot|Llama|Nvidia|Artificial Intelligence)[^<]*)</a>', result.stdout, re.IGNORECASE)
                    for url, title in titles[:10]:
                        title = title.strip()
                        if title and len(title) > 10 and len(title) < 200:
                            if not url.startswith('http'):
                                url = f"https://{source}{url}"
                            all_stories.append({
                                'title': title,
                                'url': url,
                                'source': source,
                                'score': 0,
                            })
            except:
                pass

    # Deduplicate by title
    seen = set()
    unique_stories = []
    for s in all_stories:
        key = s['title'].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique_stories.append(s)

    # Sort by score (HN stories) or just take first 12
    unique_stories.sort(key=lambda x: x['score'], reverse=True)

    print(f"  Found {len(unique_stories)} unique AI stories")
    for i, s in enumerate(unique_stories[:12]):
        print(f"    {i+1}. {s['title'][:70]} ({s['source']})")

    return unique_stories[:12]

# ── step 2: fetch article content ────────────────────────────────────

def fetch_article_content(url):
    """Fetch and extract main content from a URL."""
    try:
        result = run_cmd(f"curl -sL --max-time 15 '{url}' 2>/dev/null", check=False)
        if result.returncode == 0 and result.stdout:
            html = result.stdout
            # Remove script/style
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000]
    except:
        pass
    return ""

# ── step 3: write blog post (LLM-generated via Hermes) ──────────────

def generate_blog_post(stories, date_str):
    """Generate a blog post markdown file from the collected stories."""
    print("\n✍️  Generating blog post...")

    dt = datetime.strptime(date_str, "%Y-%m-%d")
    display_date = dt.strftime("%B %d, %Y")

    # Build the prompt/context for the blog post
    stories_context = []
    for i, story in enumerate(stories):
        content = fetch_article_content(story['url'])
        stories_context.append({
            'index': i + 1,
            'title': story['title'],
            'url': story['url'],
            'source': story['source'],
            'content': content[:2000],
        })

    # Save stories data for the LLM to process
    stories_json = BASE_DIR / ".current_stories.json"
    stories_json.write_text(json.dumps({
        'date': date_str,
        'display_date': display_date,
        'stories': stories_context,
    }, indent=2))

    print(f"  Saved {len(stories_context)} stories to {stories_json}")
    print("  Blog post content ready for generation")
    print(f"  Stories data: {stories_json}")

    return stories_json

def write_blog_post_from_llm(date_str, stories_data_path, llm_output):
    """Write the blog post markdown from the LLM-generated content."""
    display_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")

    # The LLM output is the full markdown content (without frontmatter)
    # We add frontmatter
    frontmatter = f"""---
title: "Daily AI Digest — {date_str}"
date: "{date_str}"
category: Daily Digest
excerpt: "Today's top AI news digest covering {len(stories_data_path)} stories."
tags: ai-agents, claude-code, daily-digest, ai-news
---

"""

    post_path = POSTS_DIR / f"{date_str}-daily-ai-digest.md"
    post_path.write_text(frontmatter + llm_output, encoding='utf-8')
    print(f"  ✓ Blog post written: {post_path}")
    return post_path

# ── step 4: build site ──────────────────────────────────────────────

def build_site():
    """Build the static site."""
    print("\n🔨 Building site...")
    result = run_cmd("python3 build.py")
    print(result.stdout)
    return result.returncode == 0

# ── step 5: deploy to GitHub ────────────────────────────────────────

def deploy_to_github():
    """Push to GitHub (triggers Cloudflare Pages deploy)."""
    print("\n📤 Deploying to GitHub...")

    # Configure git if not already
    run_cmd("git config user.email 'hermes@termux' 2>/dev/null", check=False)
    run_cmd("git config user.name 'Hermes' 2>/dev/null", check=False)

    # Add all changes
    run_cmd("git add -A")

    # Check if there are changes to commit
    status = run_cmd("git status --porcelain", check=False)
    if not status.stdout.strip():
        print("  No changes to commit")
        return True

    # Commit
    date_str = datetime.now().strftime("%Y-%m-%d")
    commit_result = run_cmd(
        f'git commit -m "Add Daily AI Digest for {date_str}"',
        check=False
    )

    # Push
    push_result = run_cmd("git push origin main", check=False)
    if push_result.returncode == 0:
        print("  ✓ Pushed to GitHub → Cloudflare Pages will auto-deploy")
    else:
        print(f"  ⚠ Push failed: {push_result.stderr[:200]}")
        return False

    return True

# ── step 6: generate Instagram images ───────────────────────────────

def generate_instagram_images(md_path):
    """Generate Instagram carousel images."""
    print("\n📸 Generating Instagram images...")
    result = run_cmd(f"python3 generate_images.py {md_path}")
    print(result.stdout)
    return result.returncode == 0

# ── step 7: generate caption ────────────────────────────────────────

def generate_caption(md_path):
    """Generate Instagram caption from blog post."""
    content = md_path.read_text()

    # Extract key info
    title_match = re.search(r'title:\s*"(.+?)"', content)
    title = title_match.group(1) if title_match else "Daily AI Digest"

    date_match = re.search(r'date:\s*"(.+?)"', content)
    date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    # Extract story titles
    story_titles = re.findall(r'###\s+(.+)', content)
    story_titles = [t for t in story_titles if "Why This Matters" not in t][:10]

    # Build caption
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    display_date = dt.strftime("%B %d, %Y")

    caption = f"""🤖 Daily AI Digest — {display_date}

Today's top {len(story_titles)} AI stories:

"""
    for i, t in enumerate(story_titles, 1):
        # Clean markdown formatting
        clean = re.sub(r'\*\*', '', t)
        caption += f"{i}. {clean}\n"

    caption += f"""
🔗 Read the full digest: daily-ai-digest.dev

#AI #ArtificialIntelligence #AIagents #ClaudeCode #ChatGPT #OpenAI #Anthropic #GoogleAI #tech #ainews #technews #machinelearning #daily digest #airesearch #gpt"""

    caption_path = BASE_DIR / "instagram_posts" / "caption.txt"
    caption_path.write_text(caption, encoding='utf-8')
    print(f"  ✓ Caption saved: {caption_path}")
    return caption

# ── main ─────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    date_str = datetime.now().strftime("%Y-%m-%d")

    print("=" * 60)
    print(f"🤖 Daily AI Digest Pipeline — {date_str}")
    print("=" * 60)

    if dry_run:
        print("  [DRY RUN — no commits or pushes]\n")

    # Step 1: Search for news
    stories = search_ai_news()

    if not stories:
        print("\n⚠ No AI stories found. Trying broader search...")
        # Fallback: search HN only
        stories = search_ai_news()

    if not stories:
        print("\n❌ Could not find any AI news. Exiting.")
        sys.exit(1)

    # Step 2: Generate blog post data
    stories_json = generate_blog_post(stories, date_str)

    # Step 3: Use LLM to write the actual post
    # This is where Hermes will be invoked
    print(f"\n📝 Stories data ready at: {stories_json}")
    print("  This file contains all the data needed to write the blog post.")

    # Output the stories data for the LLM agent to process
    data = json.loads(stories_json.read_text())
    print(f"\n--- STORIES DATA FOR LLM ({len(data['stories'])} stories) ---")
    for s in data['stories']:
        print(f"\n{s['index']}. {s['title']}")
        print(f"   Source: {s['source']}")
        print(f"   URL: {s['url']}")
        print(f"   Content preview: {s['content'][:200]}...")

    print(f"\n--- END STORIES DATA ---")
    print(f"\n✅ Pipeline ready. Use this data to write the blog post.")

    return data

if __name__ == '__main__':
    main()
