"""Bilder für das Referenzprojekt „Kontor“ aus den Bildschirmfotos der Demo-Fassung erzeugen.

    python3 -I werkzeuge/referenz_bilder.py <screenshots-ordner>

<screenshots-ordner>: PNG-Bildschirmfotos einer Demo-Fassung der Plattform, umbenannt in „Kontor“ und gefüllt mit den
erfundenen Daten eines Elektrobetriebs (Elektro Brunnweger GmbH, Hotel Seeblick Beispiel GmbH, Musterbau Wohnprojekte
GmbH …): Briefkopf, Leistungen, Preise, Beiträge und Galerie gehören zu diesem Beispielbetrieb, keine echten Kunden
oder Zahlen. Die Bilder werden zugeschnitten und als WebP (Qualität 80) und JPEG (Qualität 78) nach
assets/images/referenz-kontor/ geschrieben, dazu je eine 720 px breite WebP-Fassung (-720) für Handys.
"""
import os
import sys

from PIL import Image

ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'images', 'referenz-kontor')

# Quelle, Ziel, Zuschnitt (oben, Höhe) in Pixeln des Originals
BILDER = [
    ('uebersicht', 'kontor-dashboard-uebersicht', (0, 1340)),
    ('anfragen', 'kontor-anfragen', (0, 640)),
    ('kalkulation', 'kontor-kalkulation', (0, 1000)),
    ('angebot', 'kontor-angebot', (0, 1200)),
    ('rechnung', 'kontor-rechnung', (0, 1200)),
    ('kundenkarte', 'kontor-kundenkarte', (0, 1400)),
    ('zeiten-verrechnen', 'kontor-zeiten-verrechnen', (0, 1200)),
    ('belegpostfach', 'kontor-belegpostfach', (0, 1015)),
    ('auswertungen', 'kontor-auswertungen-uva', (0, 1200)),
    ('social-planer', 'kontor-social-planer', (0, 1240)),
    ('social-beitrag', 'kontor-social-beitrag', (0, 1300)),
    ('social-bibliothek', 'kontor-social-bibliothek', (0, 1071)),
    ('galerie', 'kontor-galerie', (0, 1064)),
    ('kundenportal-galerie', 'kontor-kundenportal', (0, 1300)),
    ('handy-angebot', 'kontor-handy-angebot', (0, 2202)),
    ('handy-kunden', 'kontor-handy-kunden', (0, 2202)),
    ('handy-social', 'kontor-handy-social', (0, 2202)),
]


def main(quelle):
    os.makedirs(ZIEL, exist_ok=True)
    for name, ziel, (oben, hoehe) in BILDER:
        im = Image.open(os.path.join(quelle, name + '.png')).convert('RGB')
        im = im.crop((0, oben, im.width, min(im.height, oben + hoehe)))
        im.save(os.path.join(ZIEL, ziel + '.webp'), 'WEBP', quality=80, method=6)
        im.save(os.path.join(ZIEL, ziel + '.jpg'), 'JPEG', quality=78, optimize=True, progressive=True)
        if im.width > 720:   # kleinere Fassung für Handys (srcset)
            klein = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
            klein.save(os.path.join(ZIEL, ziel + '-720.webp'), 'WEBP', quality=80, method=6)
        kb = os.path.getsize(os.path.join(ZIEL, ziel + '.webp')) // 1024
        print(f'{ziel:36} {im.width}×{im.height}  {kb} KB')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
