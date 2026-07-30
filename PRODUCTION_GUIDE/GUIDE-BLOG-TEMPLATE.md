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

Le template (`PRODUCTION_GUIDE/TEMPLATE-ARTICLE.html`) contient deja tous les blocs ci-dessous
avec des valeurs a remplacer (`NOM-DU-FICHIER`, dates, titres...). Verifie que tu as bien adapte
chacun d'eux avant de publier une nouvelle note:

- Favicon (`<link rel="icon" ...>`) : deja bon, ne change pas.
- Open Graph / Twitter Card (`og:title`, `og:description`, `og:url`, `twitter:title`,
  `twitter:description`) : a adapter au titre/description de ta note.
- `<link rel="canonical">` + les 3 `<link rel="alternate" hreflang="...">` (fr/en/x-default) :
  remplace l'URL FR et l'URL EN par les vrais chemins de ta note (une fois le miroir EN cree).
- `<link rel="alternate" type="application/rss+xml">` : deja bon, ne change pas.
- Le bloc `<script type="application/ld+json">` (JSON-LD `BlogPosting`) : adapte `headline`,
  `datePublished`, `url`, `description` (`inLanguage` reste `"fr"` ou passe a `"en"` pour le
  miroir anglais).
- Le temps de lecture estime dans l'eyebrow (`· X min de lecture`).
- Les 2 liens de partage LinkedIn/X (`.article-share`) : remplace l'URL encodee par celle de ta
  note (encode juste `:` en `%3A` et `/` en `%2F`).
- La section "Notes liees" (`.article-related`) : liste 1-2 autres notes qui partagent un
  mot-cle avec celle-ci (`data-keywords` dans `blog.html`).
- Le lien "note precedente / suivante" (`.article-pager`) : facultatif, a mettre a jour aussi sur
  les notes voisines en consequence.
- Ajouter la nouvelle note dans `sitemap.xml` et dans `rss-fr.xml`/`rss-en.xml`.

## 10) Transparence du code (pour les notes avec analyse de donnees)

Pour une note qui presente le resultat d'un script (Python/R), le template inclut un petit bouton
optionnel "Voir le code" (`.code-toggle`) en haut de l'article, a cote des mots-cles, a garder
uniquement si tu as un vrai script a montrer:

1. Place ton script dans `assets/code/` (ex: `assets/code/mon-analyse.py`).
2. Colle le vrai code dans le bloc `<pre><code>` du template (echappe `<` et `>` en `&lt;`/`&gt;`
   s'il y en a dans le code, par exemple pour des comparaisons).
3. Le bloc `<details class="code-toggle">` affiche/masque le code au clic, sans JavaScript.
4. Adapte le `href` du bouton "Telecharger le script" vers ton fichier dans `assets/code/`.
5. Si la note n'a pas de code a montrer, supprime tout le bloc `<details class="code-toggle">`.

