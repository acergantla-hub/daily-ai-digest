#!/usr/bin/env python3
"""
Daily AI Digest — Instagram Carousel Generator v3
Rich visuals per category, proper key takeaways, glass-morphism design.
All draw.text() calls use keyword args: fill= and font=
"""

import os, re, math, hashlib, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
FONTS_DIR = Path.home() / ".hermes" / "fonts"
SYS_FONTS = Path("/data/data/com.termux/files/usr/share/fonts/TTF/")
OUTPUT_DIR = BASE_DIR / "instagram_posts"
OUTPUT_DIR.mkdir(exist_ok=True)

W, H = 1080, 1080

# ── category styles: (icon, bg_gradient, accent_rgb, accent2_rgb) ──────
CAT_STYLES = {
    "policy":    ("🏛", ((15,10,40),(25,15,60),(10,8,35)),    (124,108,240),(180,110,255)),
    "safety":    ("🛡", ((40,10,15),(60,15,20),(35,8,12)),    (255,107,107),(255,209,102)),
    "industry":  ("🏭", ((40,20,10),(55,30,15),(35,15,8)),    (255,209,102),(255,107,107)),
    "products":  ("📱", ((10,20,40),(15,30,55),(8,15,35)),    (0,212,240), (52,211,153)),
    "models":    ("🧠", ((30,10,40),(45,15,55),(25,8,35)),    (180,110,255),(124,108,240)),
    "research":  ("🔬", ((10,30,40),(15,45,55),(8,25,35)),    (0,212,240), (52,211,153)),
    "hardware":  ("💻", ((10,40,30),(15,55,45),(8,35,25)),    (52,211,153),(0,212,240)),
    "business":  ("📊", ((40,15,30),(55,20,45),(35,12,25)),   (244,114,182),(255,209,102)),
    "general":   ("📰", ((15,15,25),(25,25,40),(12,12,20)),   (124,108,240),(0,212,240)),
}

# ── fonts ──────────────────────────────────────────────────────────────
def fbold(size):
    p = FONTS_DIR / "Inter-Bold.woff2"
    return ImageFont.truetype(str(p), size) if p.exists() else ImageFont.truetype(str(SYS_FONTS / "DejaVuSans-Bold.ttf"), size)

def fsemibold(size):
    p = FONTS_DIR / "Inter-SemiBold.woff2"
    return ImageFont.truetype(str(p), size) if p.exists() else ImageFont.truetype(str(SYS_FONTS / "DejaVuSans-Bold.ttf"), size)

def freg(size):
    p = FONTS_DIR / "Inter-Regular.woff2"
    return ImageFont.truetype(str(p), size) if p.exists() else ImageFont.truetype(str(SYS_FONTS / "DejaVuSans.ttf"), size)

# ── color helpers ──────────────────────────────────────────────────────
def with_alpha(color, alpha, bg=(0,0,0)):
    return tuple(int(bg[i] + (fg - bg[i]) * alpha) for i, fg in enumerate(color))

# ── drawing helpers ────────────────────────────────────────────────────
def draw_gradient_bg(img, colors):
    draw = ImageDraw.Draw(img)
    c1, c2, c3 = colors
    for y in range(H):
        r = y / H
        if r < 0.5:
            f = r * 2
            draw.line([(0,y),(W,y)], fill=(int(c1[0]+(c2[0]-c1[0])*f), int(c1[1]+(c2[1]-c1[1])*f), int(c1[2]+(c2[2]-c1[2])*f)))
        else:
            f = (r - 0.5) * 2
            draw.line([(0,y),(W,y)], fill=(int(c2[0]+(c3[0]-c2[0])*f), int(c2[1]+(c3[1]-c2[1])*f), int(c2[2]+(c3[2]-c2[2])*f)))

