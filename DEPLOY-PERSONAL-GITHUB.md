# Host on personal GitHub only → switch back to Alef on this Mac

**Personal account:** `sushmita119`  
**Work account (default on this machine after you’re done):** `sushmita-mukherjee-alef`  
**Do not use Alef GitHub for this site.**

## What you want

1. Website lives on **personal** GitHub (Pages).
2. After push, **this Mac** uses **Alef** again for `gh` / day-to-day repos.

Netlify ([cool-licorice-d7909f.netlify.app](https://cool-licorice-d7909f.netlify.app/)) is optional backup; you can ignore it once Pages works.

---

## Step 1 — Add personal GitHub once (browser only)

Do **not** paste your password in Terminal. Use GitHub’s browser login.

```bash
gh auth login -h github.com
```

Choose:

- GitHub.com  
- HTTPS  
- **Login with a web browser**  
- Complete login as **`sushmita119`**  
- If Alef is already logged in, pick **“Add account”** (second account), not “Log out”

Make personal account active **only for deploy**:

```bash
gh auth switch -h github.com -u sushmita119
gh auth status   # should show sushmita119 as active
```

---

## Step 2 — Create repo, push, enable Pages

From the wedding folder:

```bash
cd /Users/sushmitamukherjee/Documents/services/wedding
chmod +x scripts/deploy-personal-github.sh
./scripts/deploy-personal-github.sh
```

Or manually:

```bash
gh repo create parth-susmita-wedding --public --source=. --remote=origin --push
```

Live URL (after workflow runs):

**https://sushmita119.github.io/parth-susmita-wedding/**

Workflow file: `.github/workflows/pages.yml` (publishes `public/`).

---

## Step 3 — Log out of personal on this machine (use Alef again)

You stay logged in to **both** accounts in the keyring, but **active** account should be Alef:

```bash
./scripts/switch-back-alef-github.sh
# or: gh auth switch -h github.com -u sushmita-mukherjee-alef
```

Confirm:

```bash
gh auth status   # Active: sushmita-mukherjee-alef
```

**Optional — remove personal from this Mac entirely** (site still works on GitHub; you update site later by logging in as personal again or using GitHub.com in the browser):

```bash
gh auth logout -h github.com -u sushmita119
```

---

## Updating the site later

1. Edit files under `public/`, commit on `main`.
2. Temporarily: `gh auth switch -u sushmita119` → `git push origin main` → switch back to Alef.  
   Or push from [github.com](https://github.com) (upload/edit) without touching CLI auth.

---

## Security note

If a GitHub password was ever shared in chat, **change it** at GitHub → Settings → Password. Use browser or PAT for CLI, never share passwords in messages.
