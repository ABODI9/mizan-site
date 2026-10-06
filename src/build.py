#!/usr/bin/env python3
"""Generates the static Mizan site into ../site from the three i18n dictionaries.
Run:  python3 src/build.py   (then compile Tailwind, see README)"""
import os, sys, shutil, html, json
sys.path.insert(0, os.path.dirname(__file__))
from i18n_en import EN
from i18n_ar import AR
from i18n_tr import TR

def _load_dotenv(path):
    """KEY=VALUE lines from a local, git-ignored .env. Real environment variables
    win, so CI and one-off overrides (MIZAN_API_BASE=... python3 src/build.py)
    still work. No dependency: this is the whole parser."""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except FileNotFoundError:
        pass

_load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

DOMAIN = "https://mizan-ai.org"          # placeholder-free: chosen by owner
EMAIL = "support@mizan-ai.org"

# ---- Integration config. Everything external lives here, never in markup. ----
# The site only ever talks to our own API. It holds no Stripe key and loads no
# Stripe SDK: /billing/checkout returns a URL and we navigate to it.
API_BASE = os.environ.get("MIZAN_API_BASE", "https://api.mizan-ai.org")
TOKEN_KEY = "mizan_token"                 # the only key the JWT is stored under
ANDROID_PACKAGE = "com.mizan.app"
IOS_BUNDLE = "com.mizan.app"
# The one URL the app claims. Android App Links / iOS Universal Links intercept it
# when the app is installed; otherwise the browser lands on the real page below.
# Deliberately NOT a mizan:// custom scheme: those misfire on iOS.
APP_HANDOFF_PATH = "/app/billing/activated"
APP_HANDOFF_URL = DOMAIN + APP_HANDOFF_PATH
APP_LINK_PATHS = ["/app/*"]   # what the apps claim, on both platforms
STORE_LINKS = {                           # swap these two lines to change every badge
    "play": "https://play.google.com/store/apps/details?id=com.mizan.app",
    "apple": "",                          # TBA - empty renders "coming soon", not a dead link
}

OUT = os.environ.get("MIZAN_OUT") or os.path.join(os.path.dirname(__file__), "..", "site")
LANGS = [EN, AR, TR]                      # EN first = default language
# Pricing and support are sections of the home page (#pricing, #support), not pages.
PAGES = ["", "privacy", "terms", "delete-account", "login", "signup"]
# Their old URLs stay alive as tiny redirect stubs: store listings, Paddle's payment
# link and old emails may still point at them. old page -> (anchor, nav key)
MOVED_PAGES = {"pricing": ("pricing", "pricing"), "support": ("support", "support")}
NOINDEX_PAGES = ["account", "billing/success", "billing/cancel"]
PRICES = [  # tier index -> (monthly, yearly)
    (None, None), (4.99, 39.99), (7.99, 64.99), (12.99, 99.99),
]
PLAN_KEYS = [None, "basic", "smart", "pro_ai"]   # tier index -> backend plan id
                                                 # "trial" is deliberately absent: not purchasable

# ---- Paddle web checkout. OFF unless PADDLE_CLIENT_TOKEN is set (see .env.example). ----
# Off, the site keeps the backend checkout flow (POST /billing/checkout) untouched.
# Only a client-side token and price ids ever reach the browser; both are public by
# design. The build refuses anything that looks like an API key, and a token whose
# prefix does not match PADDLE_ENV, so a sandbox build cannot ship a live token and
# a live build cannot ship a sandbox one. Entitlement is never decided in the
# browser: the server grants a plan from Paddle's signed webhook.
PADDLE_ENV = os.environ.get("PADDLE_ENV", "sandbox").strip().lower()
PADDLE_JS = "https://cdn.paddle.com/paddle/v2/paddle.js"
# What the CSP must allow, per environment. Measured, not guessed: a headless run
# of the sandbox overlay under this CSP. Paddle.js injects its overlay stylesheet
# from <env>cdn.paddle.com and sets inline styles on the overlay, so style-src
# needs both. That 'unsafe-inline' is for STYLES only and only when Paddle is on;
# script-src never gains it from Paddle. The production row mirrors sandbox with
# the live hostnames and must be re-measured before go-live.
PADDLE_HOSTS = {
    "sandbox":    {"script": ["https://cdn.paddle.com"],
                   "style": ["'unsafe-inline'", "https://sandbox-cdn.paddle.com"],
                   "frame": ["https://sandbox-buy.paddle.com"],
                   "connect": ["https://sandbox-checkout-service.paddle.com"]},
    "production": {"script": ["https://cdn.paddle.com"],
                   "style": ["'unsafe-inline'", "https://cdn.paddle.com"],
                   "frame": ["https://buy.paddle.com"],
                   "connect": ["https://checkout-service.paddle.com"]},
}

def _paddle_config():
    token = os.environ.get("PADDLE_CLIENT_TOKEN", "").strip()
    if not token:
        return None
    errors = []
    if PADDLE_ENV not in PADDLE_HOSTS:
        errors.append(f'PADDLE_ENV must be "sandbox" or "production", got "{PADDLE_ENV}"')
    want = "test_" if PADDLE_ENV == "sandbox" else "live_"
    if token.startswith("pdl_"):
        errors.append("PADDLE_CLIENT_TOKEN holds an API key (pdl_...). API keys must never reach the browser; use a client-side token")
    elif not token.startswith(want):
        errors.append(f"PADDLE_CLIENT_TOKEN must start with {want} when PADDLE_ENV={PADDLE_ENV}")
    prices = {}
    for plan in PLAN_KEYS[1:]:
        prices[plan] = {}
        for period in ("monthly", "yearly"):
            var = f"PADDLE_PRICE_{plan.upper()}_{period.upper()}"
            pid = os.environ.get(var, "").strip()
            if not pid.startswith("pri_"):
                errors.append(f"{var} is missing or is not a pri_ id")
            prices[plan][period] = pid
    if errors:
        sys.exit("Paddle config refused:" + "".join("\n  - " + e for e in errors))
    return {"env": PADDLE_ENV, "token": token, "js": PADDLE_JS, "prices": prices}

PADDLE = _paddle_config()

def esc(s): return html.escape(s, quote=True)
CUR = ' aria-current="true"'
CURP = ' aria-current="page"'

def url(lang, page=""):
    """The URL every link inside the site uses: no language in it (/privacy/, not
    /en/privacy/). `lang` is accepted and ignored so call sites read the same.
    Netlify answers it with the visitor's language, chosen by the mizan_ar /
    mizan_tr cookie (see REDIRECTS); site/<page>/index.html is the fallback."""
    return "/" + (f"{page}/" if page else "")

def lang_url(lang, page=""):
    """The real file for one language, /ar/privacy/. Only for things that must
    name a language: the switcher, canonical/hreflang, the sitemap."""
    return f"/{lang['code']}/" + (f"{page}/" if page else "")

def section_url(lang, anchor):
    """A section of the one-page home, e.g. /en/#pricing."""
    return url(lang) + "#" + anchor

