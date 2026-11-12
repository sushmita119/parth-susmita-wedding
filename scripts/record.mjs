import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';
import { execSync } from 'child_process';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicDir = path.join(root, 'public');
const outVideo = path.join(publicDir, 'assets', 'invite.mp4');
const song = path.join(publicDir, 'assets', 'song.m4a');

function audioDurationSec(file) {
  return parseFloat(
    execSync(`ffprobe -v error -show_entries format=duration -of csv=p=0 "${file}"`, { encoding: 'utf8' }).trim()
  );
}

async function main() {
  const audioSec = audioDurationSec(song);
  const recordMs = Math.ceil(Math.min(audioSec, 21.5) * 1000) + 400;

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1080, height: 1920 },
    recordVideo: {
      dir: path.join(root, 'output'),
      size: { width: 1080, height: 1920 },
    },
  });
  const page = await context.newPage();
  await page.goto(`file://${publicDir}/index.html?record=1`);
  await page.waitForTimeout(recordMs);
  await context.close();
  await browser.close();

  const outDir = path.join(root, 'output');
  const webms = fs
    .readdirSync(outDir)
    .filter((f) => f.endsWith('.webm'))
    .map((f) => ({ f, t: fs.statSync(path.join(outDir, f)).mtimeMs }))
    .sort((a, b) => b.t - a.t);
  const webm = path.join(outDir, webms[0].f);
  const muxDur = Math.min(audioSec, recordMs / 1000);

  execSync(
    `ffmpeg -y -i "${webm}" -i "${song}" -filter_complex "[1:a]atrim=0:${muxDur},asetpts=PTS-STARTPTS[a]" -map 0:v -map "[a]" -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "${outVideo}"`,
    { stdio: 'inherit' }
  );
  console.log(`Wrote ${outVideo} (~${muxDur}s full reference reel)`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
