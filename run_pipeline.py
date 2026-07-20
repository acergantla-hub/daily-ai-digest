#!/usr/bin/env python3
"""
Daily AI Digest — Simple Pipeline
Runs the existing scripts in sequence with verification.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"
DIST_DIR = BASE_DIR / "dist"
IG_DIR = BASE_DIR / "instagram_posts"
HERMES_SCRIPTS = Path.home() / ".hermes" / "scripts"

def run_cmd(cmd, cwd=None, check=True):
    """Run a shell command and return success."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or str(BASE_DIR),
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr[:500]}")
        if check:
            return False
    else:
        print(f"  OK: {result.stdout.strip()[:200]}")
    return True

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    display_date = datetime.now().strftime("%B %d, %Y")
    print("=" * 60)
    print(f"🤖 Daily AI Digest Pipeline — {display_date}")
    print("=" * 60)

    # Step 1: Scrape news
    print("\n📡 [1/6] Scraping news...")
    if not run_cmd(f"python3 {HERMES_SCRIPTS}/daily-ai-digest.py > today_news.txt 2>&1"):
        return 1

    # Check if we got any news
    if not os.path.exists("today_news.txt") or os.path.getsize("today_news.txt") == 0:
        print("  No news found.")
        return 1

    # Step 2: Generate blog post using Hermes
    print("\n✍️  [2/6] Generating blog post...")
    # Read the news
    with open("today_news.txt", "r") as f:
        news_content = f.read()

    # Build prompt for Hermes
    prompt = f"""You are the Daily AI Digest writer. Your job: read the following news scraped from various sources (Hacker News, RSS feeds, YouTube, X/Twitter) and write a markdown blog post for {display_date}.

The news is provided below. You must:
- Select 12-15 of the most relevant stories
- For each story, write a 3-5 sentence summary with concrete facts
- Provide 3-5 key takeaways per story
- Group stories by theme (agents, models, business, research, hardware, policy)
- End with a "Why This Matters Today" section
- Use the exact format of existing posts in {POSTS_DIR}/
- Output ONLY the markdown content (no explanations)

NEWS CONTENT:
{news_content}

OUTPUT FILE: {POSTS_DIR}/{date_str}-daily-ai-digest.md
"""

    # Write prompt to a file for debugging
    with open("hermes_prompt.txt", "w") as f:
        f.write(prompt)

    # Run Hermes
    if not run_cmd(f'hermes chat -q "{prompt}" > {POSTS_DIR}/{date_str}-daily-ai-digest.md 2>&1'):
        return 1

    # Check the post
    post_path = POSTS_DIR / f"{date_str}-daily-ai-digest.md"
    if not post_path.exists() or post_path.stat().st_size < 500:
        print("  Blog post generation failed or too small.")
        return 1

    # Step 3: Build site
    print("\n🔨 [3/6] Building site...")
    if not run_cmd("python3 build.py"):
        return 1

    # Step 4: Generate Instagram images
    print("\n📸 [4/6] Generating Instagram images...")
    if not run_cmd(f"python3 generate_images.py {post_path}"):
        return 1

    # Step 5: Generate caption
    print("\n📝 [5/6] Generating caption...")
    if not run_cmd("python3 gen_caption.py"):
        return 1

    # Step 6: Git push
    print("\n📤 [6/6] Pushing to GitHub...")
    if not run_cmd("git add -A"):
        return 1
    # Check if there are changes
    result = subprocess.run("git status --porcelain", shell=True, cwd=str(BASE_DIR), capture_output=True, text=True)
    if not result.stdout.strip():
        print("  No changes to commit.")
    else:
        if not run_cmd(f'git commit -m "Add Daily AI Digest for {date_str}"'):
            return 1
        if not run_cmd("git push origin main"):
            return 1

    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print(f"   Blog: https://daily-ai-digest.freelancerloki.workers.dev/posts/{date_str}-daily-ai-digest.html")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())