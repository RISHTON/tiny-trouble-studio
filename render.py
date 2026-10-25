
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
    box = d.textbbox((0, 0), text, font=font)
    x = (W - (box[2] - box[0])) // 2
    d.text((x, y), text, font=font, fill=color)


def rounded(d, box, fill, radius=24, outline=None, width=3):
    d.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width
    )


def cookie(d, x, y, size=42):
    d.ellipse(
        (x-size, y-size, x+size, y+size),
        fill="#C98342",
        outline="#8D4E24",
        width=4
    )

    for dx, dy in [
        (-15, -12), (12, -18), (5, 8),
        (-20, 15), (22, 16)
    ]:
        d.ellipse(
            (x+dx-5, y+dy-5, x+dx+5, y+dy+5),
            fill="#62351E"
        )


def character(d, x, y, t, mood="sneaky"):
    bob = math.sin(t * 7) * 6
    x = int(x)
    y = int(y + bob)

    # Character shadow
    d.ellipse(
        (x-65, y+225, x+65, y+245),
        fill="#986541"
    )

    # Moving legs
    stride = math.sin(t * 8) * 18

    d.line(
        (x-22, y+175, x-30+stride, y+225),
        fill="#27315D",
        width=20
    )

    d.line(
        (x+22, y+175, x+30-stride, y+225),
        fill="#27315D",
        width=20
    )

    # Shoes
    d.ellipse(
        (x-55+stride, y+213, x-15+stride, y+232),
        fill="#29253B"
    )

    d.ellipse(
        (x+15-stride, y+213, x+55-stride, y+232),
        fill="#29253B"
    )

    # Body
    rounded(
        d,
        (x-48, y+85, x+48, y+185),
        "#6268DC",
        28
    )

    # Arms
    if mood == "reach":
        d.line(
            (x+30, y+112, x+95, y+75),
            fill="#FFD0A1",
            width=22
        )

        d.ellipse(
            (x+82, y+61, x+108, y+87),
            fill="#FFD0A1"
        )

        d.line(
            (x-30, y+115, x-55, y+150),
            fill="#FFD0A1",
            width=20
        )

    elif mood == "panic":
        d.line(
            (x-30, y+112, x-75, y+72),
            fill="#FFD0A1",
            width=22
        )

        d.line(
            (x+30, y+112, x+75, y+72),
            fill="#FFD0A1",
            width=22
        )

    else:
        d.line(
            (x-30, y+112, x-55, y+145),
            fill="#FFD0A1",
            width=20
        )

        d.line(
            (x+30, y+112, x+55, y+145),
            fill="#FFD0A1",
            width=20
        )

    # Head
    d.ellipse(
        (x-58, y-5, x+58, y+112),
        fill="#FFD0A1",
        outline="#7C4A35",
        width=4
    )

    # Hair
    d.pieslice(
        (x-61, y-15, x+61, y+65),
        180,
        355,
        fill="#503321"
    )

    # Facial expressions
    if mood == "panic":
        eye_y = y + 42

        d.ellipse(
            (x-32, eye_y-7, x-8, eye_y+23),
            fill="white"
        )

        d.ellipse(
            (x+8, eye_y-7, x+32, eye_y+23),
            fill="white"
        )

        d.ellipse(
            (x-23, eye_y+2, x-13, eye_y+16),
            fill="#252525"
        )

        d.ellipse(
            (x+13, eye_y+2, x+23, eye_y+16),
            fill="#252525"
        )

        d.line(
            (x-32, y+25, x-8, y+20),
            fill="#503321",
            width=5
        )

        d.line(
            (x+8, y+20, x+32, y+25),
            fill="#503321",
            width=5
        )

        d.ellipse(
            (x-12, y+72, x+12, y+98),
            fill="#7B3028"
        )

    elif mood == "proud":
        d.ellipse(
            (x-30, y+37, x-10, y+58),
            fill="#252525"
        )

        d.ellipse(
            (x+10, y+37, x+30, y+58),
            fill="#252525"
        )

        d.arc(
            (x-20, y+48, x+22, y+88),
            10,
            165,
            fill="#8D4534",
            width=5
        )

    else:
        d.ellipse(
            (x-30, y+35, x-10, y+58),
            fill="white"
        )

        d.ellipse(
            (x+10, y+35, x+30, y+58),
            fill="white"
        )

        d.ellipse(
            (x-24, y+42, x-13, y+55),
            fill="#252525"
        )

        d.ellipse(
            (x+13, y+42, x+24, y+55),
            fill="#252525"
        )

        d.arc(
            (x-15, y+65, x+18, y+88),
            15,
            155,
            fill="#8D4534",
            width=4
        )


