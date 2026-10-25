
import math
import os
import random
import struct
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 720, 1280
FPS = 24
SECONDS = 15
TOTAL = FPS * SECONDS
AUDIO_RATE = 44100

CHARACTER_FILE = "image.webp"
OUTPUT_FILE = "tiny_trouble_short.mp4"

os.makedirs("frames", exist_ok=True)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

try:
    BIG = ImageFont.truetype(FONT_PATH, 48)
    MID = ImageFont.truetype(FONT_PATH, 34)
except OSError:
    BIG = MID = ImageFont.load_default()

if not os.path.exists(CHARACTER_FILE):
    raise FileNotFoundError(
        "Image.webp not found. Put it beside render.py."
    )

character_original = Image.open(CHARACTER_FILE).convert("RGBA")
character_original.thumbnail((410, 650), Image.Resampling.LANCZOS)


def centered_text(draw, text, y, font, fill="#FFFFFF"):
    box = draw.textbbox((0, 0), text, font=font)
    x = (W - (box[2] - box[0])) // 2
    draw.text((x + 3, y + 4), text, font=font, fill="#392A35")
    draw.text((x, y), text, font=font, fill=fill)


def background(t):
    im = Image.new("RGB", (W, H))
    px = im.load()

    for y in range(H):
        if y < 850:
            c = int(242 - y * 0.025)
            color = (c, int(c * 0.84), int(c * 0.68))
        else:
            color = (158, 99, 62)

        for x in range(W):
            px[x, y] = color

    d = ImageDraw.Draw(im, "RGBA")

    # Warm window light
    d.rounded_rectangle(
        (45, 130, 270, 460),
        radius=24,
        fill=(255, 245, 205, 255)
    )
    d.rectangle(
        (62, 147, 253, 443),
        fill=(123, 201, 230, 255)
    )
    d.ellipse(
        (185, 180, 240, 235),
        fill=(255, 220, 112, 255)
    )
    d.line((158, 150, 158, 440), fill="white", width=9)
    d.line((62, 295, 253, 295), fill="white", width=9)

    # Floor boards
    for y in range(920, H, 85):
        d.line((0, y, W, y), fill=(100, 55, 36, 100), width=3)

    # Table
    d.rounded_rectangle(
        (325, 745, 690, 805),
        radius=18,
        fill="#764326"
    )
    d.rectangle((360, 790, 390, 1050), fill="#603820")
    d.rectangle((630, 790, 660, 1050), fill="#603820")

    # Cookie plate
    d.ellipse((390, 710, 630, 780), fill="#F8F3E9")
    d.ellipse((408, 718, 612, 770), fill="#DAD4CA")

    # Cookie
    cookie_x = int(500 + 12 * math.sin(t * 2))
    cookie_y = int(718 + 4 * math.sin(t * 3))
    d.ellipse(
        (cookie_x - 37, cookie_y - 24,
         cookie_x + 37, cookie_y + 24),
        fill="#C98242",
        outline="#8B4A25",
        width=4
    )

    for dx, dy in [(-17, -8), (9, -13), (15, 8), (-5, 10)]:
        d.ellipse(
            (cookie_x + dx - 4, cookie_y + dy - 4,
             cookie_x + dx + 4, cookie_y + dy + 4),
            fill="#58321F"
        )

    # Soft foreground vignette
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, W, 18), fill=(50, 28, 35, 45))
    return Image.alpha_composite(im.convert("RGBA"), overlay)


def add_character(im, t):
    # Character moves into the scene and reacts.
    if t < 3:
        progress = t / 3
        x = int(-100 + progress * 160)
        scale = 0.86 + progress * 0.10
        bob = math.sin(t * 9) * 5
    elif t < 6:
        x = int(60 + (t - 3) * 24)
        scale = 0.96 + 0.03 * math.sin(t * 4)
        bob = math.sin(t * 10) * 7
    elif t < 10:
        x = int(130 + 35 * math.sin((t - 6) * 3))
        scale = 1.0 + 0.04 * math.sin(t * 8)
        bob = math.sin(t * 15) * 12
    else:
        x = int(130 + 10 * math.sin(t * 2))
        scale = 1.0 + 0.02 * math.sin(t * 5)
        bob = math.sin(t * 4) * 3

    w = max(1, int(character_original.width * scale))
    h = max(1, int(character_original.height * scale))
    sprite = character_original.resize(
        (w, h), Image.Resampling.LANCZOS
    )

    # A little rotation makes the movement less static.
    angle = 0
    if 6 < t < 10:
        angle = math.sin(t * 13) * 5
        sprite = sprite.rotate(
            angle, resample=Image.Resampling.BICUBIC, expand=True
        )

    y = int(440 + bob + (1 - scale) * 120)

    # If the source image has transparency, its edges blend into the scene.
    im.alpha_composite(sprite, (x, y))


