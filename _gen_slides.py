#!/usr/bin/env python3
"""Generate all 10 slides for June 26 Daily AI Digest"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1080

# Colors
BG = (2, 2, 5)
ACCENT = (124, 108, 240)
PINK = (244, 114, 182)
CYAN = (0, 212, 240)
GREEN = (52, 211, 153)
TEXT = (240, 240, 250)
MUTED = (136, 136, 160)

# Font paths (Termux)
FONT_BOLD = "/system/fonts/DroidSans-Bold.ttf"
FONT_REG = "/system/fonts/DroidSans.ttf"

# Load fonts
def fbold(s): return ImageFont.truetype(FONT_BOLD, s)
def freg(s): return ImageFont.truetype(FONT_REG, s)

def draw_gradient(img, color):
    d = ImageDraw.Draw(img)
    for y in range(H):
        r = int(color[0] * (1 - y/H) * 0.3)
        g = int(color[1] * (1 - y/H) * 0.3)
        b = int(color[2] * (1 - y/H) * 0.3)
        d.line([(0, y), (W, y)], fill=(BG[0]+r, BG[1]+g, BG[2]+b))

def draw_bar(img, color, y0=0, h=6):
    d = ImageDraw.Draw(img)
    d.rectangle([(0, y0), (W, y0+h)], fill=color)

def tc(d, y, text, font, fill, max_w=W-160):
    """Text centered"""
    bbox = d.textbbox((0,0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if tw > max_w:
        # wrap
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = cur + " " + w if cur else w
            if d.textbbox((0,0), test, font=font)[2] < max_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        for i, line in enumerate(lines):
            bbox = d.textbbox((0,0), line, font=font)
            tw = bbox[2] - bbox[0]
            d.text(((W-tw)//2, y + i*bbox[3]*1.3), line, font=font, fill=fill)
        return y + len(lines) * bbox[3] * 1.3
    else:
        d.text((x, y), text, font=font, fill=fill)
        return y

def wrap_text(d, y, text, font, fill, max_w=W-160):
    """Wrap text and return new y"""
    bbox = d.textbbox((0,0), "A", font=font)
    line_h = bbox[3] * 1.5
    words = text.split()
    cur = ""
    for w in words:
        test = cur + " " + w if cur else w
        if d.textbbox((0,0), test, font=font)[2] < max_w:
            cur = test
        else:
            if cur:
                bbox = d.textbbox((0,0), cur, font=font)
                tw = bbox[2] - bbox[0]
                d.text(((W-tw)//2, y), cur, font=font, fill=fill)
                y += line_h
            cur = w
    if cur:
        bbox = d.textbbox((0,0), cur, font=font)
        tw = bbox[2] - bbox[0]
        d.text(((W-tw)//2, y), cur, font=font, fill=fill)
        y += line_h
    return y


stories = [
    {"num": 1, "title": "White House Pressures OpenAI to Slow-Roll GPT 5.6", "cat": "AI Policy", "color": ACCENT, "summary": "The Trump administration told OpenAI to limit distribution of its newest model to select partners, with government approving access customer by customer — a shift from hands-off to active federal oversight."},
    {"num": 2, "title": "Claude Winning Paid Consumers From ChatGPT", "cat": "Market Share", "color": PINK, "summary": "Anthropic's Claude is growing ~75% among paying consumers since January 2026, according to credit card analytics firm Indagari. The trend continued even after Anthropic refused to let its models be used by the Trump administration."},
    {"num": 3, "title": "Patronus AI Lands $50M for AI Agent Testing", "cat": "Funding", "color": CYAN, "summary": "Former Meta AI researchers founded Patronus AI to build simulated digital environments for stress-testing AI agents. Revenue has grown 15x in the past year, with nearly insatiable demand from frontier AI labs."},
    {"num": 4, "title": "Apple Skips M6, Pivots to AI-Focused M7 Mac Chips", "cat": "Hardware", "color": GREEN, "summary": "Apple is reportedly skipping its high-end M6 Mac chip generation entirely, launching an AI-focused M7 line with M7 Pro, M7 Max, and M7 Ultra instead."},
    {"num": 5, "title": "Apple Raises MacBook & iPad Prices on Memory Costs", "cat": "Pricing", "color": ACCENT, "summary": "Apple has raised prices across MacBook and iPad lines, driven by surging memory chip costs as AI-driven demand for high-bandwidth memory reshapes component pricing."},
    {"num": 6, "title": "2,000 People Tried to Hack an AI Assistant", "cat": "Security", "color": PINK, "summary": "Developer ran hackmyclaw.com where 2,000+ people emailed his AI assistant trying to extract secrets. Zero successful extractions out of 6,000+ attempts. Google suspended Gmail due to fraud detection triggers."},
    {"num": 7, "title": "900KB Transformer Compresses 100MB CSV to 7MB", "cat": "Research", "color": CYAN, "summary": "Overfitted a tiny transformer to memorize a single file and predict the next byte, achieving ~0.5 bits/byte compression. On a 100MB NYC taxi CSV it compressed to ~7MB. Open-sourced as pym-particles."},
    {"num": 8, "title": "OpenKnowledge: AI-First Obsidian Alternative", "cat": "Open Source", "color": GREEN, "summary": "A new open-source project aims to build an AI-native markdown editor and LLM wiki — integrating AI deeply into the workflow rather than bolting it on as an afterthought."},
]

out_dir = "instagram_posts"

# Clear old PNGs
for f in os.listdir(out_dir):
    if f.endswith('.png'):
        os.remove(os.path.join(out_dir, f))

# Slide 1: Cover
img = Image.new('RGB', (W, H), BG)
draw_gradient(img, ACCENT)
d = ImageDraw.Draw(img)
d.text((W//2 - 200, 400), "Daily AI Digest", font=fbold(80), fill=TEXT)
d.text((W//2 - 100, 520), "June 26, 2026", font=freg(40), fill=MUTED)
draw_bar(img, ACCENT, y0=600, h=6)
img.save(f"{out_dir}/01_cover.png")
print("✓ Cover")

# Story slides
for s in stories:
    img = Image.new('RGB', (W, H), BG)
    draw_gradient(img, s['color'])
    d = ImageDraw.Draw(img)
    
    # Number circle
    d.ellipse([(80, 80), (180, 180)], fill=s['color'])
    d.text((105, 95), str(s['num']), font=fbold(50), fill=BG)
    
    # Category
    d.text((220, 105), s['cat'], font=freg(28), fill=s['color'])
    
    # Title
    y = 250
    y = wrap_text(d, y, s['title'], fbold(52), TEXT)
    
    # Divider
    y += 40
    d.line([(80, y), (W-80, y)], fill=s['color'], width=2)
    
    # Summary
    y += 40
    y = wrap_text(d, y, s['summary'], freg(30), MUTED)
    
    # Bottom bar
    draw_bar(img, s['color'], y0=H-4, h=4)
    
    fname = f"02_story_{s['num']}.png" if s['num'] <= 2 else f"{s['num']+1}_story_{s['num']}.png"
    if s['num'] == 1:
        fname = "02_story_1.png"
    elif s['num'] == 2:
        fname = "03_story_2.png"
    else:
        fname = f"{s['num']+1}_story_{s['num']}.png"
    
    img.save(f"{out_dir}/{fname}")
    print(f"✓ Story {s['num']}: {s['title'][:40]}")

# CTA slide
img = Image.new('RGB', (W, H), BG)
draw_gradient(img, ACCENT)
d = ImageDraw.Draw(img)
d.text((W//2 - 250, 400), "Swipe to see", font=fbold(48), fill=TEXT)
d.text((W//2 - 250, 480), "today's AI news", font=fbold(48), fill=TEXT)
draw_bar(img, PINK, y0=580, h=6)
d.text((W//2 - 200, 650), "Read the full digest", font=freg(36), fill=MUTED)
d.text((W//2 - 150, 710), "daily-ai-digest.freelancerloki.workers.dev", font=freg(28), fill=MUTED)
d.text((W//2 - 100, H-200), "Follow @lancerloki1", font=fbold(36), fill=PINK)
img.save(f"{out_dir}/11_cta.png")
print("✓ CTA")

print(f"\nDone! {len(stories)+1} slides in {out_dir}/")
