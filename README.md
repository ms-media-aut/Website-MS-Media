# MS Media — Website

Moderne One-Page-Website im Apple-Stil für **MS Media**, die Werbeagentur von
Michael Stabentheiner (Klagenfurt) — Webdesign, Werbefotografie, Imagefilm und
Drohnenaufnahmen.

## Struktur

```
index.html          Startseite (One-Pager)
impressum.html      Impressum & Datenschutz
css/style.css       Design-System (Apple-inspiriert, responsiv)
js/main.js          Scroll-Animationen, Zähler, mobile Navigation
assets/images/      Fotos (siehe assets/images/README.md)
```

## Lokal ansehen

Einfach `index.html` im Browser öffnen — die Seite ist rein statisch,
kein Build-Schritt nötig. Alternativ:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## Eigene Fotos einbinden

Siehe [`assets/images/README.md`](assets/images/README.md) — Bilder mit den
richtigen Dateinamen in den Ordner legen, fertig. Ohne Bilder zeigt die Seite
automatisch hochwertige Gradient-Platzhalter.

## Anpassen

- **Farben / Akzent:** CSS-Variablen am Anfang von `css/style.css` (`--accent`, `--grad`)
- **Texte:** direkt in `index.html`
- **Kontaktformular:** aktuell `mailto:`-Fallback — für echten Versand einen
  Dienst wie Formspree/Web3Forms eintragen (`action`-Attribut des Formulars)
