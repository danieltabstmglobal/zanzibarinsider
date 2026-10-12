#!/usr/bin/env python3
"""Baut die statische Seite zanzibarinsider.com in allen Sprachen.

Aufruf:  python3 tools/build.py
Texte:   in den Seitenfunktionen unten mit tx("Deutsch", "English", ru="...", it="...").
         Fehlt eine Übersetzung, gilt Englisch (bzw. Deutsch für de).
Daten:   data/directory.json (Verzeichnis), data/comments.json (freigegebene Kommentare)
Neue Sprache: Code in LANGS eintragen und nach und nach ru=/it= ergänzen.
"""
import json, os, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://zanzibarinsider.com"
FT = "https://fumbatown.agency"
WA = "https://www.wohnsitzausland.com"
PA = "https://www.perspektiveausland.com"
WA_SZ = WA + "/laender/sansibar/"
WHATSAPP = "https://chat.whatsapp.com/CXYRM1ETmKn4OSwCPLrMH8?mode=gi_t"
FUMBA_TIMES = "https://fumba.town/the-fumba-times/"
MAIL = "office@fumbatown.agency"
TEL = "+49 155 630 586 76"
EDITORIAL_MAIL = "redaktion@zanzibarinsider.com"  # Platzhalter, Postfach einrichten

NOINDEX = {"kunden"}  # per Direktlink erreichbar, nicht in Sitemap
LANGS = ["de", "en"]               # später: "ru", "it"
LANG_NAMES = {"de": "DE", "en": "EN", "ru": "RU", "it": "IT"}
LOCALES = {"de": "de_DE", "en": "en_US", "ru": "ru_RU", "it": "it_IT"}

# Seitenkennung -> Pfad je Sprache (ohne Sprachpräfix)
SLUGS = {
    "index":      {"de": "", "en": ""},
    "reisen":     {"de": "reisen", "en": "travel"},
    "leben":      {"de": "leben", "en": "living"},
    "verzeichnis": {"de": "verzeichnis", "en": "directory"},
    "kunden":     {"de": "kunden", "en": "clients"},
}
L = "de"  # aktive Sprache, wird in build_lang gesetzt


def tx(de, en=None, **o):
    if L in o:
        return o[L]
    if L == "de":
        return de
    return en if en is not None else de


def lp():
    return "" if L == "de" else f"/{L}"


def url(page, anchor=""):
    path = page_path(page, L)
    return path + (f"#{anchor}" if anchor else "")


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- Daten
def load_dir():
    d = json.load(open(os.path.join(ROOT, "data/directory.json")))
    c = json.load(open(os.path.join(ROOT, "data/comments.json")))
    return d, c


def loc(v):
    """Wert, der str oder {de,en,...} sein kann."""
    if isinstance(v, dict):
        return v.get(L) or v.get("en") or v.get("de") or ""
    return v or ""


# ---------------------------------------------------------------- Bausteine
def nav_items():
    return [("index", tx("Start", "Home")), ("reisen", tx("Reisen", "Travel")),
            ("leben", tx("Leben auf Sansibar", "Living here")),
            ("verzeichnis", tx("Verzeichnis", "Directory"))]


def header(cur):
    items = "".join('<a href="%s"%s>%s</a>' % (url(p), ' aria-current="page"' if p == cur else "", t)
                    for p, t in nav_items())
    items += '<a href="%s">%s</a>' % (url("verzeichnis", "tipp"), tx("Mitmachen", "Join in"))
    sw = "".join(
        '<a href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (
            page_path(cur, l), l, l, ' aria-current="true"' if l == L else "", LANG_NAMES[l])
        for l in LANGS)
    return f'''<header class="site-header"><div class="wrap">
<a class="logo" href="{page_path('index', L)}">Zanzibar<span>Insider</span></a>
<button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
<nav class="nav">{items}<span class="langs">{sw}</span></nav>
</div></header>'''


def page_path(page, lang):
    s = SLUGS[page].get(lang, SLUGS[page]["en"])
    pre = "" if lang == "de" else f"/{lang}"
    return f"{pre}/{s}" if s else (pre + "/")


def footer():
    return f'''<footer class="site-footer"><div class="wrap">
<div class="foot">
<div><a class="logo" href="{page_path('index', L)}" style="display:inline-block;margin-bottom:.8rem">Zanzibar<span>Insider</span></a>
<p>{tx("Der Wegweiser für Sansibar: zum Reisen, zum Leben und für alle, die mit uns ankommen.", "Your guide to Zanzibar: for travelling, for living here and for everyone arriving with us.")}</p></div>
<div><h4>{tx("Entdecken", "Explore")}</h4><a href="{url('reisen')}">{tx("Reisen", "Travel")}</a><a href="{url('leben')}">{tx("Leben auf Sansibar", "Living here")}</a><a href="{url('verzeichnis')}">{tx("Verzeichnis", "Directory")}</a></div>
<div><h4>{tx("Initiiert von", "Initiated by")}</h4><a href="{FT}">FumbaTown Agency</a><a href="{PA}">Perspektive Ausland</a></div>
<div><h4>{tx("Weiterlesen", "Further reading")}</h4><a href="{WA_SZ}">Wohnsitz Ausland</a><a href="{FUMBA_TIMES}">The Fumba Times</a></div>
<div><h4>{tx("Kontakt", "Contact")}</h4><a href="{url('verzeichnis', 'tipp')}">{tx("Tipp einsenden", "Submit a tip")}</a><a href="mailto:{EDITORIAL_MAIL}">{EDITORIAL_MAIL}</a><a href="{WHATSAPP}">{tx("WhatsApp-Community", "WhatsApp community")}</a></div>
</div>
<div class="legal">{tx("Ein unabhängiges Community-Projekt, initiiert von FumbaTown Agency und Perspektive Ausland. Alle Angaben ohne Gewähr, keine Rechts-, Steuer- oder Anlageberatung.", "An independent community project, initiated by FumbaTown Agency and Perspektive Ausland. All information without guarantee, not legal, tax or investment advice.")} <a style="display:inline" href="{FT}/rechtliches">{tx("Impressum & Rechtliches", "Legal notice")}</a></div>
</div></footer>'''


def page(key, title, desc, body, hero_img, noindex=False):
    canon = SITE + page_path(key, L)
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{page_path(key, l)}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{page_path(key, "de")}">'
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "Zanzibar Insider",
                     "url": SITE, "inLanguage": L,
                     "publisher": {"@type": "Organization", "name": "FumbaTown Agency", "url": FT}}, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="{L}"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{'<meta name="robots" content="noindex, follow">' if noindex else ''}
<link rel="canonical" href="{canon}">{alts}
<meta property="og:type" content="website"><meta property="og:locale" content="{LOCALES[L]}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{SITE}/img/{hero_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230d2b33'/%3E%3Ctext x='32' y='45' font-size='38' text-anchor='middle' fill='%2327b3bf' font-family='Georgia' font-weight='700'%3EZ%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{ld}</script>
</head><body data-lang="{L}">
{header(key)}
{body}
{footer()}
<script src="/assets/site.js"></script>
</body></html>
'''


def hero(img, eyebrow, h1, lead, extra="", short=True, crumbs=""):
    cls = "hero short" if short else "hero home"
    return f'''<div class="{cls}" style="background-image:url('/img/{img}')"><div class="wrap">
{crumbs}<span class="eyebrow">{eyebrow}</span>
<h1>{h1}</h1><p class="lead">{lead}</p>{extra}
</div></div>'''


def crumbs(label):
    return f'<div class="crumbs"><a href="{page_path("index", L)}">{tx("Start", "Home")}</a> / {label}</div>'


def cta_band(h, p, primary=None, second=None):
    primary = primary or (f"{FT}/beratung", tx("Kostenloses Erstgespräch", "Free first consultation"))
    second = second or (f"{FT}/investorenreise", tx("Investorenreise ansehen", "See the investor trip"))
    return f'''<section class="cta-band"><div class="wrap narrow">
<h2>{h}</h2><p class="lead">{p}</p>
<div class="btn-row"><a class="btn btn-primary" href="{primary[0]}">{primary[1]}</a><a class="btn btn-ghost" href="{second[0]}">{second[1]}</a></div>
</div></section>'''


def about_block():
    return f'''<section class="about"><div class="wrap narrow">
<h3>{tx("Wer steckt dahinter?", "Who's behind this?")}</h3>
<p>{tx('Zanzibar Insider wurde von Menschen gestartet, die selbst auf Sansibar leben und arbeiten, unter anderem vom Team der <a href="' + FT + '">FumbaTown Agency</a> und von <a href="' + PA + '">Perspektive Ausland</a>. Die Seite ist offen für alle, die die Insel kennen: Tipps, Korrekturen und Erfahrungsberichte sind willkommen. Wer zu Steuern und Wegzug tiefer einsteigen will, findet das <a href="' + WA_SZ + '">Länderprofil Sansibar</a> bei Wohnsitz Ausland.',
'Zanzibar Insider was started by people who live and work on Zanzibar themselves, among others the team of <a href="' + FT + '">FumbaTown Agency</a> and <a href="' + PA + '">Perspektive Ausland</a>. The site is open to everyone who knows the island: tips, corrections and first-hand reports are welcome. For a deeper dive into taxes and leaving your home country, see the <a href="' + WA_SZ + '">Zanzibar country profile</a> at Wohnsitz Ausland.')}</p>
</div></section>'''


def contribute_band():
    return f'''<section class="band"><div class="wrap">
