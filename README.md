# Parth & Susmita — wedding website

Static site in `public/`. Events: Haldi (12 Dec), Wedding (13 Dec), Reception (16 Dec) 2026 — Siliguri.

## Local preview

```bash
npm start
```

Open http://localhost:3456

## Deploy (GitHub Pages — free URL)

Push to `main`; the workflow publishes `public/` to GitHub Pages.

First-time setup:

```bash
git init
git add .
git commit -m "feat: wedding website"
gh repo create parth-susmita-wedding --public --source=. --remote=origin --push
gh api repos/{owner}/parth-susmita-wedding/pages -X POST -f build_type=workflow
```

Live site: `https://<github-username>.github.io/parth-susmita-wedding/`

## Video build (optional)

```bash
npm run build:video
```
