# Mizan marketing site

Static site, three languages (`/ar/` default, `/en/`, `/tr/`), no framework, no backend, no build step to deploy.

```
site/          ← deploy this folder as-is (the web root)
  index.html   root: redirects to the visitor's saved language, else /ar/
  ar/ en/ tr/  each has: index, pricing/, privacy/, terms/, delete-account/, support/
  assets/      styles.css (precompiled Tailwind, 20 KB), site.js (1.7 KB), og.png
  favicon.svg, favicon.ico, apple-touch-icon.png, sitemap.xml, robots.txt, 404.html
  _headers     security + cache headers (Cloudflare Pages, Netlify)
  vercel.json  same headers for Vercel
src/           generator + translations (only needed if you change copy or classes)
```

Page weight: home ≈ 32 KB HTML + 20 KB CSS + 2 KB JS, one request each, no fonts, no external hosts. All text renders with JavaScript off; JS only adds the theme toggle, the monthly/yearly toggle and language persistence.

## Deploy

**Cloudflare Pages** — Create project → Upload assets → drag the `site/` folder. Or connect a repo and set build command *(none)*, output directory `site`.

**Netlify** — Drag `site/` onto app.netlify.com/drop. Or repo: build command *(none)*, publish directory `site`.

**Vercel** — `cd site && vercel --prod`. Or repo: framework *Other*, output directory `site`. `vercel.json` is inside `site/`.

All three serve `/en/pricing/index.html` at `/en/pricing/` with no config.

## Placeholders you still need to fill in

| # | What | Where |
|---|------|-------|
| 1 | Google Play link — `href="#"` on the two Play badges per home page (`data-store-link`) | `src/build.py` → `store_badges()` (or search `data-store-link` in `site/*/index.html`) |
| 2 | App Store link — same, Apple badges | same |
| 3 | Official store badge artwork. The badges are drawn with CSS/SVG icons; Google and Apple both require their official badge images for public use. Replace the `<a data-store-link>` contents with `<img>` of the official badges (localised AR/EN/TR versions exist for both). | `store_badges()` |
| 4 | Stripe Checkout links — `href="#"` on the three Subscribe buttons per pricing page. Each carries `data-plan="basic|smart|pro"` and, once JS runs, `data-billing="monthly|yearly"`, so you can either hardcode six links or set them in `site.js`. | `src/build.py` → `pricing()`; `site/assets/site.js` |
| 5 | Real app screenshots — the phone frame holds a CSS mock UI. Drop `home-ar.png`, `home-en.png`, `home-tr.png` (≈ 360×780) into `site/assets/screens/` and replace the contents of `<div data-screenshot-slot>` with an `<img>`. There is an HTML comment marking the spot in each home page. | `phone_mock()` |
| 6 | Open Graph image — `site/assets/og.png` is a generated 1200×630 wordmark; replace with real artwork if you have it (keep the size). | `site/assets/og.png` |
| 7 | Legal entity name / country / governing law — the Terms and Privacy refer to "Mizan" and "we". If you operate as a registered company, add its name and jurisdiction to Terms §1 and §11 and Privacy "Contact". | `src/i18n_*.py` |
| 8 | Hosting/database provider name — Privacy says "a cloud hosting provider". Google Play's Data Safety form does not require the name, but naming it (e.g. Supabase, Firebase) is better practice. | `src/i18n_*.py` → `privacy.sections[3]` |
| 9 | Retention numbers — 30 days production + 30 days backups, 7 days for email deletion requests, 12 months for support mail. Adjust to what your backend actually does. | `privacy` and `delete` in all three `i18n_*.py` |
| 10 | Last-updated date — currently 5 September 2026 in all three languages. | `"date"` key at the top of each `i18n_*.py` |
| 11 | Domain and email — `mizan-ai.org` / `support@mizan-ai.org` are set. If they change: `DOMAIN` and `EMAIL` at the top of `src/build.py`. | `src/build.py` |

## Editing copy or layout

Everything is generated from `src/`:

```bash
python3 src/build.py                                  # regenerates site/**/*.html, sitemap, robots
npx tailwindcss@3.4.17 -c src/tailwind.config.js -i src/input.css -o site/assets/styles.css --minify
```

Run the second command only if you add Tailwind classes that are not already used somewhere (the CSS is tree-shaken against `site/**/*.html`). Copy changes alone need only `build.py`. Python 3.8+ and Node 18+ are the only tools involved; nothing is needed on the server.

Translations live in `src/i18n_ar.py`, `i18n_en.py`, `i18n_tr.py` with identical keys. Arabic is Modern Standard, Gulf/Levantine-neutral; the layout is fully mirrored via `dir="rtl"` and Tailwind logical utilities (`ms-`, `ps-`, `start-`, `text-start`), not by translated text in an LTR frame.

## Theme

Dark is the default (`<html class="dark">` hardcoded, so it holds with JS off). The toggle in the header stores `mizan-theme` in localStorage. Colors are CSS variables in `src/input.css`; the light palette uses slightly darker blue/teal so links and buttons keep WCAG AA contrast on the light background. Button fills use `#2563EB` rather than the brand `#3B82F6` because white text on `#3B82F6` is 3.7:1 (fails AA); `#3B82F6` is used for links, icons and accents where it passes against the navy.

## Data Safety form (Google Play) — consistent answers

Based on the privacy policy as written:

- Collects: Name, Email address (account management); Financial info → "Other financial info" entered by user (app functionality); Purchase history (via RevenueCat, app functionality); Crash logs, Diagnostics (app functionality).
- Does not collect: Location, Contacts, Device or other IDs for advertising, Messages, Photos (receipt images are user-uploaded content → "Photos or videos, user-initiated"), Web browsing, Installed apps.
- Shared with third parties: Financial info text and receipt images with OpenAI (app functionality, only on user action); purchase status with RevenueCat.
- Data encrypted in transit: Yes. Users can request deletion: Yes (in-app, `/delete-account`). Not sold, not used for ads.

## Privacy stance of the site itself

No analytics, no cookies, no consent banner, no third-party requests at all. The only browser storage is localStorage for two preferences (`mizan-lang`, `mizan-theme`), which is not tracking and needs no banner under ePrivacy/GDPR.
# mizan-site
