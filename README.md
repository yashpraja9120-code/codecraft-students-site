# YashTech

A static, SEO-friendly website (HTML + CSS + vanilla JavaScript, no
build tools, no frameworks) built for AdSense monetization in the
technology / AI / programming-for-students niche.

## Structure

```
site/
├── index.html              Home
├── blog.html                Blog / article listing (with filters)
├── search.html               Dedicated search page
├── about.html
├── contact.html               Contact form (front-end only, see note below)
├── privacy-policy.html
├── terms.html
├── robots.txt
├── sitemap.xml
├── css/style.css              All styling
├── js/main.js                 Nav toggle, search, form handling
├── js/articles-data.js        Article metadata used by search/blog
└── articles/                  10 full articles (individual HTML pages)
```

## Run it locally

You don't need Node, Python packages, or a build step — it's plain
static HTML. Two ways to view it:

1. **Simplest:** double-click `index.html` to open it directly in
   your browser.
2. **Recommended** (avoids occasional browser restrictions on local
   scripts): serve the folder with a tiny local server.

   ```bash
   cd site
   python3 -m http.server 8000
   ```

   Then open `http://localhost:8000` in your browser.

   If you don't have Python, any static server works, e.g.:

   ```bash
   npx serve .
   ```

## Before going live

- **Replace the placeholder domain** `https://www.codecraftstudents.example`
  in `build.py` (or directly in each HTML file's `<link rel="canonical">`,
  Open Graph tags, `robots.txt`, and `sitemap.xml`) with your real domain.
- **Connect the contact form.** Right now `contact.html` only shows a
  success message in the browser — it doesn't send anything. Point it
  at a form backend such as Formspree, Netlify Forms, or your own
  server endpoint (add an `action` and `method` to the `<form>`, or
  send the data with `fetch()` in `js/main.js`).
- **Add your AdSense code.** Once your site is approved, paste your
  AdSense script into the `<head>` of each page (or add it once to the
  `head()` function in `build.py` and regenerate) and place `<ins>`
  ad units where the `.ad-slot` placeholders currently sit in the
  article template.
- **Fill in real legal details.** The Privacy Policy and Terms pages
  are solid starting templates but use placeholder jurisdiction/contact
  language — have them reviewed before publishing commercially.
- **Swap the favicon** for a real image file if you want something
  more polished than the inline SVG placeholder.

## Editing content

Every page is generated from three Python scripts so the header,
footer, and page shell only need to be written once:

- `build.py` — shared header/footer/head templates.
- `build_pages.py` — Home, Blog, Search, About, Contact, Privacy, Terms.
- `build_articles.py` — the 10 article pages and their content.

To edit an article or add a new one, edit `build_articles.py` (add
a new entry to `ARTICLES` and a matching `BODIES[...]` string), then
regenerate:

```bash
python3 build.py        # defines the shared templates (no output)
python3 build_pages.py
python3 build_articles.py
```

You can also just hand-edit the generated `.html` files directly if
you don't want to touch the generator — the generator is a
convenience, not a requirement at runtime. The live site is the plain
`.html` / `.css` / `.js` files; nothing needs Python once they're
generated.

## Adding a new article to search

If you add an article by hand-editing HTML instead of using the
generator, remember to also add its title/excerpt/tags/date to
`js/articles-data.js` — that's the file the blog and search pages
read from client-side.