<div class="split"><div class="rv"><span class="eyebrow">{tx("Mitmachen", "Join in")}</span>
<h2>{tx("Du kennst Sansibar? <em>Hilf anderen.</em>", "You know Zanzibar? <em>Help others.</em>")}</h2>
<p class="lead">{tx("Das beste Wissen steckt in den Menschen vor Ort. Empfiehl uns den guten Anwalt, den fairen Fahrer, das Café mit dem echten Espresso. Wir prüfen Tipps redaktionell und kennzeichnen, was geprüft ist.", "The best knowledge sits with the people on the island. Recommend the good lawyer, the fair driver, the café with real espresso. We review tips editorially and mark what has been checked.")}</p>
<div class="btn-row"><a class="btn btn-primary" href="{url('verzeichnis', 'tipp')}">{tx("Tipp einsenden", "Submit a tip")}</a><a class="btn btn-line" href="{WHATSAPP}">{tx("WhatsApp-Community", "WhatsApp community")}</a></div></div>
<div class="rv"><div class="card"><h3>{tx("So funktioniert es", "How it works")}</h3>
<ul class="ticks"><li>{tx("Du schickst einen Tipp oder eine Korrektur.", "You send a tip or a correction.")}</li><li>{tx("Wir prüfen Angaben und Kontakt.", "We check details and contact.")}</li><li>{tx("Der Eintrag erscheint als <b>geprüft</b> oder als <b>ungeprüft</b> mit Quelle und Datum.", "The entry appears as <b>checked</b> or <b>unchecked</b> with source and date.")}</li><li>{tx("Alle können kommentieren. Kommentare erscheinen nach Freigabe.", "Everyone can comment. Comments appear after approval.")}</li></ul></div></div>
</div></div></section>'''


def badge(status):
    if status == "geprueft":
        return f'<span class="badge ok">✓ {tx("Geprüft", "Checked")}</span>'
    return f'<span class="badge un">{tx("Ungeprüft", "Unchecked")}</span>'


def entry_html(e, comments, compact=False):
    name = loc(e["name"])
    cat = e["cat"]
    meta = []
    if e.get("loc"):
        meta.append(f'<li>📍 {esc(loc(e["loc"]))}</li>')
    if e.get("phone"):
        tel = re.sub(r"[^+\d]", "", e["phone"])
        meta.append(f'<li>📞 <a href="tel:{tel}">{esc(e["phone"])}</a></li>')
    if e.get("url"):
        host = re.sub(r"^https?://(www\.)?", "", e["url"]).split("/")[0]
        meta.append(f'<li>🔗 <a href="{esc(e["url"])}" rel="noopener">{esc(host)}</a></li>')
    tip = f'<p class="tipline"><b>{tx("Richtwert", "Rule of thumb")}:</b> {esc(loc(e["tip"]))}</p>' if e.get("tip") else ""
    cl = comments.get(e["id"], [])
    cm = "".join(f'<div class="cmt"><b>{esc(c["name"])}</b> <span class="muted small">{esc(c["date"])}</span><p>{esc(c["text"])}</p></div>' for c in cl)
    status_txt = tx("Redaktionell geprüft", "Editorially checked") if e["status"] == "geprueft" else tx("Noch nicht von uns geprüft", "Not yet checked by us")
    search = esc((name + " " + loc(e.get("loc")) + " " + loc(e["text"])).lower())
    form = "" if compact else f'''<details class="cm"><summary>{tx("Kommentare", "Comments")} ({len(cl)})</summary><div class="in">{cm or '<p class="muted small">' + tx("Noch keine Kommentare.", "No comments yet.") + '</p>'}
<form class="cform" data-entry="{esc(e['id'])}"><input name="name" placeholder="{tx('Dein Name', 'Your name')}" maxlength="60" required>
<textarea name="text" rows="3" placeholder="{tx('Deine Erfahrung, Preis, Korrektur …', 'Your experience, price, correction …')}" maxlength="1200" required></textarea>
<input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
<button class="btn btn-line btn-sm" type="submit">{tx("Kommentar senden", "Send comment")}</button><span class="fmsg small" role="status"></span></form></div></details>'''
    return f'''<article class="entry rv" id="e-{esc(e['id'])}" data-cat="{cat}" data-status="{e['status']}" data-search="{search}">
<div class="ehead">{badge(e['status'])}<h3>{esc(name)}</h3></div>
<p>{esc(loc(e['text']))}</p>{tip}
<ul class="meta">{''.join(meta)}</ul>
<p class="src small muted">{status_txt} · {tx('Quelle', 'Source')}: {esc(e.get('source', ''))} · {tx('Stand', 'As of')} {e.get('checked', '')}</p>
{form}</article>'''


def submit_form(cats):
    opts = "".join(f'<option value="{c["id"]}">{c["icon"]} {loc(c)}</option>' for c in cats)
    return f'''<form class="tform card" id="tippform">
<div class="grid g2"><label>{tx("Kategorie", "Category")}<select name="cat">{opts}</select></label>
<label>{tx("Name des Ortes oder der Person", "Name of the place or person")}<input name="name" maxlength="120" required></label></div>
<label>{tx("Was sollen andere wissen? (Ort, Preis, Erfahrung)", "What should others know? (location, price, experience)")}<textarea name="text" rows="4" maxlength="2000" required></textarea></label>
<div class="grid g2"><label>{tx("Telefon, Link oder Adresse (optional)", "Phone, link or address (optional)")}<input name="contact" maxlength="200"></label>
<label>{tx("Dein Name und Kontakt für Rückfragen (optional)", "Your name and contact for follow-up (optional)")}<input name="from" maxlength="160"></label></div>
<input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="chk"><input type="checkbox" name="ok" required> {tx("Ich bin einverstanden, dass mein Tipp redaktionell geprüft und veröffentlicht werden kann. Persönliche Angaben bleiben intern.", "I agree that my tip may be reviewed and published. Personal details stay internal.")}</label>
<button class="btn btn-primary" type="submit">{tx("Tipp absenden", "Send tip")}</button><span class="fmsg" role="status"></span>
<p class="small muted">{tx("Klappt das Formular nicht, schreib an", "If the form fails, write to")} <a href="mailto:{MAIL}?subject=Zanzibar%20Insider%20Tipp">{MAIL}</a>.</p>
</form>'''


# ---------------------------------------------------------------- Seiten
def p_index(d, c):
    cats = d["categories"]
    ents = {e["id"]: e for e in d["entries"]}
    quick = "".join(f'<a class="qcat rv" href="{url("verzeichnis")}?c={x["id"]}"><span>{x["icon"]}</span><b>{loc(x)}</b></a>' for x in cats[:6])
    body = hero("strand_luftbild.webp", tx("Indischer Ozean · Tansania", "Indian Ocean · Tanzania"),
                tx("Sansibar. <em>Entdecken.</em> Bleiben. Ankommen.", "Zanzibar. <em>Discover.</em> Stay. Arrive."),
                tx("Strände und Stone Town für die Reise, Visa, Kosten und Alltag für ein Leben auf der Insel, und Tipps von Menschen, die hier wohnen.",
                   "Beaches and Stone Town for your trip, visas, costs and daily life for living on the island, and tips from people who live here."),
                f'<div class="btn-row"><a class="btn btn-primary" href="{url("reisen")}">{tx("Reise planen", "Plan a trip")}</a><a class="btn btn-ghost" href="{url("leben")}">{tx("Hier leben", "Live here")}</a></div>',
                short=False)
    body += f'''
<section class="paths"><div class="wrap"><div class="grid g3">
<a class="path rv" href="{url('reisen')}"><img src="/img/lagune_strand.webp" alt="{tx('Weißer Strand zwischen Felsen auf Sansibar', 'White beach between rocks on Zanzibar')}" loading="lazy">
<div class="body"><span class="tag">A · {tx('Für Reisende', 'For travellers')}</span><h3>{tx('Sansibar bereisen', 'Travel Zanzibar')}</h3>
<p>{tx('Beste Reisezeit, Strände, Stone Town, Einreise, Mietwagen, Taxi und Notfallnummern.', 'Best time to go, beaches, Stone Town, entry, car rental, taxis and emergency numbers.')}</p><span class="go">{tx('Zum Reiseführer →', 'To the travel guide →')}</span></div></a>
<a class="path rv" href="{url('leben')}"><img src="/img/fumbatown_stadtbild_am_meer.webp" alt="Fumba Town" loading="lazy">
<div class="body"><span class="tag">B · {tx('Für Expats', 'For expats')}</span><h3>{tx('Länger bleiben', 'Stay longer')}</h3>
<p>{tx('Aufenthalt, Ruhestandsvisum, Steuern, Kosten, Einkaufen und Anwältin.', 'Residency, retirement visa, taxes, costs, shopping and lawyer.')}</p><span class="go">{tx('Leben auf Sansibar →', 'Living on Zanzibar →')}</span></div></a>
<a class="path rv" href="{url('verzeichnis')}"><img src="/img/fumbatown_projekt_luftaufnahme_stadtansicht.webp" alt="Fumba Town" loading="lazy">
<div class="body"><span class="tag">C · {tx('Für Bewohner', 'For residents')}</span><h3>{tx('Schon hier?', 'Already here?')}</h3>
<p>{tx('Verzeichnis, Märkte, Ärzte, Handwerker und die Community.', 'Directory, markets, doctors, tradespeople and the community.')}</p><span class="go">{tx('Zum Verzeichnis →', 'To the directory →')}</span></div></a>
</div></div></section>

<section><div class="wrap"><div class="grid g4">
<div class="fact rv"><b>{tx('90 Tage', '90 days')}</b><span>{tx('Besuchsvisum für Touristen, online oder bei Ankunft', 'Visitor visa for tourists, online or on arrival')}</span></div>
<div class="fact rv"><b>15–25 min</b><span>{tx('Vom Flughafen nach Fumba Town', 'From the airport to Fumba Town')}</span></div>
<div class="fact rv"><b>~27 °C</b><span>{tx('Durchschnittstemperatur im Jahresverlauf', 'Average temperature over the year')}</span></div>
<div class="fact rv"><b>UNESCO</b><span>{tx('Stone Town ist seit 2000 Welterbe', 'Stone Town has been a World Heritage Site since 2000')}</span></div>
</div></div></section>

<section class="band"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Insider-Verzeichnis', 'Insider directory')}</span><h2>{tx('Wo gibt es was? <em>Von Menschen vor Ort.</em>', 'Where to find what? <em>By people on the ground.</em>')}</h2>
<p class="lead">{tx('Mietwagen, Krankenhaus, Anwältin, Supermarkt, italienischer Espresso: ein wachsendes Verzeichnis, redaktionell als geprüft oder ungeprüft gekennzeichnet, mit Kommentaren der Community.', 'Rental car, hospital, lawyer, grocery, Italian espresso: a growing directory, editorially marked as checked or unchecked, with community comments.')}</p></div>
<div class="qgrid">{quick}</div>
<div class="btn-row"><a class="btn btn-primary" href="{url('verzeichnis')}">{tx('Zum Verzeichnis', 'Open the directory')}</a><a class="btn btn-line" href="{url('verzeichnis', 'tipp')}">{tx('Tipp einsenden', 'Submit a tip')}</a></div>
</div></section>
''' + f'''
<section><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">A · {tx('Für Reisende', 'For travellers')}</span><h2>{tx('Eine Insel, <em>viele Gesichter</em>', 'One island, <em>many faces</em>')}</h2>
<p class="lead">{tx('Arabische, indische, persische und afrikanische Einflüsse treffen auf türkisfarbenes Wasser. Vom lebhaften Nungwi bis ins ruhige Jambiani findest du den Strand, der zu dir passt.', 'Arabic, Indian, Persian and African influences meet turquoise water. From lively Nungwi to quiet Jambiani you will find the beach that suits you.')}</p>
<div class="btn-row"><a class="btn btn-primary" href="{url('reisen')}">{tx('Reiseführer öffnen', 'Open the travel guide')}</a></div></div>
<div class="media rv"><img src="/img/bunte_boote.webp" alt="{tx('Bunte Boote vor Sansibar', 'Colourful boats off Zanzibar')}" loading="lazy"></div>
</div></div></section>
''' + magazine_band() + contribute_band() + about_block()
    return (tx("Zanzibar Insider: Sansibar entdecken, bleiben, ankommen", "Zanzibar Insider: discover, stay and arrive on Zanzibar"),
            tx("Der unabhängige Wegweiser für Sansibar: Reisetipps, Leben und Alltag auf der Insel und ein Verzeichnis mit Empfehlungen von Menschen vor Ort.",
               "The independent guide to Zanzibar: travel tips, living and daily life on the island, and a directory of recommendations from people on the ground."),
            body, "strand_luftbild.webp")


def magazine_band():
    return f'''<section><div class="wrap"><div class="split flip">
