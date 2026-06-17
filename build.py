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
    """Generate a rich AI-themed SVG cover image based on post content."""
    import base64
    icon, (g1, g2, g3), accent = get_cat_style(category)
    h = hashlib.md5(title.encode()).hexdigest()
    accents = ['#7c6cf0', '#b46eff', '#00d4f0', '#34d399', '#f472b6', '#fbbf24']
    accent2 = accents[int(h[2:4], 16) % len(accents)]
    accent3 = accents[int(h[4:6], 16) % len(accents)]

    # Helper to safely get hex pairs from hash
    def hexval(offset, length=2):
        start = offset % 32
        end = (offset + length) % 32
        if end <= start:
            end = 32
        val = h[start:end]
        return int(val, 16) if val else 0

    # Generate nodes
    nodes = []
    for i in range(18):
        x = 8 + (hexval(i * 2) % 84)
        y = 8 + (hexval(i * 2 + 16) % 84)
        r = 1.5 + (hexval(i) % 5)
        nodes.append((x, y, r))

    # Generate connections
    connections = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 30:
                connections.append((nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1], max(0.08, 0.35 - dist / 100)))

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{g1}"/>
      <stop offset="40%" style="stop-color:{g2}"/>
      <stop offset="100%" style="stop-color:{g3}"/>
    </linearGradient>
    <radialGradient id="glow1" cx="35%" cy="40%" r="50%">
      <stop offset="0%" style="stop-color:{accent};stop-opacity:0.35"/>
      <stop offset="100%" style="stop-color:{accent};stop-opacity:0"/>
    </radialGradient>
    <radialGradient id="glow2" cx="70%" cy="65%" r="45%">
      <stop offset="0%" style="stop-color:{accent2};stop-opacity:0.2"/>
      <stop offset="100%" style="stop-color:{accent2};stop-opacity:0"/>
    </radialGradient>
    <radialGradient id="glow3" cx="50%" cy="20%" r="35%">
      <stop offset="0%" style="stop-color:{accent3};stop-opacity:0.15"/>
      <stop offset="100%" style="stop-color:{accent3};stop-opacity:0"/>
    </radialGradient>
    <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
      <stop offset="0%" style="stop-color:transparent"/>
      <stop offset="100%" style="stop-color:#000;stop-opacity:0.4"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softglow"><feGaussianBlur stdDeviation="8"/></filter>
    <filter id="bgblur"><feGaussianBlur stdDeviation="1.5"/></filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#glow1)"/>
  <rect width="1200" height="630" fill="url(#glow2)"/>
  <rect width="1200" height="630" fill="url(#glow3)"/>
  <circle cx="200" cy="150" r="180" fill="{accent}" opacity="0.04" filter="url(#bgblur)"/>
  <circle cx="900" cy="450" r="220" fill="{accent2}" opacity="0.03" filter="url(#bgblur)"/>
  <circle cx="600" cy="315" r="120" fill="{accent3}" opacity="0.03" filter="url(#bgblur)"/>
  <g opacity="0.03" stroke="white" stroke-width="0.5">''')

    for i in range(0, 1201, 60):
        svg_parts.append(f'    <line x1="{i}" y1="0" x2="{i}" y2="630"/>')
    for i in range(0, 631, 60):
        svg_parts.append(f'    <line x1="0" y1="{i}" x2="1200" y2="{i}"/>')
    svg_parts.append('  </g>')

    # Connections
    for x1, y1, x2, y2, op in connections:
        svg_parts.append(f'  <line x1="{x1*10}" y1="{y1*5.25}" x2="{x2*10}" y2="{y2*5.25}" stroke="{accent}" stroke-width="1" opacity="{op:.2f}"/>')

    # Nodes with glow halos
    for x, y, r in nodes:
        nx, ny = x * 10, y * 5.25
        svg_parts.append(f'  <circle cx="{nx}" cy="{ny}" r="{r*8}" fill="{accent}" opacity="0.06" filter="url(#softglow)"/>')
        svg_parts.append(f'  <circle cx="{nx}" cy="{ny}" r="{r*4}" fill="{accent}" opacity="0.12"/>')
        svg_parts.append(f'  <circle cx="{nx}" cy="{ny}" r="{r*1.5}" fill="{accent}" opacity="0.7" filter="url(#glow)"/>')
        svg_parts.append(f'  <circle cx="{nx}" cy="{ny}" r="{r*0.6}" fill="white" opacity="0.4"/>')

    # Floating particles
    for i in range(12):
        px = 50 + (hexval(i * 2) % 1100)
        py = 30 + (hexval(i * 2 + 8) % 570)
        pr = 1 + (hexval(i) % 3)
        p_op = 0.1 + (hexval(i + 4) % 20) / 100
        svg_parts.append(f'  <circle cx="{px}" cy="{py}" r="{pr}" fill="white" opacity="{p_op:.2f}"/>')

    # Center icon
    svg_parts.append(f'  <text x="600" y="330" text-anchor="middle" font-size="90" opacity="0.85" filter="url(#glow)">{icon}</text>')

    # Category label
    cat_label = (category or 'Daily Digest').upper()
    svg_parts.append(f'  <text x="600" y="560" text-anchor="middle" font-size="18" font-family="monospace" letter-spacing="6" fill="white" opacity="0.25">{cat_label}</text>')

    # Vignette
    svg_parts.append('  <rect width="1200" height="630" fill="url(#vignette)" opacity="0.3"/>')
    svg_parts.append('</svg>')

    svg = '\n'.join(svg_parts)
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