# ---------- SVG bits ----------
def logo(uid, size=32):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 48 48" fill="none" aria-hidden="true" focusable="false">
<defs><linearGradient id="lg{uid}" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#14B8A6"/></linearGradient></defs>
<g stroke="url(#lg{uid})" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
<path d="M24 9v31M17 40h14M7 15h34"/><circle cx="24" cy="9" r="2.4" fill="url(#lg{uid})"/>
<path d="M12 15 6 27h12zM36 15l-6 12h12z"/>
<path d="M6 27.5a6 6 0 0 0 12 0M30 27.5a6 6 0 0 0 12 0"/></g></svg>'''

ICONS = {  # 24px stroke icons, currentColor
    "ledger": '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5v13a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5z"/><path d="M8 9h8M8 12.5h8M8 16h5"/>',
    "budget": '<path d="M4 19h16"/><path d="M6 15V9M11 15V5M16 15v-3"/><path d="M4 5h5"/>',
    "goal": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
    "subs": '<path d="M20 12a8 8 0 1 1-2.3-5.7"/><path d="M20 4v5h-5"/>',
    "report": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2"/>',
    "fx": '<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c2.5 2.5 2.5 13.5 0 16M12 4c-2.5 2.5-2.5 13.5 0 16"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "chat": '<path d="M5 6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5v7a2.5 2.5 0 0 1-2.5 2.5H10l-4 4v-4H7.5A2.5 2.5 0 0 1 5 13.5z"/>',
    "camera": '<path d="M4 8.5A1.5 1.5 0 0 1 5.5 7H8l1.5-2h5L16 7h2.5A1.5 1.5 0 0 1 20 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 17.5z"/><circle cx="12" cy="13" r="3.5"/>',
    "week": '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M8 3v4M16 3v4"/>',
    "forecast": '<path d="M4 17 9.5 11l4 4L20 8"/><path d="M15 8h5v5"/>',
    "alert": '<path d="M12 4 3.5 19h17z"/><path d="M12 10v4M12 16.5v.5"/>',
    "wallet": '<path d="M4 7.5A1.5 1.5 0 0 1 5.5 6h13A1.5 1.5 0 0 1 20 7.5v10a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 17.5z"/><path d="M16 12.5h4M4 10h16"/>',
    "shield": '<path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z"/><path d="m9.5 12 2 2 3.5-4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4"/>',
    "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="m6 6 12 12M18 6 6 18"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "trash": '<path d="M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
}
def icon(name, cls="h-6 w-6"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'
# arrow that flips in RTL
def arrow(): return icon("arrow", "h-4 w-4 rtl:-scale-x-100")

def store_badges(L, uid):
    s = L["stores"]
    apple = '<svg class="h-7 w-7" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.6 2.1-3.7-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.1 1-4 2.4-1.7 3-.4 7.3 1.2 9.7.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.2-.8s1.9.8 3.2.8c1.3 0 2.2-1.2 3-2.4.9-1.4 1.3-2.7 1.3-2.8 0 0-2.5-1-2.6-3.8zM14 5.4c.7-.8 1.1-1.9 1-3-1 0-2.1.7-2.8 1.5-.6.7-1.2 1.9-1 2.9 1.1.1 2.2-.6 2.8-1.4z"/></svg>'
    play = '<svg class="h-7 w-7" viewBox="0 0 24 24" aria-hidden="true"><path fill="#34A853" d="M3.6 2.4 13 12l-9.4 9.6c-.4-.2-.6-.7-.6-1.2V3.6c0-.5.2-1 .6-1.2z"/><path fill="#FBBC04" d="m13 12 3.2-3.2 4.3 2.5c1.3.7 1.3 2.7 0 3.4l-4.3 2.5z"/><path fill="#4285F4" d="m3.6 2.4 12.6 6.4L13 12z"/><path fill="#EA4335" d="M13 12l3.2 3.2L3.6 21.6z"/></svg>'
    def badge(href, ic, top, name, label):
        # Store URLs come from STORE_LINKS; an empty one renders as a disabled
        # "coming soon" badge so we never ship a link that goes nowhere.
        inner = (f'{ic}<span class="flex flex-col leading-tight text-start">'
                 f'<span class="text-[0.7rem] text-muted">{esc(top if href else s["soon"])}</span>'
                 f'<span class="text-base font-semibold">{esc(name)}</span></span>')
        box = "inline-flex items-center gap-3 rounded-xl border border-line bg-surface px-4 py-2.5"
        if not href:
            return f'<span class="{box} text-muted opacity-70" aria-label="{esc(name)} \u2014 {esc(s["soon"])}" data-store-link>{inner}</span>'
        return (f'<a href="{href}" class="{box} text-fg hover:border-muted transition-colors" '
                f'aria-label="{esc(label)}" data-store-link>{inner}</a>')
    return ('<div class="flex scroll-mt-32 flex-wrap items-center gap-3" id="download">'
            + badge(STORE_LINKS["play"], play, s["google"], s["google2"], f'{s["google"]} {s["google2"]}')
            + badge(STORE_LINKS["apple"], apple, s["apple"], s["apple2"], f'{s["apple"]} {s["apple2"]}') + '</div>')

# ---------- Layout ----------
def data_island(L, level, extra=None):
    """Ships config and the translated strings the page's JS needs, so that no
    user-visible string is ever written inside JavaScript."""
    p = L["pricing"]
    payload = {"cfg": {
        "api": API_BASE,
        "tokenKey": TOKEN_KEY,
        "lang": L["code"],
        "plans": PLAN_KEYS[1:],
        "urls": {
            "home": url(L), "pricing": section_url(L, "pricing"), "login": url(L, "login"),
            "signup": url(L, "signup"), "account": url(L, "account"),
            "delete": url(L, "delete-account"), "support": section_url(L, "support"),
            "success": url(L, "billing/success"),
        },
    }}
    if PADDLE and level == "full":
        payload["cfg"]["paddle"] = PADDLE
    if level == "full":
        payload["i18n"] = {
            "auth": L["auth"], "account": L["account"], "billing": L["billing"],
            "delete": L["delete"]["web"], "email": EMAIL,
            "planNames": {PLAN_KEYS[i]: p["tiers"][i]["name"] for i in (1, 2, 3)},
            "periods": {"monthly": p["monthly"], "yearly": p["yearly"]},
        }
    if extra:
        payload.update(extra)
    # </ is escaped so the JSON can never close the <script> element early.
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="mizan-data">{blob}</script>'


# Runs in <head> of every page, before anything paints. On a real language file
# (/ar/privacy/) it (1) remembers the language - the mizan_ar / mizan_tr cookie is
# what Netlify routes on, English is "neither" - and (2) rewrites the address bar
# to the language-free URL (/privacy/). It only hides the prefix once the cookie is
# confirmed, so a reload at the clean URL lands on the same language. No-op on
# any URL without a language prefix. Plain string, not an f-string: single braces.
LANG_URL_JS = """<script>(function(){try{
var m=/^\\/(en|ar|tr)(\\/.*)?$/.exec(location.pathname);if(!m)return;
var l=m[1],sec=location.protocol==='https:'?';Secure':'';
['ar','tr'].forEach(function(c){document.cookie='mizan_'+c+'='+(c===l?'1;max-age=31536000':';max-age=0')+';path=/;SameSite=Lax'+sec;});
try{localStorage.setItem('mizan-lang',l);}catch(e){}
if(l==='en'||document.cookie.indexOf('mizan_'+l+'=')>-1)history.replaceState(null,'',(m[2]||'/')+location.search+location.hash);
}catch(e){}})();</script>"""

def head(L, page, title, desc, noindex=False, data="min"):
    canon = DOMAIN + lang_url(L, page)
    if noindex:
        alts = '<meta name="robots" content="noindex,nofollow">'
    else:
        alts = "".join(f'<link rel="alternate" hreflang="{X["code"]}" href="{DOMAIN}{lang_url(X, page)}">' for X in LANGS)
        alts += f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{lang_url(LANGS[0], page)}">'
    island = data_island(L, data) if data else ""
    return f'''<!DOCTYPE html>
<html lang="{L["code"]}" dir="{L["dir"]}" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
{alts}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mizan">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{L["locale"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{DOMAIN}/assets/og.png">
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#0F172A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/styles.css">
<script>(function(){{var d=document.documentElement;d.classList.add('js');try{{if(localStorage.getItem('mizan-theme')==='light'){{d.classList.remove('dark');}}}}catch(e){{}}}})();</script>
{LANG_URL_JS}
{island}
</head>
<body class="min-h-screen bg-bg text-fg antialiased">
<a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:start-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-primary-strong focus:px-4 focus:py-2 focus:text-white">{esc(L["skip"])}</a>
'''

def lang_switcher(L, page, cls=""):
    items = ""
    for X in LANGS:
        cur = X["code"] == L["code"]
        a = (f'<a href="{lang_url(X, page)}" hreflang="{X["code"]}" lang="{X["code"]}" data-lang="{X["code"]}" '
             f'class="rounded-md px-2.5 py-1 text-sm transition-colors {"bg-primary/15 text-fg font-medium" if cur else "text-muted hover:text-fg"}"'
             f'{CUR if cur else ""}>{esc(X["native"])}</a>')
        items += a
    return f'<nav aria-label="{esc(L["switcher"])}" class="flex items-center gap-0.5 rounded-lg border border-line bg-surface p-0.5 {cls}">{items}</nav>'

def theme_btn(L):
    return (f'<button type="button" data-theme-toggle class="js-only inline-flex h-9 w-9 items-center justify-center rounded-lg border border-line bg-surface text-muted hover:text-fg" aria-label="{esc(L["theme"])}" title="{esc(L["theme"])}">'
            f'<span class="dark:hidden">{icon("moon","h-5 w-5")}</span><span class="hidden dark:inline">{icon("sun","h-5 w-5")}</span></button>')

def auth_link(L, cls):
    """Renders as "Sign in"; site.js swaps it to "Account" when a token exists."""
    n = L["nav"]
    return (f'<a href="{url(L, "login")}" data-auth-link class="{cls}" '
            f'data-account-href="{url(L, "account")}" data-account-label="{esc(n["account"])}">{esc(n["signin"])}</a>')


def header(L, page):
    n = L["nav"]; home = url(L)
    brand = "ميزان" if L["code"] == "ar" else "Mizan"
    # Same order as the sections on the home page.
    links = [(home + "#pricing", n["pricing"]), (home + "#features", n["features"]), (home + "#ai", n["ai"]), (home + "#support", n["support"])]
    def nav(cls_a):
        return "".join(f'<a href="{h}" class="{cls_a}"{CURP if page and h == url(L, page) else ""}>{esc(t)}</a>' for h, t in links)
    return f'''<header class="sticky top-0 z-40 border-b border-line bg-bg/90 backdrop-blur">
