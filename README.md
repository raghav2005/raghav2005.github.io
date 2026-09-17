# Raghav Awasthi — portfolio

Live at **https://raghav2005.github.io/**.

A static portfolio with experience, projects, writing, open-source contributions, education, skills, awards, leadership, press, and hobbies. The browser receives plain HTML and CSS, with no JavaScript, trackers, or application server. The dark palette is inspired by [Tokyo Night](https://github.com/folke/tokyonight.nvim), with brighter text for long-form reading.

## Content sources

The base résumé is imported directly from [`raghav2005/cv`](https://github.com/raghav2005/cv):

- `master-resume/content.tex` — roles, projects, skills, and leadership.
- `shared/education.tex` — education.

`data/profile.json` contains the additional experience, project descriptions, awards, hobbies, and email configuration supplied for the portfolio. `scripts/content.py` merges it with the imported CV. Daily refreshes cannot erase these additions. Exact company/role and project-name matches are deduplicated if an addition later moves into the master CV. Explicit project/leadership refinements are applied after importing the base content; review those overrides if the corresponding CV descriptions change.

The importer reads existing LaTeX macros without executing TeX. Unsupported syntax fails instead of silently dropping content. All rendered text is HTML-escaped. `scripts/validate.py` checks every combined experience/project bullet, education entry, skill group, leadership item, award, and hobby against the generated pages.

## Email and downloadable résumé

All site email links display **raghavawasthi2005@gmail.com** and target **raghavawasthi2005+portfolio-website@gmail.com**. These values live together in `data/profile.json`; the footer uses the same target.

`dist/resume.pdf` is generated from the combined content on every build, using ReportLab. Its visible email and mail link use the same configuration as the website. The portfolio résumé includes the earlier experience, awards, and hobbies, while the original CV repository and its other résumé variants remain unchanged. The PDF is generated output, not a second editable content source.

## Refresh behaviour

The site refreshes from the CV's `main` branch and the public QPG blog on each deployment and daily at approximately 06:17 UTC (GitHub may delay scheduled runs). Push changes to the CV repository to update the base content. Local, uncommitted CV changes are not visible to GitHub Actions. For an immediate refresh, run **Build and deploy portfolio** in this repository's Actions tab.

The QPG RSS feed supplies new articles. Its sitemap is checked for missing archived posts; posts in the committed snapshot are retained. The Emacs article is included explicitly. A failed import or validation leaves the previous live site intact. No secrets or cross-repository write token are needed.

## Local editing

Python 3.10+ is required. Install the pinned PDF build dependency first:

```sh
python3 -m pip install -r requirements.txt

# Build from the committed snapshots, without network access.
python3 scripts/build.py
python3 scripts/validate.py
python3 -m http.server 4173 --directory dist

# Refresh base content from the published CV and blog, then rebuild.
python3 scripts/sync_content.py --remote
python3 scripts/build.py

# Or import a local CV working copy (including unpublished edits).
python3 scripts/sync_content.py --cv-dir /path/to/cv
```

`data/resume.json` and `data/writing.json` are committed snapshots for offline builds. Hosted builds refresh them before rendering. `data/links.json` holds verified project links, extra public projects, and contribution links. Add project URL overrides there, keyed by the exact project name. The two homepage feature cards are editorial selections.

`src/home.html`, `src/layout.html`, and `src/style.css` control presentation; `scripts/build.py` renders the archive and homepage sections. `scripts/build_resume.py` renders the downloadable PDF. Personal introductory copy and press context live in the templates/build script and should be reviewed when those facts change.

## Deployment

GitHub Pages uses **GitHub Actions**. `.github/workflows/pages.yml` installs the PDF dependency, refreshes content, builds `dist/`, checks coverage and internal links, and deploys. Pull requests validate committed snapshots and cannot deploy. The output includes per-page metadata, canonical URLs, a sitemap, robots.txt, a favicon, and a 404 page.

Public source files, PDFs, and blog content remain copyright their respective authors.
