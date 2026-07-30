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

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function formatNoteDate(isoDate) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const parts = String(isoDate || '').split('-').map(Number);
  const [year, month, day] = parts;

  if (!year || !month || !day) {
    return isoDate || '';
  }

  return `${String(day).padStart(2, '0')} ${months[month - 1]} ${year}`;
}

function parseTagLabels(container) {
  try {
    return JSON.parse(container.dataset.tagLabels || '{}');
  } catch (error) {
    return {};
  }
}

function initKeywordFilters(container) {
  const keywordButtons = document.querySelectorAll('.keyword-btn');
  const cards = Array.from(container.querySelectorAll('.blog-post-card'));

  if (keywordButtons.length === 0) {
    return;
  }

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

function renderBlogList() {
  const container = document.querySelector('#blog-list');

  if (!container || !container.dataset.source) {
    return;
  }

  fetch(container.dataset.source)
    .then((response) => response.json())
    .then((notes) => {
      const assetsBase = container.dataset.assets || '';
      const tagLabels = parseTagLabels(container);
      const readLabel = container.dataset.readLabel || 'Read note';

      const sorted = [...notes].sort(
        (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
      );

      if (sorted.length === 0) {
        container.innerHTML = `<p class="muted">${container.dataset.emptyLabel || 'No notes yet.'}</p>`;
        return;
      }

      container.innerHTML = sorted
        .map((note) => {
          const tagText = (note.tags || []).map((tag) => tagLabels[tag] || tag).join(' · ');

          return `
            <article class="panel blog-post-card" data-keywords="${(note.tags || []).join(',')}" data-date="${note.date}">
              <img class="blog-thumb" src="${assetsBase}${note.image}" alt="${escapeHtml(note.title)}">
              <div class="blog-post-body">
                <div class="blog-head-row">
                  <p class="muted">${formatNoteDate(note.date)}</p>
                  <p class="blog-tags">🏷 ${tagText}</p>
                </div>
                <h2>${escapeHtml(note.title)}</h2>
                <p>${escapeHtml(note.summary)}</p>
                <a class="text-link" href="note.html?slug=${encodeURIComponent(note.slug)}">${readLabel}</a>
              </div>
            </article>
          `;
        })
        .join('');

      initKeywordFilters(container);
    })
    .catch(() => {
      container.innerHTML = `<p class="muted">${container.dataset.errorLabel || 'Notes could not be loaded.'}</p>`;
    });
}

function syncNoteLangSwitch(slug) {
  if (!slug) {
    return;
  }

  const frLink = document.querySelector('#lang-switch-fr');
  const enLink = document.querySelector('#lang-switch-en');

  [frLink, enLink].forEach((link) => {
    if (!link) {
      return;
    }
    const base = link.getAttribute('href').split('?')[0];
    link.setAttribute('href', `${base}?slug=${encodeURIComponent(slug)}`);
  });
}

function renderNoteDetail() {
  const container = document.querySelector('#note-detail');

  if (!container || !container.dataset.source) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const slug = params.get('slug');
  const backHref = container.dataset.backHref || 'blog.html';
  const backLabel = container.dataset.backLabel || 'Back to notes';
  const notFoundLabel = container.dataset.notFound || 'Note not found.';

  syncNoteLangSwitch(slug);

  fetch(container.dataset.source)
    .then((response) => response.json())
    .then((notes) => {
      const note = notes.find((item) => item.slug === slug);

      if (!note) {
        container.innerHTML = `
          <p class="lead">${notFoundLabel}</p>
          <p><a class="text-link" href="${backHref}">${backLabel}</a></p>
        `;
        return;
      }

      const tagLabels = parseTagLabels(container);
      const tagsHtml = (note.tags || [])
        .map((tag) => `<span class="article-tag">${escapeHtml(tagLabels[tag] || tag)}</span>`)
        .join('');
      const bodyHtml = (note.body || []).map((paragraph) => `<p>${paragraph}</p>`).join('');
      const eyebrowPrefix = container.dataset.eyebrowPrefix || '';

      container.innerHTML = `
        <div class="article-meta-row">
          <p class="eyebrow">${eyebrowPrefix} ${formatNoteDate(note.date)}</p>
          <div class="article-tags">${tagsHtml}</div>
        </div>
        <h1>${escapeHtml(note.title)}</h1>
        <p class="lead">${note.summary}</p>
        ${bodyHtml}
        <p><a class="text-link" href="${backHref}">${backLabel}</a></p>
      `;

      const titleParts = document.title.split('|');
      const suffix = titleParts.length > 1 ? titleParts.slice(1).join('|').trim() : document.title;
      document.title = `${note.title} | ${suffix}`;
    })
    .catch(() => {
      container.innerHTML = `<p class="lead">${notFoundLabel}</p>`;
    });
}

function renderHomeNotes() {
  const container = document.querySelector('#home-notes-list');

  if (!container || !container.dataset.source) {
    return;
  }

  const limit = Number(container.dataset.limit || '3');

  fetch(container.dataset.source)
    .then((response) => response.json())
    .then((notes) => {
      const sorted = [...notes].sort(
        (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
      );

      if (sorted.length === 0) {
        container.innerHTML = `<li class="muted">${container.dataset.emptyLabel || 'No notes yet.'}</li>`;
        return;
      }

      container.innerHTML = sorted
        .slice(0, limit)
        .map(
          (note) => `
            <li><a class="text-link" href="note.html?slug=${encodeURIComponent(note.slug)}">${escapeHtml(note.title)}</a></li>
          `
        )
        .join('');
    })
    .catch(() => {
      container.innerHTML = `<li class="muted">${container.dataset.errorLabel || 'Notes could not be loaded.'}</li>`;
    });
}

renderBlogList();
renderNoteDetail();
renderHomeNotes();

