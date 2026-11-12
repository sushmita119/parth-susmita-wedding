const WEDDING_UTC = Date.UTC(2026, 11, 13, 5, 30, 0);

function initCountdown() {
  const root = document.getElementById('countdown');
  if (!root) return;

  function tick() {
    const diff = Math.max(0, WEDDING_UTC - Date.now());
    const days = Math.floor(diff / 86400000);
    const hours = Math.floor((diff / 3600000) % 24);
    const mins = Math.floor((diff / 60000) % 60);
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
  document.querySelectorAll('.reveal[data-delay]').forEach((el) => {
    el.style.setProperty('--delay', el.dataset.delay || '0');
  });

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: '0px 0px -30px 0px' }
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

function initHeader() {
  const header = document.getElementById('header');
  const hero = document.querySelector('.hero');
  if (!header || !hero) return;

  const onScroll = () => {
    const threshold = hero.offsetHeight * 0.35;
    header.classList.toggle('is-scrolled', window.scrollY > threshold);
  };

  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

function initParallax() {
  const photo = document.getElementById('hero-photo');
  const hero = document.querySelector('.hero');
  if (!photo || !hero) return;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  window.addEventListener(
    'scroll',
    () => {
      const rect = hero.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > window.innerHeight) return;
      const progress = -rect.top / (hero.offsetHeight || 1);
      const scale = 1.08 + progress * 0.12;
      const y = progress * 40;
      photo.style.transform = `scale(${scale}) translateY(${y}px)`;
    },
    { passive: true }
  );
}

function initPetals() {
  const root = document.getElementById('petals');
  if (!root || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const count = window.innerWidth < 640 ? 12 : 22;
  for (let i = 0; i < count; i++) {
    const p = document.createElement('span');
    p.className = 'petal';
    p.style.left = `${Math.random() * 100}%`;
    p.style.animationDuration = `${14 + Math.random() * 18}s`;
    p.style.animationDelay = `${Math.random() * -20}s`;
    p.style.width = `${6 + Math.random() * 8}px`;
    p.style.height = `${8 + Math.random() * 10}px`;
    root.appendChild(p);
  }
}

initCountdown();
initReveal();
initNav();
initHeader();
initParallax();
initPetals();

requestAnimationFrame(() => {
  document.querySelectorAll('.hero .reveal').forEach((el) => el.classList.add('is-visible'));
});
