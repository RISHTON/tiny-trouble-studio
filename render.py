
import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 15
SECONDS = 36
TOTAL = FPS * SECONDS

os.makedirs("frames", exist_ok=True)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

try:
    BIG = ImageFont.truetype(FONT_PATH, 58)
    MID = ImageFont.truetype(FONT_PATH, 38)
    SMALL = ImageFont.truetype(FONT_PATH, 28)
except OSError:
    BIG = MID = SMALL = ImageFont.load_default()


def text_center(d, text, y, font, color="#34254F"):
    b = d.textbbox((0, 0), text, font=font)
    x = (W - (b[2] - b[0])) // 2
    d.text((x, y), text, font=font, fill=color,
           stroke_width=0)


def rounded(d, box, fill, radius=24, outline=None, width=3):
    d.rounded_rectangle(
        box, radius=radius, fill=fill,
        outline=outline, width=width
    )


def character(d, x, y, t, mood="sneaky", scale=1.0):
    bob = math.sin(t * 7) * 6
    x = int(x)
    y = int(y + bob)

    # Shadow
    d.ellipse((x-65, y+225, x+65, y+245),
              fill="#B98A69")

    # Legs
    stride = math.sin(t * 8) * 18
    d.line((x-22, y+175, x-30+stride, y+225),
           fill="#27315D", width=20)
    d.line((x+22, y+175, x+30-stride, y+225),
           fill="#27315D", width=20)

    # Shoes
    d.ellipse((x-55+stride, y+213, x-15+stride, y+232),
              fill="#29253B")
    d.ellipse((x+15-stride, y+213, x+55-stride, y+232),
              fill="#29253B")

    # Body
    rounded(d, (x-48, y+85, x+48, y+185),
            "#6268DC", 28)

    # Arms change with the action
    if mood == "reach":
        d.line((x+30, y+112, x+95, y+75),
               fill="#FFD0A1", width=22)
        d.ellipse((x+82, y+61, x+108, y+87),
                  fill="#FFD0A1")
        d.line((x-30, y+115, x-55, y+150),
               fill="#FFD0A1", width=20)
    elif mood == "panic":
        d.line((x-30, y+112, x-75, y+72),
               fill="#FFD0A1", width=22)
        d.line((x+30, y+112, x+75, y+72),
               fill="#FFD0A1", width=22)
    else:
        d.line((x-30, y+112, x-55, y+145),
               fill="#FFD0A1", width=20)
        d.line((x+30, y+112, x+55, y+145),
               fill="#FFD0A1", width=20)

    # Head
    d.ellipse((x-58, y-5, x+58, y+112),
              fill="#FFD0A1", outline="#7C4A35", width=4)

    # Hair
    d.pieslice((x-61, y-15, x+61, y+65),
               180, 355, fill="#503321")

    # Eyebrows and eyes
    if mood == "panic":
        eye_y = y+42
        d.ellipse((x-32, eye_y-7, x-8, eye_y+23),
                  fill="white")
        d.ellipse((x+8, eye_y-7, x+32, eye_y+23),
                  fill="white")
        d.ellipse((x-23, eye_y+2, x-13, eye_y+16),
                  fill="#252525")
        d.ellipse((x+13, eye_y+2, x+23, eye_y+16),
                  fill="#252525")
        d.line((x-32, y+25, x-8, y+20),
               fill="#503321", width=5)
        d.line((x+8, y+20, x+32, y+25),
               fill="#503321", width=5)
        d.ellipse((x-12, y+72, x+12, y+98),
                  fill="#7B3028")
    elif mood == "proud":
        d.ellipse((x-30, y+37, x-10, y+58),
                  fill="#252525")
        d.ellipse((x+10, y+37, x+30, y+58),
                  fill="#252525")
        d.arc((x-20, y+48, x+22, y+88),
              10, 165, fill="#8D4534", width=5)
    else:
        d.ellipse((x-30, y+35, x-10, y+58),
                  fill="white")
        d.ellipse((x+10, y+35, x+30, y+58),
                  fill="white")
        d.ellipse((x-24, y+42, x-13, y+55),
                  fill="#252525")
        d.ellipse((x+13, y+42, x+24, y+55),
                  fill="#252525")
        d.arc((x-15, y+65, x+18, y+88),
              15, 155, fill="#8D4534", width=4)


