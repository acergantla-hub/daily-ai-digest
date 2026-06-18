#!/usr/bin/env python3
"""Test PIL text signature."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

img = Image.new("RGB", (400, 100), (10, 10, 20))
draw = ImageDraw.Draw(img)

font_path = Path.home() / ".hermes" / "fonts" / "Inter-Regular.woff2"
font = ImageFont.truetype(str(font_path), 24)

# PIL text signature: text(xy, text, fill=None, font=None, ...)
# So: text((x, y), "TEXT", fill=(r,g,b), font=font)

# Method 1: keyword args
try:
    draw.text((10, 10), "TEST1", fill=(255, 255, 255), font=font)
    print("Method 1 OK: fill=X, font=Y kwargs")
except Exception as e:
    print("Method 1 FAIL:", e)

# Method 2: positional (wrong order - font before fill)
try:
    draw.text((10, 50), "TEST2", font, (255, 255, 255))
    print("Method 2 OK: positional font, fill")
except Exception as e:
    print("Method 2 FAIL:", e)

img.save("/data/data/com.termux/files/home/daily-ai-digest/test4.png")
print("Saved")
