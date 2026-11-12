#!/usr/bin/env python3
"""Render 9:16 wedding invite video (intro + 3 events + outro)."""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "public/assets/photos"
OUT = ROOT / "public/assets"
TMP = ROOT / "output/frames"
W, H = 1080, 1920
FPS = 30
DUR_INTRO = 4
DUR_EVENT = 9
DUR_OUTRO = 4


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    paths = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def gradient_bar(draw: ImageDraw.ImageDraw, y0: int, height: int, color: tuple[int, int, int]) -> None:
    for i in range(height):
        alpha = int(200 * (1 - abs(i / height - 0.5) * 0.3))
        draw.rectangle((0, y0 + i, W, y0 + i + 1), fill=(*color, min(255, alpha)))


def cover_crop(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    scale = max(W / im.width, H / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return im.crop((left, top, left + W, top + H))


def tinted(im: Image.Image, rgb_mul: tuple[float, float, float], sat: float = 1.0) -> Image.Image:
    r, g, b = rgb_mul
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            pr, pg, pb = px[x, y]
            px[x, y] = (
                min(255, int(pr * r)),
                min(255, int(pg * g)),
                min(255, int(pb * b)),
            )
    if sat != 1.0:
        im = ImageEnhance.Color(im).enhance(sat)
    return im


def draw_centered(draw: ImageDraw.ImageDraw, text: str, y: int, fnt: ImageFont.FreeTypeFont, fill, stroke=0, stroke_fill=None) -> None:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def frame_intro(t: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H), (61, 15, 26))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    gradient_bar(draw, 0, 140, (212, 175, 55))
    gradient_bar(draw, H - 140, 140, (212, 175, 55))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    fade = min(1.0, t / (FPS * 0.8))
    gold = (int(255 * fade), int(215 * fade), int(0))
    draw_centered(draw, "Save The Date", int(H * 0.36), font(78), gold, 2, (80, 0, 0))
    draw_centered(draw, "Parth & Susmita", int(H * 0.46), font(96, True), (255, 255, 255), 2, (100, 20, 20))
    draw_centered(draw, "Together with their families", int(H * 0.56), font(40), (255, 228, 196))
    draw_centered(draw, "cordially invite you", int(H * 0.60), font(40), (255, 228, 196))
    draw_centered(draw, "Siliguri · West Bengal", int(H * 0.70), font(36), (245, 245, 245))
    return img


def frame_event(photo: Image.Image, title: str, date: str, sub: str, bar_rgb: tuple[int, int, int], tint, t: int, total: int) -> Image.Image:
    zoom = 1.02 + 0.12 * (t / max(1, total - 1))
    base = cover_crop(photo)
    bw, bh = base.size
    zw, zh = int(bw * zoom), int(bh * zoom)
    scaled = base.resize((zw, zh), Image.Resampling.LANCZOS)
    left = (zw - W) // 2
    top = (zh - H) // 2
    frame = scaled.crop((left, top, left + W, top + H))
    frame = tinted(frame, tint, sat=1.2)
    frame = frame.filter(ImageFilter.GaussianBlur(radius=0.3))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    gradient_bar(od, 0, 130, bar_rgb)
    gradient_bar(od, H - 130, 130, bar_rgb)
    od.rectangle((0, 0, W, H), fill=(0, 0, 0, 40))
    frame = Image.alpha_composite(frame.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(frame)
    draw_centered(draw, title, 200, font(74, True), (255, 255, 255), 3, (0, 0, 0))
    draw_centered(draw, date, 295, font(56), (255, 215, 0), 2, (60, 30, 0))
    draw_centered(draw, sub, 365, font(38), (255, 248, 231))
    draw_centered(draw, "Parth & Susmita", H - 220, font(46, True), (255, 255, 255), 2, (80, 40, 0))
    return frame.convert("RGB")


def frame_outro(t: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H), (26, 10, 20))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    gradient_bar(draw, 0, 140, (212, 175, 55))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_centered(draw, "Your presence is our blessing", int(H * 0.40), font(46), (255, 215, 0))
    draw_centered(draw, "Parth & Susmita", int(H * 0.50), font(88, True), (255, 255, 255), 2, (100, 0, 40))
    draw_centered(draw, "Haldi · 12 Dec  |  Wedding · 13 Dec", int(H * 0.60), font(34), (255, 228, 196))
    draw_centered(draw, "Reception · 16 Dec  |  Siliguri", int(H * 0.64), font(34), (255, 228, 196))
    return img


def write_sequence(name: str, frames: list[Image.Image], start_index: int) -> int:
    for i, fr in enumerate(frames):
        fr.save(TMP / f"frame_{start_index + i:05d}.jpg", quality=92)
    return start_index + len(frames)


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    for f in TMP.glob("frame_*.jpg"):
        f.unlink()

    idx = 0
    intro_frames = [frame_intro(t, DUR_INTRO * FPS) for t in range(DUR_INTRO * FPS)]
    idx = write_sequence("intro", intro_frames, idx)

    events = [
        ("haldi.JPG", "Haldi Ceremony", "12 December 2026", "Morning · Marigold celebrations", (230, 168, 23), (1.08, 1.05, 0.88)),
        ("victoria.JPG", "Wedding", "13 December 2026", "Sacred vows · New beginnings", (139, 21, 56), (1.12, 0.98, 0.95)),
        ("ghat8.JPG", "Reception", "16 December 2026", "Evening feast · With loved ones", (27, 58, 107), (1.02, 1.02, 1.14)),
    ]
    for file, title, date, sub, bar, tint in events:
        photo = Image.open(PHOTOS / file)
        n = DUR_EVENT * FPS
        ev = [frame_event(photo, title, date, sub, bar, tint, t, n) for t in range(n)]
        idx = write_sequence(file, ev, idx)

    outro = [frame_outro(t, DUR_OUTRO * FPS) for t in range(DUR_OUTRO * FPS)]
    write_sequence("outro", outro, idx)

    total_dur = DUR_INTRO + DUR_EVENT * 3 + DUR_OUTRO
    video_only = OUT / "invite-video-only.mp4"
    invite = OUT / "invite.mp4"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(TMP / "frame_%05d.jpg"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            str(video_only),
        ],
        check=True,
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_only),
            "-i",
            str(OUT / "song.m4a"),
            "-filter_complex",
            f"[1:a]atrim=0:{total_dur},asetpts=PTS-STARTPTS[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(invite),
        ],
        check=True,
    )
    print(f"Created {invite} ({total_dur}s)")


if __name__ == "__main__":
    main()