<div class="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
<a href="{home}" class="flex items-center gap-2.5 font-semibold" aria-label="{esc(n["home"])}">{logo("h")}<span class="text-lg">{brand}</span></a>
<nav class="hidden items-center gap-1 md:flex" aria-label="Main">{nav("rounded-md px-3 py-2 text-sm text-muted hover:text-fg hover:bg-surface")}</nav>
<div class="hidden items-center gap-2 md:flex">{lang_switcher(L, page)}{theme_btn(L)}{auth_link(L, "rounded-md px-3 py-2 text-sm text-muted hover:text-fg hover:bg-surface")}<a href="{home}#download" class="rounded-lg bg-primary-strong px-4 py-2 text-sm font-semibold text-white hover:bg-primary-hover">{esc(n["download"])}</a></div>
<details class="relative md:hidden" data-menu>
<summary class="flex h-10 w-10 cursor-pointer list-none items-center justify-center rounded-lg border border-line bg-surface [&::-webkit-details-marker]:hidden" aria-label="{esc(n["menu"])}"><span class="[[open]_&]:hidden">{icon("menu","h-5 w-5")}</span><span class="hidden [[open]_&]:block">{icon("close","h-5 w-5")}</span></summary>
<div class="absolute end-0 top-12 w-64 rounded-xl border border-line bg-surface p-2 shadow-xl">
<nav class="flex flex-col" aria-label="Main">{nav("rounded-md px-3 py-2.5 text-fg hover:bg-bg")}{auth_link(L, "rounded-md px-3 py-2.5 text-fg hover:bg-bg")}</nav>
<div class="mt-2 flex items-center justify-between gap-2 border-t border-line pt-3">{lang_switcher(L, page)}{theme_btn(L)}</div>
<a href="{home}#download" class="mt-3 block rounded-lg bg-primary-strong px-4 py-2.5 text-center font-semibold text-white hover:bg-primary-hover">{esc(n["download"])}</a>
</div></details>
</div></header>
<main id="main">
'''

def footer(L):
    f = L["footer"]; home = url(L)
    brand = "ميزان" if L["code"] == "ar" else "Mizan"
    def col(title, links):
        return (f'<div><h2 class="mb-3 text-sm font-semibold text-fg">{esc(title)}</h2><ul class="space-y-2 text-sm">'
                + "".join(f'<li><a href="{h}" class="text-muted hover:text-fg">{esc(t)}</a></li>' for h, t in links) + '</ul></div>')
    return f'''</main>
<footer class="border-t border-line bg-surface/50">
<div class="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-4">
<div class="md:col-span-2"><a href="{home}" class="flex items-center gap-2.5 font-semibold">{logo("f")}<span class="text-lg">{brand}</span></a>
<p class="mt-3 max-w-xs text-sm text-muted">{esc(f["tagline"])}</p>
<p class="mt-4 text-sm text-muted">{esc(f["email"])}: <a href="mailto:{EMAIL}" class="text-primary hover:underline" dir="ltr">{EMAIL}</a></p></div>
{col(f["product"], [(home + "#pricing", L["nav"]["pricing"]), (home + "#features", L["nav"]["features"]), (url(L, "account"), f["account"]), (home + "#support", f["support"])])}
{col(f["legal"], [(url(L, "privacy"), f["privacy"]), (url(L, "terms"), f["terms"]), (url(L, "delete-account"), f["delete"])])}
</div>
<div class="border-t border-line"><div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-5 text-xs text-muted sm:px-6"><p>{esc(f["rights"])}</p>{lang_switcher(L, "", "text-xs")}</div></div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''

# ---------- Home ----------
def phone_mock(L):
    m = L["home"]["mock"]
    bars = "".join(f'<div><div class="flex justify-between text-[11px] text-slate-400"><span>{esc(c)}</span><span dir="ltr">{p}%</span></div><div class="mt-1 h-1.5 rounded-full bg-slate-700"><div class="h-1.5 rounded-full {"bg-amber-400" if p > 80 else "bg-gradient-to-r from-blue-500 to-teal-400"}" style="width:{p}%"></div></div></div>' for c, p in m["cats"])
    tx = "".join(f'<li class="flex items-center justify-between py-2"><div><div class="text-[13px] font-medium text-slate-100">{esc(a)}</div><div class="text-[11px] text-slate-400">{esc(b)}</div></div><span dir="ltr" class="text-[13px] font-medium {"text-teal-400" if c.startswith("+") else "text-slate-100"}">{esc(c)}</span></li>' for a, b, c in m["tx"])
    return f'''<div class="relative mx-auto w-[280px] sm:w-[300px]" aria-hidden="true">
<div class="absolute -inset-8 -z-10 rounded-full bg-gradient-to-br from-primary/25 to-accent/25 blur-3xl"></div>
<div class="rounded-[2.6rem] border-[6px] border-slate-800 bg-slate-950 p-2 shadow-2xl ring-1 ring-slate-700">
<div class="relative overflow-hidden rounded-[2rem] bg-[#0F172A]" style="aspect-ratio:9/19.5">
<div class="absolute left-1/2 top-2 h-5 w-24 -translate-x-1/2 rounded-full bg-black"></div>
<!-- {m["slot"]} -->
<div data-screenshot-slot class="h-full px-4 pb-4 pt-10 text-start">
<div class="text-[11px] text-slate-400">{esc(m["greeting"])}</div>
<div class="mt-2 rounded-2xl bg-gradient-to-br from-blue-600 to-teal-500 p-4 text-white"><div class="text-[11px] opacity-80">{esc(m["balance"])}</div><div class="mt-1 text-2xl font-semibold tracking-tight" dir="ltr">{m["amount"]} <span class="text-xs font-normal opacity-80">{m["cur"]}</span></div></div>
<div class="mt-3 rounded-2xl bg-[#151B26] p-3.5 ring-1 ring-[#263244]"><div class="flex justify-between text-xs"><span class="font-medium text-slate-100">{esc(m["budget"])}</span></div><div class="mt-0.5 text-[11px] text-slate-400">{esc(m["spent"])}</div><div class="mt-3 space-y-2.5">{bars}</div></div>
<div class="mt-3 rounded-2xl bg-[#151B26] p-3.5 ring-1 ring-[#263244]"><div class="text-xs font-medium text-slate-100">{esc(m["recent"])}</div><ul class="mt-1 divide-y divide-[#263244]">{tx}</ul></div>
</div></div></div></div>'''

def section(id_, inner, cls=""):
    return f'<section id="{id_}" class="scroll-mt-20 {cls}"><div class="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">{inner}</div></section>'

