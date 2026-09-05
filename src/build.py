#!/usr/bin/env python3
"""Generates the static Mizan site into ../site from the three i18n dictionaries.
Run:  python3 src/build.py   (then compile Tailwind, see README)"""
import os, sys, shutil, html
sys.path.insert(0, os.path.dirname(__file__))
from i18n_en import EN
from i18n_ar import AR
from i18n_tr import TR

DOMAIN = "https://mizan-ai.org"          # placeholder-free: chosen by owner
EMAIL = "support@mizan-ai.org"
OUT = os.path.join(os.path.dirname(__file__), "..", "site")
LANGS = [AR, EN, TR]                      # AR first = default
PAGES = ["", "pricing", "privacy", "terms", "delete-account", "support"]
PRICES = [  # tier index -> (monthly, yearly)
    (None, None), (4.99, 39.99), (7.99, 64.99), (12.99, 99.99),
]

def esc(s): return html.escape(s, quote=True)
CUR = ' aria-current="true"'
CURP = ' aria-current="page"'

def url(lang, page=""):
    return f"/{lang['code']}/" + (f"{page}/" if page else "")

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
        # STORE LINK PLACEHOLDER: replace href="#" with the real store URL
        return (f'<a href="{href}" class="inline-flex items-center gap-3 rounded-xl border border-line bg-surface px-4 py-2.5 text-fg hover:border-muted transition-colors" '
                f'aria-label="{esc(label)}" data-store-link>{ic}<span class="flex flex-col leading-tight text-start"><span class="text-[0.7rem] text-muted">{esc(top)}</span><span class="text-base font-semibold">{esc(name)}</span></span></a>')
    return ('<div class="flex flex-wrap items-center gap-3" id="download">'
            + badge("#", play, s["google"], s["google2"], f'{s["google"]} {s["google2"]}')
            + badge("#", apple, s["apple"], s["apple2"], f'{s["apple"]} {s["apple2"]}') + '</div>')

