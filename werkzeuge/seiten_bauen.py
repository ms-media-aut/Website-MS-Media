"""Seiten von codeundlicht.at aus quelle/*.html bauen (gemeinsame Kopfzeile, Fußzeile, Metadaten, Schema).

    python3 -I werkzeuge/seiten_bauen.py          # alle Seiten neu schreiben
    python3 -I werkzeuge/seiten_bauen.py pruefen  # nur prüfen (Längen, Links, Bilder), nichts schreiben

Jede Quelldatei beginnt mit einem JSON-Block zwischen <!--- und ---> (Metadaten), danach folgt der Inhalt von <main>.
Felder: pfad (Adresse ohne Domain, z. B. "/app-entwicklung/"), titel (bis 60 Zeichen), beschreibung (bis 155),
nav (Kennung des aktiven Menüpunkts), schema (Liste zusätzlicher JSON-LD-Knoten), bild (Vorschaubild für Social Media,
Pfad ab Wurzel), krumen (Liste [Name, Pfad] für die Brotkrumen; die Startseite steht immer vorne).
Im Inhalt steht {{root}} für den relativen Weg zur Wurzel ("" auf der Startseite, "../" eine Ebene tiefer …),
damit die Seiten auch ohne Server (Datei im Browser, Vorschau) funktionieren.
"""
import html
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.normpath(os.path.join(HIER, '..'))
QUELLE = os.path.join(WURZEL, 'quelle')
DOMAIN = 'https://www.codeundlicht.at'

ZEICHEN = ('<svg viewBox="0 0 36 26" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M12 3 L2 13 L12 23"/><path d="M24 3 L34 13 L24 23"/>'
           '<line x1="18" y1="1" x2="18" y2="25"/></svg>')

NAV = [
    ('webdesign', 'Webdesign', 'webdesign-kaernten/'),
    ('apps', 'App-Entwicklung', 'app-entwicklung/'),
    ('referenz', 'Referenz', 'referenzen/kontor/'),
    ('seo', 'SEO', 'seo-optimierung/'),
    ('ueber', 'Über uns', '#ueber'),
]

ORGANISATION = {
    '@type': 'ProfessionalService',
    '@id': DOMAIN + '/#organisation',
    'name': 'Code und Licht',
    'alternateName': 'Code und Licht · Webdesign und App-Entwicklung Kärnten',
    'description': ('Webdesign, App-Entwicklung und SEO aus Klagenfurt, Kärnten: Websites, Web-Apps, Dashboards und '
                    'Kundenportale für kleine und mittelständische Unternehmen und Tourismusbetriebe.'),
    'url': DOMAIN + '/',
    'logo': DOMAIN + '/assets/images/code-und-licht-logo.png',
    'image': DOMAIN + '/assets/images/referenz-kontor/kontor-dashboard-uebersicht.jpg',
    'founder': {'@type': 'Person', 'name': 'Michael Stabentheiner', 'honorificSuffix': 'MSc'},
    'email': 'michael@codeundlicht.at',
    'telephone': '+43 664 65 92 642',
    'vatID': 'ATU69786635',
    'address': {'@type': 'PostalAddress', 'streetAddress': 'Sonnenhangstraße 71', 'postalCode': '9071',
                'addressLocality': 'Köttmannsdorf', 'addressRegion': 'Kärnten', 'addressCountry': 'AT'},
    'areaServed': [{'@type': 'City', 'name': 'Klagenfurt'}, {'@type': 'City', 'name': 'Villach'},
                   {'@type': 'AdministrativeArea', 'name': 'Kärnten'}, {'@type': 'Country', 'name': 'Österreich'}],
    'knowsAbout': ['Webdesign', 'Homepage erstellen', 'App-Entwicklung', 'Softwareentwicklung', 'Web-Apps', 'Dashboards', 'Kundenportale', 'Prozessoptimierung',
                   'Automatisierung', 'SEO', 'Suchmaschinenoptimierung', 'Landingpages', 'Spieleentwicklung'],
    'sameAs': ['https://www.instagram.com/michael.stabentheiner/', 'https://at.linkedin.com/company/michaelstabentheiner',
               'https://www.facebook.com/michael.stabentheiner/', 'https://www.michaelstabentheiner.at/'],
}