def home(L):
    h = L["home"]; feat_icons = ["ledger", "budget", "goal", "subs", "report", "fx"]; ai_icons = ["chat", "camera", "week", "forecast", "alert", "wallet"]
    hero = f'''<section class="relative overflow-hidden"><div class="mx-auto grid max-w-6xl items-center gap-12 px-4 pb-16 pt-14 sm:px-6 sm:pt-20 md:grid-cols-2 md:pb-24">
<div class="text-center md:text-start"><h1 class="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">{esc(h["h1"])}</h1>
<p class="mx-auto mt-5 max-w-xl text-lg text-muted md:mx-0">{esc(h["sub"])}</p>
<div class="mt-8 flex justify-center md:justify-start">{store_badges(L, "hero")}</div>
<p class="mt-4 text-sm text-muted">{esc(h["note"])}</p></div>
<div>{phone_mock(L)}</div></div></section>'''
    cards = "".join(f'<div class="rounded-2xl border border-line bg-surface p-6"><div class="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-primary/15 text-primary">{icon(ic)}</div><h3 class="mt-4 text-lg font-semibold">{esc(t)}</h3><p class="mt-2 text-muted">{esc(d)}</p></div>' for (t, d), ic in zip(h["features"], feat_icons))
    features = section("features", f'<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{esc(h["features_h2"])}</h2><p class="mt-3 max-w-2xl text-lg text-muted">{esc(h["features_sub"])}</p><div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{cards}</div>')
    ai_items = "".join(f'<li class="flex gap-4"><span class="mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/15 text-accent">{icon(ic, "h-5 w-5")}</span><div><h3 class="font-semibold">{esc(t)}</h3><p class="mt-1 text-muted">{esc(d)}</p></div></li>' for (t, d), ic in zip(h["ai"], ai_icons))
    ai = section("ai", f'<div class="grid gap-10 md:grid-cols-5"><div class="md:col-span-2"><h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{esc(h["ai_h2"])}</h2><p class="mt-3 text-lg text-muted">{esc(h["ai_sub"])}</p><p class="mt-6 rounded-xl border border-line bg-surface p-4 text-sm text-muted">{esc(h["ai_note"])}</p></div><ul class="grid gap-6 sm:grid-cols-2 md:col-span-3">{ai_items}</ul></div>', "border-y border-line bg-surface/40")
    langs = section("languages", f'<div class="grid items-center gap-8 md:grid-cols-2"><div><h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{esc(h["langs_h2"])}</h2><p class="mt-3 text-lg text-muted">{esc(h["langs_p"])}</p></div><div class="grid grid-cols-3 gap-3 text-center"><div class="rounded-2xl border border-line bg-surface p-5"><div class="text-2xl font-semibold" lang="ar" dir="rtl">العربية</div><div class="mt-1 text-xs text-muted" dir="ltr">RTL</div></div><div class="rounded-2xl border border-line bg-surface p-5"><div class="text-2xl font-semibold" lang="en">English</div><div class="mt-1 text-xs text-muted" dir="ltr">LTR</div></div><div class="rounded-2xl border border-line bg-surface p-5"><div class="text-2xl font-semibold" lang="tr">Türkçe</div><div class="mt-1 text-xs text-muted" dir="ltr">LTR</div></div></div></div>')
    priv = section("privacy", f'<div class="mx-auto max-w-3xl text-center"><div class="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent/15 text-accent">{icon("shield")}</div><h2 class="mt-5 text-3xl font-bold tracking-tight sm:text-4xl">{esc(h["privacy_h2"])}</h2><p class="mt-4 text-lg text-muted">{esc(h["privacy_p"])}</p><a href="{url(L, "privacy")}" class="mt-6 inline-flex items-center gap-2 font-medium text-primary hover:underline">{esc(h["privacy_link"])}{arrow()}</a></div>', "border-t border-line")
    badges_cta = store_badges(L, "cta").replace(' id="download"', "")
    cta = section("cta", f'<div class="rounded-3xl border border-line bg-gradient-to-br from-surface to-bg p-8 text-center sm:p-14"><h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{esc(h["cta_h2"])}</h2><p class="mx-auto mt-3 max-w-xl text-lg text-muted">{esc(h["cta_p"])}</p><div class="mt-8 flex justify-center">{badges_cta}</div><a href="#pricing" class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline">{esc(h["pricing_link"])}{arrow()}</a></div>')
    # One page: download (hero) -> pricing -> the rest. "full" because the pricing
    # buttons need the checkout strings and, when on, the Paddle config.
    return (head(L, "", h["title"], h["desc"], data="full") + header(L, "") + hero + pricing_section(L)
            + features + ai + langs + priv + support_section(L) + cta + footer(L))

# ---------- Pricing (a section of the home page) ----------
def pricing_section(L):
    p = L["pricing"]
    cards = ""
    for i, t in enumerate(p["tiers"]):
        m, y = PRICES[i]; pop = i == 2
        if m is None:
            price = f'<div class="mt-5"><div class="text-4xl font-bold">{esc(p["free"])}</div><div class="mt-1 text-sm text-muted">{esc(p["days"])}</div></div>'
            btn = f'<a href="{url(L, "signup")}" class="mt-6 block rounded-lg border border-line bg-bg px-4 py-2.5 text-center font-semibold hover:border-muted">{esc(p["trial_btn"])}</a>'
            inc = p["includes_first"]
        else:
            pct = round((1 - y / (m * 12)) * 100)
            price = (f'<div class="mt-5">'
                     f'<div class="m-only"><span class="text-4xl font-bold" dir="ltr">${m:.2f}</span><span class="text-muted">{esc(p["mo"])}</span></div>'
                     f'<div class="y-only"><span class="text-4xl font-bold" dir="ltr">${y:.2f}</span><span class="text-muted">{esc(p["yr"])}</span>'
                     f'<div class="mt-1 text-sm text-muted">{esc(p["eq"].format(m=f"{y/12:.2f}"))} · <span class="text-accent">{esc(p["save"].format(pct=pct))}</span></div></div>'
                     f'<div class="nojs-only mt-1 text-sm text-muted"><span dir="ltr">${y:.2f}</span>{esc(p["yr"])} · <span class="text-accent">{esc(p["save"].format(pct=pct))}</span></div>'
                     f'</div>')
            # Server-rendered as a signup link carrying the plan, so the flow survives
            # with JS off and the plan is never lost between pricing and checkout.
            # site.js keeps the period in sync and, when signed in, goes straight to
            # POST /billing/checkout instead of following the link.
            pk = PLAN_KEYS[i]
            btn = (f'<a href="{url(L, "signup")}?plan={pk}&amp;period=monthly" data-subscribe data-plan="{pk}" '
                   f'data-signup-base="{url(L, "signup")}" data-period="monthly" '
                   f'class="mt-6 block rounded-lg px-4 py-2.5 text-center font-semibold '
                   f'{"bg-primary-strong text-white hover:bg-primary-hover" if pop else "border border-line bg-bg hover:border-muted"}">{esc(p["subscribe"])}</a>')
            inc = p["includes"].format(prev=p["tiers"][i - 1]["name"])
        feats = "".join(f'<li class="flex gap-2.5"><span class="mt-0.5 text-accent">{icon("check","h-5 w-5")}</span><span>{esc(f)}</span></li>' for f in t["features"])
        badge = f'<span class="absolute -top-3 start-6 rounded-full bg-accent px-3 py-1 text-xs font-semibold text-slate-950">{esc(p["popular"])}</span>' if pop else ""
        cards += (f'<div class="relative flex flex-col rounded-2xl border {"border-accent ring-1 ring-accent" if pop else "border-line"} bg-surface p-6">{badge}'
                  f'<h3 class="text-xl font-semibold">{esc(t["name"])}</h3><p class="mt-1 text-sm text-muted">{esc(t["line"])}</p>{price}{btn}'
                  f'<p class="mt-6 text-xs font-semibold uppercase tracking-wide text-muted">{esc(inc)}</p><ul class="mt-3 space-y-2.5 text-sm">{feats}</ul></div>')
    toggle = (f'<div class="js-only mt-8 inline-flex rounded-lg border border-line bg-surface p-1" role="group" aria-label="{esc(p["monthly"])} / {esc(p["yearly"])}">'
              f'<button type="button" data-billing-btn="monthly" aria-pressed="true" class="rounded-md px-4 py-2 text-sm font-medium aria-pressed:bg-primary-strong aria-pressed:text-white">{esc(p["monthly"])}</button>'
              f'<button type="button" data-billing-btn="yearly" aria-pressed="false" class="rounded-md px-4 py-2 text-sm font-medium aria-pressed:bg-primary-strong aria-pressed:text-white">{esc(p["yearly"])}</button></div>')
    note = fill(p["note_paddle"] if PADDLE else p["note"], L).replace("{terms}", f'<a href="{url(L, "terms")}" class="text-primary hover:underline">{esc(p["note_terms"])}</a>')
    body = (f'<div class="text-center"><h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{esc(p["h1"])}</h2><p class="mx-auto mt-4 max-w-2xl text-lg text-muted">{esc(p["sub"])}</p>{toggle}</div>'
            f'<div data-billing="monthly" class="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">{cards}</div>'
            f'<div data-billing-status class="mx-auto mt-8 max-w-2xl" role="status" aria-live="polite"></div>'
            f'<p class="mx-auto mt-10 max-w-2xl text-center text-sm text-muted">{note}</p>')
    return section("pricing", body, "border-y border-line bg-surface/40")


# ---------- Support (a section of the home page) ----------
def support_section(L):
    d = L["support"]
    faq = "".join(
        f'<details class="group rounded-2xl border border-line bg-surface">'
        f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 p-5 text-lg font-semibold [&::-webkit-details-marker]:hidden">'
        f'<span>{esc(q)}</span><span class="shrink-0 text-muted transition-transform group-open:rotate-180">{icon("chevron", "h-5 w-5")}</span></summary>'
        f'<p class="px-5 pb-5 text-muted">{fill(a, L)}</p></details>' for q, a in d["faq"])
    inner = (f'<div class="grid gap-10 md:grid-cols-5"><div class="md:col-span-2">'
             f'<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{esc(d["h1"])}</h2><p class="mt-3 text-lg text-muted">{esc(d["sub"])}</p>'
             f'<div class="mt-8 flex gap-4 rounded-2xl border border-line bg-surface p-6"><span class="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">{icon("mail")}</span>'
             f'<div><h3 class="text-xl font-semibold">{esc(d["email_h"])}</h3><p class="mt-2 text-muted">{fill(d["email_p"], L)}</p></div></div></div>'
             f'<div class="md:col-span-3"><h3 class="text-xl font-semibold">{esc(d["faq_h"])}</h3><div class="mt-5 space-y-3">{faq}</div></div></div>')
    return section("support", inner, "border-t border-line")