<div class="rv"><span class="eyebrow">{tx('Lesetipp', 'Reading tip')}</span><h2>The Fumba <em>Times</em></h2>
<p class="lead">{tx('Das kostenlose Magazin aus Fumba Town: Wirtschaft, Kultur, Gesundheit, Einkaufsratgeber und Veranstaltungen rund um die Insel. Vierteljährlich als PDF, dazu laufend neue Artikel. Auf Englisch, und es lohnt sich.', 'The free magazine from Fumba Town: business, culture, health, shopping guides and events around the island. Quarterly as a PDF with new articles online in between. Well worth a read.')}</p>
<div class="btn-row"><a class="btn btn-primary" href="{FUMBA_TIMES}">{tx('Magazin lesen', 'Read the magazine')}</a></div></div>
<div class="media rv"><img src="/img/strand_restaurant.webp" alt="{tx('Strandrestaurant', 'Beach restaurant')}" loading="lazy"></div>
</div></div></section>'''


def p_reisen(d, c):
    months = [("Jan", 28, "dry"), ("Feb", 29, "dry"), ("Mär" if L == "de" else "Mar", 30, "wet"), ("Apr", 28, "wet"),
              (tx("Mai", "May"), 26, "wet"), ("Jun", 25, "dry"), ("Jul", 25, "dry"), ("Aug", 26, "dry"), ("Sep", 27, "dry"),
              ("Okt" if L == "de" else "Oct", 28, "mix"), ("Nov", 28, "wet"), ("Dez" if L == "de" else "Dec", 28, "dry")]
    mh = "".join(f'<div class="m {k}">{m}<i>{t}°</i></div>' for m, t, k in months)

    def beach(n, t, dsc):
        return f'<div class="beach rv"><b>{n}</b><span><strong>{t}.</strong> {dsc}</span></div>'
    beaches = (
        beach("Nungwi", tx("Nordküste, lebhaft", "North coast, lively"), tx("Beliebt für Sonnenuntergänge, Strandbars und Tauchen.", "Popular for sunsets, beach bars and diving.")) +
        beach("Kendwa", tx("Nordwesten, entspannt", "North-west, relaxed"), tx("Breiter Strand, gut zum Baden, auch bei Ebbe.", "Wide beach, good for swimming, even at low tide.")) +
        beach("Paje", tx("Ostküste, Kitesurf", "East coast, kitesurfing"), tx("Afrikas bekannter Kitesurf-Spot mit Schulen für alle Niveaus.", "Africa's well-known kitesurf spot with schools for all levels.")) +
        beach("Matemwe", tx("Nordosten, romantisch", "North-east, romantic"), tx("Ruhiger Strand, Ausgangspunkt für das Mnemba-Atoll.", "Quiet beach, starting point for Mnemba Atoll.")) +
        beach("Jambiani", tx("Südosten, authentisch", "South-east, authentic"), tx("Dörflicher Charakter, Seetangfarmen und Ruhe.", "Village feel, seaweed farms and calm.")) +
        beach("Fumba", tx("Südwesten, ruhig", "South-west, calm"), tx("Beach Club und Lagune bei Fumba Town, nah am Flughafen.", "Beach club and lagoon at Fumba Town, close to the airport.")))
    ents = {e["id"]: e for e in d["entries"]}
    ve = lambda i: entry_html(ents[i], c, compact=True)
    body = hero("lagune_strand.webp", "A · " + tx("Für Reisende", "For travellers"),
                tx("Dein Sansibar-<em>Reiseführer</em>", "Your Zanzibar <em>travel guide</em>"),
                tx("Von der Einreise bis zum Sundowner. Alles, was du für eine Reise nach Sansibar wissen musst.", "From entry to sundowner. Everything you need to know for a trip to Zanzibar."),
                crumbs=crumbs(tx("Reisen", "Travel")))
    body += f'''
<nav class="subnav" aria-label="{tx('Seitenübersicht', 'On this page')}"><div class="wrap">
<a href="#reisezeit">{tx('Reisezeit', 'When to go')}</a><a href="#straende">{tx('Strände', 'Beaches')}</a><a href="#stonetown">Stone Town</a><a href="#erlebnisse">{tx('Erlebnisse', 'Experiences')}</a><a href="#einreise">{tx('Einreise', 'Entry')}</a><a href="#unterwegs">{tx('Unterwegs', 'Getting around')}</a><a href="#notfall">{tx('Notfall', 'Emergency')}</a><a href="#auszeit">{tx('Auszeit', 'Getaways')}</a><a href="#anreise">{tx('Anreise', 'Getting here')}</a>
</div></nav>

<section id="reisezeit"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Wetter & Reisezeit', 'Weather & season')}</span><h2>{tx('Wann ist die <em>beste Zeit</em>?', 'When is the <em>best time</em>?')}</h2>
<p class="lead">{tx('Rund 27 °C im Jahresmittel. Zwei Regenzeiten bestimmen, wann du am meisten Sonne hast.', 'Around 27 °C on average. Two rainy seasons decide when you get the most sun.')}</p></div>
<div class="months rv">{mh}</div>
<div class="legend"><span><i style="background:#f6d9a8"></i>{tx('Trockenzeit', 'Dry season')}</span><span><i style="background:#bfdde2"></i>{tx('Regenzeit', 'Rainy season')}</span><span><i style="background:#e8e2cf"></i>{tx('Übergang', 'Transition')}</span><span>{tx('Typische Tageshöchsttemperatur in °C', 'Typical daily high in °C')}</span></div>
<div class="grid g3" style="margin-top:2rem">
<div class="card rv"><h3>{tx('Juni – September', 'June – September')}</h3><p><strong>{tx('Beste Reisezeit.', 'Best time to go.')}</strong> {tx('Große Trockenzeit mit 25 bis 27 °C, ideal für Strand und Ausflüge. Hochsaison, früh buchen.', 'Long dry season at 25 to 27 °C, ideal for beach and excursions. High season, book early.')}</p></div>
<div class="card rv"><h3>{tx('Dezember – Februar', 'December – February')}</h3><p><strong>{tx('Sehr gut.', 'Very good.')}</strong> {tx('Kurze Trockenzeit mit 28 bis 29 °C. Weihnachten und Silvester sind schnell ausgebucht.', 'Short dry season at 28 to 29 °C. Christmas and New Year book out fast.')}</p></div>
<div class="card rv"><h3>{tx('März – Mai', 'March – May')}</h3><p><strong>{tx('Große Regenzeit (Masika).', 'Long rains (Masika).')}</strong> {tx('Intensive Regenfälle, dafür die niedrigsten Preise und wenige Gäste.', 'Heavy rain, but the lowest prices and few visitors.')}</p></div>
</div></div></section>

<section id="straende" class="band"><div class="wrap"><div class="split flip">
<div><span class="eyebrow">{tx('Küste & Meer', 'Coast & sea')}</span><h2>{tx('Die schönsten <em>Strände</em>', 'The most beautiful <em>beaches</em>')}</h2>
<p class="lead">{tx('Jeder Strand hat seinen eigenen Charakter, von lebhaft bis wildromantisch.', 'Every beach has its own character, from lively to wild and romantic.')}</p>
<div style="margin-top:1rem">{beaches}</div></div>
<div class="media"><img src="/img/typischer_sansibar_strand_blaues_meer.webp" alt="{tx('Typischer Sansibar-Strand mit blauem Meer', 'Typical Zanzibar beach with blue sea')}" loading="lazy"></div>
</div></div></section>

<section id="stonetown"><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">{tx('UNESCO-Welterbe', 'UNESCO World Heritage')}</span><h2>Stone Town, <em>{tx('das Herz der Insel', 'the heart of the island')}</em></h2>
<p class="lead">{tx('Seit 2000 UNESCO-Weltkulturerbe. Verwinkelte Gassen, geschnitzte Türen, Moscheen und Märkte erzählen von Jahrhunderten Handel zwischen Arabien, Indien und Ostafrika.', 'A UNESCO World Heritage Site since 2000. Winding alleys, carved doors, mosques and markets tell of centuries of trade between Arabia, India and East Africa.')}</p>
<ul class="ticks"><li><strong>Forodhani Night Market:</strong> {tx('Seafood, Zanzibar-Pizza und frische Säfte am Wasser', 'seafood, Zanzibar pizza and fresh juices by the water')}</li>
<li><strong>{tx('Die alten Türen', 'The old doors')}:</strong> {tx('arabische und indische Schnitzkunst als Wahrzeichen', 'Arabic and Indian carving as a landmark')}</li>
<li><strong>House of Wonders:</strong> {tx('ehemaliger Sultanspalast', "former sultan's palace")}</li>
<li><strong>Spice Farm Tour:</strong> {tx('Nelken, Zimt und Vanille auf den Plantagen im Umland', 'cloves, cinnamon and vanilla on the plantations nearby')}</li></ul></div>
<div class="media rv"><img src="/img/historisches_gebo_ude_in_stonetown.webp" alt="{tx('Historisches Gebäude in Stone Town', 'Historic building in Stone Town')}" loading="lazy"></div>
</div></div></section>