def lesen(datei):
    roh = open(datei, encoding='utf-8').read()
    m = re.match(r'\s*<!---(.*?)--->\s*(.*)$', roh, re.S)
    assert m, f'{datei}: Metadaten-Block fehlt'
    return json.loads(m.group(1)), m.group(2)


def root_fuer(pfad):
    """Relativer Weg zur Wurzel: "/" → "", "/seo-optimierung/" → "../", "/impressum.html" → ""."""
    ordner = pfad if pfad.endswith('/') else pfad.rsplit('/', 1)[0] + '/'
    return '../' * ordner.strip('/').count('/') + ('../' if ordner.strip('/') else '')


def kopf(meta, root):
    pfad = meta['pfad']
    links = []
    for kennung, text, ziel in NAV:
        href = ziel if ziel.startswith('#') and pfad == '/' else root + ziel
        aktuell = ' aria-current="page"' if meta.get('nav') == kennung else ''
        links.append(f'<a href="{href}"{aktuell}>{text}</a>')
    links.append(f'<a href="{root}#kontakt" class="btn btn--primary">Projekt anfragen</a>')
    return ('<a class="skip" href="#inhalt">Zum Inhalt</a>\n'
            '<header class="hd">\n  <div class="hd__inner">\n'
            f'    <a href="{root or "./"}" class="logo" aria-label="Code und Licht, Startseite">'
            f'<span class="logo__mark">{ZEICHEN}</span><span class="logo__word">Code <em>und</em> Licht</span></a>\n'
            '    <button class="burger" id="navBurger" aria-label="Menü öffnen" aria-expanded="false" aria-controls="navLinks">'
            '<span></span><span></span></button>\n'
            f'    <nav class="nav" id="navLinks" aria-label="Hauptnavigation">\n      ' + '\n      '.join(links) +
            '\n    </nav>\n  </div>\n</header>\n')


def fuss(root):
    return f'''<footer class="ft dark">
  <div class="container">
    <div class="ft__grid">
      <div>
        <a href="{root or './'}" class="logo" aria-label="Code und Licht, Startseite"><span class="logo__mark">{ZEICHEN}</span><span class="logo__word">Code <em>und</em> Licht</span></a>
        <p style="margin-top:20px">Webdesign, App-Entwicklung und SEO aus Klagenfurt, Kärnten.<br>Sonnenhangstraße 71, 9071 Köttmannsdorf</p>
      </div>
      <div>
        <h2>Leistungen</h2>
        <ul>
          <li><a href="{root}app-entwicklung/">App-Entwicklung</a></li>
          <li><a href="{root}app-entwicklung/#dashboards">Dashboards und Kundenportale</a></li>
          <li><a href="{root}webdesign-kaernten/">Webdesign Kärnten</a></li>
          <li><a href="{root}seo-optimierung/">SEO-Optimierung</a></li>
          <li><a href="https://www.michaelstabentheiner.at/">Foto- und Videoproduktion</a></li>
        </ul>
      </div>
      <div>
        <h2>Projekte</h2>
        <ul>
          <li><a href="{root}referenzen/kontor/">Referenz Kontor</a></li>
          <li><a href="{root}kaernten-raetsel/">Kärnten-Rätsel (Spiel)</a></li>
          <li><a href="{root}#arbeiten">Weitere Arbeiten</a></li>
        </ul>
      </div>
      <div>
        <h2>Kontakt</h2>
        <ul>
          <li><a href="tel:+436646592642">+43 664 65 92 642</a></li>
          <li><a href="mailto:michael@codeundlicht.at">michael@codeundlicht.at</a></li>
          <li><a href="{root}#kontakt">Projekt anfragen</a></li>
        </ul>
      </div>
    </div>
    <div class="ft__bottom">
      <span>© <span id="year">2026</span> Code und Licht · Michael Stabentheiner, MSc</span>
      <span><a href="{root}impressum.html">Impressum</a> · <a href="{root}impressum.html#datenschutz">Datenschutz</a> · <a href="#" class="js-cookie-settings">Cookie-Einstellungen</a></span>
    </div>
  </div>
</footer>
'''