def moved_page(L, anchor, nav_key):
    """/<lang>/pricing/ and /<lang>/support/ now live on the home page. This is the
    whole old page: a stub that forwards to the section. The query string rides
    along on purpose: Paddle's payment links land on whatever URL the dashboard
    names, with ?_ptxn= on it, and the home page is what opens that checkout."""
    label = L["nav"][nav_key]
    target = lang_url(L) + "#" + anchor
    return f'''<!DOCTYPE html>
<html lang="{L["code"]}" dir="{L["dir"]}" class="dark">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(label)} — Mizan</title>
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{DOMAIN}{lang_url(L)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/styles.css">
<script>location.replace('{lang_url(L)}'+location.search+'#{anchor}');</script>
<noscript><meta http-equiv="refresh" content="0; url={target}"></noscript>
</head>
<body class="min-h-screen bg-bg text-fg antialiased">
<main class="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-4 text-center">
<a href="{target}" class="inline-flex items-center gap-2 font-medium text-primary hover:underline">{esc(label)}{arrow()}</a>
</main>
</body></html>'''

# ---------- Legal / text pages ----------
def fill(s, L):
    return (esc(s).replace("{email}", f'<a href="mailto:{EMAIL}" class="text-primary hover:underline" dir="ltr">{EMAIL}</a>')
            .replace("{date}", esc(L["date"]))
            .replace("{delete_link}", f'<a href="{url(L, "delete-account")}" class="text-primary hover:underline">{esc(L["footer"]["delete"])}</a>')
            .replace("{privacy_link}", f'<a href="{url(L, "privacy")}" class="text-primary hover:underline">{esc(L["footer"]["privacy"])}</a>')
            .replace("{account_link}", f'<a href="{url(L, "account")}" class="text-primary hover:underline">{esc(L["footer"]["account"])}</a>')
            .replace("{pricing_link}", f'<a href="{section_url(L, "pricing")}" class="text-primary hover:underline">{esc(L["nav"]["pricing"])}</a>'))

def blocks(items, L):
    out, ul = "", []
    def flush():
        nonlocal ul, out
        if ul: out += '<ul class="list-disc space-y-2 ps-6">' + "".join(f"<li>{x}</li>" for x in ul) + "</ul>"; ul = []
    for it in items:
        if it.startswith("- "): ul.append(fill(it[2:], L))
        else: flush(); out += f"<p>{fill(it, L)}</p>"
    flush(); return out

def doc_shell(L, page, d, inner, data="min"):
    return (head(L, page, d["title"], d["desc"], data=data) + header(L, page)
            + f'<article class="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20"><h1 class="text-4xl font-bold tracking-tight">{esc(d["h1"])}</h1>'
            + (f'<p class="mt-2 text-sm text-muted">{fill(d["updated"], L)}</p>' if "updated" in d else "")
            + f'<div class="doc mt-8 space-y-5 text-[1.0625rem] leading-relaxed">{inner}</div></article>' + footer(L))

def legal(L, page):
    d = L[page]
    inner = f"<p>{fill(d['intro'], L)}</p>" + "".join(f'<section><h2 class="mb-3 mt-10 text-2xl font-semibold">{esc(h)}</h2><div class="space-y-4">{blocks(items, L)}</div></section>' for h, items in d["sections"])
    return doc_shell(L, page, d, inner)

def delete_web_panel(L):
    """The signed-in delete flow: reveal -> tick -> confirm -> DELETE /auth/me.
    Both halves are rendered; site.js shows the one that matches the token."""
    w = L["delete"]["web"]
    signed_out = (f'<div data-del-signedout class="hidden">'
                  f'<h2 class="text-xl font-semibold">{esc(w["signin_h"])}</h2>'
                  f'<p class="mt-2 text-muted">{esc(w["signin_p"])}</p>'
                  f'<a href="{url(L, "login")}" class="mt-5 inline-flex rounded-lg border border-line bg-bg px-4 py-2.5 font-semibold hover:border-muted">{esc(w["signin_btn"])}</a>'
                  f'</div>')
    confirm = (f'<div data-del-confirm class="hidden mt-5 rounded-xl border border-red-500/50 bg-red-500/5 p-5">'
               f'<h3 class="font-semibold">{esc(w["confirm_h"])}</h3>'
               f'<p class="mt-2 text-sm text-muted">{esc(w["confirm_p"])}</p>'
               f'<label class="mt-4 flex items-start gap-2.5 text-sm"><input type="checkbox" data-del-check class="mt-1 h-4 w-4 shrink-0"><span>{esc(w["confirm_check"])}</span></label>'
               f'<div class="mt-5 flex flex-wrap gap-3">'
               f'<button type="button" data-del-go data-label="{esc(w["confirm_btn"])}" data-working="{esc(w["working"])}" '
               f'class="rounded-lg bg-red-600 px-4 py-2.5 font-semibold text-white hover:bg-red-700 disabled:opacity-60">{esc(w["confirm_btn"])}</button>'
               f'<button type="button" data-del-keep class="rounded-lg border border-line bg-bg px-4 py-2.5 font-semibold hover:border-muted">{esc(w["keep_btn"])}</button>'
               f'</div><div data-del-status class="mt-4" role="alert"></div></div>')
    signed_in = (f'<div data-del-signedin class="hidden">'
                 f'<h2 class="text-xl font-semibold">{esc(w["h"])}</h2>'
                 f'<p class="mt-2 text-muted">{esc(w["p"])}</p>'
                 f'<button type="button" data-del-start class="mt-5 rounded-lg border border-red-500/50 px-4 py-2.5 font-semibold text-red-600 hover:bg-red-500/10 dark:text-red-400">{esc(w["start_btn"])}</button>'
                 f'{confirm}</div>')
    done = (f'<div data-del-done class="hidden">'
            f'<h2 class="text-xl font-semibold">{esc(w["done_h"])}</h2>'
            f'<p class="mt-2 text-muted">{esc(w["done_p"])}</p>'
            f'<a href="{url(L)}" class="mt-5 inline-flex items-center gap-2 font-medium text-primary hover:underline">{esc(w["done_home"])}{arrow()}</a></div>')
    return (f'<section data-delete-web class="not-prose mt-8 rounded-2xl border border-line bg-surface p-6">'
            f'{signed_out}{signed_in}{done}</section>')


def delete_page(L):
    d = L["delete"]
    def h2(t): return f'<h2 class="mb-3 mt-10 text-2xl font-semibold">{esc(t)}</h2>'
    inner = (f"<p>{fill(d['intro'], L)}</p>"
             + delete_web_panel(L)
             + h2(d["in_app_h"]) + '<ol class="list-decimal space-y-2 ps-6">' + "".join(f"<li>{fill(s, L)}</li>" for s in d["steps"]) + "</ol>"
             + f'<p class="mt-4 rounded-xl border border-line bg-surface p-4 text-sm text-muted">{fill(d["export_tip"], L)}</p>'
             + h2(d["email_h"]) + f"<p>{fill(d['email_p'], L)}</p>"
             + h2(d["what_h"]) + '<ul class="list-disc space-y-2 ps-6">' + "".join(f"<li>{fill(s, L)}</li>" for s in d["what"]) + "</ul>"
             + h2(d["kept_h"]) + '<ul class="list-disc space-y-2 ps-6">' + "".join(f"<li>{fill(s, L)}</li>" for s in d["kept"]) + "</ul>"
             + h2(d["time_h"]) + f"<p>{fill(d['time_p'], L)}</p>")
    return doc_shell(L, "delete-account", d, inner, data="full")

# ---------- Account / auth / billing ----------
def field(fid, ftype, label, ac="", required=True, hint="", suffix=""):
    req = " required" if required else ""
    acx = f' autocomplete="{ac}"' if ac else ""
    described = f' aria-describedby="{fid}-hint"' if hint else ""
    hint_html = f'<p id="{fid}-hint" class="mt-1.5 text-sm text-muted">{esc(hint)}</p>' if hint else ""
    return (f'<div><label for="{fid}" class="block text-sm font-medium">{esc(label)}{suffix}</label>'
            f'<input id="{fid}" name="{fid}" type="{ftype}"{acx}{req}{described} '
            f'class="mt-1.5 block w-full rounded-lg border border-line bg-bg px-3.5 py-2.5 text-fg focus:border-primary focus:outline-none">'
            f'{hint_html}</div>')


def nojs_note(L):
    return f'<noscript><p class="mt-6 rounded-xl border border-line bg-surface p-4 text-sm text-muted">{fill(L["auth"]["nojs"], L)}</p></noscript>'


