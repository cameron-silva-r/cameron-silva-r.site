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

- Ouvre `https://cameron-silva-r.github.io/cameron-silva-r.site/blog.html`
- Fais `Ctrl+F5` si la nouvelle version n'apparait pas
