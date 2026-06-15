#!/usr/bin/env python3
"""
Daily AI Digest — Instagram Carousel Generator
Generates dark-themed carousel slides matching the blog style.
"""

import os
import re
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── paths ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
FONTS_DIR = Path.home() / ".hermes" / "fonts"
OUTPUT_DIR = BASE_DIR / "instagram_posts"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── colors (matching blog theme) ─────────────────────────────────────
BG = (10, 10, 15)           # #0a0a0f
SURFACE = (18, 18, 26)      # #12121a
BORDER = (42, 42, 58)       # #2a2a3a
TEXT = (228, 228, 239)      # #e4e4ef
TEXT_DIM = (136, 136, 160)  # #8888a0
ACCENT = (124, 92, 252)     # #7c5cfc
ACCENT2 = (0, 212, 170)     # #00d4aa
RED = (255, 107, 107)       # #ff6b6b
YELLOW = (255, 209, 102)    # #ffd166

# ── dimensions ───────────────────────────────────────────────────────
W, H = 1080, 1080  # Instagram square

# ── fonts ────────────────────────────────────────────────────────────
def get_font(name, size):
    path = FONTS_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.truetype("/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf", size)

def get_font_bold(size):
    path = FONTS_DIR / "Inter-Bold.woff2"
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.truetype("/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", size)

def get_font_semibold(size):
    path = FONTS_DIR / "Inter-SemiBold.woff2"
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.truetype("/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", size)

def get_font_regular(size):
    path = FONTS_DIR / "Inter-Regular.woff2"
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.truetype("/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf", size)

# ── helpers ──────────────────────────────────────────────────────────
def draw_rounded_rect(draw, xy, radius, fill, outline=None, outline_width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=outline_width)

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def draw_gradient_bar(draw, y, height=4):
    """Draw a gradient accent bar."""
    for x in range(W):
        ratio = x / W
        r = int(ACCENT[0] + (ACCENT2[0] - ACCENT[0]) * ratio)
        g = int(ACCENT[1] + (ACCENT2[1] - ACCENT[1]) * ratio)
        b = int(ACCENT[2] + (ACCENT2[2] - ACCENT[2]) * ratio)
        draw.line([(x, y), (x, y + height)], fill=(r, g, b))

# ── slide generators ─────────────────────────────────────────────────

