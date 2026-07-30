const mainEl = document.querySelector('main');
if (mainEl && !mainEl.id) {
  mainEl.id = 'main-content';
}
if (mainEl) {
  const isEnglish = document.documentElement.lang === 'en';
  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.className = 'skip-link';
  skipLink.textContent = isEnglish ? 'Skip to main content' : 'Aller au contenu principal';
  document.body.insertBefore(skipLink, document.body.firstChild);
}

const toggleButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');

if (toggleButton && nav) {
  const closeNav = () => {
    toggleButton.setAttribute('aria-expanded', 'false');
    nav.classList.remove('open');
  };

  toggleButton.addEventListener('click', () => {
    const expanded = toggleButton.getAttribute('aria-expanded') === 'true';
    toggleButton.setAttribute('aria-expanded', String(!expanded));
    nav.classList.toggle('open');
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      closeNav();
      toggleButton.focus();
    }
  });

  document.addEventListener('click', (event) => {
    const isOpen = nav.classList.contains('open');
    const clickedInsideNav = nav.contains(event.target) || toggleButton.contains(event.target);
    if (isOpen && !clickedInsideNav) {
      closeNav();
    }
  });
}

const revealTargets = document.querySelectorAll('.panel, .hero-card, .page-intro');
revealTargets.forEach((el) => el.classList.add('reveal'));

const blogList = document.querySelector('#blog-list');
const keywordButtons = document.querySelectorAll('.keyword-btn');

if (blogList) {
  const cards = Array.from(blogList.querySelectorAll('.blog-post-card'));

  cards.sort((a, b) => {
    const da = new Date(a.getAttribute('data-date') || '1900-01-01').getTime();
    const db = new Date(b.getAttribute('data-date') || '1900-01-01').getTime();
    return db - da;
  });

  cards.forEach((card) => blogList.appendChild(card));

  if (keywordButtons.length > 0) {
    keywordButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const targetKeyword = button.getAttribute('data-keyword') || 'all';

        keywordButtons.forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');

        cards.forEach((card) => {
          const words = (card.getAttribute('data-keywords') || '')
            .split(',')
            .map((word) => word.trim());

          const shouldShow = targetKeyword === 'all' || words.includes(targetKeyword);
          card.classList.toggle('is-hidden', !shouldShow);
        });
      });
    });
  }
}

