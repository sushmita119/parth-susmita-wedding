#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PHOTOS="$ROOT/public/assets/photos"
OUT="$ROOT/public/assets"
TMP="$ROOT/output"
FONT="/System/Library/Fonts/Supplemental/Georgia.ttf"
DUR_INTRO=4
DUR_EVENT=9
FPS=30

mkdir -p "$TMP"

make_intro() {
  local frames=$((DUR_INTRO * FPS))
  ffmpeg -y -f lavfi -i "color=c=0x3d0f1a:s=1080x1920:d=$DUR_INTRO" \
    -vf "
      drawbox=x=0:y=0:w=iw:h=140:color=0xD4AF37@0.85:t=fill,
      drawbox=x=0:y=ih-140:w=iw:h=140:color=0xD4AF37@0.85:t=fill,
      drawtext=fontfile=${FONT}:text='Save The Date':fontsize=78:fontcolor=white:x=(w-text_w)/2:y=h*0.38:borderw=2:bordercolor=0x8B0000,
      drawtext=fontfile=${FONT}:text='Parth \& Susmita':fontsize=96:fontcolor=0xFFD700:x=(w-text_w)/2:y=h*0.48:font=bold,
      drawtext=fontfile=${FONT}:text='Together with their families':fontsize=40:fontcolor=0xFFE4C4:x=(w-text_w)/2:y=h*0.58,
      drawtext=fontfile=${FONT}:text='cordially invite you':fontsize=40:fontcolor=0xFFE4C4:x=(w-text_w)/2:y=h*0.62,
      drawtext=fontfile=${FONT}:text='Siliguri • West Bengal':fontsize=36:fontcolor=white@0.9:x=(w-text_w)/2:y=h*0.72
    " -c:v libx264 -pix_fmt yuv420p -r "$FPS" "$TMP/00-intro.mp4"
}

make_event() {
  local img="$1"
  local title="$2"
  local date="$3"
  local subtitle="$4"
  local tint="$5"
  local border="$6"
  local out="$7"
  local frames=$((DUR_EVENT * FPS))

  ffmpeg -y -loop 1 -i "$img" -t "$DUR_EVENT" \
    -vf "
      scale=1280:1920:force_original_aspect_ratio=increase,crop=1080:1920,
      zoompan=z='if(lte(on,${frames}),min(1.02+on*0.00018,1.14),1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${frames}:s=1080x1920:fps=${FPS},
      ${tint},
      drawbox=x=0:y=0:w=iw:h=130:color=${border}@0.78:t=fill,
      drawbox=x=0:y=ih-130:w=iw:h=130:color=${border}@0.78:t=fill,
      drawbox=x=40:y=180:w=iw-80:h=ih-360:color=black@0.0:t=3,
      drawtext=fontfile=${FONT}:text='${title}':fontsize=76:fontcolor=white:x=(w-text_w)/2:y=200:borderw=3:bordercolor=black@0.35,
      drawtext=fontfile=${FONT}:text='${date}':fontsize=58:fontcolor=0xFFD700:x=(w-text_w)/2:y=290,
      drawtext=fontfile=${FONT}:text='${subtitle}':fontsize=38:fontcolor=0xFFF8E7:x=(w-text_w)/2:y=360,
      drawtext=fontfile=${FONT}:text='Parth \& Susmita':fontsize=46:fontcolor=white:x=(w-text_w)/2:y=h-220:borderw=2:bordercolor=0x8B4513
    " -c:v libx264 -pix_fmt yuv420p -r "$FPS" "$out"
}

make_intro

make_event "$PHOTOS/haldi.JPG" "Haldi Ceremony" "12 December 2026" "Morning • Marigold celebrations" \
  "eq=saturation=1.35:brightness=0.06:contrast=1.05, colorbalance=rs=0.08:gs=0.05:bs=-0.12" "0xE6A817" "$TMP/01-haldi.mp4"

make_event "$PHOTOS/victoria.JPG" "Wedding" "13 December 2026" "Sacred vows • New beginnings" \
  "eq=saturation=1.25:contrast=1.08, colorbalance=rs=0.14:gs=-0.02:bs=-0.05" "0x8B1538" "$TMP/02-wedding.mp4"

make_event "$PHOTOS/ghat8.JPG" "Reception" "16 December 2026" "Evening feast • With loved ones" \
  "eq=saturation=1.15:brightness=-0.03, colorbalance=rs=0.05:gs=0.02:bs=0.12" "0x1B3A6B" "$TMP/03-reception.mp4"

make_outro() {
  ffmpeg -y -f lavfi -i "color=c=0x1a0a14:s=1080x1920:d=4" \
    -vf "
      drawbox=x=0:y=0:w=iw:h=140:color=0xD4AF37@0.85:t=fill,
      drawtext=fontfile=${FONT}:text='Your presence is our blessing':fontsize=46:fontcolor=0xFFD700:x=(w-text_w)/2:y=h*0.42,
      drawtext=fontfile=${FONT}:text='Parth \& Susmita':fontsize=88:fontcolor=white:x=(w-text_w)/2:y=h*0.52,
      drawtext=fontfile=${FONT}:text='See you in Siliguri':fontsize=42:fontcolor=0xFFE4C4:x=(w-text_w)/2:y=h*0.62
    " -c:v libx264 -pix_fmt yuv420p -r "$FPS" "$TMP/04-outro.mp4"
}

make_outro

cat > "$TMP/concat.txt" <<EOF
file '${TMP}/00-intro.mp4'
file '${TMP}/01-haldi.mp4'
file '${TMP}/02-wedding.mp4'
file '${TMP}/03-reception.mp4'
file '${TMP}/04-outro.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "$TMP/concat.txt" -c copy "$TMP/video-only.mp4"

TOTAL_DUR=$((DUR_INTRO + DUR_EVENT * 3 + 4))
ffmpeg -y -i "$TMP/video-only.mp4" -i "$OUT/song.m4a" \
  -filter_complex "[1:a]atrim=0:${TOTAL_DUR},asetpts=PTS-STARTPTS[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "$OUT/invite.mp4"

echo "Wrote $OUT/invite.mp4 (${TOTAL_DUR}s)"