def rr(draw, xy, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bb = draw.textbbox((0,0), test, font=font)
        if bb[2]-bb[0] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def tc(draw, y, text, font, fill, xc=W//2):
    bb = draw.textbbox((0,0), text, font=font)
    draw.text((xc - (bb[2]-bb[0])//2, y), text, font=font, fill=fill)

def draw_nodes(img, accent, accent2, seed=42, alpha=0.12):
    draw = ImageDraw.Draw(img)
    rng = random.Random(seed)
    nodes = [(rng.randint(50,W-50), rng.randint(50,H-50), rng.randint(2,6)) for _ in range(25)]
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            dx, dy = nodes[i][0]-nodes[j][0], nodes[i][1]-nodes[j][1]
            d = math.sqrt(dx*dx+dy*dy)
            if d < 200:
                a = max(0.03, alpha - d/2000)
                col = with_alpha(accent, a) if (i+j)%2==0 else with_alpha(accent2, a)
                draw.line([(nodes[i][0],nodes[i][1]),(nodes[j][0],nodes[j][1])], fill=col, width=1)
    for x,y,r in nodes:
        draw.ellipse([x-r*4,y-r*4,x+r*4,y+r*4], fill=with_alpha(accent, alpha*0.4))
        draw.ellipse([x-r,y-r,x+r,y+r], fill=with_alpha(accent2, alpha*1.2))

def draw_bar(img, accent, y0=0, h=6):
    draw = ImageDraw.Draw(img)
    a2 = (int(accent[0]*0.7), int(accent[1]*0.5), min(255,int(accent[2]*1.3)))
    for x in range(W):
        r = x/W
        draw.line([(x,y0),(x,y0+h)], fill=(int(accent[0]*(1-r)+a2[0]*r), int(accent[1]*(1-r)+a2[1]*r), int(accent[2]*(1-r)+a2[2]*r)))

def draw_vignette(img):
    draw = ImageDraw.Draw(img)
    for i in range(150):
        a = int(60*(1-i/150))
        draw.rectangle([i,i,W-i,H-i], outline=with_alpha((0,0,0), a/255))

# ── slides ─────────────────────────────────────────────────────────────

def gen_cover(date_str, num_stories, categories, accent, accent2):
    img = Image.new("RGB", (W,H), (10,10,20))
    draw_gradient_bg(img, ((8,6,25),(15,10,40),(8,6,25)))
    draw_nodes(img, accent, accent2, seed=42, alpha=0.10)
    draw_vignette(img)
    draw_bar(img, accent)
    d = ImageDraw.Draw(img)

    # Brand badge
    y = 120
    bw, bh = 300, 64
    bx = W//2 - bw//2
    rr(d, [bx, y, bx+bw, y+bh], 32, with_alpha(accent, 0.08), accent, 1)
    tc(d, y+14, "⚡  DAILY AI DIGEST", fbold(28), (228,228,239))

    y += bh + 30
    tc(d, y, date_str, freg(32), (136,136,160))

    y += 50
    d.line([(200,y),(W-200,y)], fill=(42,42,58), width=1)

    y += 40
    tc(d, y, str(num_stories), fbold(120), (228,228,239))
    y += 130
    tc(d, y, "TODAY'S TOP AI STORIES", fsemibold(24), accent)

    # Category pills
    y += 60
    seen, x_start = [], 60
    for c in categories:
        cl = c.lower()
        if cl not in seen:
            seen.append(cl)
    for cat in seen[:6]:
        txt = cat.upper()
        bb = d.textbbox((0,0), txt, font=freg(18))
        tw = bb[2]-bb[0]+24
        if x_start+tw > W-60:
            y += 44; x_start = 60
        rr(d, [x_start, y, x_start+tw, y+36], 18, with_alpha(accent, 0.10), accent, 1)
        d.text((x_start+12, y+8), txt, font=freg(18), fill=(180,160,255))
        x_start += tw+12

    d.line([(200,H-80),(W-200,H-80)], fill=(42,42,58), width=1)
    tc(d, H-60, "daily-ai-digest.freelancerloki.workers.dev", freg(22), (80,80,100))
    draw_bar(img, accent, y0=H-4, h=4)
    return img


def gen_story(index, title, category, summary_lines, takeaways, date_str, accent, accent2, icon):
    img = Image.new("RGB", (W,H), (10,10,20))
    draw_gradient_bg(img, ((8,6,25),(15,10,40),(8,6,25)))
    draw_nodes(img, accent, accent2, seed=index*7, alpha=0.08)
    draw_bar(img, accent)
    draw_vignette(img)
    d = ImageDraw.Draw(img)

    # Number circle
    cr, cx, cy = 32, 80, 80
    for g in range(60, cr, -2):
        a = 0.12*(1-(g-cr)/(60-cr))
        d.ellipse([cx-g, cy-g, cx+g, cy+g], fill=with_alpha(accent, a))
    d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=accent)
    tc(d, cy-14, str(index), fbold(28), (255,255,255), xc=cx)

    # Category badge
    cx2 = cx+cr+20
    ctxt = icon + "  " + category.upper()
    bb = d.textbbox((0,0), ctxt, font=freg(20))
    tw = bb[2]-bb[0]+20
    rr(d, [cx2, cy-16, cx2+tw, cy+20], 12, with_alpha(accent, 0.15), accent, 1)
    d.text((cx2+10, cy-10), ctxt, font=freg(20), fill=accent2)

    # Date
    d.text((W-60, cy-10), date_str, font=freg(18), fill=(100,100,120), anchor="rm")

    # Title
    y = 150
    tl = wrap(title, fbold(44), W-120, d)
    for i, line in enumerate(tl[:2]):
        d.text((60, y+i*54), line, font=fbold(44), fill=(228,228,239))

    y = y + len(tl[:2])*54 + 20
    d.line([(60,y),(200,y)], fill=accent, width=3)
    d.line([(210,y),(W-60,y)], fill=(42,42,58), width=1)

    # Summary
    y += 24
    for line in summary_lines[:2]:
        wl = wrap(line, freg(26), W-120, d)
        for w in wl[:2]:
            d.text((60, y), w, font=freg(26), fill=(160,160,185))
            y += 34
        if y > 520: break

    # Key Takeaways card
    if takeaways:
        cy0 = max(y+30, 560)
        cy1 = min(cy0 + 20 + len(takeaways[:3])*38, cy0+150)
        rr(d, [50, cy0, W-50, cy1], 16, with_alpha((0,0,0), 0.40), accent, 1)
        d.text((70, cy0+12), "🔑  KEY TAKEAWAYS", font=fsemibold(20), fill=accent)
        ty = cy0+44
        for t in takeaways[:3]:
            d.text((70, ty), "▸  "+t, font=freg(22), fill=(200,200,220))
            ty += 32

    d.line([(60,H-50),(W-60,H-50)], fill=(30,30,45), width=1)
    tc(d, H-38, "Daily AI Digest  •  Story "+str(index)+" of 12", freg(16), (80,80,100))
    draw_bar(img, accent, y0=H-3, h=3)
    return img


def gen_cta(date_str, accent, accent2):
    img = Image.new("RGB", (W,H), (10,10,20))
    draw_gradient_bg(img, ((8,6,25),(20,12,50),(8,6,25)))
    draw_nodes(img, accent, accent2, seed=99, alpha=0.10)
    draw_bar(img, accent)
    draw_vignette(img)
    d = ImageDraw.Draw(img)

    y = 200
    tc(d, y, "🤖", fbold(80), (228,228,239))
    y += 100
    tc(d, y, "Read the Full", fbold(52), (228,228,239))
    y += 62
    tc(d, y, "Daily AI Digest", fbold(52), accent)
    y += 80

    bw, bh = 480, 70
    bx = W//2 - bw//2
    for g in range(30, 0, -2):
        rr(d, [bx-g, y-g, bx+bw+g, y+bh+g], 36+g, with_alpha(accent, 0.04), accent, 1)
    rr(d, [bx, y, bx+bw, y+bh], 35, (20,15,50), accent, 2)
    tc(d, y+18, "daily-ai-digest.freelancerloki.workers.dev", fsemibold(30), accent2)

    y += bh+60
    tc(d, y, "Follow for daily AI news", freg(30), (136,136,160))
    y += 40
    tc(d, y, "@lancerloki1", fsemibold(28), accent)

    d.line([(200,H-80),(W-200,H-80)], fill=(42,42,58), width=1)
    tc(d, H-55, date_str, freg(20), (80,80,100))
    draw_bar(img, accent, y0=H-4, h=4)
    return img


# ── parser ─────────────────────────────────────────────────────────────

def parse_post(md_path):
    content = md_path.read_text()
    fm = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    meta = {}
    if fm:
        for line in fm.group(1).splitlines():
            if ':' in line:
                k,_,v = line.partition(':')
                meta[k.strip()] = v.strip().strip('"').strip("'")
        body = content[fm.end():]
    else:
        body = content

    stories = []
    for section in re.split(r'\n---\n', body):
        section = section.strip()
        if not section: continue
        tm = re.match(r'###\s+(.+)', section)
        if not tm: continue
        title = tm.group(1).strip()
        cm = re.search(r'\*\*(.+?)\*\*', section)
        category = cm.group(1) if cm else "General"

        lines = section.split('\n')
        summary_lines = []
        for line in lines:
            s = line.strip()
            if (s and not s.startswith('**') and not s.startswith('[')
                and not s.startswith('###') and not s.startswith('!')
                and not s.startswith('*') and not s.startswith('---')
                and 'KEY TAKEAWAYS' not in s.upper()):
                summary_lines.append(s)
            if len(summary_lines) >= 2: break

        takeaways = []
        in_kt = False
        for line in lines:
            s = line.strip()
            if 'KEY TAKEAWAYS' in s.upper():
                in_kt = True; continue
            if in_kt:
                if s.startswith('- ') or s.startswith('• ') or s.startswith('▸'):
                    t = s.lstrip('-•▸ ').strip()
                    if t: takeaways.append(t)
                elif s.startswith('[') or (s == '' and takeaways):
                    break

        if not takeaways and summary_lines:
            for sl in summary_lines[:2]:
                for sent in re.split(r'[.!?]', sl):
                    sent = sent.strip()
                    if 20 < len(sent) < 120:
                        takeaways.append(sent)

        stories.append({'title': title, 'category': category, 'summary': summary_lines, 'takeaways': takeaways[:3]})

    return {'meta': meta, 'stories': stories, 'date': meta.get('date',''), 'tags': [t.strip() for t in meta.get('tags','').split(',') if t.strip()]}


def get_cat_style(category):
    cat = category.lower()
    for key in CAT_STYLES:
        if key in cat: return CAT_STYLES[key]
    kw_map = {
        'policy': ['policy','gov','regulation','law','ban','coalition','frontier'],
        'safety': ['safety','security','filter','violent','content','jailbreak'],
        'industry': ['industry','layoff','worker','company','gulag','engineer'],
        'products': ['product','feature','docs','mode','tool','gemini'],
        'models': ['model','llm','weights','open weights','glm','opus','sonnet'],
        'research': ['research','benchmark','battle','royale','study','inference'],
        'hardware': ['hardware','chip','cpu','gpu','compute','x86','ace','specification'],
        'business': ['business','roi','enterprise','invest','fund','revenue'],
    }
    for cat_key, keywords in kw_map.items():
        if any(w in cat for w in keywords):
            return CAT_STYLES[cat_key]
    return CAT_STYLES['general']


# ── main ──────────────────────────────────────────────────────────────

def generate_all_slides(md_path, output_dir=None):
    out = Path(output_dir) if output_dir else OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    data = parse_post(md_path)
    if not data:
        print("ERROR: Could not parse post"); return []

    date_str = data['date']
    stories = data['stories']
    from datetime import datetime
    try:
        display_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')
    except:
        display_date = date_str

    fs0 = get_cat_style(stories[0]['category']) if stories else CAT_STYLES['general']
    main_acc, main_acc2 = fs0[2], fs0[3]
    paths = []

    # Cover
    cover = gen_cover(display_date, len(stories), [s['category'] for s in stories], main_acc, main_acc2)
    p = out / "01_cover.png"; cover.save(p, "PNG"); paths.append(str(p))
    print("  ✓ Cover")

    # Stories
    for i, s in enumerate(stories, 1):
        st = get_cat_style(s['category'])
        slide = gen_story(i, s['title'], s['category'], s['summary'], s['takeaways'], display_date, st[2], st[3], st[0])
        p = out / (str(i+1).zfill(2) + "_story_" + str(i) + ".png"); slide.save(p, "PNG"); paths.append(str(p))
        print("  ✓ Story " + str(i) + ": " + s['title'][:42] + "... [" + s['category'] + "] (" + str(len(s['takeaways'])) + " KT)")

    # CTA
    cta = gen_cta(display_date, main_acc, main_acc2)
    p = out / (str(len(stories)+2).zfill(2) + "_cta.png"); cta.save(p, "PNG"); paths.append(str(p))
    print("  ✓ CTA")

    print("\n" + str(len(paths)) + " slides in " + str(out) + "/")
    return paths


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_images.py <md_post> [output_dir]"); sys.exit(1)
    generate_all_slides(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None)