def make_frame(i):
    t = i / FPS
    im = background(t)

    # Slight camera zoom at the surprise moment.
    if 6.0 <= t <= 8.5:
        zoom = 1.0 + 0.055 * math.sin(
            math.pi * (t - 6.0) / 2.5
        )
        nw, nh = int(W * zoom), int(H * zoom)
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        left = (nw - W) // 2
        top = (nh - H) // 2
        im = im.crop((left, top, left + W, top + H))

    add_character(im, t)
    d = ImageDraw.Draw(im, "RGBA")

    # Small flying crumbs during the accident.
    if 7 <= t <= 10:
        random.seed(42)
        for k in range(18):
            phase = (t - 7) * 90 + k * 23
            cx = int(500 + math.sin(phase) * (35 + k * 2))
            cy = int(700 + math.cos(phase * 0.7) * (20 + k * 2))
            r = 3 + k % 4
            d.ellipse(
                (cx-r, cy-r, cx+r, cy+r),
                fill=(201, 130, 66, 240)
            )

    if t < 3:
        caption = "OPERATION: COOKIE"
    elif t < 6:
        caption = "JUST ONE BITE..."
    elif t < 8:
        caption = "OH NO!"
    elif t < 11:
        caption = "ACT NATURAL"
    else:
        caption = "I SAW NOTHING!"

    d.rounded_rectangle(
        (30, 42, 690, 116),
        radius=22,
        fill=(35, 27, 39, 220)
    )
    centered_text(d, caption, 57, MID)

    # Reaction burst
    if 6.5 < t < 8.0:
        centered_text(d, "?!", 220, BIG, "#FFE58B")

    im.convert("RGB").save(
        f"frames/frame_{i:04d}.jpg",
        quality=94
    )


def make_audio():
    random.seed(7)
    total = AUDIO_RATE * SECONDS

    # Build a playful original tune and timed sound effects.
    with wave.open("soundtrack.wav", "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(AUDIO_RATE)

        chunk = 4096
        for start in range(0, total, chunk):
            data = bytearray()

            for n in range(start, min(start + chunk, total)):
                t = n / AUDIO_RATE
                music = 0.0

                # Light playful plucked melody.
                if t < 15:
                    beat = int(t / 0.24)
                    notes = [523, 659, 784, 659, 587, 698, 880, 698]
                    freq = notes[beat % len(notes)]
                    local = t % 0.24
                    env = math.exp(-local * 7)
                    music += 0.14 * env * math.sin(
                        2 * math.pi * freq * t
                    )
                    music += 0.045 * env * math.sin(
                        2 * math.pi * freq * 2 * t
                    )

                # Sneaky footsteps at 1.0 and 2.0 seconds.
                for onset in (1.0, 2.0, 4.0, 4.45):
                    dt = t - onset
                    if 0 <= dt < 0.12:
                        music += 0.20 * math.exp(-dt * 30) * math.sin(
                            2 * math.pi * (100 - 250 * dt) * dt
                        )

                # Comedic whoosh at the reach.
                dt = t - 5.7
                if 0 <= dt < 0.65:
                    noise = random.uniform(-1, 1)
                    music += noise * 0.12 * math.sin(
                        math.pi * dt / 0.65
                    )

                # Boing at the surprise.
                dt = t - 7.0
                if 0 <= dt < 0.6:
                    freq = 180 + 420 * math.exp(-dt * 5)
                    music += 0.28 * math.exp(-dt * 4) * math.sin(
                        2 * math.pi * freq * dt
                    )

                # Cookie crunch at 9.0 seconds.
                dt = t - 9.0
                if 0 <= dt < 0.22:
                    music += random.uniform(-0.22, 0.22) * math.exp(-dt * 8)

                # Tiny comic sting at the ending.
                dt = t - 11.7
                if 0 <= dt < 0.45:
                    music += 0.16 * math.exp(-dt * 5) * math.sin(
                        2 * math.pi * 880 * dt
                    )

                sample = max(-0.95, min(0.95, music))
                value = int(sample * 32767)
                data.extend(struct.pack("<hh", value, value))

            wf.writeframes(data)


def main():
    print("Rendering 15-second cartoon...")

    for i in range(TOTAL):
        make_frame(i)

    print("Creating music and sound effects...")
    make_audio()

    print("Combining video and audio with FFmpeg...")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", "frames/frame_%04d.jpg",
        "-i", "soundtrack.wav",
        "-t", str(SECONDS),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        OUTPUT_FILE
    ], check=True)

    print("DONE:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
