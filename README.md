# Spacefruit website

A static, responsive website for Spacefruit, hosted on GitHub Pages. No paid hosting, build service, database or API key is required. The site uses the four creator-supplied Kickstarter images, with optimized WebP copies and full PNG originals for the image viewer.

## Edit your story and Kickstarter link

Open [site-content.json](site-content.json) in GitHub and click the pencil button. Change the values, then commit to `main`. GitHub Pages republishes the update.

- `kickstarterUrl`: paste the full official Kickstarter campaign or pre-launch HTTPS URL. All campaign buttons update automatically. While blank, visitors see an honest pending-link message and can follow the creator's existing Linktree.
- `kickstarterButtonText`: the main campaign button label.
- `founderName` and `founderRole`: your name and short introduction.
- `storyIntro`: the opening line of your About section.
- `storyParagraphs`: your story, with one quoted string per paragraph. The supplied first-person copy is an editable draft based on the project, not a completed personal biography.
- `creatorLinksUrl`: your public creator links.

Keep JSON syntax valid: quoted keys and values, commas between entries, and no trailing commas. Content is inserted as text rather than HTML. The page includes fallback story text if configuration cannot load.

## Hosting

Expected URL: https://kingqueue.github.io/spacefruit_website/

Publishing source: `main` branch, `/` (root). `.nojekyll` keeps this buildless. GitHub Pages is free for this public repository. No custom domain is required.

## Local preview

Run `python -m http.server 8876 --bind 127.0.0.1` from this folder, then open http://127.0.0.1:8876/. Opening `index.html` directly is insufficient for loading editable JSON in some browsers.

## Content and assets

- `index.html`: semantic sections, metadata, gallery, FAQ and fallback copy.
- `styles.css`: cloud-white/forest-green responsive theme; reduced-motion support.
- `app.js`: six-tool selector, keyboard navigation, mobile menu, image viewer and editable content.
- `site-content.json`: creator-editable About text and campaign destination.
- `assets/`: all four supplied images, WebP delivery versions and site mark.

Illustrative robot imagery is labeled as concept rendering. CAD images are labeled as prototypes. The supplied Kickstarter screenshot is an early draft, not a live funding counter. The site does not claim production readiness, certification, patent status, tested autonomous performance, shipping dates or unverified funding figures. Tool illustrations are schematic drawings, not mechanical CAD.