def draw_room(d):
    # Permanent walls
    d.rectangle((0, 0, W, 900), fill="#F2D8B5")

    # Wall panels
    for px in range(25, W, 115):
        d.line(
            (px, 0, px, 900),
            fill="#E5C49D",
            width=3
        )

    # Window
    rounded(
        d,
        (45, 135, 290, 455),
        "#FFF5D6",
        12
    )

    d.rectangle(
        (60, 150, 275, 440),
        fill="#9EDDF4"
    )

    # Sun outside
    d.ellipse(
        (205, 175, 250, 220),
        fill="#FFE38A"
    )

    # Window frame
    d.line(
        (167, 150, 167, 440),
        fill="#FFFFFF",
        width=9
    )

    d.line(
        (60, 295, 275, 295),
        fill="#FFFFFF",
        width=9
    )

    # Curtains
    d.polygon(
        [(45, 135), (100, 135), (85, 440), (45, 455)],
        fill="#C95D5D"
    )

    d.polygon(
        [(235, 135), (290, 135), (290, 455), (250, 440)],
        fill="#C95D5D"
    )

    # Wall clock
    d.ellipse(
        (535, 145, 635, 245),
        fill="#FFF8E7",
        outline="#7B533C",
        width=7
    )

    d.line(
        (585, 195, 585, 165),
        fill="#513321",
        width=5
    )

    d.line(
        (585, 195, 610, 210),
        fill="#513321",
        width=5
    )

    # Picture
    rounded(
        d,
        (390, 270, 520, 390),
        "#8A4F2D",
        8
    )

    d.rectangle(
        (402, 282, 508, 378),
        fill="#B9DFA7"
    )

    d.ellipse(
        (425, 300, 485, 360),
        fill="#F8D57E"
    )

    # Floor
    d.rectangle(
        (0, 900, W, 920),
        fill="#FFFFFF"
    )

    d.rectangle(
        (0, 920, W, H),
        fill="#B8794D"
    )

    for fy in range(960, H, 90):
        d.line(
            (0, fy, W, fy),
            fill="#995E3B",
            width=3
        )

    for fx in range(70, W, 160):
        d.line(
            (fx, 920, fx-50, H),
            fill="#995E3B",
            width=2
        )

    # Plant and pot
    d.rectangle(
        (65, 785, 140, 850),
        fill="#B85F43"
    )

    d.line(
        (102, 790, 102, 700),
        fill="#447C48",
        width=8
    )

    d.ellipse(
        (65, 700, 105, 745),
        fill="#4E9C59"
    )

    d.ellipse(
        (100, 675, 145, 720),
        fill="#5EAA60"
    )

    d.ellipse(
        (85, 735, 130, 775),
        fill="#3E8549"
    )


def make_frame(i):
    t = i / FPS

    # Same room background in every scene
    im = Image.new("RGB", (W, H), "#F2D8B5")
    d = ImageDraw.Draw(im)

    draw_room(d)

    # Table
    rounded(
        d,
        (350, 725, 675, 775),
        "#8A4F2D",
        12
    )

    d.rectangle(
        (380, 765, 405, 1000),
        fill="#704024"
    )

    d.rectangle(
        (620, 765, 645, 1000),
        fill="#704024"
    )

    # Plate
    d.ellipse(
        (420, 705, 610, 755),
        fill="#FFFFFF"
    )

    d.ellipse(
        (440, 711, 590, 748),
        fill="#E8E2D9"
    )

    # Scene 1: Sneaking
    if t < 9:
        caption = "OPERATION: COOKIE"

        x = 130 + int(t * 12)
        character(d, x, 700, t, "sneaky")
        cookie(d, 520, 690)

        if 5 < t < 8:
            text_center(d, "SHHH...", 540, MID)

    # Scene 2: Reaching
    elif t < 18:
        caption = "JUST ONE BITE!"

        character(d, 330, 700, t, "reach")
        cookie(d, 520, 690)

        if t > 14:
            text_center(d, "ALMOST...", 535, MID)

    # Scene 3: Panic and crumbs
    elif t < 27:
        caption = "UH-OH!"

        character(d, 475, 700, t, "panic")

        for k in range(12):
            cx = int(520 + math.sin(t*4+k)*95)
            cy = int(670 + math.cos(t*5+k)*65)

            d.ellipse(
                (cx-6, cy-6, cx+6, cy+6),
                fill="#C98342"
            )

        if t > 22:
            rounded(
                d,
                (95, 1010, 625, 1160),
                "#FFFFFF"
            )

            text_center(
                d,
                "WHO ATE THE COOKIE?",
                1055,
                SMALL
            )

    # Scene 4: Comedy ending
    else:
        caption = "CASE CLOSED?"

        character(d, 470, 700, t, "proud")

        # Crumbs on character's face
        for cx, cy in [
            (451, 770),
            (490, 780),
            (475, 800)
        ]:
            d.ellipse(
                (cx, cy, cx+9, cy+9),
                fill="#C98342"
            )

        # Empty plate
        d.ellipse(
            (420, 705, 610, 755),
            fill="#FFFFFF"
        )

        d.ellipse(
            (440, 711, 590, 748),
            fill="#E8E2D9"
        )

        rounded(
            d,
            (85, 1000, 635, 1185),
            "#FFFFFF"
        )

        text_center(
            d,
            "CASE CLOSED",
            1020,
            MID
        )

        text_center(
            d,
            "I SAW NOTHING!",
            1075,
            SMALL
        )

        if t > 33:
            text_center(
                d,
                "FOLLOW FOR MORE!",
                1140,
                SMALL
            )

    # Caption banner
    rounded(
        d,
        (35, 45, 685, 125),
        "#FFFFFF",
        22
    )

    text_center(
        d,
        caption,
        62,
        MID
    )

    im.save(
        f"frames/frame_{i:04d}.png"
    )


def main():
    print("Drawing improved cartoon...")

    for i in range(TOTAL):
        make_frame(i)

    print("Creating vertical MP4...")

    subprocess.run([
        "ffmpeg",
        "-y",
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

    print("SUCCESS: improved cartoon created!")


if __name__ == "__main__":
    main()
