const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
};

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...JSON_HEADERS, ...headers },
  });
}

const REGIONS = new Set(["central", "east", "north", "west", "south"]);

function clean(v, max) {
  return String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, max);
}

async function hashIp(request, env) {
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  const salt = env.RATE_SALT || "auckland-fpv-fallback-salt";
  const data = new TextEncoder().encode(`${salt}:${ip}`);
  const buf = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}

export async function onRequestPost({ request, env }) {
  try {
    const body = await request.json();

    // honeypot: real users never fill this
    if (clean(body.website, 50)) {
      return json({ ok: true, queued: true }); // silently accept, drop it
    }

    const name = clean(body.name, 90);
    const region = clean(body.region, 20).toLowerCase();
    const lat = Number(body.lat);
    const lon = Number(body.lon);
    const mapsUrl = clean(body.maps_url, 300);
    const access = clean(body.access, 500);
    const why = clean(body.why, 1200);
    const hazards = clean(body.hazards, 500);
    const submitter = clean(body.submitter, 90);

    if (name.length < 3) {
      return json({ ok: false, error: "Give the spot a name (at least 3 characters)." }, 400);
    }
    if (!REGIONS.has(region)) {
      return json({ ok: false, error: "Pick a region." }, 400);
    }
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      return json({ ok: false, error: "Need a valid latitude and longitude." }, 400);
    }
    if (why.length < 20) {
      return json({ ok: false, error: "Tell us a bit more about the spot (at least 20 characters)." }, 400);
    }
    if (mapsUrl && !/^https:\/\/(maps\.app\.goo\.gl|goo\.gl\/maps|www\.google\.com\/maps|maps\.google\.com)/.test(mapsUrl)) {
      return json({ ok: false, error: "That doesn't look like a Google Maps link." }, 400);
    }

    const ipHash = await hashIp(request, env);

    const recent = await env.fpv_community
      .prepare(
        `SELECT COUNT(*) AS c FROM submissions
          WHERE ip_hash = ? AND created_at > datetime('now','-1 day')`
      )
      .bind(ipHash)
      .first();

    if (recent && recent.c >= 5) {
      return json({ ok: false, error: "That's a lot of suggestions for one day. Try again tomorrow." }, 429);
    }

    await env.fpv_community
      .prepare(
        `INSERT INTO submissions (name, region, lat, lon, maps_url, access, why, hazards, submitter, ip_hash)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      )
      .bind(name, region, lat, lon, mapsUrl || null, access || null, why, hazards || null, submitter || null, ipHash)
      .run();

    return json({ ok: true, queued: true });
  } catch (err) {
    return json({ ok: false, error: "Could not submit that. Try again shortly." }, 500);
  }
}
