"""Bilder für das Referenzprojekt „Kontor“ aus den Oberflächen-Screenshots der Studio-Plattform erzeugen.

    python3 -I werkzeuge/referenz_bilder.py <screenshots-ordner> <archivo-ttf> <opensans-ttf>

<screenshots-ordner>: die Bilder aus system/ansicht/bilder/ (Repo Michaelstabentheiner, Zweig system-kunden-angebote).
Sie zeigen nur die erfundenen Daten des Oberflächentests (Alpenblick Tourismus GmbH, Bergfilm Studio, Anna Muster …).
Der Programmname im Logo wird durch „Kontor“ ersetzt (Archivo wie im Original, „Kon“ hell, „tor“ in Sand), die
Bilder werden zugeschnitten und als WebP (Qualität 80) und JPEG (Qualität 78) nach assets/images/referenz-kontor/
geschrieben, dazu je eine 720 px breite WebP-Fassung (-720) für Handys. Wo der Name im Fließtext steht (Belegpostfach, Social Hub), wird die Zeile mit Open Sans neu gesetzt
(TTF aus brand/ci-2026/fonts/opensans-latin-400-600.woff2, umgewandelt mit fontTools). Ausgelassen sind Ansichten mit Markt- oder Steuerkennzahlen und Hinweisen auf interne Werkzeuge.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'images', 'referenz-kontor')

# Quelle, Ziel, Zuschnitt (oben, Höhe) in Pixeln des 1440 px breiten Originals, Logo ersetzen
BILDER = [
    ('uebersicht', 'kontor-dashboard-uebersicht', (0, 1340), True),
    ('uebersicht', 'kontor-dashboard-hero', (0, 900), True),
    ('anfragen', 'kontor-anfragen', (0, 640), True),
    ('kalkulation', 'kontor-kalkulation', (0, 1000), True),
    ('angebot', 'kontor-angebot', (0, 1200), True),
    ('rechnung', 'kontor-rechnung', (0, 1200), True),
    ('kundenkarte', 'kontor-kundenkarte', (0, 1400), True),
    ('zeiten-verrechnen', 'kontor-zeiten-verrechnen', (0, 1200), True),
    ('belegpostfach', 'kontor-belegpostfach', (0, 1038), True),
    ('auswertungen', 'kontor-auswertungen-uva', (0, 1200), True),
    ('social-planer', 'kontor-social-planer', (0, 1340), True),
    ('kb-auswahl', 'kontor-kundenportal-auswahl', (0, 1542), False),
    ('kb-portal', 'kontor-kundenportal', (0, 1500), False),
    ('kb-galerien', 'kontor-galerien', (0, 1000), True),
    ('handy-angebot', 'kontor-handy-angebot', (0, 1688), False),
    ('handy-kartei', 'kontor-handy-kunden', (0, 1688), False),
]


def logo_ersetzen(im, schrift_pfad):
    d = ImageDraw.Draw(im)
    grund = im.getpixel((150, 8))
    d.rectangle((58, 10, 150, 44), fill=grund)
    f = ImageFont.truetype(schrift_pfad, 19)
    try:
        f.set_variation_by_axes([520, 100])
    except Exception:
        pass
    # ganzes Wort in Sand, dann „Kon“ hell darüber: gleiche Laufweite wie ein Wort, keine Lücke an der Farbgrenze
    d.text((62, 17), 'Kontor', font=f, fill=(203, 189, 147))
    d.text((62, 17), 'Kon', font=f, fill=(236, 233, 228))


# Untertitel, in denen der Programmname im Fließtext steht: (Bild, Zeile oben/unten, Grundlinie, alter Text, neuer Text)
ZEILEN = {
    'kontor-belegpostfach': (118, 138, 131,
                             'Belege fotografieren oder hochladen; LensHub liest Datum, Betrag, Steuer und',
                             'Belege fotografieren oder hochladen; Kontor liest Datum, Betrag, Steuer und'),
    'kontor-social-planer': (140, 161, 154,
                             'LensHub veröffentlicht zur geplanten Zeit von selbst.',
                             'Kontor veröffentlicht zur geplanten Zeit von selbst.'),
}


def zeile_ersetzen(im, textschrift, oben, unten, grundlinie, alt, neu):
    """Zeile übermalen und neu setzen; Schriftgröße so gewählt, dass der alte Text so breit wäre wie im Bild."""
    px = im.load()
    xs = [x for x in range(232, 1100) if any(sum(px[x, y]) > 300 for y in range(oben, unten))]
    breite = xs[-1] - xs[0]
    d = ImageDraw.Draw(im)
    groesse = min((g / 4 for g in range(44, 64)), key=lambda g: abs(ImageFont.truetype(textschrift, g).getlength(alt) - breite))
    f = ImageFont.truetype(textschrift, groesse)
    d.rectangle((xs[0] - 2, oben, 1100, unten), fill=px[1090, oben])
    d.text((xs[0] - 2, grundlinie), neu, font=f, fill=(150, 150, 147), anchor='ls')


def main(quelle, schrift, textschrift):
    os.makedirs(ZIEL, exist_ok=True)
    for name, ziel, (oben, hoehe), logo in BILDER:
        im = Image.open(os.path.join(quelle, name + '.webp')).convert('RGB')
        im = im.crop((0, oben, im.width, min(im.height, oben + hoehe)))
        if logo:
            logo_ersetzen(im, schrift)
        if ziel in ZEILEN:
            zeile_ersetzen(im, textschrift, *ZEILEN[ziel])
        im.save(os.path.join(ZIEL, ziel + '.webp'), 'WEBP', quality=80, method=6)
        im.save(os.path.join(ZIEL, ziel + '.jpg'), 'JPEG', quality=78, optimize=True, progressive=True)
        if im.width > 720:   # kleinere Fassung für Handys (srcset)
            klein = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
            klein.save(os.path.join(ZIEL, ziel + '-720.webp'), 'WEBP', quality=80, method=6)
        kb = os.path.getsize(os.path.join(ZIEL, ziel + '.webp')) // 1024
        print(f'{ziel:36} {im.width}×{im.height}  {kb} KB')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