def schema(meta):
    graph = [dict(ORGANISATION), {
        '@type': 'WebSite', '@id': DOMAIN + '/#website', 'url': DOMAIN + '/', 'name': 'Code und Licht',
        'inLanguage': 'de-AT', 'publisher': {'@id': DOMAIN + '/#organisation'}}]
    seite = {'@type': meta.get('seitentyp', 'WebPage'), '@id': DOMAIN + meta['pfad'] + '#seite', 'url': DOMAIN + meta['pfad'],
             'name': meta['titel'], 'description': meta['beschreibung'], 'inLanguage': 'de-AT',
             'isPartOf': {'@id': DOMAIN + '/#website'}, 'about': {'@id': DOMAIN + '/#organisation'}}
    if meta.get('bild'):
        seite['primaryImageOfPage'] = {'@type': 'ImageObject', 'url': DOMAIN + meta['bild']}
    graph.append(seite)
    krumen = [['Start', '/']] + meta.get('krumen', [])
    if len(krumen) > 1:
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': DOMAIN + p} for i, (n, p) in enumerate(krumen)]})
    graph += meta.get('schema', [])
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1)


def shot(root, name, alt, art='lazy', groessen='(max-width: 900px) 100vw, 60vw'):
    """Bildschirmfoto aus assets/images/referenz-kontor/ als <figure>: WebP mit 720er-Fassung, JPEG als Rückfall,
    Breite und Höhe aus der Datei, beim ersten Bild der Seite (art=eager) mit hoher Priorität."""
    from PIL import Image
    ordner = os.path.join(WURZEL, 'assets', 'images', 'referenz-kontor')
    b, h = Image.open(os.path.join(ordner, name + '.webp')).size
    pfad = root + 'assets/images/referenz-kontor/' + name
    klein = os.path.exists(os.path.join(ordner, name + '-720.webp'))
    srcset = f'{pfad}-720.webp 720w, {pfad}.webp {b}w' if klein else f'{pfad}.webp {b}w'
    laden = 'fetchpriority="high"' if art == 'eager' else 'loading="lazy"'
    klasse = 'shot shot--phone' if h > b * 1.6 else 'shot'   # nur echte Handy-Bildschirme schmal
    return (f'<figure class="{klasse}"><picture><source type="image/webp" srcset="{srcset}" sizes="{groessen}">'
            f'<img src="{pfad}.jpg" alt="{html.escape(alt)}" width="{b}" height="{h}" {laden} decoding="async"></picture></figure>')


