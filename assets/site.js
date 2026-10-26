/* Community ratings + suggest-a-spot for the Auckland FPV site.
   Depends on the inline `SPOTS` array defined by each page. */
(function () {
  "use strict";

  var fmt = function (n) { return (Math.round(n * 10) / 10).toFixed(1); };

  function updateBar(bar, value) {
    if (!bar) return;
    var fill = bar.querySelector("i");
    var num = bar.querySelector("b");
    var v = Math.max(0, Math.min(5, value));
    if (fill) {
      fill.style.width = (v / 5) * 100 + "%";
      fill.className = bar.dataset.metric === "quiet" && v <= 2 ? "bad" : "good";
    }
    if (num) num.textContent = fmt(v);
  }

  function applyRatings(ratings) {
    if (typeof SPOTS === "undefined") return;
    SPOTS.forEach(function (s) {
      var card = document.querySelector('.card[data-spot="' + s.id + '"]');
      if (!card) return;
      var agg = ratings && ratings[s.id];
      var box = card.querySelector(".community");
      if (!agg || !agg.n) {
        if (box) box.hidden = true;
        return;
      }
      if (box) {
        box.hidden = false;
        var note = box.querySelector(".cnote");
        if (note) {
          note.textContent =
            agg.n +
            " community rating" + (agg.n === 1 ? "" : "s") +
            " \u00b7 averaged with the editor rating";
        }
      }
      ["seclusion", "quiet", "flying"].forEach(function (key) {
        var bar = card.querySelector('.bar[data-metric="' + key + '"]');
        if (!bar) return;
        var editor = parseFloat(bar.dataset.editorial);
        if (!isFinite(editor)) return;
        var blended = (agg[key] * agg.n + editor) / (agg.n + 1);
        updateBar(bar, blended);
      });
    });
  }

  function loadRatings() {
    fetch("/api/ratings", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d && d.ok) applyRatings(d.ratings); })
      .catch(function () { /* offline or file:// - keep editor ratings */ });
  }

  /* ---------- rate this spot ---------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".ratebtn");
    if (!btn) return;
    var box = btn.closest(".ratebox");
    var form = box.querySelector(".rateform");
    form.hidden = !form.hidden;
    btn.textContent = form.hidden ? "Rate this spot" : "Cancel";
  });

  document.addEventListener("input", function (e) {
    if (e.target.matches(".rateform input[type=range]")) {
      var out = e.target.parentElement.querySelector("output");
      if (out) out.textContent = e.target.value;
    }
  });

  document.addEventListener("submit", function (e) {
    var form = e.target.closest(".rateform");
    if (!form) return;
    e.preventDefault();
    var card = form.closest(".card");
    var msg = form.closest(".ratebox").querySelector(".ratemsg");
    var data = new FormData(form);
    msg.textContent = "Saving\u2026";

    fetch("/api/rate", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        spot_id: card.dataset.spot,
        seclusion: Number(data.get("seclusion")),
        quiet: Number(data.get("quiet")),
        flying: Number(data.get("flying"))
      })
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.ok) {
          msg.textContent = d.error || "Could not save that.";
          return;
        }
        msg.textContent = "Thanks \u2014 counted.";
        form.hidden = true;
        var btn = form.closest(".ratebox").querySelector(".ratebtn");
        if (btn) btn.textContent = "Rate this spot";
        loadRatings();
      })
      .catch(function () {
        msg.textContent = "Could not reach the server.";
      });
  });

  /* ---------- suggest a spot ---------- */
  var dlg = document.getElementById("suggestModal");
  var openBtn = document.getElementById("suggestBtn");
  var closeBtn = document.getElementById("closeModal");
  var sform = document.getElementById("suggestForm");

  if (openBtn && dlg && dlg.showModal) {
    openBtn.addEventListener("click", function () { dlg.showModal(); });
  }
  if (closeBtn && dlg) {
    closeBtn.addEventListener("click", function () { dlg.close(); });
  }
  if (dlg) {
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }

  function parseCoords(text) {
    if (!text) return null;
    var m =
      text.match(/@(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)/) ||
      text.match(/[?&]q=(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)/) ||
      text.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/);
    if (!m) return null;
    var lat = parseFloat(m[1]);
    var lon = parseFloat(m[2]);
    if (!isFinite(lat) || !isFinite(lon)) return null;
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) return null;
    return { lat: lat, lon: lon };
  }

  var mapsInput = sform && sform.querySelector('[name="maps_url"]');
  var latInput = document.getElementById("fLat");
  var lonInput = document.getElementById("fLon");
  var geoHint = document.getElementById("geoHint");

  if (mapsInput) {
    mapsInput.addEventListener("input", function () {
      var c = parseCoords(mapsInput.value);
      if (c && latInput && lonInput) {
        latInput.value = c.lat.toFixed(5);
        lonInput.value = c.lon.toFixed(5);
        if (geoHint) geoHint.textContent = "Coordinates pulled from the link.";
      }
    });
  }

  var geoBtn = document.getElementById("geoBtn");
  if (geoBtn) {
    geoBtn.addEventListener("click", function () {
      if (!navigator.geolocation) {
        if (geoHint) geoHint.textContent = "This browser can't share location \u2014 paste a Maps link instead.";
        return;
      }
      if (geoHint) geoHint.textContent = "Getting your location\u2026";
      navigator.geolocation.getCurrentPosition(
        function (p) {
          if (latInput) latInput.value = p.coords.latitude.toFixed(5);
          if (lonInput) lonInput.value = p.coords.longitude.toFixed(5);
          if (geoHint) geoHint.textContent = "Location filled in.";
        },
        function () {
          if (geoHint) geoHint.textContent = "Location unavailable \u2014 paste a Maps link instead.";
        },
        { timeout: 10000 }
      );
    });
  }

  if (sform) {
    sform.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = document.getElementById("suggestMsg");
      var btn = sform.querySelector('button[type="submit"]');
      var data = new FormData(sform);
      var payload = {
        name: data.get("name"),
        region: data.get("region"),
        lat: Number(data.get("lat")),
        lon: Number(data.get("lon")),
        maps_url: data.get("maps_url"),
        access: data.get("access"),
        why: data.get("why"),
        hazards: data.get("hazards"),
        submitter: data.get("submitter"),
        website: data.get("website")
      };

      if (!payload.website) delete payload.website;

      msg.textContent = "Sending\u2026";
      if (btn) btn.disabled = true;

      fetch("/api/suggest", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (!d.ok) {
            msg.textContent = d.error || "Could not send that.";
            if (btn) btn.disabled = false;
            return;
          }
          var ok = document.createElement("div");
          ok.className = "okmsg";
          ok.innerHTML =
            "<b>Thanks \u2014 that's queued.</b><br>Spots are reviewed once a day: airspace, access and legality get checked before anything is added to the site.";
          sform.replaceWith(ok);
        })
        .catch(function () {
          msg.textContent = "Could not reach the server. Try again shortly.";
          if (btn) btn.disabled = false;
        });
    });
  }

  loadRatings();
})();
