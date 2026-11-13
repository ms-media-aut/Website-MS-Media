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
webdesign-kaernten/      Webdesign Kärnten und Klagenfurt (gebaut)
app-entwicklung/         App-Entwicklung (gebaut)
referenzen/kontor/       Referenzprojekt Kontor (gebaut)
seo-optimierung/         SEO-Optimierung (gebaut)
impressum.html           Impressum und Datenschutz (gebaut)
css/site.css             Gestaltung nach CI 2026
css/style.css            alte Gestaltung, nur noch für das Kärnten-Rätsel
js/main.js               Menü am Handy, Einblenden, Kontaktformular, Cookie-Hinweis
kaernten-raetsel/        Spiel (eigene Seite)
contact.php              Versand des Kontaktformulars
llms.txt, sitemap.xml, robots.txt  für Suchmaschinen und KI-Suchen
assets/                  Schriften (Open Sans, Archivo), Bilder, Videos
```

## Seiten ändern

Texte in `quelle/` bearbeiten, dann bauen und prüfen:

```bash
python3 -I werkzeuge/seiten_bauen.py          # schreibt die Seiten, prüft Title (≤ 60), Beschreibung (≤ 155), eine H1, Links, Bilder
python3 -m http.server 8000                   # ansehen unter http://localhost:8000
```

Die gebauten HTML-Dateien nicht direkt bearbeiten; sie werden beim nächsten Bauen überschrieben.

## Hochladen

Die Seite liegt als statische Dateien auf dem Webserver (Upload als ZIP). Hochgeladen werden alle Dateien außer
`quelle/`, `werkzeuge/`, `.claude/`, `.git/` und `README.md`. Die Videos in `assets/video/` liegen schon am Server.

## SEO (Recherche 13.11.2026, Google-Suchvorschläge Österreich)

| Seite | Hauptbegriffe |
|---|---|
| Startseite | Webdesign Kärnten, App-Entwicklung Kärnten, Werbeagentur/Webagentur Klagenfurt |
| /webdesign-kaernten/ | Webdesign Kärnten, Webdesign Klagenfurt, Webdesigner Villach, Website/Homepage erstellen lassen Kärnten/Klagenfurt |
| /app-entwicklung/ | App-Entwicklung Kärnten/Österreich, App entwickeln lassen, individuelle Software, Softwareentwicklung Kärnten |
| /seo-optimierung/ | SEO Kärnten, SEO Klagenfurt, SEO-Agentur Kärnten/Klagenfurt, SEO Villach |
| /referenzen/kontor/ | Referenz Web-App, Kundenportal, Dashboard, Auftragsverwaltung |

Lighthouse Handy (13.11.2026, lokal): Startseite 91, Webdesign 99, App-Entwicklung 99, Kontor 97, SEO 100;
Barrierefreiheit, Best Practices und SEO überall 100.
