#!/usr/bin/env python3
"""
Daily AI Digest — Premium Static Site Builder v3.0
Reads markdown posts from ./posts/ and generates a world-class AI media platform in ./dist/
"""

import os
import re
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

try:
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc, nl2br
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "-q"])
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc, nl2br

BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"
APP_DIR = BASE_DIR / "app"
DIST_DIR = BASE_DIR / "dist"
TEMPLATE_FILE = APP_DIR / "post-template.html"
INDEX_FILE = APP_DIR / "index.html"
ABOUT_FILE = APP_DIR / "about.html"

# Category → (icon, gradient_colors, accent)
CAT_STYLES = {
    "daily digest": ("📡", ("#0f0a2a", "#0a1a30", "#0f0a2a"), "#7c6cf0"),
    "weekly tools": ("🛠", ("#0a2a1a", "#0a3020", "#0a2a1a"), "#34d399"),
    "launch": ("🚀", ("#1a0a2a", "#2a0a1a", "#1a0a2a"), "#f472b6"),
    "general": ("📰", ("#0a0a2a", "#1a1a30", "#0a0a2a"), "#00d4f0"),
}

def slugify(title):
    s = re.sub(r'[^\w\s-]', '', title.lower())
    return re.sub(r'[\s_]+', '-', s.strip())

def parse_frontmatter(content):
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
    md = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'nl2br'])
    return md.convert(md_text)

def cat_class(category):
    cat = (category or 'General').lower()
    if 'digest' in cat and 'tool' not in cat: return 'digest'
    if 'tool' in cat: return 'tools'
    return 'general'

def get_cat_style(category):
    cat = (category or 'general').lower()
    for key, val in CAT_STYLES.items():
        if key in cat:
            return val
    return CAT_STYLES["general"]

def generate_thumbnail_svg(title, category, tags):
    """Generate a unique SVG thumbnail based on post content."""
    icon, (g1, g2, g3), accent = get_cat_style(category)
    
    # Create a deterministic but unique pattern from title hash
    h = hashlib.md5(title.encode()).hexdigest()
    seed = int(h[:8], 16)
    
    # Generate pseudo-random node positions for neural network look
    nodes = []
    for i in range(8):
        x = 10 + (int(h[i*2:i*2+2], 16) % 80)
        y = 10 + (int(h[i*2+16:i*2+18], 16) % 80)
        r = 2 + (int(h[i], 16) % 4)
        nodes.append((x, y, r))
    
    # Generate connections between nearby nodes
    connections = []
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < 35:
                connections.append((nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1], max(0.1, 0.4 - dist/100)))
    
    # Build SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{g1}"/>
      <stop offset="50%" style="stop-color:{g2}"/>
      <stop offset="100%" style="stop-color:{g3}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="45%" r="40%">
      <stop offset="0%" style="stop-color:{accent};stop-opacity:0.25"/>
      <stop offset="100%" style="stop-color:{accent};stop-opacity:0"/>
    </radialGradient>
    <filter id="blur">
      <feGaussianBlur stdDeviation="1.5"/>
    </filter>
  </defs>
  <rect width="100" height="100" fill="url(#bg)"/>
  <rect width="100" height="100" fill="url(#glow)"/>
  <circle cx="50" cy="45" r="22" fill="none" stroke="{accent}" stroke-width="0.4" opacity="0.2" filter="url(#blur)"/>
  <circle cx="50" cy="45" r="15" fill="none" stroke="{accent}" stroke-width="0.3" opacity="0.15"/>
  <circle cx="50" cy="45" r="8" fill="{accent}" opacity="0.06"/>
  <circle cx="50" cy="45" r="3" fill="{accent}" opacity="0.12"/>
