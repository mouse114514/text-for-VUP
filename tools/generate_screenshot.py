from PIL import Image, ImageDraw, ImageFont
import os

W, H = 800, 600
BG = (26, 26, 46)
GREEN = (100, 255, 100)
WHITE = (230, 230, 230)
DIM_GREEN = (40, 120, 40)
ACCENT = (255, 200, 60)

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
out_dir = os.path.join(root_dir, "screenshots")
os.makedirs(out_dir, exist_ok=True)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

try:
    font_large = ImageFont.truetype("Consolas", 64)
    font_small = ImageFont.truetype("Consolas", 18)
    font_tiny = ImageFont.truetype("Consolas", 14)
except (OSError, IOError):
    try:
        font_large = ImageFont.truetype("cour.ttf", 64)
        font_small = ImageFont.truetype("cour.ttf", 18)
        font_tiny = ImageFont.truetype("cour.ttf", 14)
    except (OSError, IOError):
        font_large = ImageFont.load_default()
        font_small = font_large
        font_tiny = font_large

def center_xy(text, font, y):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    return (W - tw) // 2, y

def draw_char(char, x, y, font, color, alpha=255, offset=(0, 0)):
    if alpha < 255:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer)
        ldraw.text((x + offset[0], y + offset[1]), char, font=font, fill=(*color, alpha))
        img.paste(layer, (0, 0), layer)
    else:
        draw.text((x + offset[0], y + offset[1]), char, font=font, fill=color)

# Title bar area
draw.rectangle([(0, 0), (W, 28)], fill=(18, 18, 34))
draw.text((10, 4), "Text for VUP  —  Face Tracking Active", font=font_tiny, fill=(140, 140, 160))

# Close/minimize buttons
for bx, col in [(W - 8, (255, 80, 80)), (W - 22, (255, 200, 60)), (W - 36, (80, 200, 80))]:
    draw.ellipse([bx - 4, 8, bx + 4, 16], fill=col)

# Status bar at bottom
draw.rectangle([(0, H - 26), (W, H)], fill=(18, 18, 34))
draw.text((10, H - 20), "Tracking: OK  |  FPS: 29.7  |  Model: face_landmarker_v2", font=font_tiny, fill=(100, 100, 120))

# Top row: "=P"  (eyes + mouth shape)
top_y = 180
bot_y = 310

# Draw ghost/tracking-offset version (dim)
cx, cy = center_xy("=P", font_large, top_y)
draw_char("=P", cx, cy, font_large, DIM_GREEN, alpha=100, offset=(-12, -8))

cx2, cy2 = center_xy("oo", font_large, bot_y)
draw_char("oo", cx2, cy2, font_large, DIM_GREEN, alpha=100, offset=(-12, -8))

# Draw main character
draw_char("=P", cx, cy, font_large, WHITE)
draw_char("oo", cx2, cy2, font_large, GREEN)

# Small labels above character parts
draw.text((cx + 10, top_y - 30), "eyes", font=font_tiny, fill=(120, 120, 140))
draw.text((cx2 + 15, bot_y - 25), "mouth", font=font_tiny, fill=(120, 120, 140))

# Tracking data overlay (top-right corner)
track_x = W - 220
track_y = 40
draw.rectangle([(track_x - 6, track_y - 6), (W - 10, track_y + 68)], fill=(0, 0, 0, 160), outline=(40, 40, 60))
draw.text((track_x, track_y), "TRACKING DATA", font=font_tiny, fill=ACCENT)
draw.text((track_x, track_y + 16), f"L-Eye:  0.87", font=font_small, fill=(180, 255, 180))
draw.text((track_x, track_y + 34), f"R-Eye:  0.92", font=font_small, fill=(180, 255, 180))
draw.text((track_x, track_y + 52), f"Mouth:  0.34", font=font_small, fill=(255, 200, 180))

# FPS / info overlay (bottom-right)
draw.text((W - 150, H - 46), "CPU: 12%  |  Mem: 184MB", font=font_tiny, fill=(80, 80, 100))

# Guidance lines
for gy in [top_y + 72, bot_y + 68]:
    draw.line([(0, gy), (W, gy)], fill=(40, 40, 60), width=1)

out_path = os.path.join(out_dir, "demo.png")
img.save(out_path)
print(f"Screenshot saved to {out_path}")
print(f"Size: {img.size[0]}x{img.size[1]}")
