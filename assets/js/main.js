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
