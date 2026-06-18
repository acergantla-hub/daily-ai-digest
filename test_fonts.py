#!/usr/bin/env python3
"""Quick emoji render test."""
from PIL import Image, ImageDraw, ImageFont
import os

sys_fonts = '/data/data/com.termux/files/usr/share/fonts/TTF/'
hermes_fonts = os.path.expanduser('~/.hermes/fonts')

img = Image.new('RGB', (400, 100), (10, 10, 20))
draw = ImageDraw.Draw(img)

# Try Inter
try:
    font = ImageFont.truetype(str(hermes_fonts) + '/Inter-Bold.woff2', 48)
    draw.text((10, 10), 'Test ABC 123', font=font, fill=(255,255,255))
    print('Inter-Bold OK')
except Exception as e:
    print('Inter-Bold fail:', e)

# Try emoji with DejaVu
try:
    font2 = ImageFont.truetype(sys_fonts + 'DejaVuSans.ttf', 40)
    draw.text((10, 55), 'Test no emoji', font=font2, fill=(255,255,255))
    print('DejaVu text OK')
except Exception as e:
    print('DejaVu fail:', e)

out = '/data/data/com.termux/files/home/test_emoji.png'
img.save(out)
print('Saved:', out)