'''
    # Add connections
    for x1, y1, x2, y2, op in connections:
        svg += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{accent}" stroke-width="0.3" opacity="{op:.2f}"/>\n'
    
    # Add nodes
    for x, y, r in nodes:
        svg += f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{accent}" opacity="0.5"/>\n'
        svg += f'  <circle cx="{x}" cy="{y}" r="{r*2.5}" fill="{accent}" opacity="0.08"/>\n'
    
    # Add icon in center
    svg += f'  <text x="50" y="52" text-anchor="middle" font-size="28" opacity="0.9">{icon}</text>\n'
    
    # Add subtle grid lines
    for i in range(0, 101, 20):
        svg += f'  <line x1="{i}" y1="0" x2="{i}" y2="100" stroke="white" stroke-width="0.1" opacity="0.04"/>\n'
        svg += f'  <line x1="0" y1="{i}" x2="100" y2="{i}" stroke="white" stroke-width="0.1" opacity="0.04"/>\n'
    
    svg += '</svg>'
    
    # Encode as data URI
    import base64
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"

def build_posts_data(posts):
    """Build JSON data for the index page."""
    result = []
    for p in posts:
        image = p.get('image', '')
        if not image:
            image = generate_thumbnail_svg(p['title'], p.get('category', ''), p.get('tags', []))
        result.append({
            'title': p['title'],
            'date': p['date'],
            'dateDisplay': p['date_display'],
            'category': p.get('category', 'General'),
            'categoryClass': cat_class(p.get('category', '')),
            'excerpt': p.get('excerpt', ''),
            'tags': p.get('tags', []),
            'url': f"/posts/{p['slug']}.html",
            'image': image
        })
    return result

def build_post_page(post, template_html):
    """Build an individual post page from template."""
    tags_html = ''.join(f'<span class="post-header-tag">{t}</span>' for t in post.get('tags', []))
    
    html = template_html
    html = html.replace('{{TITLE}}', post['title'])
    html = html.replace('{{DATE}}', post['date_display'])
    html = html.replace('{{CATEGORY}}', post.get('category', 'General'))
    html = html.replace('{{EXCERPT}}', post.get('excerpt', ''))
    html = html.replace('{{TAGS}}', tags_html)
    html = html.replace('{{CONTENT}}', post['body_html'])
    return html

def build_index(posts_data_json):
    """Build the index.html with real post data."""
    html = INDEX_FILE.read_text()
    
    # Replace the POSTS_DATA placeholder
    old_data = re.search(r'const POSTS_DATA = \[.*?\];', html, re.DOTALL)
    if old_data:
        html = html[:old_data.start()] + f'const POSTS_DATA = {posts_data_json};' + html[old_data.end():]
    
    return html

def build():
    print("🔨 Building Daily AI Digest v3.0 — World-Class AI Media Platform...")

    # Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()
    (DIST_DIR / "posts").mkdir()

    # Read template
    template_html = TEMPLATE_FILE.read_text()

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

        body_html = md_to_html(body)

        post = {
            'title': title,
            'slug': slug,
            'date': date_str,
            'date_display': display,
            'tags': tags,
            'category': category,
            'excerpt': excerpt,
            'body_html': body_html,
        }
        posts.append(post)

        # Build individual post page
        page_html = build_post_page(post, template_html)
        (DIST_DIR / "posts" / f"{slug}.html").write_text(page_html, encoding='utf-8')
        print(f"  ✓ Post: {title}")

    # Sort posts by date descending
    posts.sort(key=lambda x: x['date'], reverse=True)

    # Build posts data JSON
    posts_data = build_posts_data(posts)
    posts_json = json.dumps(posts_data, indent=2)

    # Build index with real data
    index_html = build_index(posts_json)
    (DIST_DIR / "index.html").write_text(index_html, encoding='utf-8')
    print(f"  ✓ Home page ({len(posts)} posts)")

    # Copy about page
    if ABOUT_FILE.exists():
        shutil.copy2(ABOUT_FILE, DIST_DIR / "about.html")
        print("  ✓ About page")

    # Copy assets (story images)
    assets_src = BASE_DIR / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, DIST_DIR / "assets", dirs_exist_ok=True)
        print("  ✓ Assets (images)")

    print(f"\n✅ Build complete! {len(posts)} posts generated.")
    print(f"   Output: {DIST_DIR}/")
    print(f"   Deploy: Push to GitHub → Cloudflare Pages → /dist")


if __name__ == '__main__':
    build()
