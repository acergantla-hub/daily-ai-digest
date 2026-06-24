from PIL import Image, ImageDraw, ImageFont
import os

stories = [
    ("slide_1.png", "Five Eyes Warns:\nAI Cyber Attacks\n'Months, Not Years'\nAway", None),
    ("slide_2.png", "OpenAI Launches\nOpen-Source\nBug Patching\nInitiative", None),
    ("slide_3.png", "Groq Raises\n$650M After\nNvidia Deal\nCollapsed", None),
    ("slide_4.png", "Baseten Hits\n$13B Valuation\nin Record\nAI Infra Bet", "baseten.png"),
    ("slide_5.png", "Alphabet Has\nWorst Day in\na Year on\nAI Concerns", None),
    ("slide_6.png", "AI Catches Heart\nCondition Doctors\nThought Was\nAsthma", None),
]

W, H = 1080, 1080
BG_COLOR = (10, 10, 30)
ACCENT = (0, 200, 255)
WHITE = (255, 255, 255)

for filename, title, bg_img in stories:
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    if bg_img and os.path.exists(bg_img):
        try:
            bg = Image.open(bg_img).resize((W, H)).convert("RGB")
            img = Image.blend(bg, Image.new("RGB", (W, H), BG_COLOR), 0.6)
            draw = ImageDraw.Draw(img)
        except Exception as e:
            print(f"  Could not load {bg_img}: {e}")

    font_paths = [
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/system/fonts/Roboto-Bold.ttf",
    ]
    font_title = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_title = ImageFont.truetype(fp, 72)
                font_sub = ImageFont.truetype(fp, 36)
                break
            except:
                continue
    if not font_title:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    lines = title.split("\n")
    total_height = len(lines) * 90
    y_start = (H - total_height) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        y = y_start + i * 90
        draw.line([(x, y - 15), (x + text_w, y - 15)], fill=ACCENT, width=3)
        draw.text((x, y), line, fill=WHITE, font=font_title)

    draw.rectangle([(0, H - 80), (W, H)], fill=ACCENT)
    tagline = "@lancerloki1  |  Daily AI Digest"
    bbox = draw.textbbox((0, 0), tagline, font=font_sub)
    text_w = bbox[2] - bbox[0]
    draw.text(((W - text_w) // 2, H - 60), tagline, fill=(10, 10, 30), font=font_sub)

    img.save(filename)
    print(f"  Saved {filename}")

print("Done!")
