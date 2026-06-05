from PIL import Image, ImageDraw, ImageFont
import os

W, H = 800, 600
BG = (26, 26, 46); GREEN = (100, 255, 100); WHITE = (230, 230, 230); ACCENT = (255, 200, 60)

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'screenshots')
os.makedirs(out_dir, exist_ok=True)

img = Image.new('RGB', (W, H), BG)
draw = ImageDraw.Draw(img)

try:
    font_large = ImageFont.truetype('Consolas', 64)
    font_small = ImageFont.truetype('Consolas', 18)
    font_tiny = ImageFont.truetype('Consolas', 14)
except:
    font_large = font_small = font_tiny = ImageFont.load_default()

def cxy(text, font, y):
    b = draw.textbbox((0,0), text, font=font)
    tw = b[2]-b[0]
    return (W-tw)//2, y

# Title bar
draw.rectangle([(0,0),(W,28)], fill=(18,18,34))
draw.text((10,4), 'Text for VUP  ---  Face Tracking Active', font=font_tiny, fill=(140,140,160))
for bx,cl in [(W-8,(255,80,80)),(W-22,(255,200,60)),(W-36,(80,200,80))]:
    draw.ellipse([bx-4, 8, bx+4, 16], fill=cl)

# Status bar
draw.rectangle([(0,H-26),(W,H)], fill=(18,18,34))
draw.text((10,H-20), 'Tracking: OK  |  FPS: 29.7  |  Model: face_landmarker_v2', font=font_tiny, fill=(100,100,120))

# Mini grid legend
gs, gx0, gy0 = 28, 340, 28
cell_data = {
    (0,0): ((255,80,80),'Eye'), (0,1): ((255,200,60),'Mouth'),
    (1,0): ((160,80,255),'L Hand'), (1,1): ((160,80,255),'R Hand')
}
chars = [['=','P'],['o','o']]
for r in range(2):
    for c in range(2):
        x = gx0 + c*(gs+4); y = gy0 + r*(gs+4)
        col, lbl = cell_data[(r,c)]
        draw.rectangle([x,y,x+gs,y+gs], fill=col, outline=(60,60,80))
        b = draw.textbbox((0,0), chars[r][c], font=font_tiny)
        tw = b[2]-b[0]; th = b[3]-b[1]
        draw.text((x+(gs-tw)//2, y+(gs-th)//2-2), chars[r][c], font=font_tiny, fill=(0,0,0))
        draw.text((x, y+gs+2), lbl, font=font_tiny, fill=(120,120,140))

# Main character
top_y, bot_y = 180, 320
cx, cy = cxy('=P', font_large, top_y)
cx2, cy2 = cxy('oo', font_large, bot_y)

# Ghost for tracking feel
def ghost(txt, x, y):
    ly = Image.new('RGBA', (W,H), (0,0,0,0))
    ld = ImageDraw.Draw(ly)
    ld.text((x-12, y-8), txt, font=font_large, fill=(40,120,40,100))
    img.paste(ly, (0,0), ly)
ghost('=P', cx, cy)
ghost('oo', cx2, cy2)
draw.text((cx,cy), '=P', font=font_large, fill=WHITE)
draw.text((cx2,cy2), 'oo', font=font_large, fill=GREEN)

# Role labels on the character
for t,x,y,cl in [
    ('Eye (0,0)', cx, top_y-28, (255,130,130)),
    ('Mouth (0,1)', cx+60, top_y-28, (255,220,120)),
    ('L Hand (1,0)', cx2, bot_y-28, (200,150,255)),
    ('R Hand (1,1)', cx2+60, bot_y-28, (200,150,255)),
]:
    draw.text((x,y), t, font=font_tiny, fill=cl)

# Tracking panel
tx, ty = W-230, 100
draw.rectangle([(tx-6,ty-6),(W-10,ty+100)], fill=(0,0,0,160), outline=(40,40,60))
draw.text((tx,ty), 'TRACKING', font=font_tiny, fill=ACCENT)
draw.text((tx,ty+18), 'L-Eye:  0.87', font=font_small, fill=(180,255,180))
draw.text((tx,ty+38), 'R-Eye:  0.92', font=font_small, fill=(180,255,180))
draw.text((tx,ty+58), 'Mouth:  0.34', font=font_small, fill=(255,200,180))
draw.text((tx,ty+78), 'Hands:  2 detected', font=font_small, fill=(200,180,255))

# Guide lines
for gy in [top_y+72, bot_y+68]:
    draw.line([(0,gy),(W,gy)], fill=(40,40,60), width=1)

out = os.path.join(out_dir, 'demo.png')
img.save(out)
print(f'Saved to {out}')
