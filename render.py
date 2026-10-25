
import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 15
SECONDS = 30
TOTAL = FPS * SECONDS

os.makedirs("frames", exist_ok=True)

try:
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_big = ImageFont.truetype(FONT, 58)
    font_mid = ImageFont.truetype(FONT, 36)
except OSError:
    font_big = ImageFont.load_default()
    font_mid = ImageFont.load_default()


def centered(draw, text, y, font, fill):
    box = draw.textbbox((0, 0), text, font=font)
    x = (W - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)


def make_frame(frame_number):
    t = frame_number / FPS
    im = Image.new("RGB", (W, H), "#A9E5FF")
    d = ImageDraw.Draw(im)

    # Room and floor
    d.rectangle((0, 700, W, 1000), fill="#F7DDB2")
    d.rectangle((0, 1000, W, H), fill="#B8794D")

    # Window
    d.rounded_rectangle(
        (55, 180, 300, 510), radius=18,
        fill="#FFF4CE", outline="#FFFFFF", width=12
    )
    d.rectangle((170, 190, 183, 500), fill="#FFFFFF")
    d.rectangle((65, 335, 290, 348), fill="#FFFFFF")

    # Table
    d.rounded_rectangle(
        (365, 750, 665, 790), radius=12, fill="#8A4F2D"
    )
    d.rectangle((395, 780, 420, 960), fill="#704024")
    d.rectangle((610, 780, 635, 960), fill="#704024")

    # Cookie and plate
    cookie_gone = t >= 21
    cookie_x = 520
    d.ellipse((435, 735, 600, 775), fill="#F4F0E8")
    if not cookie_gone:
        d.ellipse(
            (cookie_x - 42, 680, cookie_x + 42, 752),
            fill="#C98342", outline="#8D4E24", width=5
        )
        for dx, dy in [(-18, 12), (12, 4), (0, 32), (22, 42), (-23, 43)]:
            d.ellipse(
                (cookie_x + dx - 6, 712 + dy - 6,
                 cookie_x + dx + 6, 712 + dy + 6),
                fill="#62351E"
            )
    else:
        for dx, dy in [(-25, 0), (10, -8), (30, 8), (-5, 12)]:
            d.ellipse(
                (cookie_x + dx, 750 + dy,
                 cookie_x + dx + 12, 762 + dy),
                fill="#C98342"
            )

    # Sneaking character
    progress = min(max((t - 3) / 17, 0), 1)
    x = int(115 + progress * 300)
    bob = int(math.sin(t * 5) * 7)

    # Shadow
    d.ellipse((x - 60, 940, x + 65, 965), fill="#A56B49")

    # Body
    d.rounded_rectangle(
        (x - 48, 815 + bob, x + 48, 935 + bob),
        radius=28, fill="#5D66D8"
    )

    # Legs
    d.line(
        (x - 20, 925 + bob, x - 35, 960),
        fill="#25305C", width=19
    )
    d.line(
        (x + 20, 925 + bob, x + 35, 960),
        fill="#25305C", width=19
    )

    # Head
    d.ellipse(
        (x - 58, 710 + bob, x + 58, 830 + bob),
        fill="#FFD0A1", outline="#7C4A35", width=4
    )

    # Hair
    d.arc(
        (x - 58, 700 + bob, x + 58, 790 + bob),
        180, 350, fill="#513321", width=20
    )

    # Eyes
    eye_y = 765 + bob
    d.ellipse((x - 30, eye_y, x - 12, eye_y + 22), fill="#252525")
    d.ellipse((x + 12, eye_y, x + 30, eye_y + 22), fill="#252525")

    # Expression
    if t < 20:
        d.arc(
            (x - 15, 780 + bob, x + 18, 807 + bob),
            15, 150, fill="#8D4534", width=4
        )
    else:
        d.ellipse(
            (x - 13, 785 + bob, x + 13, 809 + bob),
            fill="#7B3028"
        )

    # Arms reaching for cookie
    if 12 <= t < 22:
        d.line(
            (x + 35, 845 + bob, x + 100, 810),
            fill="#FFD0A1", width=22
        )
        d.ellipse((x + 88, 797, x + 112, 822), fill="#FFD0A1")
    else:
        d.line(
            (x + 35, 845 + bob, x + 65, 880),
            fill="#FFD0A1", width=22
        )

    # Story captions
    if t < 4:
        d.rounded_rectangle(
            (45, 55, 675, 155), radius=25, fill="#FFFFFF"
        )
        centered(d, "THE COOKIE HEIST", 77, font_mid, "#34254F")
    elif 4 <= t < 12:
        centered(d, "ACT NATURAL...", 85, font_mid, "#34254F")
    elif 12 <= t < 20:
        centered(d, "JUST ONE COOKIE!", 85, font_mid, "#34254F")
    elif 20 <= t < 25:
        centered(d, "UH-OH!", 85, font_big, "#B92D3D")
    else:
        d.rounded_rectangle(
            (55, 1050, 665, 1195), radius=28, fill="#FFFFFF"
        )
        centered(d, "MISSION", 1065, font_mid, "#34254F")
        centered(d, "ACCOMPLISHED?", 1110, font_mid, "#D34B36")

    im.save(f"frames/frame_{frame_number:04d}.png")


print("Drawing cartoon frames...")
for i in range(TOTAL):
    make_frame(i)

print("Making vertical MP4...")
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

print("SUCCESS: tiny_trouble_short.mp4 created!")