# ---------- Layout ----------
def head(L, page, title, desc):
    canon = DOMAIN + url(L, page)
    alts = "".join(f'<link rel="alternate" hreflang="{X["code"]}" href="{DOMAIN}{url(X, page)}">' for X in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{url(AR, page)}">'
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
</head>
<body class="min-h-screen bg-bg text-fg antialiased">
<a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:start-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-primary-strong focus:px-4 focus:py-2 focus:text-white">{esc(L["skip"])}</a>
'''

def lang_switcher(L, page, cls=""):
    items = ""
    for X in LANGS:
        cur = X["code"] == L["code"]
        a = (f'<a href="{url(X, page)}" hreflang="{X["code"]}" lang="{X["code"]}" data-lang="{X["code"]}" '
             f'class="rounded-md px-2.5 py-1 text-sm transition-colors {"bg-primary/15 text-fg font-medium" if cur else "text-muted hover:text-fg"}"'
             f'{CUR if cur else ""}>{esc(X["native"])}</a>')
        items += a
    return f'<nav aria-label="{esc(L["switcher"])}" class="flex items-center gap-0.5 rounded-lg border border-line bg-surface p-0.5 {cls}">{items}</nav>'

def theme_btn(L):
    return (f'<button type="button" data-theme-toggle class="js-only inline-flex h-9 w-9 items-center justify-center rounded-lg border border-line bg-surface text-muted hover:text-fg" aria-label="{esc(L["theme"])}" title="{esc(L["theme"])}">'
            f'<span class="dark:hidden">{icon("moon","h-5 w-5")}</span><span class="hidden dark:inline">{icon("sun","h-5 w-5")}</span></button>')

def header(L, page):
    n = L["nav"]; home = url(L)
    brand = "ميزان" if L["code"] == "ar" else "Mizan"
    links = [(home + "#features", n["features"]), (home + "#ai", n["ai"]), (url(L, "pricing"), n["pricing"]), (url(L, "support"), n["support"])]
    def nav(cls_a):
        return "".join(f'<a href="{h}" class="{cls_a}"{CURP if page and h == url(L, page) else ""}>{esc(t)}</a>' for h, t in links)
    return f'''<header class="sticky top-0 z-40 border-b border-line bg-bg/90 backdrop-blur">
<div class="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
<a href="{home}" class="flex items-center gap-2.5 font-semibold" aria-label="{esc(n["home"])}">{logo("h")}<span class="text-lg">{brand}</span></a>
<nav class="hidden items-center gap-1 md:flex" aria-label="Main">{nav("rounded-md px-3 py-2 text-sm text-muted hover:text-fg hover:bg-surface")}</nav>
<div class="hidden items-center gap-2 md:flex">{lang_switcher(L, page)}{theme_btn(L)}<a href="{home}#download" class="ms-1 rounded-lg bg-primary-strong px-4 py-2 text-sm font-semibold text-white hover:bg-primary-hover">{esc(n["download"])}</a></div>
<details class="relative md:hidden" data-menu>
<summary class="flex h-10 w-10 cursor-pointer list-none items-center justify-center rounded-lg border border-line bg-surface [&::-webkit-details-marker]:hidden" aria-label="{esc(n["menu"])}"><span class="[[open]_&]:hidden">{icon("menu","h-5 w-5")}</span><span class="hidden [[open]_&]:block">{icon("close","h-5 w-5")}</span></summary>
<div class="absolute end-0 top-12 w-64 rounded-xl border border-line bg-surface p-2 shadow-xl">
<nav class="flex flex-col" aria-label="Main">{nav("rounded-md px-3 py-2.5 text-fg hover:bg-bg")}</nav>
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
{col(f["product"], [(home + "#features", L["nav"]["features"]), (url(L, "pricing"), L["nav"]["pricing"]), (url(L, "support"), f["support"])])}
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
    cta = section("cta", f'<div class="rounded-3xl border border-line bg-gradient-to-br from-surface to-bg p-8 text-center sm:p-14"><h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{esc(h["cta_h2"])}</h2><p class="mx-auto mt-3 max-w-xl text-lg text-muted">{esc(h["cta_p"])}</p><div class="mt-8 flex justify-center">{badges_cta}</div><a href="{url(L, "pricing")}" class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline">{esc(h["pricing_link"])}{arrow()}</a></div>')
    return head(L, "", h["title"], h["desc"]) + header(L, "") + hero + features + ai + langs + priv + cta + footer(L)

# ---------- Pricing ----------
def pricing(L):
    p = L["pricing"]
    cards = ""
    for i, t in enumerate(p["tiers"]):
        m, y = PRICES[i]; pop = i == 2
        if m is None:
            price = f'<div class="mt-5"><div class="text-4xl font-bold">{esc(p["free"])}</div><div class="mt-1 text-sm text-muted">{esc(p["days"])}</div></div>'
            btn = f'<a href="{url(L)}#download" class="mt-6 block rounded-lg border border-line bg-bg px-4 py-2.5 text-center font-semibold hover:border-muted">{esc(p["trial_btn"])}</a>'
            inc = p["includes_first"]
        else:
            pct = round((1 - y / (m * 12)) * 100)
            price = (f'<div class="mt-5">'
                     f'<div class="m-only"><span class="text-4xl font-bold" dir="ltr">${m:.2f}</span><span class="text-muted">{esc(p["mo"])}</span></div>'
                     f'<div class="y-only"><span class="text-4xl font-bold" dir="ltr">${y:.2f}</span><span class="text-muted">{esc(p["yr"])}</span>'
                     f'<div class="mt-1 text-sm text-muted">{esc(p["eq"].format(m=f"{y/12:.2f}"))} · <span class="text-accent">{esc(p["save"].format(pct=pct))}</span></div></div>'
                     f'<div class="nojs-only mt-1 text-sm text-muted"><span dir="ltr">${y:.2f}</span>{esc(p["yr"])} · <span class="text-accent">{esc(p["save"].format(pct=pct))}</span></div>'
                     f'</div>')
            # SUBSCRIBE PLACEHOLDER: href="#" -> Stripe Checkout link (data-plan / data-billing tell you which)
            btn = (f'<a href="#" data-subscribe data-plan="{["trial","basic","smart","pro"][i]}" class="mt-6 block rounded-lg px-4 py-2.5 text-center font-semibold '
                   f'{"bg-primary-strong text-white hover:bg-primary-hover" if pop else "border border-line bg-bg hover:border-muted"}">{esc(p["subscribe"])}</a>')
            inc = p["includes"].format(prev=p["tiers"][i - 1]["name"])
        feats = "".join(f'<li class="flex gap-2.5"><span class="mt-0.5 text-accent">{icon("check","h-5 w-5")}</span><span>{esc(f)}</span></li>' for f in t["features"])
        badge = f'<span class="absolute -top-3 start-6 rounded-full bg-accent px-3 py-1 text-xs font-semibold text-slate-950">{esc(p["popular"])}</span>' if pop else ""
        cards += (f'<div class="relative flex flex-col rounded-2xl border {"border-accent ring-1 ring-accent" if pop else "border-line"} bg-surface p-6">{badge}'
                  f'<h2 class="text-xl font-semibold">{esc(t["name"])}</h2><p class="mt-1 text-sm text-muted">{esc(t["line"])}</p>{price}{btn}'
                  f'<p class="mt-6 text-xs font-semibold uppercase tracking-wide text-muted">{esc(inc)}</p><ul class="mt-3 space-y-2.5 text-sm">{feats}</ul></div>')
    toggle = (f'<div class="js-only mt-8 inline-flex rounded-lg border border-line bg-surface p-1" role="group" aria-label="{esc(p["monthly"])} / {esc(p["yearly"])}">'
              f'<button type="button" data-billing-btn="monthly" aria-pressed="true" class="rounded-md px-4 py-2 text-sm font-medium aria-pressed:bg-primary-strong aria-pressed:text-white">{esc(p["monthly"])}</button>'
              f'<button type="button" data-billing-btn="yearly" aria-pressed="false" class="rounded-md px-4 py-2 text-sm font-medium aria-pressed:bg-primary-strong aria-pressed:text-white">{esc(p["yearly"])}</button></div>')
    note = esc(p["note"]).replace("{terms}", f'<a href="{url(L, "terms")}" class="text-primary hover:underline">{esc(p["note_terms"])}</a>')
    body = (f'<div class="mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-20"><div class="text-center"><h1 class="text-4xl font-bold tracking-tight sm:text-5xl">{esc(p["h1"])}</h1><p class="mx-auto mt-4 max-w-2xl text-lg text-muted">{esc(p["sub"])}</p>{toggle}</div>'
            f'<div data-billing="monthly" class="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">{cards}</div><p class="mx-auto mt-10 max-w-2xl text-center text-sm text-muted">{note}</p></div>')
    return head(L, "pricing", p["title"], p["desc"]) + header(L, "pricing") + body + footer(L)

# ---------- Legal / text pages ----------
def fill(s, L):
    return (esc(s).replace("{email}", f'<a href="mailto:{EMAIL}" class="text-primary hover:underline" dir="ltr">{EMAIL}</a>')
            .replace("{date}", esc(L["date"]))
            .replace("{delete_link}", f'<a href="{url(L, "delete-account")}" class="text-primary hover:underline">{esc(L["footer"]["delete"])}</a>')
            .replace("{privacy_link}", f'<a href="{url(L, "privacy")}" class="text-primary hover:underline">{esc(L["footer"]["privacy"])}</a>'))

def blocks(items, L):
    out, ul = "", []
    def flush():
        nonlocal ul, out
        if ul: out += '<ul class="list-disc space-y-2 ps-6">' + "".join(f"<li>{x}</li>" for x in ul) + "</ul>"; ul = []
    for it in items:
        if it.startswith("- "): ul.append(fill(it[2:], L))
        else: flush(); out += f"<p>{fill(it, L)}</p>"
    flush(); return out

def doc_shell(L, page, d, inner):
    return (head(L, page, d["title"], d["desc"]) + header(L, page)
            + f'<article class="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20"><h1 class="text-4xl font-bold tracking-tight">{esc(d["h1"])}</h1>'
            + (f'<p class="mt-2 text-sm text-muted">{fill(d["updated"], L)}</p>' if "updated" in d else "")
            + f'<div class="doc mt-8 space-y-5 text-[1.0625rem] leading-relaxed">{inner}</div></article>' + footer(L))

def legal(L, page):
    d = L[page]
    inner = f"<p>{fill(d['intro'], L)}</p>" + "".join(f'<section><h2 class="mb-3 mt-10 text-2xl font-semibold">{esc(h)}</h2><div class="space-y-4">{blocks(items, L)}</div></section>' for h, items in d["sections"])
    return doc_shell(L, page, d, inner)

def delete_page(L):
    d = L["delete"]
    def h2(t): return f'<h2 class="mb-3 mt-10 text-2xl font-semibold">{esc(t)}</h2>'
    inner = (f"<p>{fill(d['intro'], L)}</p>"
             + h2(d["in_app_h"]) + '<ol class="list-decimal space-y-2 ps-6">' + "".join(f"<li>{fill(s, L)}</li>" for s in d["steps"]) + "</ol>"
             + f'<p class="mt-4 rounded-xl border border-line bg-surface p-4 text-sm text-muted">{fill(d["export_tip"], L)}</p>'
             + h2(d["email_h"]) + f"<p>{fill(d['email_p'], L)}</p>"
             + h2(d["what_h"]) + '<ul class="list-disc space-y-2 ps-6">' + "".join(f"<li>{fill(s, L)}</li>" for s in d["what"]) + "</ul>"
             + h2(d["kept_h"]) + '<ul class="list-disc space-y-2 ps-6">' + "".join(f"<li>{fill(s, L)}</li>" for s in d["kept"]) + "</ul>"
             + h2(d["time_h"]) + f"<p>{fill(d['time_p'], L)}</p>")
    return doc_shell(L, "delete-account", d, inner)

def support(L):
    d = L["support"]
    faq = "".join(f'<div class="rounded-2xl border border-line bg-surface p-5"><h3 class="text-lg font-semibold">{esc(q)}</h3><p class="mt-2 text-muted">{fill(a, L)}</p></div>' for q, a in d["faq"])
    inner = (f'<div class="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20"><h1 class="text-4xl font-bold tracking-tight">{esc(d["h1"])}</h1><p class="mt-3 text-lg text-muted">{esc(d["sub"])}</p>'
             f'<div class="mt-8 flex gap-4 rounded-2xl border border-line bg-surface p-6"><span class="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">{icon("mail")}</span><div><h2 class="text-xl font-semibold">{esc(d["email_h"])}</h2><p class="mt-2 text-muted">{fill(d["email_p"], L)}</p></div></div>'
             f'<h2 class="mt-12 text-2xl font-semibold">{esc(d["faq_h"])}</h2><div class="mt-5 space-y-4">{faq}</div></div>')
    return head(L, "support", d["title"], d["desc"]) + header(L, "support") + inner + footer(L)

# ---------- Root redirect ----------
def root():
    links = "".join(f'<a href="{url(X)}" hreflang="{X["code"]}" lang="{X["code"]}" dir="{X["dir"]}" data-lang="{X["code"]}" class="rounded-lg border border-line bg-surface px-5 py-2.5 hover:border-muted">{esc(X["native"])}</a>' for X in LANGS)
    alts = "".join(f'<link rel="alternate" hreflang="{X["code"]}" href="{DOMAIN}{url(X)}">' for X in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}/ar/">'
    return f'''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mizan · ميزان</title>
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{DOMAIN}/ar/">{alts}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/styles.css">
<script>(function(){{var l='ar';try{{var s=localStorage.getItem('mizan-lang');if(s==='en'||s==='tr'||s==='ar')l=s;}}catch(e){{}}location.replace('/'+l+'/');}})();</script>
<noscript><meta http-equiv="refresh" content="0; url=/ar/"></noscript>
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
SITE_JS = r"""(function () {
  'use strict';
  var d = document.documentElement;
  // Language choice: persist on click of any switcher link
  document.querySelectorAll('[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('mizan-lang', a.getAttribute('data-lang')); } catch (e) {}
    });
  });
  // Theme toggle
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () {
      var dark = d.classList.toggle('dark');
      try { localStorage.setItem('mizan-theme', dark ? 'dark' : 'light'); } catch (e) {}
      var m = document.querySelector('meta[name="theme-color"]');
      if (m) m.setAttribute('content', dark ? '#0F172A' : '#F8FAFC');
    });
  });
  // Pricing billing toggle
  var grid = document.querySelector('[data-billing]');
  if (grid) {
    var btns = document.querySelectorAll('[data-billing-btn]');
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-billing-btn');
        grid.setAttribute('data-billing', v);
        btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        document.querySelectorAll('[data-subscribe]').forEach(function (a) { a.setAttribute('data-billing', v); });
      });
    });
    document.querySelectorAll('[data-subscribe]').forEach(function (a) { a.setAttribute('data-billing', 'monthly'); });
  }
  // Close mobile menu when a link inside it is clicked
  var menu = document.querySelector('[data-menu]');
  if (menu) menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { menu.removeAttribute('open'); }); });
})();
"""

def sitemap():
    today = "2026-09-05"; out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in PAGES:
        for L in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{X["code"]}" href="{DOMAIN}{url(X, p)}"/>' for X in LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN}{url(AR, p)}"/>'
            out.append(f'<url><loc>{DOMAIN}{url(L, p)}</loc><lastmod>{today}</lastmod>{alts}</url>')
    out.append("</urlset>"); return "\n".join(out)

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><defs><linearGradient id="g" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#14B8A6"/></linearGradient></defs><rect width="48" height="48" rx="11" fill="#0F172A"/><g fill="none" stroke="url(#g)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" transform="translate(4 4) scale(.833)"><path d="M24 9v31M17 40h14M7 15h34"/><circle cx="24" cy="9" r="2.4" fill="url(#g)"/><path d="M12 15 6 27h12zM36 15l-6 12h12z"/><path d="M6 27.5a6 6 0 0 0 12 0M30 27.5a6 6 0 0 0 12 0"/></g></svg>'''

HEADERS = """/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'

/assets/*
  Cache-Control: public, max-age=86400
"""

VERCEL = """{
  "trailingSlash": true,
  "headers": [
    { "source": "/(.*)", "headers": [
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
      { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" },
      { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'" }
    ] },
    { "source": "/assets/(.*)", "headers": [ { "key": "Cache-Control", "value": "public, max-age=86400" } ] }
  ]
}
"""

def write(rel, content):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(content)

def main():
    if os.path.isdir(OUT):
        for n in os.listdir(OUT):
            if n in ("assets",): continue  # keep compiled css / images
            p = os.path.join(OUT, n); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for L in LANGS:
        write(f"{L['code']}/index.html", home(L))
        write(f"{L['code']}/pricing/index.html", pricing(L))
        write(f"{L['code']}/privacy/index.html", legal(L, "privacy"))
        write(f"{L['code']}/terms/index.html", legal(L, "terms"))
        write(f"{L['code']}/delete-account/index.html", delete_page(L))
        write(f"{L['code']}/support/index.html", support(L))
    write("index.html", root())
    write("assets/site.js", SITE_JS)
    write("favicon.svg", FAVICON)
    write("sitemap.xml", sitemap())
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    write("_headers", HEADERS)
    write("vercel.json", VERCEL)
    write("404.html", head(EN, "", "Page not found — Mizan", "This page does not exist.").replace('<html lang="en" dir="ltr" class="dark">', '<html lang="en" class="dark">') + header(EN, "")
          + '<div class="mx-auto max-w-3xl px-4 py-24 text-center"><h1 class="text-4xl font-bold">404</h1><p class="mt-3 text-muted">This page does not exist.</p><div class="mt-6 flex justify-center gap-3">' + "".join(f'<a href="{url(X)}" hreflang="{X["code"]}" lang="{X["code"]}" class="rounded-lg border border-line bg-surface px-4 py-2 hover:border-muted">{X["native"]}</a>' for X in LANGS) + "</div></div>" + footer(EN))
    print("site written to", os.path.abspath(OUT))

if __name__ == "__main__":
    main()