def auth_page(L, mode):
    a = L["auth"]; d = a[mode]
    other = "signup" if mode == "login" else "login"
    fields = ""
    if mode == "signup":
        fields += field("name", "text", a["name"], ac="name", required=False,
                        suffix=f' <span class="font-normal text-muted">({esc(a["name_opt"])})</span>')
    fields += field("email", "email", a["email"], ac="email")
    fields += field("password", "password", a["password"],
                    ac=("new-password" if mode == "signup" else "current-password"),
                    hint=(a["password_hint"] if mode == "signup" else ""))
    trial = f'<p class="mt-4 text-sm text-muted">{esc(d["trial_note"])}</p>' if mode == "signup" else ""
    inner = (f'<h1 class="text-3xl font-bold tracking-tight">{esc(d["h1"])}</h1>'
             f'<p class="mt-3 text-muted">{esc(d["sub"])}</p>'
             f'<p data-intent-note class="hidden mt-5 rounded-xl border border-accent/40 bg-accent/10 p-3.5 text-sm"></p>'
             f'<form data-auth-form="{mode}" novalidate class="mt-8 space-y-5">{fields}'
             f'<div data-form-error class="hidden rounded-xl border border-red-500/50 bg-red-500/10 p-4 text-sm" role="alert"></div>'
             f'<button type="submit" data-submit data-label="{esc(d["submit"])}" data-working="{esc(a["working"])}" '
             f'class="w-full rounded-lg bg-primary-strong px-4 py-2.5 font-semibold text-white hover:bg-primary-hover disabled:opacity-60">{esc(d["submit"])}</button>'
             f'</form>'
             f'<div data-auth-status class="mt-5" role="status" aria-live="polite"></div>'
             f'{trial}'
             f'<p class="mt-6 text-sm text-muted">{esc(d["alt"])} <a href="{url(L, other)}" data-carry-intent class="text-primary hover:underline">{esc(d["alt_link"])}</a></p>'
             f'<p class="mt-2 text-sm"><a href="{section_url(L, "pricing")}" class="text-muted hover:text-fg">{esc(a["back_pricing"])}</a></p>'
             f'{nojs_note(L)}')
    body = f'<div class="mx-auto max-w-md px-4 py-14 sm:px-6 sm:py-20">{inner}</div>'
    return head(L, mode, d["title"], d["desc"], data="full") + header(L, mode) + body + footer(L)


def account_page(L):
    ac = L["account"]
    def card(inner, attrs="", cls=""):
        return f'<section {attrs} class="rounded-2xl border border-line bg-surface p-6 {cls}">{inner}</section>'
    def dt_row(attrs, label_html, value_attr, cls=""):
        return (f'<div {attrs} class="flex justify-between gap-4 {cls}">{label_html}'
                f'<dd {value_attr} class="font-medium"></dd></div>')

    ident = card(f'<div class="flex flex-wrap items-center justify-between gap-3">'
                 f'<p data-identity class="hidden text-sm text-muted">{esc(ac["signed_in_as"])} <span data-email class="font-medium text-fg" dir="ltr"></span></p>'
                 f'<button type="button" data-signout class="rounded-lg border border-line bg-bg px-3.5 py-2 text-sm font-semibold hover:border-muted">{esc(ac["signout"])}</button></div>')
    plan_card = card(f'<h2 class="text-xl font-semibold">{esc(ac["plan_h"])}</h2>'
                     f'<p data-plan-name class="mt-3 text-3xl font-bold"></p>'
                     f'<dl class="mt-4 space-y-2 text-sm">'
                     + dt_row("", f'<dt class="text-muted">{esc(ac["status_l"])}</dt>', "data-status")
                     + dt_row("data-renew", '<dt data-renew-label class="text-muted"></dt>', "data-renew-value", "hidden")
                     + dt_row("data-provider-row", f'<dt class="text-muted">{esc(ac["provider_l"])}</dt>', "data-provider", "hidden")
                     + f'</dl><p data-status-note class="hidden mt-4 rounded-xl border border-line bg-bg p-3.5 text-sm text-muted"></p>',
                     "data-plan-card", "hidden")
    # Someone who has just paid must never be told they have no subscription.
    activating = card(f'<h2 class="text-xl font-semibold">{esc(ac["activating_h"])}</h2>'
                      f'<p class="mt-2 text-muted">{esc(ac["activating_p"])}</p>'
                      f'<button type="button" data-activating-retry class="mt-5 rounded-lg bg-primary-strong px-4 py-2.5 font-semibold text-white hover:bg-primary-hover disabled:opacity-60">{esc(ac["activating_btn"])}</button>',
                      "data-activating-card", "hidden")
    no_plan = card(f'<h2 class="text-xl font-semibold">{esc(ac["no_plan_h"])}</h2>'
                   f'<p class="mt-2 text-muted">{esc(ac["no_plan_p"])}</p>'
                   f'<a href="{section_url(L, "pricing")}" class="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary-strong px-4 py-2.5 font-semibold text-white hover:bg-primary-hover">{esc(ac["see_plans"])}{arrow()}</a>',
                   "data-no-plan-card", "hidden")
    manage = card(f'<h2 class="text-xl font-semibold">{esc(ac["manage_h"])}</h2>'
                  f'<p class="mt-2 text-muted">{esc(ac["manage_p"])}</p>'
                  f'<button type="button" data-portal class="mt-5 rounded-lg bg-primary-strong px-4 py-2.5 font-semibold text-white hover:bg-primary-hover disabled:opacity-60">{esc(ac["manage_btn"])}</button>'
                  f'<div data-portal-status class="mt-4" role="status" aria-live="polite"></div>',
                  "data-manage-card", "hidden")
    # store_p names the store ({store}), so site.js fills it when the card is shown.
    store = card(f'<h2 class="text-xl font-semibold">{esc(ac["store_h"])}</h2>'
                 f'<p data-store-text class="mt-2 text-muted"></p>', "data-store-card", "hidden")
    usage = card(f'<h2 class="text-xl font-semibold">{esc(ac["usage_h"])}</h2>'
                 f'<dl data-usage class="mt-4 space-y-3 text-sm"></dl>', "data-usage-card", "hidden")
    delete = card(f'<h2 class="text-xl font-semibold">{esc(ac["delete_h"])}</h2>'
                  f'<p class="mt-2 text-muted">{esc(ac["delete_p"])}</p>'
                  f'<a href="{url(L, "delete-account")}" class="mt-5 inline-flex rounded-lg border border-red-500/50 px-4 py-2.5 font-semibold text-red-600 hover:bg-red-500/10 dark:text-red-400">{esc(ac["delete_btn"])}</a>',
                  "", "border-red-500/30")
    body = (f'<div data-account class="mx-auto max-w-2xl px-4 py-14 sm:px-6 sm:py-20">'
            f'<h1 class="text-4xl font-bold tracking-tight">{esc(ac["h1"])}</h1>'
            f'<p data-account-loading class="mt-8 text-muted">{esc(ac["loading"])}</p>'
            f'<div data-account-status class="mt-8" role="status" aria-live="polite"></div>'
            f'<div data-account-body class="hidden mt-8 space-y-5">{ident}{plan_card}{activating}{no_plan}{manage}{store}{usage}{delete}</div>'
            f'{nojs_note(L)}</div>')
    return (head(L, "account", ac["title"], ac["desc"], noindex=True, data="full")
            + header(L, "account") + body + footer(L))


def billing_success(L):
    b = L["billing"]["success"]
    badges_success = store_badges(L, "success").replace(' id="download"', "")
    waiting = (f'<div data-state="wait"><h1 class="text-3xl font-bold tracking-tight">{esc(b["h1_wait"])}</h1>'
               f'<p class="mt-3 text-muted">{esc(b["wait_p"])}</p>'
               f'<div class="mt-6 h-1 w-full overflow-hidden rounded-full bg-line"><div class="h-1 w-1/3 animate-pulse rounded-full bg-primary"></div></div></div>')
    ok = (f'<div data-state="ok" class="hidden">'
          f'<div class="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent/15 text-accent">{icon("check")}</div>'
          f'<h1 class="mt-5 text-3xl font-bold tracking-tight">{esc(b["h1_ok"])}</h1>'
          f'<p class="mt-3 text-muted">{esc(b["ok_p"])}</p>'
          f'<dl class="mt-6 space-y-2 rounded-2xl border border-line bg-surface p-5 text-sm">'
          f'<div class="flex justify-between gap-4"><dt class="text-muted">{esc(b["plan_l"])}</dt><dd data-plan-name class="font-semibold"></dd></div>'
          f'<div data-renew class="hidden flex justify-between gap-4"><dt data-renew-label class="text-muted"></dt><dd data-renew-value class="font-semibold"></dd></div>'
          f'</dl>'
          # Two handoff variants; site.js reveals exactly one. A button that cannot
          # work is worse than no button, so the deep link is phone-only.
          f'<div data-handoff-mobile class="hidden mt-8">'
          f'<h2 class="text-xl font-semibold">{esc(b["next_h"])}</h2>'
          f'<p class="mt-2 text-muted">{esc(b["next_p"])}</p>'
          f'<a href="{APP_HANDOFF_URL}" class="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary-strong px-5 py-3 text-base font-semibold text-white hover:bg-primary-hover sm:w-auto">{esc(b["open_app"])}{arrow()}</a>'
          f'</div>'
          f'<div data-handoff-desktop class="hidden mt-8">'
          f'<h2 class="text-xl font-semibold">{esc(b["desktop_h"])}</h2>'
          f'<p data-desktop-text class="mt-2 text-muted">{esc(b["desktop_p_generic"])}</p>'
          f'<div class="mt-5">{badges_success}</div>'
          f'</div>'
          f'<a href="{url(L, "account")}" class="mt-8 inline-flex items-center gap-2 font-medium text-primary hover:underline">{esc(b["account_link"])}{arrow()}</a></div>')
    pending = (f'<div data-state="pending" class="hidden">'
               f'<h1 class="text-3xl font-bold tracking-tight">{esc(b["pending_h"])}</h1>'
               f'<p class="mt-3 text-muted">{fill(b["pending_p"], L)}</p>'
               f'<a href="{section_url(L, "support")}" class="mt-6 inline-flex items-center gap-2 font-medium text-primary hover:underline">{esc(L["nav"]["support"])}{arrow()}</a></div>')
    ref = (f'<p data-ref class="hidden mt-8 text-xs text-muted">{esc(b["ref"])}: '
           f'<span data-ref-value dir="ltr" class="break-all"></span></p>')
    body = (f'<div data-billing-success class="mx-auto max-w-xl px-4 py-16 sm:px-6 sm:py-24">'
            f'{waiting}{ok}{pending}{ref}{nojs_note(L)}</div>')
    return (head(L, "billing/success", b["title"], b["desc"], noindex=True, data="full")
            + header(L, "billing/success") + body + footer(L))