def cookie(d, x, y, size=42):
    d.ellipse((x-size, y-size, x+size, y+size),
              fill="#C98342", outline="#8D4E24", width=4)
    for dx, dy in [(-15, -12), (12, -18), (5, 8),
                   (-20, 15), (22, 16)]:
        d.ellipse((x+dx-5, y+dy-5, x+dx+5, y+dy+5),
                  fill="#62351E")


def make_frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), "#A9E5FF")
    d = ImageDraw.Draw(im)

    # Background changes between scenes
    if t < 9:
        sky, floor = "#A9E5FF", "#B8794D"
    elif t < 18:
        sky, floor = "#FFE4A8", "#B8794D"
    elif t < 27:
        sky, floor = "#F8C7D8", "#8C6BC4"
    else:
        sky, floor = "#B8E8C5", "#B8794D"

    d.rectangle((0, 0, W, H), fill=sky)
    d.rectangle((0, 900, W, H), fill=floor)

    # Room window
    rounded(d, (45, 160, 290, 465), "#FFF5D6", 20,
            "#FFFFFF", 10)
    d.line((167, 170, 167, 455), fill="#FFFFFF", width=10)
    d.line((55, 310, 280, 310), fill="#FFFFFF", width=10)

    # Table
    rounded(d, (350, 725, 675, 775), "#8A4F2D", 12)
    d.rectangle((380, 765, 405, 1000), fill="#704024")
    d.rectangle((620, 765, 645, 1000), fill="#704024")

    # Plate
    d.ellipse((420, 705, 610, 755), fill="#FFFFFF")
    d.ellipse((440, 711, 590, 748), fill="#E8E2D9")

    # Four scenes
    if t < 9:
        caption = "OPERATION: COOKIE"
        x = 130 + int(min(t / 9, 1) * 120)
        mood = "sneaky"
        character(d, x, 700, t, mood)
        cookie(d, 520, 690)
        if 5 < t < 8:
            text_center(d, "SHHH...", 540, MID)

    elif t < 18:
        caption = "JUST ONE BITE!"
        x = 300 + int(math.sin(t * 2) * 15)
        character(d, x, 700, t, "reach")
        cookie(d, 520, 690)
        if t > 14:
            text_center(d, "ALMOST...", 535, MID)

    elif t < 27:
        caption = "UH-OH!"
        x = 475
        character(d, x, 700, t, "panic")
        # Flying cookie crumbs
        for k in range(12):
            cx = int(520 + math.sin(t*4+k)*95)
            cy = int(670 + math.cos(t*5+k)*65)
            d.ellipse((cx-6, cy-6, cx+6, cy+6),
                      fill="#C98342")
        if t > 22:
            rounded(d, (95, 1010, 625, 1160), "#FFFFFF")
            text_center(d, "WHO ATE THE COOKIE?", 1055, SMALL)

    else:
        caption = "CASE CLOSED?"
        character(d, 470, 700, t, "proud")
        # Crumbs on the face
        for cx, cy in [(451, 770), (490, 780), (475, 800)]:
            d.ellipse((cx, cy, cx+9, cy+9), fill="#C98342")
        # Empty plate
        d.ellipse((420, 705, 610, 755), fill="#FFFFFF")
        d.ellipse((440, 711, 590, 748), fill="#E8E2D9")
        rounded(d, (85, 1000, 635, 1185), "#FFFFFF")
        text_center(d, "CASE CLOSED", 1020, MID)
        text_center(d, "I SAW NOTHING!", 1075, SMALL)
        if t > 33:
            text_center(d, "FOLLOW FOR MORE!", 1140, SMALL)

    # Scene caption
    rounded(d, (35, 45, 685, 125), "#FFFFFF", 22)
    text_center(d, caption, 62, MID)

    im.save(f"frames/frame_{i:04d}.png")


print("Drawing improved cartoon...")
for i in range(TOTAL):
    make_frame(i)

print("Creating MP4...")
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", "frames/frame_%04d.png",
    "-f", "lavfi",
    "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
    "-t", str(SECONDS),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-shortest",
    "-movflags", "+faststart",
    "tiny_trouble_short.mp4"
], check=True)

print("SUCCESS: improved 36-second cartoon created!")
