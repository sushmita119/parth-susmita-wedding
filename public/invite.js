const refBg = document.getElementById('ref-bg');
const audio = document.getElementById('audio');
const playBtn = document.getElementById('play-btn');
const overlays = [...document.querySelectorAll('.overlay[data-from]')];
const DURATION = 21.2;

function updateOverlays(t) {
  overlays.forEach((el) => {
    const from = parseFloat(el.dataset.from);
    const to = parseFloat(el.dataset.to);
    el.classList.toggle('visible', t >= from && t < to);
  });
}

function tick() {
  const t = refBg.currentTime;
  updateOverlays(t);
  if (!refBg.paused) requestAnimationFrame(tick);
}

async function playAll() {
  playBtn.classList.add('hidden');
  refBg.muted = true;
  refBg.currentTime = 0;
  audio.currentTime = 0;
  try {
    await Promise.all([refBg.play(), audio.play()]);
    requestAnimationFrame(tick);
  } catch {
    playBtn.classList.remove('hidden');
  }
}

refBg.addEventListener('timeupdate', () => updateOverlays(refBg.currentTime));

refBg.addEventListener('ended', () => {
  overlays.forEach((el) => el.classList.remove('visible'));
});

playBtn.addEventListener('click', playAll);

if (new URLSearchParams(location.search).has('record')) {
  document.body.classList.add('record');
  refBg.muted = true;
  playBtn.click();
}