def seite(meta, inhalt):
    root = root_fuer(meta['pfad'])
    inhalt = inhalt.replace('{{root}}', root)
    inhalt = re.sub(r'\{\{shot:([^|}]+)\|([^|}]+)(?:\|([^|}]+))?(?:\|([^}]+))?\}\}',
                    lambda m: shot(root, m.group(1).strip(), m.group(2).strip(), (m.group(3) or 'lazy').strip(),
                                   (m.group(4) or '(max-width: 900px) 100vw, 60vw').strip()), inhalt)
    bild = DOMAIN + meta.get('bild', '/assets/images/referenz-kontor/kontor-dashboard-uebersicht.jpg')
    t, b = html.escape(meta['titel']), html.escape(meta['beschreibung'])
    vorab = ''.join(f'  <link rel="preload" as="image" href="{root}{p}" type="image/webp" fetchpriority="high">\n'
                    for p in meta.get('vorladen', []))
    return f'''<!DOCTYPE html>
<html lang="de-AT">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t}</title>
  <meta name="description" content="{b}">
  <meta name="robots" content="{meta.get('robots', 'index, follow, max-image-preview:large')}">
  <link rel="canonical" href="{DOMAIN}{meta['pfad']}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="de_AT">
  <meta property="og:site_name" content="Code und Licht">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{b}">
  <meta property="og:url" content="{DOMAIN}{meta['pfad']}">
  <meta property="og:image" content="{bild}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#25221F">
  <link rel="icon" href="{root}assets/images/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{root}assets/images/apple-touch-icon.png">
  <link rel="preload" href="{root}assets/fonts/opensans-latin-400-600.woff2" as="font" type="font/woff2" crossorigin>
{vorab}  <link rel="stylesheet" href="{root}css/site.css">
  <script type="application/ld+json">
{schema(meta)}
  </script>
</head>
<body>
{kopf(meta, root)}
<main id="inhalt">
{inhalt.strip()}
</main>

{fuss(root)}
<script src="{root}js/main.js" defer></script>
</body>
</html>
'''


def ziel_datei(meta):
    if meta.get('datei'):
        return os.path.join(WURZEL, meta['datei'])
    return os.path.join(WURZEL, meta['pfad'].strip('/'), 'index.html')


def pruefen(meta, fertig, datei):
    fehler = []
    if len(meta['titel']) > 60:
        fehler.append(f"Title {len(meta['titel'])} Zeichen")
    if len(meta['beschreibung']) > 155:
        fehler.append(f"Beschreibung {len(meta['beschreibung'])} Zeichen")
    if fertig.count('<h1') != 1:
        fehler.append(f"{fertig.count('<h1')} × H1")
    basis = os.path.dirname(datei)
    refs = re.findall(r'(?:src|href)="([^"#?]*)', fertig)
    for satz in re.findall(r'srcset="([^"]+)"', fertig):
        refs += [teil.strip().split(' ')[0] for teil in satz.split(',')]
    for ref in refs:
        if ref.startswith(('http', 'mailto:', 'tel:', 'data:')) or ref == '':
            continue
        weg = os.path.normpath(os.path.join(basis, ref))
        if ref.endswith('/'):
            weg = os.path.join(weg, 'index.html')
        if not os.path.exists(weg):
            fehler.append(f'fehlt: {ref}')
    for img in re.findall(r'<img [^>]*>', fertig):
        if 'alt=' not in img:
            fehler.append('Bild ohne alt: ' + img[:60])
        if 'width=' not in img or 'height=' not in img:
            fehler.append('Bild ohne Maße: ' + img[:60])
    return fehler


def main(schreiben):
    alle = []
    for name in sorted(os.listdir(QUELLE)):
        if name.endswith('.html'):
            meta, inhalt = lesen(os.path.join(QUELLE, name))
            alle.append((name, meta, inhalt))
    for name, meta, inhalt in alle:
        datei = ziel_datei(meta)
        fertig = seite(meta, inhalt)
        if schreiben:
            os.makedirs(os.path.dirname(datei), exist_ok=True)
            open(datei, 'w', encoding='utf-8').write(fertig)
    probleme = 0
    for name, meta, inhalt in alle:
        datei = ziel_datei(meta)
        fertig = seite(meta, inhalt)
        fehler = pruefen(meta, fertig, datei)
        probleme += len(fehler)
        woerter = len(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', inhalt)))
        print(f"{meta['pfad']:28} Title {len(meta['titel']):2}  Beschreibung {len(meta['beschreibung']):3}  "
              f"Wörter {woerter:4}  {'OK' if not fehler else '; '.join(fehler)}")
    if probleme:
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:] != ['pruefen'])
