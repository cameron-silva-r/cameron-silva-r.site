# Site GitHub Pages - Cameron Silva

Ce dossier contient un site statique pret pour GitHub Pages.

## Pages incluses

- Accueil (`index.html`)
- CV (`cv.html`)
- Research Projects (`projects.html`)
- Blog (`blog.html`)
- Contact me (`contact.html`)

## Lancer en local (option simple)

Double-clique `index.html`, ou utilise un serveur local:

```powershell
cd C:\RENAULT\SITE_GITHUB_PAGES
python -m http.server 8000
```

Puis ouvre `http://localhost:8000`.

## Publier sur GitHub Pages

### Option A - Branche principale (root)

1. Place le contenu de ce dossier a la racine de ton repo GitHub (ou adapte selon ton organisation).
2. Sur GitHub: `Settings` > `Pages`.
3. Dans `Build and deployment`, choisis:
   - Source: `Deploy from a branch`
   - Branch: `main` et dossier `/ (root)`
4. Sauvegarde. Ton site sera en ligne en quelques minutes.

### Option B - Dossier `/docs`

1. Copie le contenu dans un dossier `docs/` a la racine du repo.
2. Dans GitHub Pages, choisis `main` et dossier `/docs`.
3. Sauvegarde.

## Personnalisation rapide

- Modifie le nom, email et liens sociaux dans les pages HTML.
- Edite les couleurs dans `assets/css/styles.css` via les variables `:root`.
- Remplace les sections de contenu par ton CV/projets/billets reels.
