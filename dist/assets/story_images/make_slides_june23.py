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
        g = color1[1]  # keep it simple
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

def draw_shield(draw, cx, cy, s, color):
    pts = [(cx,cy-s),(cx+s,cy-s//2),(cx+s,cy+s//3),(cx,cy+s),(cx-s,cy+s//3),(cx-s,cy-s//2)]
    draw.polygon(pts, fill=color, outline=WHITE)

def draw_chip_icon(draw, cx, cy, w=80, h=55, color=ACCENT):
    draw.rectangle([(cx-w,cy-h),(cx+w,cy+h)], fill=color, outline=WHITE, width=2)
    for i in range(-w+15, w, 25):
        draw.rectangle([(cx+i-6,cy-h-18),(cx+i+6,cy-h)], fill=(180,180,180))
        draw.rectangle([(cx+i-6,cy+h),(cx+i+6,cy+h+18)], fill=(180,180,180))
    draw.rectangle([(cx-w//2,cy-h//2),(cx+w//2,cy+h//2)], fill=(60,60,100), outline=ACCENT, width=2)

def draw_heart_icon(draw, cx, cy, s=90):
    pts = []
    for t in range(0, 360, 4):
        rad = math.radians(t)
        x = 16*math.sin(rad)**3
        y = -(13*math.cos(rad)-5*math.cos(2*rad)-2*math.cos(3*rad)-math.cos(4*rad))
        pts.append((cx+int(x*s/17), cy+int(y*s/17)))
    draw.polygon(pts, fill=RED)
    # pulse
    draw.line([(cx-s-20,cy+s+15),(cx-s//2,cy+s+15)], fill=WHITE, width=3)
    draw.line([(cx-s//2,cy+s+15),(cx,cy+s-10)], fill=WHITE, width=3)
    draw.line([(cx,cy+s-10),(cx+10,cy+s+25)], fill=WHITE, width=3)
    draw.line([(cx+10,cy+s+25),(cx+s//2,cy+s+15)], fill=WHITE, width=3)
    draw.line([(cx+s//2,cy+s+15),(cx+s+20,cy+s+15)], fill=WHITE, width=3)

def draw_chart_down(draw, cx, cy, color=RED):
    draw.line([(cx-150,cy-50),(cx-50,cy-100)], fill=color, width=5)
    draw.line([(cx-50,cy-100),(cx+50,cy+30)], fill=color, width=5)
    draw.line([(cx+50,cy+30),(cx+150,cy+100)], fill=color, width=5)

def draw_bug_fix(draw, cx, cy, s=60):
    draw.ellipse([(cx-s,cy-s//2),(cx+s,cy+s//2)], fill=GREEN)
    draw.ellipse([(cx-s//3,cy-s),(cx+s//3,cy-s//2)], fill=GREEN)
    for a in [-40,-20,20,40]:
        rad = math.radians(a)
        for side in [-1,1]:
            draw.line([(cx+side*s,cy),(cx+side*s+25*math.cos(rad),cy+25*math.sin(rad))], fill=GREEN, width=3)
    draw.line([(cx-12,cy+5),(cx-2,cy+18),(cx+18,cy-12)], fill=DARK, width=5)

# ── SLIDE 1: Five Eyes ──
img, draw = make_bg((5,5,20),(10,5,35))
# network nodes
positions = [(540,220),(320,380),(760,380),(380,580),(700,580)]
for i,(x,y) in enumerate(positions):
    c = RED if i==0 else ACCENT
    glow_circle(draw, x, y, 20 if i==0 else 15, c)
    if i > 0:
        draw.line([(540,220),(x,y)], fill=(c[0]//3,c[1]//3,c[2]//3), width=2)
draw_shield(draw, 540, 450, 55, (RED[0]//2,RED[1]//2,RED[1]//2))
# warning
draw.polygon([(540,680),(495,760),(585,760)], fill=ORANGE)
draw.text((528,700), '!', fill=WHITE, font=font_sub)
add_title(draw, ['Five Eyes Warns:','AI Cyber Attacks','"Months, Not Years"','Away'], 790)
add_footer(draw, RED)
img.save('slide1_june23.png')
print('slide1 done')

# ── SLIDE 2: OpenAI Open-Source Bug ──
img, draw = make_bg((5,15,30),(10,5,25))
draw_bug_fix(draw, 450, 360, 65)
glow_circle(draw, 680, 280, 30, ACCENT)
glow_circle(draw, 320, 480, 25, PURPLE)
# code symbols
try:
    big = ImageFont.truetype('/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', 100)
except:
    big = font_title
draw.text((220,240), '{ }', fill=ACCENT, font=big)
draw.text((620,420), '</>', fill=PURPLE, font=big)
add_title(draw, ['OpenAI Launches','Open-Source Bug','Patching Initiative'], 740)
add_footer(draw, GREEN)
img.save('slide2_june23.png')
print('slide2 done')

# ── SLIDE 3: Groq ──
img, draw = make_bg((10,5,30),(5,15,25))
draw_chip_icon(draw, 540, 350)
glow_circle(draw, 300, 250, 22, GREEN)
glow_circle(draw, 780, 250, 22, GREEN)
for pos in [(180,350),(900,350),(180,520),(900,520)]:
    draw.text(pos, '$', fill=(GREEN[0]//2,GREEN[1]//2,GREEN[2]//2), font=font_title)
add_title(draw, ['Groq Raises','$650M After Nvidia','Deal Collapsed'], 680)
add_footer(draw, ACCENT)
img.save('slide3_june23.png')
print('slide3 done')

# ── SLIDE 4: Baseten ──
img, draw = make_bg((5,10,35),(15,5,20))
# bars
for x,h,c in [(280,250,GREEN),(440,380,ACCENT),(600,180,PURPLE),(760,450,ORANGE)]:
    draw.rectangle([(x-35,600-h),(x+35,600)], fill=c, outline=WHITE, width=2)
# rocket
draw.polygon([(540,160),(515,260),(565,260)], fill=ORANGE)
draw.rectangle([(520,260),(560,340)], fill=WHITE)
draw.polygon([(525,340),(540,385),(555,340)], fill=ORANGE)
add_title(draw, ['Baseten Hits','$13B Valuation','in AI Infra'], 690)
add_footer(draw, ORANGE)
img.save('slide4_june23.png')
print('slide4 done')

# ── SLIDE 5: Alphabet ──
img, draw = make_bg((15,5,20),(5,10,30))
draw_chart_down(draw, 540, 350, RED)
glow_circle(draw, 540, 350, 45, (RED[0]//3,RED[1]//3,RED[2]//3))
for i,c in enumerate([(234,67,53),(66,133,244),(52,168,83),(251,188,4)]):
    draw.ellipse([(280+i*120-18,560-18),(280+i*120+18,560+18)], fill=c)
add_title(draw, ['Alphabet Has Worst','Day in a Year','on AI Concerns'], 720)
add_footer(draw, RED)
img.save('slide5_june23.png')
print('slide5 done')

# ── SLIDE 6: Heart ──
img, draw = make_bg((15,5,25),(5,10,20))
draw_heart_icon(draw, 540, 350)
glow_circle(draw, 540, 350, 110, (RED[0]//4,RED[1]//4,RED[2]//4))
# stethoscope
draw.arc([(400,220),(680,480)], 200, 340, fill=WHITE, width=5)
draw.ellipse([(525,415),(555,445)], fill=WHITE)
# sparkles
for pos in [(280,200),(800,200),(230,480),(850,480),(540,140)]:
    draw.text(pos, '*', fill=ACCENT, font=font_title)
add_title(draw, ['AI Catches Heart','Condition Doctors','Thought Was Asthma'], 680)
add_footer(draw, RED)
img.save('slide6_june23.png')
print('slide6 done')

print('All done!')
