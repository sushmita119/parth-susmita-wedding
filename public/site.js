const WEDDING_UTC = Date.UTC(2026, 11, 13, 5, 30, 0);

const audio = document.getElementById('bg-music');
/** In-file seek (0 when audio file is pre-trimmed to the lyric). */
const LYRICS_OFFSET_SEC = audio ? Number.parseFloat(audio.dataset.lyricsOffset || '0') : 0;
const curtain = document.getElementById('curtain');
const enterSite = document.getElementById('enter-site');
const musicFab = document.getElementById('music-fab');
const header = document.getElementById('header');
const coverImg = document.getElementById('cover-img');

function seekToLyrics() {
  if (!audio || !Number.isFinite(LYRICS_OFFSET_SEC)) return;
  if (LYRICS_OFFSET_SEC <= 0) {
    audio.currentTime = 0;
    return;
  }
  audio.currentTime = LYRICS_OFFSET_SEC;
}

function initMusicLoopGuard() {
  if (!audio || LYRICS_OFFSET_SEC <= 0) return;

  audio.addEventListener('timeupdate', () => {
    if (audio.paused || audio.seeking) return;
    if (audio.currentTime < LYRICS_OFFSET_SEC - 0.35) {
      audio.currentTime = LYRICS_OFFSET_SEC;
    }
  });
}

function initCountdown() {
  const root = document.getElementById('countdown');
  if (!root) return;

  const tick = () => {
    const diff = Math.max(0, WEDDING_UTC - Date.now());
    const days = Math.floor(diff / 86400000);
    const hours = Math.floor((diff / 3600000) % 24);
    const mins = Math.floor((diff / 60000) % 60);
    const secs = Math.floor((diff / 1000) % 60);

    root.innerHTML = [days, hours, mins, secs]
      .map((v, i) => {
        const labels = ['Days', 'Hours', 'Mins', 'Secs'];
        return `<div class="countdown-item"><strong>${v}</strong><span>${labels[i]}</span></div>`;
      })
      .join('');
  };

  tick();
  setInterval(tick, 1000);
}

function initReveal() {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
}

function initNav() {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('nav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    const open = !nav.classList.contains('is-open');
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  });

  nav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
}

function initHeader() {
  const cover = document.getElementById('cover');
  if (!header || !cover) return;

  const onScroll = () => {
    const past = window.scrollY > cover.offsetHeight * 0.35;
    header.classList.toggle('header--solid', past);
  };

  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

function initParallax() {
  if (!coverImg || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  window.addEventListener(
    'scroll',
    () => {
      const cover = document.getElementById('cover');
      if (!cover) return;
      const rect = cover.getBoundingClientRect();
      if (rect.bottom < 0) return;
      const p = Math.max(0, -rect.top) / (cover.offsetHeight || 1);
      coverImg.style.transform = `scale(${1 + p * 0.06}) translateY(${p * 24}px)`;
    },
    { passive: true }
  );
}

function setMusicPlaying(playing) {
  if (!musicFab) return;
  musicFab.classList.toggle('is-muted', !playing);
  musicFab.setAttribute('aria-pressed', String(playing));
}

async function playMusic(fromLyrics = true) {
  if (!audio) return false;
  if (fromLyrics) seekToLyrics();
  audio.volume = 0.55;
  try {
    await audio.play();
    if (fromLyrics) seekToLyrics();
    setMusicPlaying(true);
    return true;
  } catch {
    setMusicPlaying(false);
    return false;
  }
}

function stopMusic() {
  if (!audio) return;
  audio.pause();
  setMusicPlaying(false);
}

function dismissCurtain(withMusic) {
  document.body.classList.add('is-ready');
  if (curtain) {
    curtain.classList.add('is-hidden');
    curtain.setAttribute('aria-hidden', 'true');
  }
  if (withMusic) void playMusic(true);
  else setMusicPlaying(false);
}

enterSite?.addEventListener('click', () => dismissCurtain(true));

musicFab?.addEventListener('click', async () => {
  if (!audio) return;
  if (audio.paused) await playMusic(true);
  else stopMusic();
});

if (audio) {
  audio.addEventListener('loadedmetadata', () => {
    if (!audio.paused) return;
    seekToLyrics();
  });
}

initMusicLoopGuard();
initCountdown();
initReveal();
initNav();
initHeader();
initParallax();
