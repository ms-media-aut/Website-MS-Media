/* Code und Licht — interactions */
(function () {
  "use strict";

  /* ---------- Scroll reveal ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Animated counters ---------- */
  function animateCount(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    var suffix = el.getAttribute("data-suffix") || "";
    var isYear = target >= 1900 && target <= 2100;
    var start = isYear ? target - 12 : 0;
    var duration = 1600;
    var t0 = null;

    function format(n) {
      return isYear ? String(n) : n.toLocaleString("de-AT") + suffix;
    }
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = format(Math.round(start + (target - start) * eased));
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  var counters = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var cio = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCount(entry.target);
            cio.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---------- Mobile navigation ---------- */
  var burger = document.getElementById("navBurger");
  var links = document.getElementById("navLinks");
  if (burger && links) {
    burger.addEventListener("click", function () {
      var open = links.classList.toggle("is-open");
      burger.classList.toggle("is-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      burger.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        links.classList.remove("is-open");
        burger.classList.remove("is-open");
        burger.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Media slots: load real images if present ---------- */
  document.querySelectorAll(".media-slot[data-img]").forEach(function (slot) {
    var src = slot.getAttribute("data-img");
    var img = new Image();
    img.alt = slot.getAttribute("data-alt") || "";
    img.onload = function () {
      img.setAttribute("loading", "lazy");
      slot.prepend(img);
      var fb = slot.querySelector(".media-slot__fallback");
      if (fb && !fb.querySelector(".play-badge")) fb.style.display = "none";
      if (fb && fb.querySelector(".play-badge")) fb.style.background = "rgba(0,0,0,0.25)";
    };
    img.src = src;
  });

  /* ---------- Kontaktformular: AJAX-Versand via FormSubmit ---------- */
  var contactForm = document.getElementById("contactForm");
  if (contactForm) {
    var statusEl = document.getElementById("contactStatus");
    var submitBtn = document.getElementById("contactSubmit");
    var submitLabel = submitBtn ? submitBtn.textContent : "Nachricht senden";

    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();

      // Honeypot: Bots füllen verstecke Felder aus, Menschen nicht
      var honey = contactForm.querySelector('[name="_honey"]');
      if (honey && honey.value) {
        statusEl.textContent = "Danke für Ihre Nachricht! Wir melden uns innerhalb von 24 Stunden.";
        statusEl.className = "contact__status contact__status--success";
        contactForm.reset();
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Wird gesendet …";
      statusEl.textContent = "";
      statusEl.className = "contact__status";

      var ajaxUrl = contactForm.action.replace(
        "https://formsubmit.co/",
        "https://formsubmit.co/ajax/"
      );

      fetch(ajaxUrl, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(contactForm),
      })
        .then(function (res) {
          if (!res.ok) throw new Error("Netzwerkfehler");
          return res.json();
        })
        .then(function () {
          statusEl.textContent = "Danke für Ihre Nachricht! Wir melden uns innerhalb von 24 Stunden.";
          statusEl.className = "contact__status contact__status--success";
          contactForm.reset();
        })
        .catch(function () {
          statusEl.textContent =
            "Leider ist etwas schiefgelaufen. Bitte schreiben Sie uns direkt an office@michaelstabentheiner.at.";
          statusEl.className = "contact__status contact__status--error";
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = submitLabel;
        });
    });
  }

  /* ---------- Hero video: bei reduzierter Bewegung pausieren ---------- */
  var heroVideo = document.querySelector(".hero__video");
  if (heroVideo && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    heroVideo.removeAttribute("autoplay");
    heroVideo.pause();
  }

  /* ---------- Footer year ---------- */
  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  /* ---------- Cookie-Consent + Google Analytics ---------- */
  var GA_ID = "G-SJPBQ5LKML";
  var CONSENT_KEY = "cul-consent";
  var banner = null;

  function loadAnalytics() {
    if (window.culAnalyticsLoaded) return;
    window.culAnalyticsLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", GA_ID, { anonymize_ip: true });
  }

  function hideBanner() {
    if (banner) {
      banner.remove();
      banner = null;
    }
  }

  function showBanner() {
    if (banner) return;
    banner = document.createElement("div");
    banner.className = "cookie-banner";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-label", "Cookie-Einwilligung");
    banner.innerHTML =
      '<p>Wir verwenden Google Analytics, um zu verstehen, wie unsere Website genutzt wird, und sie laufend zu verbessern. ' +
      'Mehr dazu in unserer <a href="/impressum.html#datenschutz">Datenschutzerklärung</a>.</p>' +
      '<div class="cookie-banner__actions">' +
      '<button type="button" class="cookie-banner__decline">Ablehnen</button>' +
      '<button type="button" class="cookie-banner__accept">Akzeptieren</button>' +
      "</div>";
    document.body.appendChild(banner);

    banner.querySelector(".cookie-banner__accept").addEventListener("click", function () {
      localStorage.setItem(CONSENT_KEY, "accepted");
      loadAnalytics();
      hideBanner();
    });
    banner.querySelector(".cookie-banner__decline").addEventListener("click", function () {
      localStorage.setItem(CONSENT_KEY, "declined");
      hideBanner();
    });
  }

  var consent = localStorage.getItem(CONSENT_KEY);
  if (consent === "accepted") {
    loadAnalytics();
  } else if (consent !== "declined") {
    showBanner();
  }

  document.querySelectorAll(".js-cookie-settings").forEach(function (el) {
    el.addEventListener("click", function (e) {
      e.preventDefault();
      localStorage.removeItem(CONSENT_KEY);
      showBanner();
    });
  });
})();