<section id="erlebnisse" class="band"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Erlebnisse', 'Experiences')}</span><h2>{tx('Was du <em>erleben</em> kannst', 'What you can <em>experience</em>')}</h2></div>
<div class="gallery">
<figure class="tall rv"><img src="/img/schildkro_ten_im_meer.webp" alt="{tx('Schildkröten im Meer', 'Turtles in the sea')}" loading="lazy"><figcaption>{tx('Schnorcheln & Tauchen: Mnemba-Atoll', 'Snorkelling & diving: Mnemba Atoll')}</figcaption></figure>
<figure class="rv"><img src="/img/strand_mit_holzboot.webp" alt="{tx('Strand mit Holzboot', 'Beach with wooden boat')}" loading="lazy"><figcaption>{tx('Kitesurfen in Paje', 'Kitesurfing in Paje')}</figcaption></figure>
<figure class="rv"><img src="/img/segelboot_im_meer.webp" alt="{tx('Segelboot im Meer', 'Sailing boat at sea')}" loading="lazy"><figcaption>{tx('Dhow-Touren & Sundowner', 'Dhow trips & sundowners')}</figcaption></figure>
<figure class="rv"><img src="/img/restaurant_auf_dem_felsen.webp" alt="{tx('Restaurant auf dem Felsen im Meer', 'Restaurant on the rock in the sea')}" loading="lazy"><figcaption>{tx('Restaurant auf dem Felsen', 'Restaurant on the rock')}</figcaption></figure>
<figure class="rv"><img src="/img/boot_und_massai_am_strand.webp" alt="{tx('Boot und Massai am Strand', 'Boat and Maasai on the beach')}" loading="lazy"><figcaption>{tx('Kultur & Begegnung', 'Culture & encounters')}</figcaption></figure>
</div>
<div class="grid g3" style="margin-top:2rem">
<div class="card rv"><h3>{tx('Delfin-Touren', 'Dolphin tours')}</h3><p>{tx('Von Kizimkazi aus. Schwimmen mit freilebenden Delfinen, gut für Familien.', 'From Kizimkazi. Swim with wild dolphins, good for families.')}</p></div>
<div class="card rv"><h3>{tx('Höhlen & Mangroven', 'Caves & mangroves')}</h3><p>{tx('Kuza Cave mit Süßwasser oder Kajak durch die Mangroven.', 'Kuza Cave with fresh water or kayaking through the mangroves.')}</p></div>
<div class="card rv"><h3>{tx('Safari auf dem Festland', 'Mainland safari')}</h3><p>{tx('Mikumi oder Selous lassen sich gut mit dem Strandurlaub verbinden.', 'Mikumi or Selous combine well with a beach holiday.')}</p></div>
</div></div></section>

<section id="einreise"><div class="wrap narrow">
<div class="head"><span class="eyebrow">{tx('Einreise & Versicherung', 'Entry & insurance')}</span><h2>{tx('Visum und Pflichtversicherung <em>ohne Stress</em>', 'Visa and mandatory insurance <em>without stress</em>')}</h2></div>
<details open><summary>{tx('Touristenvisum (eVisa) ausfüllen: Tipps', 'Filling in the tourist visa (eVisa): tips')}</summary><div class="in"><ul>
<li>{tx('Beantragen kannst du es online vor der Reise oder bei Ankunft am Flughafen. Online spart in der Hochsaison oft 20 bis 45 Minuten am Schalter. Kosten: 50 USD, gültig bis 90 Tage.', 'You can apply online before the trip or on arrival at the airport. Online often saves 20 to 45 minutes at the counter in high season. Cost: 50 USD, valid up to 90 days.')}</li>
<li>{tx('Name, Geburtsdatum und Passnummer genau so eintragen wie im Reisepass. Der Pass muss noch mindestens sechs Monate gültig sein.', 'Enter name, date of birth and passport number exactly as in the passport. The passport must be valid for at least six more months.')}</li>
<li>{tx('Bei der Adresse der Unterkunft genügt der Name der Unterkunft oder „Fumba Town“. Beruf ehrlich angeben, auch „self-employed“ ist in Ordnung.', 'For the address of your accommodation the name of the accommodation or "Fumba Town" is enough. State your profession honestly, "self-employed" is fine.')}</li>
<li>{tx('Ein Passfoto und ein Scan der Passseite bereithalten. Bestätigung ausdrucken oder offline auf dem Handy speichern, das Netz am Flughafen ist nicht immer stabil.', 'Have a passport photo and a scan of the passport page ready. Print the confirmation or save it offline on your phone, the network at the airport is not always stable.')}</li>
<li>{tx('Ein Foto wird zusätzlich am Schalter gemacht. Formulare ändern sich, im Zweifel zählt die Anzeige auf dem offiziellen Portal.', 'A photo is also taken at the counter. Forms change, in case of doubt what the official portal shows applies.')}</li></ul>
<p><a class="btn btn-line btn-sm" href="https://visa.immigration.go.tz">visa.immigration.go.tz</a></p></div></details>
<details><summary>{tx('Pflichtversicherung (ZIC) abschließen: Tipps', 'Taking out the mandatory insurance (ZIC): tips')}</summary><div class="in"><ul>
<li>{tx('Seit 1.10.2024 ist die Versicherung für Reisende nach Sansibar vorgeschrieben, etwa 44 USD pro Person, mit Familienrabatten. Abschluss online in wenigen Minuten.', 'Since 1 October 2024 the insurance is required for visitors to Zanzibar, about 44 USD per person, with family discounts. Takes a few minutes online.')}</li>
<li>{tx('Eine Pflichtpolice ersetzt keine Auslandskrankenversicherung. Zusätzlich eine private Versicherung mit Rückholung abschließen.', 'The mandatory policy does not replace travel health insurance. Add a private policy with repatriation.')}</li>
<li>{tx('Bestätigung bei Ankunft bereithalten, am besten ausgedruckt.', 'Have the confirmation ready on arrival, best printed.')}</li></ul>
<p><a class="btn btn-line btn-sm" href="https://visitzanzibar.go.tz">visitzanzibar.go.tz</a></p></div></details>
<details><summary>{tx('Gesundheit, Geld, SIM', 'Health, money, SIM')}</summary><div class="in"><ul>
<li>{tx('Keine Pflichtimpfungen. Empfohlen: Hepatitis A und B, Tetanus, Diphtherie, Typhus. Gelbfieber nur bei Einreise aus Endemiegebieten.', 'No mandatory vaccinations. Recommended: hepatitis A and B, tetanus, diphtheria, typhoid. Yellow fever only when arriving from endemic areas.')}</li>
<li>{tx('Mückenschutz, nur abgefülltes Wasser, Sonnencreme SPF 30 oder höher, Mittagshitze von 12 bis 15 Uhr meiden.', 'Mosquito protection, bottled water only, sunscreen SPF 30 or higher, avoid the midday heat from 12 to 3 pm.')}</li>
<li>{tx('Währung ist der Tansanische Schilling, US-Dollar werden in Touristengebieten akzeptiert. Etwa 2.700 bis 2.900 TZS je Euro, am Flughafen ist der Kurs oft schlechter. Geldautomaten in Stone Town und Fumba Town.', 'The currency is the Tanzanian shilling, US dollars are accepted in tourist areas. About 2,700 to 2,900 TZS per euro, the airport rate is often worse. ATMs in Stone Town and Fumba Town.')}</li>
<li>{tx('Lokale SIM (Vodacom, Airtel, Zantel) für ca. 25 USD inklusive Datenpaket, am besten direkt nach der Gepäckausgabe.', 'Local SIM (Vodacom, Airtel, Zantel) for about 25 USD including data, best bought right after baggage claim.')}</li>
<li>{tx('Kultur: In den Städten Schultern und Knie bedecken, vor Fotos von Menschen fragen. „Mambo“ und „Habari“ sind die Standardgrüße.', 'Culture: in towns cover shoulders and knees, ask before photographing people. "Mambo" and "Habari" are the standard greetings.')}</li></ul></div></details>
</div></section>

<section id="unterwegs" class="band"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Unterwegs', 'Getting around')}</span><h2>{tx('Mietwagen, Taxi und <em>Fahrten</em>', 'Rental car, taxi and <em>transfers</em>')}</h2>
<p class="lead">{tx('Es herrscht Linksverkehr. Für den Mietwagen brauchst du zusätzlich einen vorläufigen tansanischen Führerschein, den der Vermieter in der Regel für rund 10 USD organisiert.', 'Traffic drives on the left. For a rental car you also need a temporary Tanzanian driving licence, which the rental company usually arranges for around 10 USD.')}</p></div>
<div class="grid g3 entries">{ve('kibabu-cars')}{ve('karibu-kwetu')}{ve('taxi-flughafen')}</div>
<div class="note">{tx('Mehr Anbieter und Erfahrungen findest du im', 'More providers and experiences are in the')} <a href="{url('verzeichnis', 'liste')}">{tx('Verzeichnis', 'directory')}</a>. {tx('Deine Empfehlung fehlt? Schick uns einen Tipp.', 'Your recommendation missing? Send us a tip.')}</div>
</div></section>

<section id="notfall"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Notfall & Gesundheit', 'Emergency & health')}</span><h2>{tx('Wenn es <em>ernst</em> wird', 'When it gets <em>serious</em>')}</h2></div>
<div class="grid g3 entries">{ve('notruf')}{ve('mnazi-mmoja')}{ve('urban-care')}</div>
<div class="note">{tx('Nummern ändern sich. Speichere vor der Reise Nummer und Adresse deiner Unterkunft sowie die Hotline deiner Auslandskrankenversicherung offline.', 'Numbers change. Before the trip save the address and number of your accommodation and the hotline of your travel health insurance offline.')}</div>
</div></section>

<section id="auszeit"><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">{tx('Übernachten & Auszeit', 'Stays & getaways')}</span><h2>{tx('Mal <em>woanders</em> aufwachen', 'Wake up <em>somewhere else</em>')}</h2>
<p class="lead">{tx('Zum Verlängern des Urlaubs, für ein Wochenende oder wenn du in Fumba Town lebst und einen anderen schönen Ort auf der Insel besuchen willst.', 'To extend your holiday, for a weekend, or when you live in Fumba Town and want to visit another beautiful place on the island.')}</p></div>
<div class="entries rv">{ve('soul-beach-hotel')}</div>
</div></div></section>

