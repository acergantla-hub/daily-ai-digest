#!/usr/bin/env python3
"""Debug color issues."""
from PIL import Image, ImageDraw
from pathlib import Path
import os

img = Image.new("RGB", (400, 200), (10, 10, 20))
draw = ImageDraw.Draw(img)

# Test with_alpha output
def blend_over(bg, fg, alpha):
    return tuple(int(bg[i] + (fg[i] - bg[i]) * alpha) for i in range(3))

def with_alpha(color, alpha, bg=(0, 0, 0)):
    return blend_over(bg, color, alpha)

c = with_alpha((124, 108, 240), 0.1)
print("Color type:", type(c), "value:", c)
print("Element types:", [type(x) for x in c])

# Does text work?
try:
    font_path = Path.home() / ".hermes" / "fonts" / "Inter-Regular.woff2"
    font = ImageFont.truetype(str(font_path), 18)
    draw.text((10, 10), "TEST", font=font, fill=c)
    print("Text OK with with_alpha color")
except Exception as e:
    print("Text FAIL:", e)

# Test with direct tuple
try:
    draw.text((10, 40), "TEST2", font=font, fill=(180, 160, 255))
    print("Text OK with direct tuple")
except Exception as e:
    print("Text2 FAIL:", e)

img.save("/data/data/com.termux/files/home/daily-ai-digest/test3.png")
print("Saved test3.png")