def billing_cancel(L):
    c = L["billing"]["cancel"]
    body = (f'<div class="mx-auto max-w-xl px-4 py-16 sm:px-6 sm:py-24">'
            f'<h1 class="text-3xl font-bold tracking-tight">{esc(c["h1"])}</h1>'
            f'<p class="mt-3 text-muted">{esc(c["p"])}</p>'
            f'<a href="{section_url(L, "pricing")}" class="mt-8 inline-flex items-center gap-2 rounded-lg bg-primary-strong px-4 py-2.5 font-semibold text-white hover:bg-primary-hover">{esc(c["back"])}{arrow()}</a></div>')
    return (head(L, "billing/cancel", c["title"], c["desc"], noindex=True)
            + header(L, "billing/cancel") + body + footer(L))


def app_handoff_page():
    """/app/billing/activated - the page the OS hides when the app is installed.
    No language prefix (the app claims one URL), so all three languages are
    rendered and site.js reveals the visitor's. English shows without JS."""
    blocks = ""
    for X in LANGS:
        a = X["app"]
        badges = store_badges(X, "app" + X["code"]).replace(' id="download"', "")
        blocks += (
            f'<div data-applang="{X["code"]}" lang="{X["code"]}" dir="{X["dir"]}" '
            f'class="{"" if X is LANGS[0] else "hidden "}text-center">'
            f'<div class="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent/15 text-accent">{icon("check")}</div>'
            f'<h1 class="mt-5 text-3xl font-bold tracking-tight">{esc(a["h1"])}</h1>'
            f'<p data-app-text class="mx-auto mt-4 max-w-md text-muted">{esc(a["p_generic"])}</p>'
            f'<h2 class="mt-8 text-sm font-semibold uppercase tracking-wide text-muted">{esc(a["get_h"])}</h2>'
            f'<div class="mt-4 flex flex-wrap justify-center gap-3">{badges}</div>'
            f'<a href="{lang_url(X, "account")}" class="mt-8 inline-flex items-center gap-2 font-medium text-primary hover:underline">{esc(a["account_link"])}{arrow()}</a>'
            f'</div>')
    switcher = "".join(
        f'<button type="button" data-applang-btn="{X["code"]}" lang="{X["code"]}" '
        f'class="rounded-md px-2.5 py-1 text-sm text-muted hover:text-fg aria-pressed:bg-primary/15 aria-pressed:font-medium aria-pressed:text-fg" '
        f'aria-pressed="{"true" if X is LANGS[0] else "false"}">{esc(X["native"])}</button>'
        for X in LANGS)
    island = data_island(LANGS[0], "min", {"app": {X["code"]: X["app"] for X in LANGS}})
    L0 = LANGS[0]
    return f'''<!DOCTYPE html>
<html lang="{L0["code"]}" dir="{L0["dir"]}" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(L0["app"]["title"])}</title>
<meta name="description" content="{esc(L0["app"]["desc"])}">
<meta name="robots" content="noindex,nofollow">
<link rel="canonical" href="{APP_HANDOFF_URL}">
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#0F172A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/styles.css">
<script>(function(){{var d=document.documentElement;d.classList.add('js');try{{if(localStorage.getItem('mizan-theme')==='light'){{d.classList.remove('dark');}}}}catch(e){{}}}})();</script>
{island}
</head>
<body class="min-h-screen bg-bg text-fg antialiased">
<main data-app-handoff class="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center gap-8 px-4 py-16">
<a href="/" class="flex items-center gap-2.5 font-semibold">{logo("a")}<span class="text-lg">Mizan</span></a>
<div class="w-full">{blocks}</div>
<nav aria-label="{esc(L0["app"]["lang_label"])}" class="flex items-center gap-0.5 rounded-lg border border-line bg-surface p-0.5">{switcher}</nav>
</main>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


# ---------- Language-free URL fallback ----------
def router(page=""):
    """site/<page>/index.html (and site/index.html for the home page): the page that
    answers a language-free URL when the host did not rewrite it. On Netlify the
    rules in _redirects (REDIRECTS) win over this file and serve the visitor's
    language directly; anywhere else this forwards to /<lang>/<page>/, and the
    snippet in that page's <head> hides the prefix again."""
    path = url(EN, page)
    links = "".join(f'<a href="{lang_url(X, page)}" hreflang="{X["code"]}" lang="{X["code"]}" dir="{X["dir"]}" data-lang="{X["code"]}" class="rounded-lg border border-line bg-surface px-5 py-2.5 hover:border-muted">{esc(X["native"])}</a>' for X in LANGS)
    alts = "".join(f'<link rel="alternate" hreflang="{X["code"]}" href="{DOMAIN}{lang_url(X, page)}">' for X in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{lang_url(EN, page)}">'
    return f'''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mizan · ميزان</title>
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{DOMAIN}{lang_url(EN, page)}">{alts}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/styles.css">
<script>(function(){{var l='en';try{{var s=localStorage.getItem('mizan-lang');if(s==='en'||s==='tr'||s==='ar')l=s;}}catch(e){{}}if(/(^|; )mizan_ar=/.test(document.cookie))l='ar';else if(/(^|; )mizan_tr=/.test(document.cookie))l='tr';location.replace('/'+l+'{path}'+location.search+location.hash);}})();</script>
<noscript><meta http-equiv="refresh" content="0; url={lang_url(EN, page)}"></noscript>
</head>
<body class="min-h-screen bg-bg text-fg antialiased">
<main class="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center gap-6 px-4 text-center">
{logo("r", 56)}<h1 class="text-2xl font-semibold">Mizan · ميزان</h1>
<p class="text-muted">{esc(EN["redirect"]["p"])}</p>
<div class="flex flex-wrap justify-center gap-3">{links}</div>
</main>
<script src="/assets/site.js" defer></script>
</body></html>'''

# ---------- Static extras ----------
def read_src(name):
    with open(os.path.join(os.path.dirname(__file__), name), encoding="utf-8") as f:
        return f.read()


# The client lives in src/site.js (real file, real tooling) and is copied verbatim.
SITE_JS = read_src("site.js")

# Android App Links. Served raw from the domain root, no redirect, no rewrite.
# TODO(owner): replace BOTH placeholders with real SHA-256 fingerprints.
#   TODO_UPLOAD_KEY        = your upload key certificate
#   TODO_PLAY_APP_SIGNING  = the Play app signing certificate
#     (Play Console > Release > Setup > App signing)
# Both are needed: builds you sideload are signed with the upload key, while what
# users install from Play is re-signed by Google. One fingerprint verifies only
# one of those. The value must stay a JSON array of one object.
ASSETLINKS = json.dumps([{
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
        "namespace": "android_app",
        "package_name": ANDROID_PACKAGE,
        "sha256_cert_fingerprints": ["TODO_UPLOAD_KEY", "TODO_PLAY_APP_SIGNING"],
    },
}], indent=2) + "\n"

# iOS Universal Links. Extensionless file; the content type is forced in _headers
# because Netlify cannot guess it. TODO(owner): replace TODO_TEAMID with the
# Apple Developer Team ID, so appID reads e.g. "ABCDE12345.com.mizan.app".
AASA = json.dumps({
    "applinks": {
        "apps": [],
        "details": [{"appID": "TODO_TEAMID." + IOS_BUNDLE, "paths": APP_LINK_PATHS}],
    },
}, indent=2) + "\n"

# connect-src must name the API or the browser blocks every call to it.
# With Paddle on, the CDN script, the checkout frame and the checkout service are
# added for that environment only; without them the overlay is blocked silently.
_PH = PADDLE_HOSTS[PADDLE["env"]] if PADDLE else {"script": [], "style": [], "frame": [], "connect": []}
_SCRIPT_SRC = " ".join(["'self'", "'unsafe-inline'"] + _PH["script"])
_STYLE_SRC = " ".join(["'self'"] + _PH["style"])
_CONNECT_SRC = " ".join(["'self'", API_BASE] + _PH["connect"])
_FRAME_SRC = ("frame-src " + " ".join(_PH["frame"]) + "; ") if _PH["frame"] else ""
CSP = (f"default-src 'self'; script-src {_SCRIPT_SRC}; style-src {_STYLE_SRC}; "
       "img-src 'self' data:; font-src 'self'; "
       f"connect-src {_CONNECT_SRC}; "
       + _FRAME_SRC
       + "form-action 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")

def sitemap():
    today = "2026-09-05"; out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in PAGES:
        for L in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{X["code"]}" href="{DOMAIN}{lang_url(X, p)}"/>' for X in LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN}{lang_url(AR, p)}"/>'
            out.append(f'<url><loc>{DOMAIN}{lang_url(L, p)}</loc><lastmod>{today}</lastmod>{alts}</url>')
    out.append("</urlset>"); return "\n".join(out)

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><defs><linearGradient id="g" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#14B8A6"/></linearGradient></defs><rect width="48" height="48" rx="11" fill="#0F172A"/><g fill="none" stroke="url(#g)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" transform="translate(4 4) scale(.833)"><path d="M24 9v31M17 40h14M7 15h34"/><circle cx="24" cy="9" r="2.4" fill="url(#g)"/><path d="M12 15 6 27h12zM36 15l-6 12h12z"/><path d="M6 27.5a6 6 0 0 0 12 0M30 27.5a6 6 0 0 0 12 0"/></g></svg>'''

