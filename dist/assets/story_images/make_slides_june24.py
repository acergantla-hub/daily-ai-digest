from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1080, 1080
ACCENT = (0, 200, 255)
DARK = (10, 10, 30)
WHITE = (255, 255, 255)
PURPLE = (120, 80, 255)
GREEN = (0, 255, 150)
RED = (255, 80, 80)
ORANGE = (255, 165, 0)

def get_fonts():
    font_paths = [
        '/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/system/fonts/Roboto-Bold.ttf',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, 68), ImageFont.truetype(fp, 34), ImageFont.truetype(fp, 28)
    return ImageFont.load_default(), ImageFont.load_default(), ImageFont.load_default()

font_title, font_sub, font_small = get_fonts()

def make_bg(color1=(5,5,25), color2=(15,10,40)):
    img = Image.new('RGB', (W, H), DARK)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(color1[0]*(1-y/H) + color2[0]*(y/H))
        g = color1[1]
        b = int(color1[2]*(1-y/H) + color2[2]*(y/H))
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img, draw

def add_footer(draw, color, text='@lancerloki1  |  Daily AI Digest'):
    draw.rectangle([(0, H-70), (W, H)], fill=color)
    bbox = draw.textbbox((0,0), text, font=font_small)
    tw = bbox[2]-bbox[0]
    draw.text(((W-tw)//2, H-48), text, fill=DARK if color==ACCENT or color==GREEN or color==ORANGE else WHITE, font=font_small)

def add_title(draw, lines, y_start, color=WHITE):
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_sub)
        tw = bbox[2]-bbox[0]
        draw.text(((W-tw)//2, y), line, fill=color, font=font_sub)
        y += 44
    return y

def glow_circle(draw, cx, cy, r, color):
    for i in range(r+30, r, -3):
        a = int(60 * (1 - (r+30-i)/30))
        draw.ellipse([(cx-i,cy-i),(cx+i,cy+i)], fill=(color[0]//4,color[1]//4,color[2]//4))
    draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], fill=color)

def draw_chart_down(draw, cx, cy, color=RED):
    draw.line([(cx-150,cy-50),(cx-50,cy-100)], fill=color, width=5)
    draw.line([(cx-50,cy-100),(cx+50,cy+30)], fill=color, width=5)
    draw.line([(cx+50,cy+30),(cx+150,cy+100)], fill=color, width=5)

def draw_chip_icon(draw, cx, cy, w=80, h=55, color=ACCENT):
    draw.rectangle([(cx-w,cy-h),(cx+w,cy+h)], fill=color, outline=WHITE, width=2)
    for i in range(-w+15, w, 25):
        draw.rectangle([(cx+i-6,cy-h-18),(cx+i+6,cy-h)], fill=(180,180,180))
        draw.rectangle([(cx+i-6,cy+h),(cx+i+6,cy+h+18)], fill=(180,180,180))
    draw.rectangle([(cx-w//2,cy-h//2),(cx+w//2,cy+h//2)], fill=(60,60,100), outline=ACCENT, width=2)

def draw_slack_icon(draw, cx, cy, s=60, color=PURPLE):
    # Slack-like hashtag
    draw.rectangle([(cx-s,cy-s//3),(cx-s+8,cy+s//3)], fill=color)
    draw.rectangle([(cx+s-8,cy-s//3),(cx+s,cy+s//3)], fill=color)
    draw.rectangle([(cx-s//3,cy-s),(cx+s//3,cy-s+8)], fill=color)
    draw.rectangle([(cx-s//3,cy+s-8),(cx+s//3,cy+s)], fill=color)
    draw.rectangle([(cx-s//2,cy-s//2),(cx-s//2+8,cy+s//2)], fill=color)
    draw.rectangle([(cx+s//2-8,cy-s//2),(cx+s//2,cy+s//2)], fill=color)

def draw_gavel(draw, cx, cy, color=ORANGE):
    # simple gavel
    draw.rectangle([(cx-10,cy-60),(cx+10,cy+60)], fill=color)
    draw.rectangle([(cx-40,cy-80),(cx+40,cy-55)], fill=color)
    draw.line([(cx,cy+60),(cx,cy+100)], fill=color, width=6)

def draw_globe(draw, cx, cy, r, color=ACCENT):
    draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], outline=color, width=3)
    draw.arc([(cx-r,cy-r),(cx+r,cy+r)], 180, 360, fill=color, width=2)
    draw.line([(cx,cy-r),(cx,cy+r)], fill=color, width=2)
    for y_off in [-r//2, 0, r//2]:
        draw.arc([(cx-r,cy+y_off-10),(cx+r,cy+y_off+10)], 0, 180, fill=color, width=2)

def draw_warning_tri(draw, cx, cy, s, color=ORANGE):
    draw.polygon([(cx,cy-s),(cx-s,cy+s),(cx+s,cy+s)], fill=color)
    draw.text((cx-12,cy-s+18), '!', fill=WHITE, font=font_sub)

def draw_cloudflare_icon(draw, cx, cy, color=ORANGE):
    # flame shape
    draw.polygon([(cx,cy-60),(cx+30,cy-20),(cx+50,cy+10),(cx+40,cy+50),(cx,cy+60),(cx-40,cy+50),(cx-50,cy+10),(cx-30,cy-20)], fill=color)

def draw_factory(draw, cx, cy, color=RED):
    # factory with X
    draw.rectangle([(cx-80,cy-30),(cx+80,cy+80)], fill=color)
    draw.rectangle([(cx-60,cy-70),(cx-30,cy-30)], fill=color)
    draw.rectangle([(cx+20,cy-60),(cx+50,cy-30)], fill=color)
    draw.line([(cx-40,cy+10),(cx+40,cy+50)], fill=WHITE, width=5)
    draw.line([(cx+40,cy+10),(cx-40,cy+50)], fill=WHITE, width=5)

# ── SLIDE 1: Global AI Sell-Off ──
img, draw = make_bg((15,5,20),(5,10,30))
draw_chart_down(draw, 540, 300, RED)
glow_circle(draw, 540, 300, 50, (RED[0]//3,RED[1]//3,RED[2]//3))
# falling bars
for x,h,c in [(200,150,RED),(350,250,RED),(500,180,RED),(650,300,RED),(800,200,RED)]:
    draw.rectangle([(x-25,500-h),(x+25,500)], fill=c, outline=WHITE, width=2)
# dollar crash
try:
    big = ImageFont.truetype('/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', 120)
except:
    big = font_title
draw.text((380,550), '$', fill=RED, font=big)
add_title(draw, ['Global AI Sell-Off:','Tech Stocks in Freefall','as Bubble Fears Mount'], 740)
add_footer(draw, RED)
img.save('assets/story_images/slide1_june24.png')
print('slide1 done')

# ── SLIDE 2: Oracle Cuts 21K Jobs ──
img, draw = make_bg((15,5,25),(5,10,20))
draw_factory(draw, 540, 350)
# people icons disappearing
for i in range(5):
    x = 200 + i*150
    y = 550
    alpha = 100 if i < 2 else 40
    draw.ellipse([(x-20,y-60),(x+20,y-20)], fill=(alpha,alpha,alpha+50))
    draw.rectangle([(x-25,y-20),(x+25,y+50)], fill=(alpha,alpha,alpha+50))
add_title(draw, ['Oracle Cuts','21,000 Jobs','While Pivoting to AI'], 680)
add_footer(draw, RED)
img.save('assets/story_images/slide2_june24.png')
print('slide2 done')

# ── SLIDE 3: Meta Halts AI Training Tracking ──
img, draw = make_bg((5,15,30),(10,5,25))
# eye with slash
draw.ellipse([(440,280),(640,380)], outline=RED, width=4)
draw.ellipse([(490,310),(590,350)], fill=RED)
draw.line([(420,260),(660,400)], fill=RED, width=5)
# lock
draw.rectangle([(460,430),(620,530)], fill=GREEN, outline=WHITE, width=3)
draw.arc([(490,390),(590,440)], 180, 0, fill=GREEN, width=4)
draw.rectangle([(535,410),(545,440)], fill=GREEN)
add_title(draw, ['Meta Halts Worker','Tracking for AI','Training Over Privacy'], 620)
add_footer(draw, GREEN)
img.save('assets/story_images/slide3_june24.png')
print('slide3 done')

# ── SLIDE 4: Anthropic Slack Agents ──
img, draw = make_bg((10,5,30),(5,15,25))
draw_slack_icon(draw, 540, 320, 80, PURPLE)
glow_circle(draw, 540, 320, 100, (PURPLE[0]//3,PURPLE[1]//3,PURPLE[2]//3))
# chat bubbles
draw.rounded_rectangle([(280,420),(480,490)], radius=20, fill=(40,40,60), outline=ACCENT, width=2)
draw.rounded_rectangle([(600,500),(800,570)], radius=20, fill=(40,40,60), outline=PURPLE, width=2)
draw.text((310,440), 'AI agent...', fill=WHITE, font=font_small)
draw.text((630,520), 'Done!', fill=WHITE, font=font_small)
add_title(draw, ['Anthropic Drops','Workplace AI Agents','Directly in Slack'], 650)
add_footer(draw, PURPLE)
img.save('assets/story_images/slide4_june24.png')
print('slide4 done')

# ── SLIDE 5: Senate AI Hearing ──
img, draw = make_bg((5,10,35),(15,5,20))
draw_gavel(draw, 540, 320, ORANGE)
# columns
draw.rectangle([(300,200),(310,500)], fill=WHITE)
draw.rectangle([(770,200),(780,500)], fill=WHITE)
# divided line
draw.line([(300,350),(780,350)], fill=ORANGE, width=3)
# left/right arrows
draw.polygon([(250,350),(280,330),(280,370)], fill=GREEN)
draw.polygon([(830,350),(800,330),(800,370)], fill=RED)
add_title(draw, ['Senate AI Hearing:','Innovation vs.','Oversight Battle'], 600)
add_footer(draw, ORANGE)
img.save('assets/story_images/slide5_june24.png')
print('slide5 done')

# ── SLIDE 6: AI Chatbot Warrant ──
img, draw = make_bg((10,5,25),(5,15,30))
# chatbot with magnifier
draw.rounded_rectangle([(350,250),(730,400)], radius=30, fill=(40,40,60), outline=ACCENT, width=3)
draw.ellipse([(500,300),(580,380)], outline=ACCENT, width=3)
draw.line([(540,340),(540,380)], fill=ACCENT, width=3)
# magnifying glass
draw.ellipse([(680,350),(780,450)], outline=ORANGE, width=4)
draw.line([(760,430),(810,480)], fill=ORANGE, width=6)
# question mark
draw.text((420,280), '?', fill=WHITE, font=font_title)
add_title(draw, ['Judge Allows Search','Warrant Targeting','AI Chatbot Records'], 550)
add_footer(draw, ORANGE)
img.save('assets/story_images/slide6_june24.png')
print('slide6 done')

# ── SLIDE 7: Cloudflare CEO Warning ──
img, draw = make_bg((15,5,20),(5,10,25))
draw_cloudflare_icon(draw, 540, 300, ORANGE)
# small biz icon (store with X)
draw.rectangle([(380,420),(500,520)], fill=(100,100,120), outline=WHITE, width=2)
draw.rectangle([(580,420),(700,520)], fill=(100,100,120), outline=WHITE, width=2)
draw.line([(390,430),(490,510)], fill=RED, width=4)
draw.line([(490,430),(390,510)], fill=RED, width=4)
draw.line([(590,430),(690,510)], fill=RED, width=4)
draw.line([(690,430),(590,510)], fill=RED, width=4)
add_title(draw, ['Cloudflare CEO:','AI Agents Threaten','Small Businesses'], 620)
add_footer(draw, ORANGE)
img.save('assets/story_images/slide7_june24.png')
print('slide7 done')

# ── SLIDE 8: UN Environmental Ask ──
img, draw = make_bg((5,15,30),(10,5,35))
draw_globe(draw, 540, 320, 100, GREEN)
# factory smoke
for i in range(3):
    x = 380 + i*120
    draw.ellipse([(x,200),(x+40,240)], fill=(80,80,80))
    draw.ellipse([(x+10,170),(x+50,210)], fill=(80,80,80))
# leaf
draw.polygon([(540,450),(510,500),(540,550),(570,500)], fill=GREEN)
draw.line([(540,450),(540,550)], fill=DARK, width=3)
add_title(draw, ['UN Demands AI','Companies Reveal','Environmental Impact'], 650)
add_footer(draw, GREEN)
img.save('assets/story_images/slide8_june24.png')
print('slide8 done')

print('All done!')
