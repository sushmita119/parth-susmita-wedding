const WEDDING_UTC = Date.UTC(2026, 11, 13, 5, 30, 0); // 13 Dec 2026, morning IST rough anchor

function initCountdown() {
  const root = document.getElementById('countdown');
  if (!root) return;

  function tick() {
    const now = Date.now();
    const diff = Math.max(0, WEDDING_UTC - now);
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const mins = Math.floor((diff / (1000 * 60)) % 60);
    const secs = Math.floor((diff / 1000) % 60);

    root.innerHTML = [
      { v: days, l: 'Days' },
      { v: hours, l: 'Hours' },
      { v: mins, l: 'Mins' },
      { v: secs, l: 'Secs' },
    ]
      .map(
        ({ v, l }) =>
          `<div class="countdown-item"><strong>${v}</strong><span>${l}</span></div>`
      )
      .join('');
  }

  tick();
  setInterval(tick, 1000);
}

function initReveal() {
  const items = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );
  items.forEach((el) => io.observe(el));
}

function initNav() {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('nav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    const open = !nav.classList.contains('is-open');
    nav.classList.toggle('is-open', open);
    document.body.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  });

  nav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('is-open');
      document.body.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
}

initCountdown();
initReveal();
initNav();

// Hero visible on load
document.querySelectorAll('.hero .reveal').forEach((el) => {
  requestAnimationFrame(() => el.classList.add('is-visible'));
});
