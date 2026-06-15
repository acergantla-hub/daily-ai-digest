#!/usr/bin/env python3
"""
Daily AI Digest — Static Site Generator
Reads markdown posts from ./posts/ and generates a static site in ./dist/
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path

try:
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "-q"])
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc

BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"
TEMPLATE_DIR = BASE_DIR / "templates"
DIST_DIR = BASE_DIR / "dist"
BASE_TEMPLATE = TEMPLATE_DIR / "base.html"

# ── helpers ──────────────────────────────────────────────────────────

def slugify(title):
    s = re.sub(r'[^\w\s-]', '', title.lower())
    return re.sub(r'[\s_]+', '-', s.strip())

def parse_frontmatter(content):
    """Extract YAML-like frontmatter from markdown content."""
    meta = {}
    body = content
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        body = content[fm_match.end():]
        for line in fm_match.group(1).splitlines():
            if ':' in line:
                key, _, val = line.partition(':')
                meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body

def md_to_html(md_text):
    md = markdown.Markdown(extensions=[
        'fenced_code',
        'codehilite',
        'tables',
        'toc',
        'nl2br',
    ])
    return md.convert(md_text)

def render_base(title, content_html, page_type="home"):
    template = BASE_TEMPLATE.read_text()
    template = template.replace('{{title}}', title)
    template = template.replace('{{content}}', content_html)
    return template

def build_post_list(posts):
    """Build the home page with a list of posts."""
    items = []
    for p in sorted(posts, key=lambda x: x['date'], reverse=True):
        tags_html = ''.join(f'<span class="tag">{t}</span>' for t in p.get('tags', []))
        excerpt = p.get('excerpt', '')
        category = p.get('category', '')
        items.append(f'''
    <a href="/posts/{p["slug"]}.html" class="post-card">
      <div class="post-card-inner">
        <div class="post-meta">
          <span class="post-date">{p['date_display']}</span>
          {f'<span class="post-category">{category}</span>' if category else ''}
        </div>
        <h2>{p['title']}</h2>
        <p>{excerpt}</p>
        {"<div class='tags'>" + tags_html + "</div>" if tags_html else ""}
      </div>
    </a>''')

    post_count = len(posts)
    # Count unique categories
    categories = set(p.get('category', 'General') for p in posts)

    content = f'''
<section class="hero">
  <div class="hero-badge"><span class="live-dot"></span> LIVE &mdash; DAILY UPDATES</div>
  <h1>
    <span class="line1">Your Daily Dose of</span>
    <span class="line2">AI Agent News</span>
  </h1>
  <p class="hero-sub">Curated updates on AI agents, Claude Code, automation tools, and the latest in AI. Fresh posts every single day.</p>
  <div class="hero-stats">
    <div class="stat">
      <span class="stat-number">{post_count}</span>
      <span class="stat-label">Articles</span>
    </div>
    <div class="stat">
      <span class="stat-number">{len(categories)}</span>
      <span class="stat-label">Categories</span>
    </div>
    <div class="stat">
      <span class="stat-number">365</span>
      <span class="stat-label">Days/Year</span>
    </div>
  </div>
</section>
<div class="section-label-row">
  <span class="section-label">Latest Posts</span>
  <div class="section-line"></div>
</div>
<section class="posts-list">
  {''.join(items)}
</section>'''
    return render_base('Home', content)

def build_post_page(post_meta, post_body_html, post):
    """Build an individual post page."""
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in post.get('tags', []))
    category = post.get('category', 'General')

    content = f'''
<article class="post-page">
  <a href="/" class="back-link">&#8592; Back to all posts</a>
  <header class="post-header">
    <div class="post-meta">
      <span class="post-date">{post['date_display']}</span>
      <span class="post-category">{category}</span>
    </div>
    <h1>{post['title']}</h1>
    {"<div class='tags'>" + tags_html + "</div>" if tags_html else ""}
  </header>
  <div class="post-content">
    {post_body_html}
  </div>
</article>'''
    return render_base(post['title'], content)

def build_about_page():
    content = '''
<div class="about-page">
  <h1>About Daily AI Digest</h1>
  <p>Daily AI Digest is your go-to source for curated news and updates on AI agents, automation tools, Claude Code, and the broader AI ecosystem.</p>
  <p>Every day, we scan X (Twitter), YouTube, Hacker News, and leading AI blogs to bring you the most relevant, actionable, and fresh content. No fluff — just what matters.</p>
  <p>Each post includes the source, why it matters, a recommended response, and a draft hook you can use for your own social media.</p>
  <p><strong>Topics we cover:</strong></p>
  <ul>
    <li>AI Agents & Agent Frameworks</li>
    <li>Claude Code & AI Coding Assistants</li>
    <li>Open-source AI Tools & Models</li>
    <li>AI Automation & Workflows</li>
    <li>Startup & Industry News</li>
  </ul>
  <p>Stay ahead of the curve. Check back daily.</p>
</div>'''
    return render_base('About', content)

# ── main build ───────────────────────────────────────────────────────

def build():
    print("🔨 Building Daily AI Digest site...")

    # Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()
    (DIST_DIR / "posts").mkdir()

    # Copy assets
    assets_dir = BASE_DIR / "assets"
    if assets_dir.exists():
        shutil.copytree(assets_dir, DIST_DIR / "assets")

    # Parse all posts
    posts = []
    for f in sorted(POSTS_DIR.glob("*.md")):
        raw = f.read_text()
        meta, body = parse_frontmatter(raw)
        title = meta.get('title', f.stem.replace('-', ' ').title())
        date_str = meta.get('date', datetime.now().strftime('%Y-%m-%d'))
        tags = [t.strip() for t in meta.get('tags', '').split(',') if t.strip()]
        category = meta.get('category', '')
        excerpt = meta.get('excerpt', '')
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        display = dt.strftime('%B %d, %Y')
        slug = meta.get('slug', slugify(title))

        post = {
            'title': title,
            'slug': slug,
            'date': date_str,
            'date_display': display,
            'tags': tags,
            'category': category,
            'excerpt': excerpt,
        }
        posts.append(post)

        # Build individual post page
        body_html = md_to_html(body)
        page_html = build_post_page(meta, body_html, post)
        (DIST_DIR / "posts" / f"{slug}.html").write_text(page_html, encoding='utf-8')
        print(f"  ✓ Post: {title}")

    # Build home page
    home_html = build_post_list(posts)
    (DIST_DIR / "index.html").write_text(home_html, encoding='utf-8')
    print(f"  ✓ Home page ({len(posts)} posts)")

    # Build about page
    about_html = build_about_page()
    (DIST_DIR / "about.html").write_text(about_html, encoding='utf-8')
    print("  ✓ About page")

    print(f"\n✅ Build complete! {len(posts)} posts generated.")
    print(f"   Output: {DIST_DIR}/")
    print(f"   Deploy: Push to GitHub and connect to Cloudflare Pages → point to /dist")

if __name__ == '__main__':
    build()
