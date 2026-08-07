# elia-apps.github.io

The **public marketing and application-information site** for Elia — a small
family of calm, private, offline-first apps for birth, the early days with your
baby, and the childhood years that follow.

Live at **https://getelia.app** (custom domain; also served at https://elia-apps.github.io)

## Role in the Elia ecosystem

This repository is the **public presentation layer of the Elia ecosystem** — and
only that. It is **not an Elia Platform client**: it has no Elia Account login,
no authenticated user area, no access to user, family, child, or synchronized
application data, no Premium or billing management, no synchronization, and no
backend. It handles no private family data, and has **no current runtime
dependency on Elia Platform**.

- **Application implementation** — data models, business rules, app behavior —
  lives in the private application repositories, not here.
- **Shared account, family, Premium, synchronization, cloud, and security
  architecture** live in the private Elia Platform repository.
- **A platform-facing web client is not approved and not planned.** It would
  require a separate product and architecture decision.

See [`docs/elia-ecosystem.md`](docs/elia-ecosystem.md) for the full boundary,
the applications represented here, and documentation ownership.

## Generated site — do not hand-edit the HTML

Every `.html` file in this repository is **generated** by
`tools/generate_i18n.py`, including the English pages at the root. Editing HTML
directly will be silently overwritten the next time the generator runs.

To change any content, copy, or metadata: edit `tools/generate_i18n.py`, then

```bash
python3 tools/generate_i18n.py
```

The generator also writes `sitemap.xml`.

## Structure

```
.
├── index.html              # Landing page (generated)
├── 404.html                # Not-found page (generated)
├── apps/
│   ├── contractions/       # Overview + privacy/ + support/
│   ├── feeding/            # Overview + privacy/ + support/
│   └── moments/            # Overview + privacy/ + support/
├── de/, es/                # Full localized copies of the above
├── assets/
│   ├── css/styles.css      # Shared design system (light + dark)
│   └── img/                # Logo, per-app icons, screenshots
├── docs/
│   └── elia-ecosystem.md   # Role, boundaries, related repositories
├── tools/
│   └── generate_i18n.py    # Source of truth for all pages
├── CNAME                   # Custom domain (getelia.app)
├── robots.txt              # Crawling + sitemap reference
├── sitemap.xml             # Generated
└── .nojekyll               # Serve files as-is (no Jekyll processing)
```

## Design

Plain HTML/CSS/JS — no build step and no dependencies. Colors, tone, and copy
follow the Elia brand and design docs held in the application repositories. The
palette and dark mode live as CSS custom properties in `assets/css/styles.css`;
each app page overrides the accent (Contractions = rose, Feeding = honey,
Moments = sage).

## Adding a new app

1. Add its copy to the `T`, `APP`, and `SUPPORT` tables in
   `tools/generate_i18n.py`, in every supported language.
2. Add the route to the `routes` list in `sitemap()` and to the page loop at the
   bottom of the generator.
3. Add icons to `assets/img/`, and screenshots to
   `assets/img/shots/<app>/en/` if available.
4. Run `python3 tools/generate_i18n.py`.

## Local preview

Any static server works, e.g.:

```
python3 -m http.server 8000
```

Then open http://localhost:8000