<section id="anreise" class="band"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Anreise', 'Getting here')}</span><h2>{tx('So kommst du <em>auf die Insel</em>', 'How to get <em>to the island</em>')}</h2>
<p class="lead">{tx('Es gibt keinen Direktflug aus dem deutschsprachigen Raum. Die besten Verbindungen laufen über Dubai, Istanbul, Doha oder Nairobi.', 'There is no direct flight from German-speaking countries. The best connections run via Dubai, Istanbul, Doha or Nairobi.')}</p></div>
<div class="grid g4">
<div class="card rv"><h3>Frankfurt</h3><p>{tx('über Dubai, ca. 14 Std.', 'via Dubai, approx. 14 h')}</p></div>
<div class="card rv"><h3>{tx('München', 'Munich')}</h3><p>{tx('über Istanbul, ca. 11 Std.', 'via Istanbul, approx. 11 h')}</p></div>
<div class="card rv"><h3>{tx('Wien', 'Vienna')}</h3><p>{tx('über Doha, ca. 12 Std.', 'via Doha, approx. 12 h')}</p></div>
<div class="card rv"><h3>{tx('Zürich', 'Zurich')}</h3><p>{tx('über Nairobi, ca. 10 Std.', 'via Nairobi, approx. 10 h')}</p></div>
</div>
<div class="grid g3" style="margin-top:22px">
<div class="card rv"><h3>{tx('Nach Fumba Town', 'To Fumba Town')}</h3><p>{tx('15 bis 25 Min., Taxi ca. 15 bis 25 USD.', '15 to 25 min, taxi approx. 15 to 25 USD.')}</p></div>
<div class="card rv"><h3>{tx('Nach Stone Town', 'To Stone Town')}</h3><p>{tx('10 bis 15 Min., Taxi ca. 10 bis 15 USD.', '10 to 15 min, taxi approx. 10 to 15 USD.')}</p></div>
<div class="card rv"><h3>{tx('Nach Nungwi / Paje', 'To Nungwi / Paje')}</h3><p>{tx('45 bis 90 Min., Taxi ca. 50 bis 80 USD, Mietwagen empfohlen.', '45 to 90 min, taxi approx. 50 to 80 USD, rental car recommended.')}</p></div>
</div></div></section>
''' + contribute_band() + f'''
<section class="cta-band"><div class="wrap narrow">
<h2>{tx("Länger bleiben als zwei Wochen?", "Staying longer than two weeks?")}</h2>
<p class="lead">{tx("Viele kommen als Urlauber und bleiben. Was du über Aufenthalt, Kosten und Alltag wissen solltest, steht auf der Seite Leben auf Sansibar.", "Many arrive as travellers and stay. What you need to know about residence, costs and daily life is on the Living in Zanzibar page.")}</p>
<div class="btn-row"><a class="btn btn-primary" href="{url('leben')}">{tx("Leben auf Sansibar", "Living in Zanzibar")}</a></div>
</div></section>'''
    return (tx("Sansibar Reiseführer: Reisezeit, Strände, Visum & Tipps | Zanzibar Insider", "Zanzibar travel guide: best time, beaches, visa & tips | Zanzibar Insider"),
            tx("Beste Reisezeit, die schönsten Strände, Stone Town, Einreise mit eVisa, Mietwagen, Taxi und Notfallnummern für deine Reise nach Sansibar.",
               "Best time to go, the most beautiful beaches, Stone Town, entry with eVisa, car rental, taxis and emergency numbers for your trip to Zanzibar."),
            body, "lagune_strand.webp")


def p_leben(d, c):
    ents = {e["id"]: e for e in d["entries"]}
    ve = lambda i: entry_html(ents[i], c, compact=True)
    body = hero("fumbatown_stadtbild_am_meer.webp", "B · " + tx("Für Expats", "For expats"),
                tx("Leben auf <em>Sansibar</em>", "Living on <em>Zanzibar</em>"),
                tx("Aufenthalt, Steuern, Kosten und Alltag: das Wichtigste für alle, die länger bleiben wollen. Mit klaren Zahlen und ohne Schönfärberei.",
                   "Residency, taxes, costs and daily life: the essentials for everyone who wants to stay longer. With clear numbers and no sugar-coating."),
                crumbs=crumbs(tx("Leben auf Sansibar", "Living here")))
    docs = [("Reisepass, mindestens 6 Monate gültig", "Passport, valid for at least 6 months"), ("Passbilder", "Passport photos"),
            ("Ausgefüllte Formulare (TIF1 und Data Sheet)", "Completed forms (TIF1 and Data Sheet)"),
            ("Rentenbescheinigung oder Ruhestandsbrief (Firmeninhaber können ihn selbst erstellen)", "Proof of pension or retirement letter (company owners can write it themselves)"),
            ("Kontoauszüge als Nachweis der finanziellen Mittel", "Bank statements as proof of funds"),
            ("Mietvertrag oder Eigentumsnachweis", "Rental contract or proof of ownership"),
            ("Krankenversicherungsnachweis", "Proof of health insurance"), ("Polizeiliches Führungszeugnis", "Police clearance certificate"),
            ("Gesundheitszeugnis eines anerkannten Arztes oder Krankenhauses", "Health certificate from a recognised doctor or hospital")]
    steps = [("Alle Unterlagen sammeln", "Collect all documents"), ("Formulare ausfüllen und unterschreiben", "Fill in and sign the forms"),
             ("Antrag bei der tansanischen Botschaft oder vor Ort einreichen", "Submit the application at the Tanzanian embassy or on site"),
             ("Antragsgebühr entrichten (ca. 500 USD)", "Pay the application fee (approx. 500 USD)"),
             ("Bearbeitung abwarten (ca. 4 bis 8 Wochen)", "Wait for processing (approx. 4 to 8 weeks)"),
             ("Bei Zusage: Einreise nach Tansania", "On approval: enter Tanzania"),
             ("Biometrische Registrierung im Immigration Office", "Biometric registration at the Immigration Office"),
             ("Aufenthaltstitel in Empfang nehmen", "Receive the residence permit")]
    dl = "".join(f"<li>{tx(a, b)}</li>" for a, b in docs)
    sl = "".join(f"<li>{tx(a, b)}</li>" for a, b in steps)
    body += f'''
<nav class="subnav" aria-label="{tx('Seitenübersicht', 'On this page')}"><div class="wrap">
<a href="#warum">{tx('Warum Sansibar', 'Why Zanzibar')}</a><a href="#aufenthalt">{tx('Aufenthalt', 'Residency')}</a><a href="#steuern">{tx('Steuern', 'Taxes')}</a><a href="#kosten">{tx('Kosten & Wohnen', 'Costs & housing')}</a><a href="#alltag">{tx('Alltag', 'Daily life')}</a><a href="#recht">{tx('Anwältin', 'Lawyer')}</a>
</div></nav>

<section id="warum"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Warum Sansibar', 'Why Zanzibar')}</span><h2>{tx('Ein Lebensmittelpunkt <em>am Indischen Ozean</em>', 'A home base <em>on the Indian Ocean</em>')}</h2>
<p class="lead">{tx('Immer mehr Deutschsprachige prüfen Sansibar als neuen Wohnort. Das sind die Gründe, die sie nennen.', 'More and more people are considering Zanzibar as a new place to live. These are the reasons they give.')}</p></div>
<div class="grid g3">
<div class="card rv"><span class="icon">☀️</span><h3>{tx('Klima', 'Climate')}</h3><p>{tx('Rund 27 °C im Jahresmittel, Meeresluft und kein langer dunkler Winter.', 'Around 27 °C on average, sea air and no long dark winter.')}</p></div>
<div class="card rv"><span class="icon">💶</span><h3>{tx('Lebenshaltung', 'Cost of living')}</h3><p>{tx('Lokal lebt es sich deutlich günstiger als in Deutschland, Österreich oder der Schweiz. Für ein Expat-Paar sind 2.000 bis 3.500 USD im Monat ein sinnvoller Planungswert.', 'Living locally is much cheaper than in Germany, Austria or Switzerland. For an expat couple 2,000 to 3,500 USD a month is a sensible planning figure.')}</p></div>
<div class="card rv"><span class="icon">🤝</span><h3>Community</h3><p>{tx('Eine wachsende internationale Gemeinschaft in Fumba Town mit Nachbarn aus über 60 Nationen.', 'A growing international community in Fumba Town with neighbours from over 60 nations.')}</p></div>
<div class="card rv"><span class="icon">✈️</span><h3>{tx('Anbindung', 'Connections')}</h3><p>{tx('Flughafen in 15 bis 25 Minuten, Europa über Dubai, Istanbul, Doha oder Nairobi in 10 bis 14 Stunden.', 'Airport in 15 to 25 minutes, Europe via Dubai, Istanbul, Doha or Nairobi in 10 to 14 hours.')}</p></div>
<div class="card rv"><span class="icon">🏥</span><h3>{tx('Medizin', 'Healthcare')}</h3><p>{tx('Klinik und Apotheken vor Ort, Krankenhaus in Stone Town. Für ernste Fälle sind Daressalam oder Nairobi die Anlaufstellen.', 'Clinic and pharmacies nearby, hospital in Stone Town. For serious cases Dar es Salaam or Nairobi are the options.')}</p></div>
<div class="card rv"><span class="icon">🏡</span><h3>{tx('Wohnen', 'Housing')}</h3><p>{tx('Moderne Projekte wie Fumba Town mit Strand, Pool und Restaurants zu Fuß erreichbar.', 'Modern projects like Fumba Town with beach, pool and restaurants within walking distance.')}</p></div>
</div></div></section>

