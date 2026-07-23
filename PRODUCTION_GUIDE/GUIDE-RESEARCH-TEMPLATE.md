# Guide rapide - Publier un Research Project

## 1) Creer la page detail du projet

1. Duplique `projects/TEMPLATE-RESEARCH-PROJECT.html`.
2. Renomme le fichier, par exemple `projects/mon-projet-2026.html`.
3. Remplis les champs (titre, date, tags, resume, sections).
4. Mets tes images dans `assets/img/` et tes PDF dans `assets/docs/`.

## 2) Ajouter le projet dans la page Research Projects

Ouvre `projects.html`, puis ajoute une carte dans:
- colonne gauche: `En cours`
- colonne droite: `Termines`

Dans la carte, selon disponibilite:
- PDF dispo: lien `Telecharger le PDF`
- PDF non dispo: `PDF non disponible`
- Code dispo: lien `Code open-source`
- Code non dispo: `Code open-source non disponible`

## 3) Ajouter un lien vers la page detail (optionnel)

Dans la carte projet, ajoute:

```html
<a class="text-link" href="projects/mon-projet-2026.html">Voir le projet</a>
```

## 4) Publier

```powershell
cd C:\RENAULT\SITE_GITHUB_PAGES
git add .
git commit -m "Add research project"
git push
```

## 5) Verifier en ligne

- `https://cameron-silva-r.github.io/cameron-silva-r.site/projects.html`
- `Ctrl+F5` si cache navigateur
