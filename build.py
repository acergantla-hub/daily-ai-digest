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

def cat_class(category):
    cat = (category or 'General').lower()
    if 'digest' in cat: return 'cat-digest'
    if 'tool' in cat: return 'cat-tools'
    return 'cat-general'

def build_post_list(posts):
    """Build the home page with editorial grid layout."""
    sorted_posts = sorted(posts, key=lambda x: x['date'], reverse=True)

    # Featured card (latest post)
    featured = sorted_posts[0] if sorted_posts else None
    featured_html = ''
    if featured:
        tags_html = ''.join(f'<span class="post-card-tag">{t}</span>' for t in featured.get('tags', []))
        cat_cls = cat_class(featured.get('category', ''))
        featured_html = f'''
    <a href="/posts/{featured["slug"]}.html" class="post-card post-card-featured">
      <div class="post-card-visual">
        <div class="post-card-icon" style="background:linear-gradient(135deg, #6c5ce7, #a29bfe);color:white;">✦</div>
      </div>
      <div>
        <div class="post-card-meta">
          <span class="post-card-date">{featured['date_display']}</span>
          <span class="post-card-category {cat_cls}">{featured.get('category', 'General')}</span>
        </div>
        <h2>{featured['title']}</h2>
        <p>{featured.get('excerpt', '')}</p>
        {"<div class='post-card-tags'>" + tags_html + "</div>" if tags_html else ""}
        <div class="post-card-arrow">Read article →</div>
      </div>
    </a>'''

    # Grid cards (remaining posts)
    grid_items = []
    for p in sorted_posts[1:]:
        tags_html = ''.join(f'<span class="post-card-tag">{t}</span>' for t in p.get('tags', []))
        cat_cls = cat_class(p.get('category', ''))
        grid_items.append(f'''
    <a href="/posts/{p["slug"]}.html" class="post-card">
      <div class="post-card-meta">
        <span class="post-card-date">{p['date_display']}</span>
        <span class="post-card-category {cat_cls}">{p.get('category', 'General')}</span>
      </div>
      <h2>{p['title']}</h2>
      <p>{p.get('excerpt', '')}</p>
      {"<div class='post-card-tags'>" + tags_html + "</div>" if tags_html else ""}
      <div class="post-card-arrow">Read →</div>
    </a>''')

    post_count = len(posts)
    categories = set(p.get('category', 'General') for p in posts)

    content = f'''
<section class="hero">
  <div class="hero-eyebrow"><span class="hero-eyebrow-dot"></span><span class="hero-eyebrow-text">Updated daily</span></div>
  <h1>Your daily dose of <em>AI agent</em> news.</h1>
  <p class="hero-desc">Curated updates on AI agents, Claude Code, automation tools, and the latest in the AI ecosystem. No fluff — just what matters.</p>
  <div class="hero-stats">
    <div>
      <div class="hero-stat-num">{post_count}</div>
      <div class="hero-stat-label">Articles</div>
    </div>
    <div>
      <div class="hero-stat-num">{len(categories)}</div>
      <div class="hero-stat-label">Categories</div>
    </div>
    <div>
      <div class="hero-stat-num">365</div>
      <div class="hero-stat-label">Days/Year</div>
    </div>
  </div>
</section>
<div class="section-header">
  <h2 class="section-title">Latest Posts</h2>
</div>
<section class="posts-grid">
  {featured_html}
  {''.join(grid_items)}
</section>'''
    return render_base('Home', content)

def build_post_page(post_meta, post_body_html, post):
    """Build an individual post page."""
    tags_html = ''.join(f'<span class="post-header-tag">{t}</span>' for t in post.get('tags', []))
    category = post.get('category', 'General')
    cat_cls = cat_class(category)

    content = f'''
<article class="post-page">
  <a href="/" class="post-back">← Back to all posts</a>
  <header class="post-header">
    <div class="post-header-meta">
      <span class="post-header-date">{post['date_display']}</span>
      <span class="post-header-category {cat_cls}">{category}</span>
    </div>
    <h1>{post['title']}</h1>
    {"<div class='post-header-tags'>" + tags_html + "</div>" if tags_html else ""}
  </header>
  <div class="post-content">
    {post_body_html}
  </div>
</article>'''
    return render_base(post['title'], content)

def build_about_page():
    content = '''
<div class="about-page">
  <h1>About <em>Daily AI Digest</em></h1>
  <p>Daily AI Digest is your go-to source for curated news and updates on AI agents, automation tools, Claude Code, and the broader AI ecosystem.</p>
  <p>Every day, we scan Hacker News, leading AI blogs, and company announcements to bring you the most relevant, actionable, and fresh content. No fluff — just what matters.</p>
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
