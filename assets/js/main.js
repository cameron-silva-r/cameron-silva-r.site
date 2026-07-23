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

const filterButtons = document.querySelectorAll('.filter-btn');
const projectRows = document.querySelectorAll('.project-row');

if (filterButtons.length > 0 && projectRows.length > 0) {
  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.getAttribute('data-filter');

      filterButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');

      projectRows.forEach((row) => {
        const status = row.getAttribute('data-status');
        const shouldShow = target === 'all' || status === target;
        row.classList.toggle('is-hidden', !shouldShow);
      });
    });
  });
}

