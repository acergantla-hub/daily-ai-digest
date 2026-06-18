#!/usr/bin/env python3
"""Debug rounded rect."""
from PIL import Image, ImageDraw

img = Image.new("RGB", (400, 200), (10, 10, 20))
draw = ImageDraw.Draw(img)

# Test 1: basic rounded rect
try:
    draw.rounded_rectangle([50, 50, 350, 150], radius=20, fill=(255, 0, 0), outline=(0, 255, 0), width=2)
    print("Test 1 OK: basic rounded_rect")
except Exception as e:
    print("Test 1 FAIL:", e)

# Test 2: with blended color
try:
    color = (int(124 * 0.1), int(108 * 0.1), int(240 * 0.1))
    draw.rounded_rectangle([50, 50, 350, 150], radius=20, fill=color, outline=(124, 108, 240), width=1)
    print("Test 2 OK: blended color rounded_rect")
except Exception as e:
    print("Test 2 FAIL:", e)

img.save("/data/data/com.termux/files/home/daily-ai-digest/test_rect.png")
print("Saved test_rect.png")