<section id="aufenthalt" class="band"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Aufenthalt & Visa', 'Residency & visas')}</span><h2>{tx('Wege, <em>länger zu bleiben</em>', 'Ways <em>to stay longer</em>')}</h2>
<p class="lead">{tx('Je nach Lebenssituation gibt es verschiedene Möglichkeiten. Die Angaben zu Ruhestandsvisum und Golden Visa stammen von der FumbaTown Agency, die Anträge begleitet.', 'There are several options depending on your situation. The details on the retirement visa and golden visa come from FumbaTown Agency, which supports the applications.')}</p></div>
<div class="grid g2">
<div class="card rv"><h3>{tx('Besuchsvisum', 'Visitor visa')}</h3><p>{tx('eVisa oder Visa on Arrival, 50 USD, bis zu 90 Tage. Dazu die Pflichtversicherung (ca. 44 USD). Remote-Arbeit im Touristenstatus ist eine Grauzone.', 'eVisa or visa on arrival, 50 USD, up to 90 days. Plus the mandatory insurance (approx. 44 USD). Remote work on a tourist visa is a grey area.')}</p></div>
<div class="card rv"><h3>Class A / Class B</h3><p>{tx('Class A für den Aufbau eines Geschäfts über ein ZIPA-Zertifikat, Class B als Arbeitsvisum, gebunden an einen Arbeitgeber vor Ort.', 'Class A for building a business via a ZIPA certificate, Class B as a work visa tied to a local employer.')}</p></div>
</div>
<div style="margin-top:22px">
<details open><summary>{tx('Ruhestandsvisum (Resident Permit Class C, Retirement)', 'Retirement visa (Resident Permit Class C, Retirement)')}</summary><div class="in">
<p>{tx('Aufenthaltstitel für Rentner ab 55 Jahren, ohne die Mindestinvestition des Golden Visa. Gültig 12 Monate und jährlich verlängerbar. Arbeiten ist damit nicht vorgesehen.', 'Residence permit for retirees aged 55 and over, without the minimum investment of the golden visa. Valid for 12 months and renewable annually. It is not intended for working.')}</p>
<h4 style="margin:.8rem 0 .3rem">{tx('Voraussetzungen', 'Requirements')}</h4><ul>
<li>{tx('Renteneinkünfte oder andere passive Einkünfte von mindestens 1.500 USD im Monat (gesetzliche oder private Rente, Mieteinnahmen, Zinsen)', 'Pension or other passive income of at least 1,500 USD a month (state or private pension, rental income, interest)')}</li>
<li>{tx('Nachweis, dass du dich und gegebenenfalls Angehörige selbst finanzieren kannst', 'Proof that you can support yourself and any dependants')}</li>
<li>{tx('Fester Wohnsitz per Mietvertrag oder Immobilienkauf. Die Immobilie darf unter 100.000 USD liegen und muss nicht vollständig bezahlt sein. In Fumba Town sind Wohnungen ab 35.000 € zu kaufen oder ab 350 € im Monat zu mieten.', 'Fixed residence via rental contract or property purchase. The property may be below 100,000 USD and need not be fully paid. In Fumba Town flats start from €35,000 to buy or from €350 a month to rent.')}</li></ul>
<h4 style="margin:.8rem 0 .3rem">{tx('Unterlagen', 'Documents')}</h4><ul>{dl}</ul>
<h4 style="margin:.8rem 0 .3rem">{tx('Ablauf', 'Process')}</h4><ol style="margin-left:1.2rem">{sl}</ol>
<p style="margin-top:.8rem"><strong>{tx('Kosten:', 'Costs:')}</strong> {tx('Die staatliche Antragsgebühr liegt bei etwa 500 USD. Die FumbaTown Agency und ihre Anwältin übernehmen Anträge, Nachweise und Behördengänge für eine einmalige Pauschale von 1.400 USD, die staatliche Gebühr kommt hinzu.', 'The government application fee is about 500 USD. FumbaTown Agency and its lawyer handle applications, evidence and authority visits for a one-off flat fee of 1,400 USD, the government fee comes on top.')}</p>
<p><a class="btn btn-line btn-sm" href="{FT}/ruhestandsvisum">{tx('Mehr zum Ruhestandsvisum', 'More on the retirement visa')}</a></p></div></details>
<details><summary>{tx('Golden Visa (Class C über Immobilienkauf)', 'Golden visa (Class C via property purchase)')}</summary><div class="in">
<ul><li>{tx('Voraussetzung: Immobilienkauf ab 100.000 USD in einem ZIPA-Projekt wie Fumba Town. Der Anspruch besteht, solange du Eigentümer bist.', 'Requirement: property purchase from 100,000 USD in a ZIPA project such as Fumba Town. The entitlement lasts as long as you own the property.')}</li>
<li>{tx('Gilt für bis zu 6 Personen: die Eltern und bis zu 4 finanziell abhängige Kinder. Die Altersgrenze für Kinder liegt bei 21 Jahren, der Antrag kann zuletzt mit 18 gestellt werden.', 'Covers up to 6 people: the parents and up to 4 financially dependent children. The age limit for children is 21, the application can be made at 18 at the latest.')}</li>
<li>{tx('Das Visum steht im Reisepass und wird alle 2 Jahre verlängert: etwa 500 USD für die Hauptperson und etwa 50 USD je weitere Person.', 'The visa is in the passport and renewed every 2 years: about 500 USD for the main applicant and about 50 USD per additional person.')}</li>
<li>{tx('Ältere Kinder brauchen eine eigene Lösung, etwa Studenten- oder Arbeitsvisum oder eine eigene Investition.', 'Older children need their own solution, such as a student or work visa or their own investment.')}</li></ul>
<p><a class="btn btn-line btn-sm" href="{FT}/golden-visa">{tx('Mehr zum Golden Visa', 'More on the golden visa')}</a></p></div></details>
</div>
<div class="note"><strong>{tx('Wichtig:', 'Important:')}</strong> {tx('Eine Staatsbürgerschaft ist praktisch nicht erreichbar, doppelte Staatsbürgerschaft gibt es nicht. Die Residence Permit allein löst noch keine Steueransässigkeit aus. Bearbeitungszeiten und Gebühren können sich ändern.', 'Citizenship is practically unattainable, dual citizenship does not exist. The residence permit alone does not trigger tax residency. Processing times and fees may change.')}</div>
<p class="small muted" style="margin-top:1rem">{tx('Persönliche Begleitung bei Aufenthaltstiteln und Immobilienkauf bietet unter anderem die', 'Personal support with residence permits and property purchases is offered by, among others,')} <a href="{FT}/beratung">FumbaTown Agency</a>.</p>
</div></section>

<section id="steuern"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Steuern', 'Taxes')}</span><h2>{tx('Was auf Sansibar <em>und in Deutschland</em> gilt', 'What applies <em>in Zanzibar and in Germany</em>')}</h2>
<p class="lead">{tx('Die Steuersituation hängt davon ab, ob du in einer ZIPA-Freezone wie Fumba Town wohnst und wie du deinen deutschen Wohnsitz aufgibst. Quelle ist das', 'Your tax situation depends on whether you live in a ZIPA free zone such as Fumba Town and how you give up your German residence. Source is the')} <a href="{WA_SZ}">{tx('Länderprofil Sansibar von Wohnsitz Ausland', 'Zanzibar country profile by Wohnsitz Ausland (German)')}</a>.</p></div>
<table class="tbl rv">
<tr><th>{tx('Auslandseinkünfte in den Freezones', 'Foreign income in the free zones')}</th><td>{tx('Dafür gibt es derzeit keine Regelung, nach Auskunft der ZIPA effektiv 0 %. Die Lücke soll später geschlossen werden, der Stand ist nicht dauerhaft garantiert.', 'There is currently no rule for it, effectively 0% according to ZIPA. The gap is to be closed later, the status is not guaranteed permanently.')}</td></tr>
<tr><th>{tx('Mieteinnahmen', 'Rental income')}</th><td>{tx('10 % in den Freezones, die einzige geregelte Ausnahme.', '10% in the free zones, the only regulated exception.')}</td></tr>
<tr><th>{tx('Außerhalb der Zonen', 'Outside the zones')}</th><td>{tx('Residenten zahlen auf das Welteinkommen 0 bis 30 %. Als Short-term Resident (lebenslang höchstens 2 Jahre) werden nur tansanische Einkünfte besteuert. Nichtresidenten zahlen 15 % final auf tansanisches Arbeitseinkommen.', 'Residents pay 0 to 30% on worldwide income. As a short-term resident (a maximum of 2 years in a lifetime) only Tanzanian income is taxed. Non-residents pay 15% final on Tanzanian employment income.')}</td></tr>
<tr><th>{tx('Wann bist du ansässig?', 'When are you resident?')}</th><td>{tx('Ständige Wohnstätte plus irgendein Aufenthalt im Steuerjahr, 183 Tage im Steuerjahr oder durchschnittlich mehr als 122 Tage in drei Jahren.', 'A permanent home plus any stay in the tax year, 183 days in the tax year, or an average of more than 122 days over three years.')}</td></tr>
<tr><th>{tx('Mehrwertsteuer', 'VAT')}</th><td>{tx('15 % auf Sansibar (18 % für Banken, Telekom und digitale Dienste).', '15% on Zanzibar (18% for banks, telecoms and digital services).')}</td></tr>
<tr><th>{tx('Deutsche Seite', 'German side')}</th><td>{tx('Kein Doppelbesteuerungsabkommen mit Deutschland (Stand 1.1.2026). Wegzugsbesteuerung nach § 6 AStG bei wesentlichen Beteiligungen ab 1 %. Die erweiterte beschränkte Steuerpflicht kann bis zu 10 Jahre nachwirken.', 'No double taxation treaty with Germany (as of 1 Jan 2026). Exit tax under § 6 AStG for substantial shareholdings from 1%. Extended limited tax liability can continue for up to 10 years.')}</td></tr>
</table>
<div class="note"><strong>{tx('Voraussetzung für den Wegzug:', 'Requirement for leaving:')}</strong> {tx('Deutsche Wohnung aufgeben und den Lebensmittelpunkt nachweisbar verlagern, sonst bleibt die unbeschränkte deutsche Steuerpflicht bestehen. Das ist ein Überblick und keine individuelle Steuer- oder Rechtsberatung.', 'Give up the German home and demonstrably move your centre of life, otherwise unlimited German tax liability remains. This is an overview and not individual tax or legal advice.')}</div>
<div class="btn-row"><a class="btn btn-primary" href="{WA_SZ}">{tx('Länderprofil Sansibar', 'Zanzibar country profile')}</a><a class="btn btn-line" href="{WA}/7-schritte/">{tx('7 Schritte zum Wegzug', '7 steps to leaving')}</a><a class="btn btn-line" href="{FT}/steuern-sansibar">{tx('Steuern bei Fumba Town', 'Taxes at Fumba Town')}</a></div>
</div></section>

<section id="kosten" class="band"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Kosten & Wohnen', 'Costs & housing')}</span><h2>{tx('Was ein Leben <em>wirklich kostet</em>', 'What life <em>really costs</em>')}</h2>
<p class="lead">{tx('Richtwerte aus dem Länderprofil (Numbeo, dünne Datenbasis) und aus unserer Erfahrung. Importware kostet oft deutlich mehr als in Europa, lokale Produkte und Märkte sind günstig.', 'Rules of thumb from the country profile (Numbeo, thin data) and from our experience. Imported goods often cost much more than in Europe, local products and markets are cheap.')}</p></div>
<div class="grid g4">
<div class="fact rv"><b>≈ 4 €</b><span>{tx('Einfaches Essen', 'Simple meal')}</span></div>
<div class="fact rv"><b>≈ 19 €</b><span>{tx('Abendessen für zwei', 'Dinner for two')}</span></div>
<div class="fact rv"><b>≈ 43 €</b><span>{tx('Internet pro Monat', 'Internet per month')}</span></div>
<div class="fact rv"><b>2.000–3.500 $</b><span>{tx('Planungswert Expat-Paar pro Monat', 'Planning figure expat couple per month')}</span></div>
</div>
<div class="split" style="margin-top:2.4rem">
<div class="rv"><h3>{tx('Wohnen und Grundbesitz', 'Housing and land')}</h3>
<ul class="ticks"><li>{tx('Immobilie ab rund 100.000 USD in genehmigten ZIPA-Projekten, Einsteigerwohnungen in Fumba Town liegen darunter.', 'Property from around 100,000 USD in approved ZIPA projects, entry-level flats in Fumba Town are below that.')}</li>
<li>{tx('Das Land gehört dem Staat. Ausländer erhalten ein Leasehold über 33 Jahre, verlängerbar bis 99 Jahre.', 'The land belongs to the state. Foreigners receive a 33-year leasehold, extendable to 99 years.')}</li>
<li>{tx('Nur in ZIPA-genehmigten Projekten kaufen, Entwickler-Zertifikat prüfen, Zusagen schriftlich festhalten.', 'Only buy in ZIPA-approved projects, check the developer certificate, get promises in writing.')}</li>
<li>{tx('Erst mieten und ausprobieren: Wohnungen in Fumba Town ab etwa 350 € im Monat.', 'Rent first and try it out: flats in Fumba Town from about €350 a month.')}</li></ul>
<p style="margin-top:1rem">{tx('Neue Wohnprojekte mit Aufenthaltsoption gibt es in den ZIPA-Freezones, zum Beispiel in Fumba Town. Übersicht und aktuelle Preise:', 'New housing projects with a residence option are available in the ZIPA free zones, for example in Fumba Town. Overview and current prices:')} <a href="{FT}/projekte">fumbatown.agency/projekte</a></p>
<div class="btn-row"><a class="btn btn-primary" href="{FT}/wohnung-mieten">{tx('Wohnung mieten', 'Rent a flat')}</a><a class="btn btn-line" href="{FT}/moebelpakete">{tx('Möbelpakete', 'Furniture packages')}</a></div></div>
<div class="rv"><h3>{tx('Einkaufen: Shopping-Weisheiten', 'Shopping wisdom')}</h3>
<ul class="ticks"><li>{tx('Wenn du etwas Wichtiges siehst, kauf es gleich. Importware kann beim nächsten Besuch weg sein.', 'If you see something important, buy it right away. Imported goods may be gone on your next visit.')}</li>
<li>{tx('Auf Märkten wird verhandelt, Preise vorher vergleichen.', 'Markets expect bargaining, compare prices beforehand.')}</li>
<li>{tx('Lokal ist oft besser: Gewürze, Obst, Fisch, Kunsthandwerk.', 'Local is often better: spices, fruit, fish, crafts.')}</li>
<li>{tx('Lieferdienste und Bestellgemeinschaften in der WhatsApp-Community sparen Wege.', 'Delivery services and ordering groups in the WhatsApp community save trips.')}</li></ul></div>
</div></div></section>