HEADERS = f"""/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: {CSP}

/assets/*
  Cache-Control: public, max-age=86400

/.well-known/assetlinks.json
  Content-Type: application/json
  Cache-Control: public, max-age=300
  Access-Control-Allow-Origin: *

/.well-known/apple-app-site-association
  Content-Type: application/json
  Cache-Control: public, max-age=300
  Access-Control-Allow-Origin: *
"""

VERCEL = """{
  "trailingSlash": true,
  "headers": [
    { "source": "/(.*)", "headers": [
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
      { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" },
      { "key": "Content-Security-Policy", "value": "__CSP__" }
    ] },
    { "source": "/assets/(.*)", "headers": [ { "key": "Cache-Control", "value": "public, max-age=86400" } ] },
    { "source": "/.well-known/assetlinks.json", "headers": [ { "key": "Content-Type", "value": "application/json" } ] },
    { "source": "/.well-known/apple-app-site-association", "headers": [ { "key": "Content-Type", "value": "application/json" } ] }
  ]
}
""".replace("__CSP__", CSP)

# Every page that has a language-free URL (and so needs a rewrite and a fallback).
CLEAN_PAGES = list(dict.fromkeys(PAGES + NOINDEX_PAGES + list(MOVED_PAGES)))

def redirects():
    """Netlify: answer /privacy/ with /ar/privacy/ (or /tr/...) when the visitor's
    mizan_ar / mizan_tr cookie says so, English otherwise. Status 200 is a rewrite:
    the address bar keeps /privacy/ and the query string is passed through. The
    trailing ! forces the rule even though site/privacy/index.html (the router
    fallback) exists. Cookie conditions match the cookie NAME only, which is why
    there is one cookie per language and English is "neither". Exact paths only:
    this is not a catch-all, so /.well-known/* and /app/* are never touched."""
    out = ["# Generated by src/build.py (redirects()); do not edit this file.",
           "# Language-free URLs: rewrite (200, URL unchanged) to the visitor's language."]
    for page in CLEAN_PAGES:
        src = url(EN, page)
        for X in LANGS[1:]:
            out.append(f"{src} {lang_url(X, page)} 200! Cookie=mizan_{X['code']}")
        out.append(f"{src} {lang_url(EN, page)} 200!")
    return "\n".join(out) + "\n"

_FP = json.loads(ASSETLINKS)[0]["target"]["sha256_cert_fingerprints"]
ASSETLINKS_HAS_FINGERPRINT = bool(_FP) and not any(f.startswith("TODO") for f in _FP)
AASA_HAS_TEAM_ID = "TODO_TEAMID" not in AASA


# Files build.py does not generate and must therefore not delete.
KEEP = {"assets", "favicon.ico", "apple-touch-icon.png"}


def write(rel, content):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(content)

def main():
    if os.path.isdir(OUT):
        for n in os.listdir(OUT):
            if n in KEEP: continue  # never regenerated: compiled css, binary icons
            p = os.path.join(OUT, n); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for L in LANGS:
        write(f"{L['code']}/index.html", home(L))
        for old, (anchor, nav_key) in MOVED_PAGES.items():
            write(f"{L['code']}/{old}/index.html", moved_page(L, anchor, nav_key))
        write(f"{L['code']}/privacy/index.html", legal(L, "privacy"))
        write(f"{L['code']}/terms/index.html", legal(L, "terms"))
        write(f"{L['code']}/delete-account/index.html", delete_page(L))
        write(f"{L['code']}/login/index.html", auth_page(L, "login"))
        write(f"{L['code']}/signup/index.html", auth_page(L, "signup"))
        write(f"{L['code']}/account/index.html", account_page(L))
        write(f"{L['code']}/billing/success/index.html", billing_success(L))
        write(f"{L['code']}/billing/cancel/index.html", billing_cancel(L))
    for page in CLEAN_PAGES:   # fallback for hosts that ignore _redirects
        write(f"{page}/index.html" if page else "index.html", router(page))
    write("_redirects", redirects())
    write("assets/site.js", SITE_JS)
    write("favicon.svg", FAVICON)
    write("sitemap.xml", sitemap())
    write("robots.txt", "User-agent: *\nAllow: /\n"
                        "Disallow: /*/account/\nDisallow: /*/billing/\n"
                        "Disallow: /account/\nDisallow: /billing/\n\n"
                        f"Sitemap: {DOMAIN}/sitemap.xml\n")
    write(".well-known/assetlinks.json", ASSETLINKS)
    write(".well-known/apple-app-site-association", AASA)
    # Same bytes under a .json name. Netlify cannot be made to set Content-Type on
    # the extensionless file (neither _headers nor netlify.toml [[headers]] wins),
    # and iOS rejects anything but application/json. netlify.toml rewrites the
    # canonical path to this twin with status 200 - a rewrite, not a redirect:
    # the canonical URL still answers 200 itself, with no Location header.
    write(".well-known/aasa.json", AASA)
    # A FILE, not a directory: Netlify serves app/billing/activated.html at
    # /app/billing/activated with 200. A directory would make it 301 to a
    # trailing slash, and this URL must answer directly.
    write("app/billing/activated.html", app_handoff_page())
    write("_headers", HEADERS)
    write("vercel.json", VERCEL)
    write("404.html", head(EN, "", "Page not found — Mizan", "This page does not exist.").replace('<html lang="en" dir="ltr" class="dark">', '<html lang="en" class="dark">') + header(EN, "")
          + '<div class="mx-auto max-w-3xl px-4 py-24 text-center"><h1 class="text-4xl font-bold">404</h1><p class="mt-3 text-muted">This page does not exist.</p><div class="mt-6 flex justify-center gap-3">' + "".join(f'<a href="{lang_url(X)}" hreflang="{X["code"]}" lang="{X["code"]}" class="rounded-lg border border-line bg-surface px-4 py-2 hover:border-muted">{X["native"]}</a>' for X in LANGS) + "</div></div>" + footer(EN))
    print("site written to", os.path.abspath(OUT))
    print("   api      :", API_BASE)
    print("   app link:", APP_HANDOFF_URL)
    if PADDLE:
        print(f"   paddle   : {PADDLE['env'].upper()} checkout, token {PADDLE['token'][:9]}..., "
              f"{sum(len(v) for v in PADDLE['prices'].values())} prices")
        if PADDLE["env"] == "sandbox":
            print("   WARNING  : sandbox checkout build. Test cards only; do not deploy this build to production.")
    else:
        print("   paddle   : off (PADDLE_CLIENT_TOKEN not set); backend checkout flow")
    if not ASSETLINKS_HAS_FINGERPRINT:
        print("   WARNING  : .well-known/assetlinks.json still has TODO fingerprints "
              "(Android App Links stay unverified until both are real)")
    if not AASA_HAS_TEAM_ID:
        print("   WARNING  : .well-known/apple-app-site-association still has TODO_TEAMID "
              "(iOS Universal Links stay unverified until the Team ID is set)")

if __name__ == "__main__":
    main()
