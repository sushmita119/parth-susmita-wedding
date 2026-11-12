#!/usr/bin/env python3
"""Fast invite render: 5 static slides + ffmpeg zoompan."""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "public/assets/photos"
OUT = ROOT / "public/assets"
SLIDES = ROOT / "output/slides"
TMP = ROOT / "output"
W, H = 1080, 1920


def fnt(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    p = (
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Georgia.ttf"
    )
    return ImageFont.truetype(p, size)


def portrait_crop(im: Image.Image, focus_y: float = 0.32) -> Image.Image:
    """Center vertical 3:4 slice from landscape photo, then scale to frame."""
    im = im.convert("RGB")
    tw = int(im.height * 3 / 4)
    tw = min(tw, im.width)
    left = (im.width - tw) // 2
    im = im.crop((left, 0, left + tw, im.height))
    fh, fw = int(H * 0.52), int(W * 0.72)
    im = im.resize((fw, fh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), (253, 246, 236))
    px = (W - fw) // 2
    py = int(H * 0.22)
    canvas.paste(im, (px, py))
    return canvas


def center(draw: ImageDraw.ImageDraw, text: str, y: int, font, fill, stroke=0, stroke_fill=None):
    bb = draw.textbbox((0, 0), text, font=font)
    draw.text(((W - bb[2] + bb[0]) // 2 - bb[0], y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def slide_intro() -> Path:
    img = Image.new("RGB", (W, H), (61, 15, 26))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 120), fill=(212, 175, 55))
    d.rectangle((0, H - 120, W, H), fill=(212, 175, 55))
    center(d, "Save The Date", int(H * 0.38), fnt(72), (255, 215, 0), 2, (80, 0, 0))
    center(d, "Parth & Susmita", int(H * 0.48), fnt(90, True), (255, 255, 255), 2, (80, 0, 0))
    center(d, "Haldi · Wedding · Reception", int(H * 0.58), fnt(38), (255, 228, 196))
    center(d, "Siliguri, West Bengal", int(H * 0.64), fnt(36), (255, 228, 196))
    p = SLIDES / "00-intro.png"
    img.save(p, optimize=True)
    return p


def slide_photo(file: str, title: str, date: str, sub: str, bar: tuple[int, int, int], tint: tuple[float, float, float]) -> Path:
    base = portrait_crop(Image.open(PHOTOS / file))
    im = ImageEnhance.Color(base).enhance(1.12)
    d = ImageDraw.Draw(im)
    d.rectangle((int(W * 0.12), int(H * 0.18), int(W * 0.88), int(H * 0.76)), outline=(212, 175, 55), width=6)
    d.rectangle((0, 0, W, 90), fill=bar)
    d.rectangle((0, H - 90, W, H), fill=bar)
    center(d, title, 175, fnt(70, True), (255, 255, 255), 2, (0, 0, 0))
    center(d, date, 265, fnt(54), (255, 215, 0), 2, (40, 20, 0))
    center(d, sub, 335, fnt(36), (255, 248, 231))
    center(d, "Parth & Susmita", H - 200, fnt(44, True), (255, 255, 255), 2, (0, 0, 0))
    name = {"haldi.JPG": "01-haldi", "victoria.JPG": "02-wedding", "ghat8.JPG": "03-reception"}[file]
    p = SLIDES / f"{name}.png"
    im.save(p, optimize=True)
    return p


def slide_outro() -> Path:
    img = Image.new("RGB", (W, H), (26, 10, 20))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 120), fill=(212, 175, 55))
    center(d, "Your presence is our blessing", int(H * 0.42), fnt(46), (255, 215, 0))
    center(d, "Parth & Susmita", int(H * 0.52), fnt(82, True), (255, 255, 255))
    center(d, "12 Dec · Haldi  |  13 Dec · Wedding", int(H * 0.62), fnt(34), (255, 228, 196))
    center(d, "16 Dec · Reception  |  Siliguri", int(H * 0.66), fnt(34), (255, 228, 196))
    p = SLIDES / "04-outro.png"
    img.save(p, optimize=True)
    return p


def clip(png: Path, sec: float, out: Path) -> None:
    frames = int(sec * 24)
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0004,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s=1080x1920:fps=24"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(png), "-t", str(sec),
            "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", str(out),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    SLIDES.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    slides = [
        (slide_intro(), 3.5, TMP / "c00.mp4"),
        (slide_photo("haldi.JPG", "Haldi Ceremony", "12 December 2026", "Morning celebrations", (230, 168, 23), (1.08, 1.06, 0.88)), 8, TMP / "c01.mp4"),
        (slide_photo("victoria.JPG", "Wedding", "13 December 2026", "Sacred vows", (139, 21, 56), (1.1, 0.98, 0.95)), 8, TMP / "c02.mp4"),
        (slide_photo("ghat8.JPG", "Reception", "16 December 2026", "Evening with loved ones", (27, 58, 107), (1.02, 1.02, 1.12)), 8, TMP / "c03.mp4"),
        (slide_outro(), 3.5, TMP / "c04.mp4"),
    ]

    for png, sec, mp4 in slides:
        clip(png, sec, mp4)

    total = sum(s for _, s, _ in slides)
    list_file = TMP / "concat.txt"
    list_file.write_text("\n".join(f"file '{mp4}'" for _, _, mp4 in slides) + "\n")
    vo = TMP / "vo.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(vo)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(vo), "-i", str(OUT / "song.m4a"),
            "-filter_complex", f"[1:a]atrim=0:{total},asetpts=PTS-STARTPTS[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            str(OUT / "invite.mp4"),
        ],
        check=True,
        capture_output=True,
    )
    print(f"Done: {OUT / 'invite.mp4'} ({total:.1f}s)")


if __name__ == "__main__":
    main()