<section id="alltag"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Alltag', 'Daily life')}</span><h2>{tx('Einkaufen, essen, <em>ankommen</em>', 'Shopping, eating, <em>settling in</em>')}</h2>
<p class="lead">{tx('Wo bekomme ich was? Eine Auswahl aus dem Verzeichnis, die wir laufend erweitern. Kommentare und Korrekturen sind willkommen.', 'Where do I get what? A selection from the directory, which we keep expanding. Comments and corrections are welcome.')}</p></div>
<div class="grid g3 entries">{ve('soul-beach-hotel')}{ve('darajani')}{ve('kwetu-kwetu')}{ve('lieferdienste')}{ve('zanzibar-coffee-house')}{ve('amore-mio')}{ve('whatsapp-fumba')}</div>
<div class="btn-row"><a class="btn btn-primary" href="{url('verzeichnis')}">{tx('Ganzes Verzeichnis', 'Whole directory')}</a><a class="btn btn-line" href="{url('verzeichnis', 'tipp')}">{tx('Tipp einsenden', 'Submit a tip')}</a></div>
</div></section>

<section id="recht" class="band"><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">{tx('Recht & Behörden', 'Legal & authorities')}</span><h2>{tx('Unsere <em>Anwältin</em> vor Ort', 'Our <em>lawyer</em> on the ground')}</h2>
<p class="lead">{tx('Clara Wella ist unsere Ansprechpartnerin für Aufenthaltstitel, Immobilienkauf und Verträge auf Sansibar. Wir arbeiten seit Langem mit ihr zusammen und empfehlen sie.', 'Clara Wella is our contact for residence permits, property purchases and contracts on Zanzibar. We have worked with her for a long time and recommend her.')}</p>
<div class="btn-row"><a class="btn btn-primary" href="tel:+255776162033">+255 776 162 033</a><a class="btn btn-line" href="https://wa.me/255776162033">WhatsApp</a></div></div>
<div class="entries rv">{ve('clara-wella')}</div>
</div></div></section>
''' + magazine_band() + contribute_band()
    return (tx("Leben auf Sansibar: Aufenthalt, Steuern, Kosten | Zanzibar Insider", "Living on Zanzibar: residency, taxes, costs | Zanzibar Insider"),
            tx("Auswandern nach Sansibar: Ruhestandsvisum, Golden Visa, Steuern in den ZIPA-Freezones, Kosten, Wohnen, Einkaufen und Alltag für Expats.",
               "Moving to Zanzibar: retirement visa, golden visa, taxes in the ZIPA free zones, costs, housing, shopping and daily life for expats."),
            body, "fumbatown_stadtbild_am_meer.webp")


def p_verzeichnis(d, c):
    cats = d["categories"]
    chips = f'<button class="chip on" data-cat="">{tx("Alle", "All")}</button>' + "".join(
        f'<button class="chip" data-cat="{x["id"]}">{x["icon"]} {loc(x)}</button>' for x in cats)
    ents = sorted(d["entries"], key=lambda e: (e["status"] != "geprueft", loc(e["name"]).lower()))
    items = "".join(entry_html(e, c) for e in ents)
    body = hero("strand_restaurant.webp", tx("Insider-Verzeichnis", "Insider directory"),
                tx("Das Sansibar-<em>Verzeichnis</em>", "The Zanzibar <em>directory</em>"),
                tx("Mietwagen, Krankenhaus, Anwältin, Supermarkt, Café: Tipps von Menschen vor Ort, redaktionell gekennzeichnet und von der Community kommentiert.",
                   "Rental car, hospital, lawyer, grocery, café: tips from people on the ground, editorially labelled and commented on by the community."),
                crumbs=crumbs(tx("Verzeichnis", "Directory")))
    body += f'''
<section id="liste"><div class="wrap">
<div class="legendbox rv">
<div>{badge('geprueft')} <span>{tx('Von uns persönlich geprüft oder empfohlen, mit Quelle und Datum.', 'Checked or recommended by us in person, with source and date.')}</span></div>
<div>{badge('ungeprueft')} <span>{tx('Hinweis aus Community oder öffentlicher Quelle, noch nicht von uns bestätigt. Bitte vor Ort prüfen.', 'Tip from the community or a public source, not yet confirmed by us. Please verify on site.')}</span></div>
</div>
<div class="filters"><input id="q" type="search" placeholder="{tx('Suchen: Auto, Arzt, Pizza …', 'Search: car, doctor, pizza …')}" aria-label="{tx('Suchen', 'Search')}">
<div class="chips">{chips}</div>
<label class="chk"><input type="checkbox" id="onlyok"> {tx('Nur geprüfte Einträge', 'Checked entries only')}</label></div>
<p class="muted small" id="count"></p>
<div class="grid g2 entries" id="entries">{items}</div>
<p class="muted" id="none" hidden>{tx('Nichts gefunden. Schick uns gern einen Tipp.', 'Nothing found. Feel free to send us a tip.')}</p>
</div></section>

<section id="tipp" class="band"><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">{tx('Mitmachen', 'Join in')}</span><h2>{tx('Tipp <em>einsenden</em>', 'Submit a <em>tip</em>')}</h2>
<p class="lead">{tx('Gute Adresse, fairer Preis, neue Nummer oder eine Korrektur? Schreib es auf. Wir prüfen es und veröffentlichen es mit dem passenden Status.', 'A good address, fair price, new number or a correction? Write it down. We check it and publish it with the right status.')}</p>
<ul class="ticks"><li>{tx('Besonders gesucht: Supermärkte mit realistischen Preisen, italienischer Espresso, Ärzte, Handwerker, Autovermieter, Taxis mit Nummer.', 'Especially wanted: supermarkets with realistic prices, Italian espresso, doctors, tradespeople, car rentals, taxis with a number.')}</li>
<li>{tx('Du bist selbst Anbieter? Gib an, dass du Inhaber bist, damit wir es transparent kennzeichnen.', 'You are a provider yourself? State that you are the owner so we can label it transparently.')}</li></ul></div>
<div class="rv">{submit_form(cats)}</div>
</div></div></section>
''' + magazine_band()
    return (tx("Sansibar-Verzeichnis: Mietwagen, Ärzte, Anwältin, Einkaufen | Zanzibar Insider", "Zanzibar directory: car rental, doctors, lawyer, shopping | Zanzibar Insider"),
            tx("Insider-Verzeichnis für Sansibar mit geprüften und ungeprüften Tipps zu Mietwagen, Gesundheit, Recht, Einkaufen und Essen, ergänzt durch Kommentare der Community.",
               "Insider directory for Zanzibar with checked and unchecked tips on car rental, health, legal, shopping and food, complemented by community comments."),
            body, "strand_restaurant.webp")


def p_kunden(d, c):
    ents = {e["id"]: e for e in d["entries"]}
    ve = lambda i: entry_html(ents[i], c, compact=True)
    body = hero("fumbatown_projekt_luftaufnahme_stadtansicht.webp", "C · " + tx("Für Kunden", "For clients"),
                tx("Willkommen, <em>wir bringen dich an</em>", "Welcome, <em>we will get you there</em>"),
                tx("Dein Bereich als Kunde der FumbaTown Agency oder von Perspektive Ausland: dein Weg, die Checkliste für die Reise und alle Links an einem Ort.",
                   "Your area as a client of FumbaTown Agency or Perspektive Ausland: your path, the checklist for the trip and all links in one place."),
                crumbs=crumbs(tx("Für Kunden", "For clients")))

    def stp(h, t, href, lab):
        return f'<div class="step rv"><h3>{h}</h3><p>{t}</p><p style="margin-top:.6rem"><a href="{href}">{lab} →</a></p></div>'
    body += f'''
<nav class="subnav" aria-label="{tx('Seitenübersicht', 'On this page')}"><div class="wrap">
<a href="#weg">{tx('Dein Weg', 'Your path')}</a><a href="#checkliste">{tx('Checkliste', 'Checklist')}</a><a href="#fumbatown">FumbaTown Agency</a><a href="#perspektive">Perspektive Ausland</a><a href="#wohnsitz">Wohnsitz Ausland</a><a href="#vorort">{tx('Vor Ort', 'On the ground')}</a><a href="#kontakt">{tx('Kontakt', 'Contact')}</a>
</div></nav>

<section id="weg"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Dein Weg', 'Your path')}</span><h2>{tx('Wo stehst du <em>gerade?</em>', 'Where are you <em>right now?</em>')}</h2>
<p class="lead">{tx('Von der ersten Frage bis zum Einzug. Je nachdem, wo du im Prozess bist, findest du hier den nächsten Schritt.', 'From the first question to moving in. Depending on where you are in the process, you find the next step here.')}</p></div>
<div class="steps">
{stp(tx('Erstgespräch', 'First call'), tx('Ziele, Budget und Zeitplan klären.', 'Clarify goals, budget and timeline.'), FT + '/beratung', tx('Termin buchen', 'Book a call'))}
{stp(tx('Investorenreise', 'Investor trip'), tx('Projekt und Insel vor Ort ansehen.', 'See the project and island on site.'), FT + '/investorenreise', tx('Reise ansehen', 'See the trip'))}
{stp(tx('Einheit wählen', 'Choose a unit'), tx('Immobilien, Grundrisse und Zahlungspläne.', 'Properties, floor plans and payment plans.'), FT + '/projekte', tx('Projekte', 'Projects'))}
{stp(tx('Kauf & Recht', 'Purchase & legal'), tx('Verträge, Anwältin und Aufenthalt.', 'Contracts, lawyer and residency.'), FT + '/mustervertraege', tx('Mustervertrag', 'Sample contract'))}
{stp(tx('Einzug', 'Moving in'), tx('Einrichtung, Vermietung, Betreuung.', 'Furnishing, letting, support.'), FT + '/einrichtung', tx('Einrichtung', 'Furnishing'))}
</div></div></section>

