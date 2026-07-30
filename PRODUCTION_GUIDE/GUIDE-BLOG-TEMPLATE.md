# Guide rapide - Publier un article blog

## 1) Creer une nouvelle page article

1. Duplique `blog/TEMPLATE-ARTICLE.html`.
2. Renomme le fichier, par exemple `blog/mon-sujet-2026.html`.
3. Ouvre le fichier et modifie:
   - `<title>`
   - la date dans `Blog · ...`
   - les tags (blocs `article-tag`)
   - le titre `h1`
   - le texte
   - les images (`src` + `alt` + `figcaption`)

## 2) Ajouter une carte dans la liste du blog

Ouvre `blog.html` et ajoute un bloc `article` dans `#blog-list` en haut de la liste.

Champs importants:
- `data-date="YYYY-MM-DD"` -> sert au tri du plus recent au plus ancien
- `data-keywords="mot1,mot2"` -> sert au filtre
- `href="blog/mon-sujet-2026.html"` -> lien vers ton article

## 3) Ajouter un nouveau mot-cle au filtre (si besoin)

Dans `blog.html`, dans la zone des boutons de filtre:

```html
<button class="keyword-btn" type="button" data-keyword="nouveau-mot">Nouveau mot</button>
```

Le `data-keyword` du bouton doit etre identique aux mots dans `data-keywords` des cartes.

## 4) Ajouter tes images

Place tes images dans `assets/img/`, par exemple:
- `assets/img/article-2026-cover.jpg`
- `assets/img/article-2026-graph-1.png`

Puis reference-les dans ton article avec:

```html
<img src="../assets/img/article-2026-cover.jpg" alt="Description image">
```

## 5) Publier

```powershell
cd C:\RENAULT\SITE_GITHUB_PAGES
git add .
git commit -m "Add new blog article"
git push
```

## 6) Verifier en ligne

- Ouvre `https://cameron-silva.fr/blog.html`
- Fais `Ctrl+F5` si la nouvelle version n'apparait pas

## 7) Version anglaise (en/blog/)

Chaque note doit avoir un miroir anglais pour que le site reste bilingue:

1. Duplique ton fichier FR fini et place-le dans `en/blog/nom-en-anglais.html`
   (le nom de fichier peut differer du FR, ex: `deficit-public-et-donnees.html` ->
   `public-deficit-and-data.html`).
2. Traduis le contenu (title, meta description, eyebrow, h1, lead, paragraphes).
3. Verifie les 2 liens `.lang-switch` (FR -> EN et EN -> FR) pointent bien l'un vers
   l'autre avec le bon chemin relatif.
4. Ajoute une carte dans `en/blog.html` (`#blog-list`), memes champs data-date/data-keywords
   qu'en FR mais avec des mots-cles en anglais (`publicpolicy` au lieu de `politiquespubliques`).

## 8) Mettre a jour la page d'accueil

Dans `index.html` (et `en/index.html`), la section "Dernieres notes" (`.overview-list`) est une
liste statique des 3 notes les plus recentes. Ajoute/retire un `<li><a class="text-link"
href="blog/...">Titre</a></li>` pour que la home reste a jour, dans les 2 langues.

## 9) Bonnes pratiques SEO / partage deja en place a reprendre

Chaque page du site a deja: un favicon (`<link rel="icon" ... href=".../assets/img/favicon.svg">`),
des balises Open Graph/Twitter Card, et les articles ont un lien `rel="alternate"` vers le flux RSS
(`rss-fr.xml` / `rss-en.xml`). Pour une nouvelle note, copie ces balises depuis un article existant
(`blog/deficit-public-et-donnees.html` par exemple) et adapte titre/description/url/date.

Pense aussi a:
- Ajouter un temps de lecture estime dans l'eyebrow (`· 3 min de lecture`).
- Ajouter un lien "note precedente / suivante" (`.article-pager`) en bas de chaque article, et
  mettre a jour ceux des notes voisines en consequence.
- Ajouter la nouvelle note dans `sitemap.xml` et dans `rss-fr.xml`/`rss-en.xml`.
