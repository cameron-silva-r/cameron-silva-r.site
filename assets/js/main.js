const toggleButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');

if (toggleButton && nav) {
  toggleButton.addEventListener('click', () => {
    const expanded = toggleButton.getAttribute('aria-expanded') === 'true';
    toggleButton.setAttribute('aria-expanded', String(!expanded));
    nav.classList.toggle('open');
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