<section id="checkliste" class="band"><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">{tx('Vor deiner Reise', 'Before your trip')}</span><h2>{tx('Checkliste <em>für die Anreise</em>', 'Checklist <em>for your arrival</em>')}</h2>
<ul class="ticks">
<li><strong>{tx('Reisepass', 'Passport')}</strong> {tx('mit mindestens sechs Monaten Gültigkeit prüfen', 'check at least six months of validity')}</li>
<li><strong>eVisa</strong> {tx('online beantragen (50 USD, bis 90 Tage)', 'apply online (50 USD, up to 90 days)')}</li>
<li><strong>{tx('ZIC-Versicherung', 'ZIC insurance')}</strong> {tx('abschließen (ca. 44 USD pro Person)', 'take out (approx. 44 USD per person)')}</li>
<li><strong>{tx('Auslandskrankenversicherung', 'Travel health insurance')}</strong> {tx('mit Rückholdeckung', 'with repatriation cover')}</li>
<li><strong>{tx('Einreiseformular', 'Entry form')}:</strong> {tx('als Adresse „Fumba Town“ genügt', '"Fumba Town" is enough as the address')}</li>
<li><strong>{tx('Termine', 'Appointments')}</strong> {tx('mit unserem Team vorab bestätigen', 'confirm with our team beforehand')}</li>
<li><strong>{tx('US-Dollar', 'US dollars')}</strong> {tx('für die Ankunft, Rest per Geldautomat vor Ort', 'for arrival, the rest from an ATM on site')}</li></ul>
<p class="small muted" style="margin-top:1rem">{tx('Details zu Einreise und Gesundheit stehen im', 'Details on entry and health are in the')} <a href="{url('reisen', 'einreise')}">{tx('Reiseführer', 'travel guide')}</a>.</p></div>
<div class="media rv"><img src="/img/landkarte_mit_tanzania_und_sansibar.webp" alt="{tx('Landkarte von Tansania und Sansibar', 'Map of Tanzania and Zanzibar')}" loading="lazy"></div>
</div></div></section>

<section id="fumbatown"><div class="wrap">
<div class="head"><span class="eyebrow">FumbaTown Agency</span><h2>{tx('Alles rund um <em>Fumba Town</em>', 'Everything about <em>Fumba Town</em>')}</h2></div>
<div class="links">
<a href="{FT}/fumba-town"><div>{tx('Das Projekt', 'The project')}<span>{tx('Fumba Town im Überblick', 'Fumba Town at a glance')}</span></div></a>
<a href="{FT}/projekte"><div>{tx('Projekte & Einheiten', 'Projects & units')}<span>{tx('Apartments, Penthouses, Villen', 'Apartments, penthouses, villas')}</span></div></a>
<a href="{FT}/investorenreise"><div>{tx('Investorenreise', 'Investor trip')}<span>{tx('Termine und Anmeldung', 'Dates and registration')}</span></div></a>
<a href="{FT}/wohnung-mieten"><div>{tx('Wohnung mieten', 'Rent a flat')}<span>{tx('Probewohnen vor dem Kauf', 'Try before you buy')}</span></div></a>
<a href="{FT}/moebelpakete"><div>{tx('Möbelpakete', 'Furniture packages')}<span>{tx('Einrichtung aus einer Hand', 'Furnishing from one source')}</span></div></a>
<a href="{FT}/stadtmanagement"><div>{tx('Stadtmanagement', 'Town management')}<span>{tx('Betreuung vor Ort', 'Support on site')}</span></div></a>
<a href="{FT}/golden-visa"><div>Golden Visa<span>{tx('Aufenthalt über Immobilien', 'Residency through property')}</span></div></a>
<a href="{FT}/faq"><div>{tx('Häufige Fragen', 'FAQ')}<span>{tx('Rund um Kauf und Umzug', 'About buying and moving')}</span></div></a>
</div></div></section>

<section id="perspektive" class="band"><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">Perspektive Ausland</span><h2>{tx('Dein <em>Plan B</em> mit Community', 'Your <em>Plan B</em> with community')}</h2>
<p class="lead">{tx('Perspektive Ausland richtet sich an Unternehmer, Freiberufler, Investoren und Familien, die sich mehr internationale Möglichkeiten schaffen wollen, vom Plan B bis zum vollständigen Wegzug.', 'Perspektive Ausland is for entrepreneurs, freelancers, investors and families who want more international options, from Plan B to a full move abroad.')}</p>
<ul class="ticks"><li>{tx('Seminare, Reisen und Workshops', 'Seminars, trips and workshops')}</li><li>{tx('Podcast und YouTube mit Wissen aus der Praxis', 'Podcast and YouTube with practical knowledge')}</li><li>{tx('Persönliche Beratung und Begleitung bei der Umsetzung', 'Personal consulting and support with implementation')}</li></ul>
<div class="btn-row"><a class="btn btn-primary" href="{PA}/veranstaltungen">{tx('Veranstaltungen', 'Events')}</a><a class="btn btn-line" href="{PA}/club">{tx('Der Club', 'The club')}</a><a class="btn btn-line" href="{PA}/mandatierung">{tx('Termin buchen', 'Book a call')}</a></div></div>
<div class="media rv"><img src="/img/segelboot.webp" alt="{tx('Segelboot auf dem Meer', 'Sailing boat at sea')}" loading="lazy"></div>
</div></div></section>

<section id="wohnsitz"><div class="wrap"><div class="split flip">
<div class="rv"><span class="eyebrow">Wohnsitz Ausland</span><h2>{tx('Steuern und Aufenthalt <em>nachlesen</em>', 'Read up on <em>taxes and residency</em>')}</h2>
<p class="lead">{tx('Länderprofile für 64 Länder, Steuerwissen zum Wegzug und die 7 Schritte, wie du einen Wohnsitzwechsel strukturiert angehst. Für Sansibar ist das Länderprofil die maßgebliche Quelle für Steuerfragen.', 'Country profiles for 64 countries, tax knowledge for leaving, and the 7 steps for approaching a change of residence in a structured way. For Zanzibar the country profile is the authoritative source for tax questions.')}</p>
<div class="btn-row"><a class="btn btn-primary" href="{WA_SZ}">{tx('Länderprofil Sansibar', 'Zanzibar profile')}</a><a class="btn btn-line" href="{WA}/steuerwissen/">{tx('Steuerwissen', 'Tax knowledge')}</a><a class="btn btn-line" href="{WA}/beratung/">{tx('Beratung', 'Consulting')}</a></div></div>
<div class="media rv"><img src="/img/frau_am_strand.webp" alt="{tx('Frau am Strand', 'Woman on the beach')}" loading="lazy"></div>
</div></div></section>

<section id="vorort" class="band"><div class="wrap">
<div class="head"><span class="eyebrow">{tx('Vor Ort', 'On the ground')}</span><h2>{tx('Wichtige Kontakte <em>für den Alltag</em>', 'Important contacts <em>for daily life</em>')}</h2></div>
<div class="grid g3 entries">{ve('clara-wella')}{ve('whatsapp-fumba')}{ve('fumba-times')}</div>
<div class="btn-row"><a class="btn btn-primary" href="{url('verzeichnis')}">{tx('Zum Verzeichnis', 'To the directory')}</a></div>
</div></section>

<section id="kontakt" class="dark"><div class="wrap"><div class="split">
<div class="rv"><span class="eyebrow">{tx('Kontakt', 'Contact')}</span><h2>{tx('Wir sind <em>für dich da</em>', 'We are <em>here for you</em>')}</h2>
<p class="lead">{tx('Wenn du schon im Prozess bist, schreib oder ruf uns an und nenne kurz, wo du stehst. Für ein neues Gespräch buche direkt einen Termin.', 'If you are already in the process, write or call us and say briefly where you stand. For a new conversation book an appointment directly.')}</p>
<div class="btn-row"><a class="btn btn-primary" href="{FT}/beratung">{tx('Beratungstermin buchen', 'Book a consultation')}</a><a class="btn btn-ghost" href="{FT}/rueckruf">{tx('Rückruf anfordern', 'Request a call back')}</a></div></div>
<div class="rv"><table class="tbl" style="color:var(--ink)">
<tr><th>{tx('E-Mail', 'Email')}</th><td><a href="mailto:{MAIL}">{MAIL}</a></td></tr>
<tr><th>{tx('Telefon', 'Phone')}</th><td><a href="tel:+4915563058676">{TEL}</a></td></tr>
<tr><th>{tx('Kontaktformular', 'Contact form')}</th><td><a href="{FT}/kontakt">fumbatown.agency/kontakt</a></td></tr>
</table></div>
</div></div></section>
''' + contribute_band()
    return (tx("Für Kunden: FumbaTown Agency & Perspektive Ausland | Zanzibar Insider", "For clients: FumbaTown Agency & Perspektive Ausland | Zanzibar Insider"),
            tx("Dein Bereich als Kunde der FumbaTown Agency und von Perspektive Ausland: Weg, Checkliste, Links und Kontakt.",
               "Your area as a client of FumbaTown Agency and Perspektive Ausland: path, checklist, links and contact."),
            body, "fumbatown_projekt_luftaufnahme_stadtansicht.webp")


PAGES = {"index": p_index, "reisen": p_reisen, "leben": p_leben, "verzeichnis": p_verzeichnis, "kunden": p_kunden}


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)


def build_lang(lang, d, c):
    global L
    L = lang
    for key, fn in PAGES.items():
        title, desc, body, img = fn(d, c)
        rel = page_path(key, lang).strip("/")
        fname = (rel + ".html") if (rel and key != "index") else (rel + "/index.html" if rel else "index.html")
        write(fname, page(key, title, desc, body, img, noindex=(key in NOINDEX)))


def main():
    d, c = load_dir()
    for lang in LANGS:
        build_lang(lang, d, c)
    urls = [SITE + page_path(k, l) for l in LANGS for k in PAGES if k not in NOINDEX]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("gebaut:", len(urls), "Seiten")


if __name__ == "__main__":
    main()
