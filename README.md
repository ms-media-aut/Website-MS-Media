# MS Media — Website

Website von **Code und Licht** (codeundlicht.at), die Werbeagentur von
Michael Stabentheiner (Klagenfurt) — Webdesign, Werbefotografie, Imagefilm und
Drohnenaufnahmen.

## Stand November 2026

Neu aufgebaut im CI 2026 von Michael Stabentheiner (Gold/Sand, Anthrazit, Papier, Open Sans, Radius 0); das Logo
„Code und Licht“ bleibt. Schwerpunkte: App-Entwicklung, Dashboards und Kundenportale, Webdesign, SEO für bestehende
Websites; großes Referenzprojekt „Kontor“ (Web-App einer Foto- und Videoproduktion, Bilder mit Beispieldaten).

## Struktur

```
quelle/*.html            Inhalte der Seiten (Metadaten als JSON-Block oben, dann der Inhalt von <main>)
werkzeuge/seiten_bauen.py  baut daraus die fertigen Seiten (Kopf, Menü, Fußzeile, Title, Beschreibung, Schema)
werkzeuge/referenz_bilder.py  Bildschirmfotos der Referenz Kontor (Name im Logo ersetzt, WebP und JPEG, 720er-Fassung)
index.html               Startseite (gebaut)
app-entwicklung/         App-Entwicklung (gebaut)
referenzen/kontor/       Referenzprojekt Kontor (gebaut)
seo-optimierung/         SEO-Optimierung (gebaut)
impressum.html           Impressum und Datenschutz (gebaut)
css/site.css             Gestaltung nach CI 2026
css/style.css            alte Gestaltung, nur noch für das Kärnten-Rätsel
js/main.js               Menü am Handy, Einblenden, Kontaktformular, Cookie-Hinweis
kaernten-raetsel/        Spiel (eigene Seite)
contact.php              Versand des Kontaktformulars
assets/                  Schriften (Open Sans, Archivo), Bilder, Videos
```

## Seiten ändern

Texte in `quelle/` bearbeiten, dann bauen und prüfen:

```bash
python3 -I werkzeuge/seiten_bauen.py          # schreibt die Seiten, prüft Title (≤ 60), Beschreibung (≤ 155), eine H1, Links, Bilder
python3 -m http.server 8000                   # ansehen unter http://localhost:8000
```

Die gebauten HTML-Dateien nicht direkt bearbeiten; sie werden beim nächsten Bauen überschrieben.
