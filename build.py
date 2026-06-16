#!/usr/bin/env python3
"""
Daily AI Digest — Premium Static Site Builder v2.0
Reads markdown posts from ./posts/ and generates a premium dark-themed static site in ./dist/
"""

import os
import re
import json
import shutil
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

def build_posts_data(posts):
    """Build JSON data for the index page."""
    result = []
    for p in posts:
        result.append({
            'title': p['title'],
            'date': p['date'],
            'dateDisplay': p['date_display'],
            'category': p.get('category', 'General'),
            'categoryClass': cat_class(p.get('category', '')),
            'excerpt': p.get('excerpt', ''),
            'tags': p.get('tags', []),
            'url': f"/posts/{p['slug']}.html",
            'image': p.get('image', '')
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
    print("🔨 Building Daily AI Digest v2.0 — Premium Edition...")

    # Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()
    (DIST_DIR / "posts").mkdir()

    # Copy app files
    for f in APP_DIR.glob("*.html"):
        if f.name != 'post-template.html':
            shutil.copy2(f, DIST_DIR / f.name)

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

    print(f"\n✅ Build complete! {len(posts)} posts generated.")
    print(f"   Output: {DIST_DIR}/")
    print(f"   Deploy: Push to GitHub → Cloudflare Pages → /dist")

if __name__ == '__main__':
    build()
