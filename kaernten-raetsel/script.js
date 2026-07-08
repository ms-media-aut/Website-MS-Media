/* Kärnten-Rätsel — Spiellogik (nutzt KAERNTEN_OUTLINE / ROUND_POOL aus data.js) */
(function () {
  "use strict";

  const ROUNDS_PER_GAME = 5;
  const MAX_SCORE = 5000;
  const DECAY_KM = 25;
  const HINT_PENALTY = 1000;

  function shuffled(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  const ROUNDS = shuffled(ROUND_POOL).slice(0, Math.min(ROUNDS_PER_GAME, ROUND_POOL.length));

  const svg = document.getElementById("krMap");
  if (!svg) return;
  const VB_W = 800, PAD = 40;

  const lons = KAERNTEN_OUTLINE.map((p) => p[0]);
  const lats = KAERNTEN_OUTLINE.map((p) => p[1]);
  const lonMin = Math.min(...lons), lonMax = Math.max(...lons);
  const latMin = Math.min(...lats), latMax = Math.max(...lats);
  const centerLon = (lonMin + lonMax) / 2;
  const centerLat = (latMin + latMax) / 2;
  const cosLat0 = Math.cos((centerLat * Math.PI) / 180);
  const spanX = (lonMax - lonMin) * cosLat0;
  const spanY = latMax - latMin;
  const scale = (VB_W - PAD * 2) / spanX;
  const VB_H = Math.round(spanY * scale + PAD * 2);
  svg.setAttribute("viewBox", "0 0 " + VB_W + " " + VB_H);

  function project(lon, lat) {
    return { x: (lon - centerLon) * cosLat0 * scale + VB_W / 2, y: (centerLat - lat) * scale + VB_H / 2 };
  }
  function unproject(x, y) {
    return { lon: (x - VB_W / 2) / (cosLat0 * scale) + centerLon, lat: centerLat - (y - VB_H / 2) / scale };
  }
  function haversineKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLon = ((lon2 - lon1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  const NS = "http://www.w3.org/2000/svg";
  const pathD =
    KAERNTEN_OUTLINE.map((p, i) => {
      const { x, y } = project(p[0], p[1]);
      return (i === 0 ? "M" : "L") + x.toFixed(2) + "," + y.toFixed(2);
    }).join(" ") + " Z";
  const outlinePath = document.createElementNS(NS, "path");
  outlinePath.setAttribute("d", pathD);
  outlinePath.setAttribute("class", "kr-outline");
  svg.appendChild(outlinePath);

  function makeMarker(cls, x, y) {
    const g = document.createElementNS(NS, "g");
    g.setAttribute("class", "kr-marker " + cls);
    const ring = document.createElementNS(NS, "circle");
    ring.setAttribute("class", "kr-ring");
    ring.setAttribute("cx", x); ring.setAttribute("cy", y); ring.setAttribute("r", 13);
    const dot = document.createElementNS(NS, "circle");
    dot.setAttribute("class", "kr-dot");
    dot.setAttribute("cx", x); dot.setAttribute("cy", y); dot.setAttribute("r", 7);
    g.appendChild(ring); g.appendChild(dot);
    return g;
  }

  function quadrantName(lon, lat) {
    const n = lat >= centerLat, e = lon >= centerLon;
    if (n && e) return "Nordosten";
    if (n && !e) return "Nordwesten";
    if (!n && e) return "Südosten";
    return "Südwesten";
  }
  function elevationBand(alt) {
    if (alt == null) return null;
    if (alt < 600) return "Talregion (unter 600 m)";
    if (alt < 1000) return "Mittellage (600–1000 m)";
    if (alt < 1800) return "Hochlage (1000–1800 m)";
    return "Hochgebirge (über 1800 m)";
  }
  function buildClue(r) {
    const parts = ["Der Ort liegt im " + quadrantName(r.lon, r.lat) + " Kärntens"];
    const band = elevationBand(r.alt);
    if (band) parts.push("auf " + Math.round(r.alt) + " m Seehöhe — " + band);
    return parts.join(", ") + ".";
  }

  let roundIndex = 0, guess = null, locked = false, guessEl = null, hintUsed = false;
  const results = [];

  const guessBtn = document.getElementById("krGuessBtn");
  const nextBtn = document.getElementById("krNextBtn");
  const hint = document.getElementById("krHint");
  const clueBtn = document.getElementById("krClueBtn");
  const clueText = document.getElementById("krClueText");
  const resultCard = document.getElementById("krResultCard");
  const summaryCard = document.getElementById("krSummaryCard");
  const gridEl = document.getElementById("krGrid");
  const progressEl = document.getElementById("krProgress");

  function clearDynamicMapEls() {
    svg.querySelectorAll(".kr-marker, .kr-link-line").forEach((el) => el.remove());
  }

  function loadRound() {
    const r = ROUNDS[roundIndex];
    document.getElementById("krPhoto").src = r.img;
    document.getElementById("krRoundIndicator").textContent = "Runde " + (roundIndex + 1) + " / " + ROUNDS.length;
    document.getElementById("krProgressCount").textContent = (roundIndex + 1) + " / " + ROUNDS.length;
    document.getElementById("krProgressFill").style.width = (roundIndex / ROUNDS.length) * 100 + "%";
    guess = null; locked = false; guessEl = null; hintUsed = false;
    clueText.textContent = "";
    clueBtn.disabled = false;
    clearDynamicMapEls();
    guessBtn.disabled = true; guessBtn.style.display = "inline-flex";
    nextBtn.style.display = "none";
    hint.textContent = "Noch kein Tipp gesetzt";
    resultCard.hidden = true;
  }

  function svgPointFromEvent(evt) {
    const pt = svg.createSVGPoint();
    const src = evt.touches ? evt.touches[0] : evt;
    pt.x = src.clientX; pt.y = src.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  }

  svg.addEventListener("click", (evt) => {
    if (locked) return;
    const { x, y } = svgPointFromEvent(evt);
    guess = unproject(x, y);
    if (guessEl) svg.removeChild(guessEl);
    guessEl = makeMarker("kr-guess", x, y);
    svg.appendChild(guessEl);
    guessBtn.disabled = false;
    hint.textContent = "Tipp gesetzt — verschiebbar bis zur Abgabe";
  });

  clueBtn.addEventListener("click", () => {
    if (hintUsed || locked) return;
    hintUsed = true;
    clueBtn.disabled = true;
    clueText.textContent = buildClue(ROUNDS[roundIndex]);
  });

  guessBtn.addEventListener("click", () => {
    if (!guess || locked) return;
    locked = true;
    const r = ROUNDS[roundIndex];
    const actual = project(r.lon, r.lat);
    const guessPt = project(guess.lon, guess.lat);

    const line = document.createElementNS(NS, "line");
    line.setAttribute("class", "kr-link-line");
    line.setAttribute("x1", guessPt.x); line.setAttribute("y1", guessPt.y);
    line.setAttribute("x2", actual.x); line.setAttribute("y2", actual.y);
    svg.insertBefore(line, guessEl);
    svg.appendChild(makeMarker("kr-actual", actual.x, actual.y));

    const distKm = haversineKm(guess.lat, guess.lon, r.lat, r.lon);
    const locationScore = Math.round(MAX_SCORE * Math.exp(-distKm / DECAY_KM));
    const hintPenalty = hintUsed ? HINT_PENALTY : 0;
    const score = Math.max(0, locationScore - hintPenalty);
    results.push({ name: r.name, distKm, score, locationScore, hintPenalty });

    document.getElementById("krScoreValue").innerHTML = score + "<small> / " + MAX_SCORE + "</small>";
    document.getElementById("krDistValue").textContent =
      distKm < 1 ? "Volltreffer — nur " + Math.round(distKm * 1000) + " m daneben" : distKm.toFixed(1) + " km vom echten Ort entfernt";
    const breakdownParts = [locationScore + " Punkte für Entfernung"];
    if (hintPenalty > 0) breakdownParts.push("−" + hintPenalty + " Hinweis");
    document.getElementById("krBreakdown").textContent = breakdownParts.join(" · ");
    document.getElementById("krPlaceValue").textContent = "Aufgenommen: " + r.name;
    resultCard.hidden = false;
    hint.textContent = "";
    clueBtn.disabled = true;
    guessBtn.style.display = "none";
    nextBtn.textContent = roundIndex === ROUNDS.length - 1 ? "Ergebnis ansehen" : "Nächstes Foto";
    nextBtn.style.display = "inline-flex";
    document.getElementById("krProgressFill").style.width = ((roundIndex + 1) / ROUNDS.length) * 100 + "%";
  });

  nextBtn.addEventListener("click", () => {
    roundIndex++;
    if (roundIndex >= ROUNDS.length) showSummary();
    else loadRound();
  });

  const MAX_TOTAL = MAX_SCORE * ROUNDS.length;
  const HIGHSCORE_KEY = "kaernten-raetsel-highscores";

  function toBase64Unicode(str) {
    const bytes = new TextEncoder().encode(str);
    let bin = "";
    bytes.forEach((b) => (bin += String.fromCharCode(b)));
    return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function fromBase64Unicode(b64) {
    const norm = b64.replace(/-/g, "+").replace(/_/g, "/");
    const bin = atob(norm);
    const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  }
  function encodeChallenge(name, total, scores) {
    return toBase64Unicode(JSON.stringify({ n: name, t: total, r: scores }));
  }
  function decodeChallenge(code) {
    try {
      const obj = JSON.parse(fromBase64Unicode(code));
      if (typeof obj.n === "string" && typeof obj.t === "number" && Array.isArray(obj.r)) return obj;
    } catch (e) {}
    return null;
  }

  const params = new URLSearchParams(location.search);
  const challengeCode = params.get("c");
  const CHALLENGE = challengeCode ? decodeChallenge(challengeCode) : null;
  if (CHALLENGE) {
    const banner = document.getElementById("krChallengeBanner");
    document.getElementById("krChallengeText").textContent =
      CHALLENGE.n + " fordert dich heraus: " + CHALLENGE.t + " / " + MAX_TOTAL + " Punkte zu schlagen!";
    banner.hidden = false;
  }

  const SEED_HIGHSCORES = [
    { name: "Sabine", total: 29140 },
    { name: "Gipfelstürmer", total: 27860 },
    { name: "Julia", total: 26310 },
    { name: "Wörthersee-Kini", total: 24980 },
    { name: "Anna", total: 23450 },
    { name: "Nockberge_Nick", total: 21770 },
    { name: "Lisa", total: 19980 },
    { name: "Dobrathias", total: 18120 },
    { name: "Gerlitzenhex", total: 16340 },
    { name: "Kevin", total: 14260 },
  ].map((e) => ({ ...e, seed: true }));

  function loadHighscores() {
    try {
      const raw = localStorage.getItem(HIGHSCORE_KEY);
      const list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch (e) { return []; }
  }
  function saveHighscoreEntry(name, total) {
    const list = loadHighscores();
    list.push({ name, total, date: new Date().toISOString() });
    list.sort((a, b) => b.total - a.total);
    localStorage.setItem(HIGHSCORE_KEY, JSON.stringify(list.slice(0, 10)));
  }
  function renderHighscores() {
    const combined = [...SEED_HIGHSCORES, ...loadHighscores()].sort((a, b) => b.total - a.total).slice(0, 10);
    const el = document.getElementById("krHighscoreList");
    el.innerHTML = "";
    combined.forEach((entry, i) => {
      const li = document.createElement("li");
      const rank = document.createElement("span"); rank.className = "kr-rank"; rank.textContent = i + 1 + ".";
      const name = document.createElement("span"); name.className = "kr-pname"; name.textContent = entry.name;
      const score = document.createElement("span"); score.className = "kr-pscore"; score.textContent = entry.total + " / " + MAX_TOTAL;
      li.appendChild(rank); li.appendChild(name); li.appendChild(score);
      el.appendChild(li);
    });
  }

  async function copyToClipboard(text) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (e) {}
    try {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return ok;
    } catch (e) { return false; }
  }

  function shareUrl() {
    return location.origin + location.pathname;
  }
  function challengeUrl() {
    const name = document.getElementById("krNameInput").value.trim() || "Anonym";
    const scores = results.map((r) => r.score);
    const code = encodeChallenge(name, currentTotal, scores);
    return { name, url: shareUrl() + "?c=" + code };
  }
  function updateShareLinks() {
    const url = shareUrl();
    const text = "Ich hab beim Kärnten-Rätsel von Code und Licht " + currentTotal + " / " + MAX_TOTAL + " Punkten erreicht!";
    document.getElementById("krShareWhatsapp").href = "https://wa.me/?text=" + encodeURIComponent(text + " " + url);
  }
  function updateChallengeLinks() {
    const { name, url } = challengeUrl();
    const text = name + " fordert dich heraus: " + currentTotal + " / " + MAX_TOTAL + " Punkte beim Kärnten-Rätsel zu schlagen!";
    document.getElementById("krChallengeWhatsapp").href = "https://wa.me/?text=" + encodeURIComponent(text + " " + url);
  }

  let currentTotal = 0;

  function showSummary() {
    progressEl.style.display = "none";
    gridEl.style.display = "none";
    resultCard.hidden = true;
    const total = results.reduce((s, r) => s + r.score, 0);
    currentTotal = total;
    document.getElementById("krTotalScore").innerHTML = total + "<small> / " + MAX_TOTAL + "</small>";
    const body = document.getElementById("krSummaryBody");
    body.innerHTML = results
      .map(
        (r, i) =>
          "<tr><td>" + (i + 1) + "</td><td class=\"kr-place\">" + r.name + "</td>" +
          "<td class=\"kr-num\">" + r.distKm.toFixed(1) + " km</td>" +
          "<td class=\"kr-num\">" + r.score + "</td></tr>"
      )
      .join("");

    const compareBanner = document.getElementById("krCompareBanner");
    if (CHALLENGE) {
      const diff = total - CHALLENGE.t;
      compareBanner.hidden = false;
      if (diff > 0) {
        compareBanner.className = "kr-compare kr-compare--win";
        compareBanner.textContent = "Geschafft — du hast " + CHALLENGE.n + " um " + diff + " Punkte geschlagen!";
      } else if (diff < 0) {
        compareBanner.className = "kr-compare kr-compare--lose";
        compareBanner.textContent = CHALLENGE.n + " war um " + -diff + " Punkte besser. Nächstes Mal!";
      } else {
        compareBanner.className = "kr-compare";
        compareBanner.textContent = "Unentschieden gegen " + CHALLENGE.n + " — exakt gleich viele Punkte!";
      }
    }

    renderHighscores();
    updateShareLinks();
    updateChallengeLinks();
    summaryCard.hidden = false;
  }

  document.getElementById("krSaveScoreBtn").addEventListener("click", () => {
    const status = document.getElementById("krSaveStatus");
    const name = document.getElementById("krNameInput").value.trim();
    if (!name) { status.textContent = "Bitte einen Namen eingeben."; return; }
    saveHighscoreEntry(name, currentTotal);
    renderHighscores();
    status.textContent = "Gespeichert für " + name + ".";
  });

  document.getElementById("krShareCopyBtn").addEventListener("click", async () => {
    const status = document.getElementById("krShareStatus");
    const ok = await copyToClipboard(shareUrl());
    status.textContent = ok ? "Link kopiert." : "Kopieren fehlgeschlagen.";
  });
  document.getElementById("krChallengeCopyBtn").addEventListener("click", async () => {
    const status = document.getElementById("krShareStatus");
    const { url } = challengeUrl();
    const ok = await copyToClipboard(url);
    status.textContent = ok ? "Herausforderungs-Link kopiert." : "Kopieren fehlgeschlagen.";
  });
  document.getElementById("krNameInput").addEventListener("input", () => updateChallengeLinks());
  document.getElementById("krRestartBtn").addEventListener("click", () => location.reload());

  loadRound();
})();
