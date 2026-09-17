# Raghav Awasthi — portfolio

Live at **https://raghav2005.github.io/**.

A fast, accessible, static portfolio with experience, projects, writing, open-source contributions, education, skills, leadership, and press. Plain HTML and CSS; no JavaScript, application server, or runtime dependencies. Python 3.10+ builds the pages using the standard library.

## The CV is the source of truth

Experience, project achievements, education, skills, and leadership are imported directly from [`raghav2005/cv`](https://github.com/raghav2005/cv):

- `master-resume/content.tex` — every role, project, skill group, and leadership bullet.
- `shared/education.tex` — education.
- `master-resume/Resume.pdf` — the downloadable complete résumé.

The importer reads the existing LaTeX macros; it does not execute LaTeX. It rejects unsupported syntax instead of quietly dropping content. Every imported bullet is checked against the rendered pages. Content is HTML-escaped.

The site refreshes from the CV's `main` branch and the public QPG blog on each deployment and daily at approximately 06:17 UTC (GitHub may delay scheduled runs). Push CV source and its rebuilt PDF to the CV repository to publish updates. Local, uncommitted CV edits are not visible to GitHub Actions. For an immediate refresh, run **Build and deploy portfolio** in this repository's Actions tab.

The initial master source and PDF were published separately from unrelated in-progress CV edits. The résumé download reflects the PDF committed in the CV repository: rebuild it when editing the LaTeX. This website does not compile TeX or modify the CV repository.

The QPG RSS feed supplies new articles. Its sitemap is checked for missing archived posts; already known older posts are retained. The Emacs article is included explicitly. A failed import stops deployment and leaves the previous live site intact. No secrets or cross-repository write token are needed.

## Local editing

```sh
# Use the latest committed snapshots (offline).
python3 scripts/build.py
python3 scripts/validate.py
python3 -m http.server 4173 --directory dist

# Refresh from the published CV and blog.
python3 scripts/sync_content.py --remote

# Import a local CV working copy (including unpublished edits).
python3 scripts/sync_content.py --cv-dir /path/to/cv
```

`data/resume.json` and `data/writing.json` are committed snapshots for offline builds; hosted builds refresh them before rendering. `data/links.json` holds verified project links, extra public projects, and contribution links. Add future project URL overrides there, keyed by the exact résumé project name. New CV projects and roles appear without template edits. The two homepage feature cards are editorial selections.

`src/home.html`, `src/layout.html`, and `src/style.css` control presentation; `scripts/build.py` renders the archive and home sections. Personal introductory copy, contact links, and press context live in the templates/build script and should be reviewed when those facts change. There are no tracking scripts, cookie banners, or contact-form services.

## Deployment

GitHub Pages uses **GitHub Actions**. `.github/workflows/pages.yml` refreshes content, builds `dist/`, verifies coverage and internal links, and deploys it. Pull requests only build and validate the committed snapshots and cannot deploy. The output includes per-page metadata, canonical URLs, a sitemap, robots.txt, a favicon, and a 404 page.

Public source files, PDFs, and blog content remain copyright their respective authors.