def generate_cover_slide(date_str, num_stories, tags):
    """Slide 1: Cover card with date and story count."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gradient top bar
    draw_gradient_bar(draw, 0, 6)

    # Logo area
    logo_y = 100
    draw.text((W // 2, logo_y), "Daily", font=get_font_bold(48), fill=TEXT, anchor="mm")
    draw.text((W // 2, logo_y + 55), "AI Digest", font=get_font_bold(48), fill=ACCENT, anchor="mm")

    # Date
    date_y = logo_y + 140
    draw.text((W // 2, date_y), date_str, font=get_font_regular(36), fill=TEXT_DIM, anchor="mm")

    # Divider
    draw.line([(140, date_y + 50), (W - 140, date_y + 50)], fill=BORDER, width=1)

    # Story count badge
    badge_y = date_y + 100
    draw_rounded_rect(draw, [W // 2 - 200, badge_y, W // 2 + 200, badge_y + 80], 40, SURFACE, ACCENT, 2)
    draw.text((W // 2, badge_y + 22), f"{num_stories} Stories", font=get_font_semibold(32), fill=TEXT, anchor="mm")
    draw.text((W // 2, badge_y + 55), "Today's Top AI News", font=get_font_regular(22), fill=TEXT_DIM, anchor="mm")

    # Tags
    tag_y = badge_y + 130
    x = 60
    for tag in tags[:8]:
        tag_text = f"#{tag}"
        bbox = draw.textbbox((0, 0), tag_text, font=get_font_regular(20))
        tw = bbox[2] - bbox[0] + 20
        if x + tw > W - 60:
            tag_y += 45
            x = 60
        draw_rounded_rect(draw, [x, tag_y, x + tw, tag_y + 34], 17, (124, 92, 252, 31))
        draw.text((x + 10, tag_y + 8), tag_text, font=get_font_regular(20), fill=ACCENT)
        x += tw + 10

    # Bottom bar
    draw_gradient_bar(draw, H - 6, 6)
    draw.text((W // 2, H - 40), "daily-ai-digest.dev", font=get_font_regular(20), fill=TEXT_DIM, anchor="mm")

    return img

def generate_story_slide(index, title, category, summary_lines, key_takeaways, date_str):
    """Slides 2-N: Individual story cards."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Top gradient bar
    draw_gradient_bar(draw, 0, 4)

    # Story number badge
    badge_x, badge_y = 60, 50
    draw_rounded_rect(draw, [badge_x, badge_y, badge_x + 80, badge_y + 36], 18, ACCENT)
    draw.text((badge_x + 40, badge_y + 8), f"#{index}", font=get_font_bold(20), fill=(255, 255, 255), anchor="mm")

    # Category
    cat_x = badge_x + 100
    draw.text((cat_x, badge_y + 8), category, font=get_font_regular(22), fill=ACCENT2)

    # Date on right
    draw.text((W - 60, badge_y + 8), date_str, font=get_font_regular(20), fill=TEXT_DIM, anchor="rm")

    # Title
    title_y = badge_y + 60
    title_lines = wrap_text(title, get_font_bold(42), W - 120, draw)
    for i, line in enumerate(title_lines[:3]):
        draw.text((60, title_y + i * 52), line, font=get_font_bold(42), fill=TEXT)

    # Divider
    div_y = title_y + len(title_lines[:3]) * 52 + 20
    draw.line([(60, div_y), (W - 60, div_y)], fill=BORDER, width=1)

    # Summary
    summary_y = div_y + 24
    for line in summary_lines[:4]:
        wrapped = wrap_text(line, get_font_regular(26), W - 120, draw)
        for wl in wrapped[:2]:
            draw.text((60, summary_y), wl, font=get_font_regular(26), fill=TEXT_DIM)
            summary_y += 34
        if summary_y > 500:
            break

    # Key Takeaways box
    box_y = max(summary_y + 30, 550)
    if box_y < 800:
        draw_rounded_rect(draw, [50, box_y, W - 50, box_y + 200], 16, SURFACE, BORDER, 1)
        draw.text((70, box_y + 16), "Key Takeaways", font=get_font_semibold(24), fill=ACCENT)

        takeaway_y = box_y + 52
        for takeaway in key_takeaways[:4]:
            wrapped = wrap_text(f"• {takeaway}", get_font_regular(22), W - 140, draw)
            for wl in wrapped[:2]:
                draw.text((70, takeaway_y), wl, font=get_font_regular(22), fill=TEXT)
                takeaway_y += 30
            if takeaway_y > box_y + 180:
                break

    # Bottom bar
    draw_gradient_bar(draw, H - 4, 4)
    draw.text((W // 2, H - 30), f"Daily AI Digest  •  Story {index}", font=get_font_regular(18), fill=TEXT_DIM, anchor="mm")

    return img

def generate_cta_slide(date_str):
    """Final slide: Call to action."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(draw, 0, 6)

    # Big text
    y = 280
    draw.text((W // 2, y), "Read the Full", font=get_font_bold(56), fill=TEXT, anchor="mm")
    draw.text((W // 2, y + 65), "Daily AI Digest", font=get_font_bold(56), fill=ACCENT, anchor="mm")

    # URL box
    box_y = y + 140
    draw_rounded_rect(draw, [140, box_y, W - 140, box_y + 70], 35, SURFACE, ACCENT, 2)
    draw.text((W // 2, box_y + 22), "daily-ai-digest.dev", font=get_font_semibold(32), fill=ACCENT2, anchor="mm")

    # Follow CTA
    cta_y = box_y + 130
    draw.text((W // 2, cta_y), "Follow for daily", font=get_font_regular(36), fill=TEXT_DIM, anchor="mm")
    draw.text((W // 2, cta_y + 45), "AI news updates", font=get_font_regular(36), fill=TEXT_DIM, anchor="mm")

    # Bottom
    draw_gradient_bar(draw, H - 6, 6)
    draw.text((W // 2, H - 50), date_str, font=get_font_regular(22), fill=TEXT_DIM, anchor="mm")

    return img

# ── main generator ───────────────────────────────────────────────────

def parse_post_for_slides(md_path):
    """Parse a markdown post and extract stories for slides."""
    content = md_path.read_text()
    meta_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not meta_match:
        return None

    meta = {}
    for line in meta_match.group(1).splitlines():
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip()] = val.strip().strip('"').strip("'")

    body = content[meta_match.end():]

    # Parse individual stories
    stories = []
    sections = re.split(r'\n---\n', body)
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract story title (### heading)
        title_match = re.match(r'###\s+(.+)', section)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        # Extract category
        cat_match = re.search(r'\*\*(.+?)\*\*', section)
        category = cat_match.group(1) if cat_match else "AI News"

        # Extract summary (paragraph after category line)
        lines = section.split('\n')
        summary_lines = []
        for line in lines[2:]:
            line = line.strip()
            if line and not line.startswith('**') and not line.startswith('[') and not line.startswith('###'):
                summary_lines.append(line)
            if len(summary_lines) >= 3:
                break

        # Extract key takeaways
        takeaways = []
        in_takeaways = False
        for line in lines:
            if 'Key Takeaways' in line:
                in_takeaways = True
                continue
            if in_takeaways:
                if line.strip().startswith('- '):
                    takeaways.append(line.strip()[2:])
                elif line.strip().startswith('['):
                    break

        if title and title != "Why This Matters Today":
            stories.append({
                'title': title,
                'category': category,
                'summary': summary_lines,
                'takeaways': takeaways,
            })

    return {
        'meta': meta,
        'stories': stories,
        'date': meta.get('date', ''),
        'tags': [t.strip() for t in meta.get('tags', '').split(',') if t.strip()],
    }

def generate_all_slides(md_path, output_dir=None):
    """Generate all Instagram slides for a blog post."""
    if output_dir is None:
        output_dir = OUTPUT_DIR
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    data = parse_post_for_slides(md_path)
    if not data:
        print("ERROR: Could not parse post")
        return []

    date_str = data['date']
    stories = data['stories']
    tags = data['tags']

    # Format date for display
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        display_date = dt.strftime('%B %d, %Y')
    except:
        display_date = date_str

    slide_paths = []

    # Slide 1: Cover
    cover = generate_cover_slide(display_date, len(stories), tags)
    cover_path = output_dir / "01_cover.png"
    cover.save(cover_path, "PNG")
    slide_paths.append(str(cover_path))
    print(f"  ✓ Cover slide")

    # Slides 2-N: Stories
    for i, story in enumerate(stories, 1):
        slide = generate_story_slide(
            i, story['title'], story['category'],
            story['summary'], story['takeaways'], display_date
        )
        slide_path = output_dir / f"{i+1:02d}_story_{i}.png"
        slide.save(slide_path, "PNG")
        slide_paths.append(str(slide_path))
        print(f"  ✓ Story {i}: {story['title'][:50]}")

    # Final slide: CTA
    cta = generate_cta_slide(display_date)
    cta_path = output_dir / f"{len(stories)+2:02d}_cta.png"
    cta.save(cta_path, "PNG")
    slide_paths.append(str(cta_path))
    print(f"  ✓ CTA slide")

    print(f"\n✅ {len(slide_paths)} slides generated in {output_dir}/")
    return slide_paths

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_images.py <path_to_md_post> [output_dir]")
        sys.exit(1)
    md_path = Path(sys.argv[1])
    out_dir = sys.argv[2] if len(sys.argv) > 2 else None
    generate_all_slides(md_path, out_dir)
