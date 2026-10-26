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

function num(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return null;
  if (n < 0 || n > 5) return null;
  // snap to 0.5 steps
  return Math.round(n * 2) / 2;
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
    const spotId = String(body.spot_id || "").trim();
    if (!/^[a-z0-9-]{2,60}$/.test(spotId)) {
      return json({ ok: false, error: "Unknown spot." }, 400);
    }

    const seclusion = num(body.seclusion);
    const quiet = num(body.quiet);
    const flying = num(body.flying);
    if (seclusion === null || quiet === null || flying === null) {
      return json({ ok: false, error: "Ratings must be between 0 and 5." }, 400);
    }

    const ipHash = await hashIp(request, env);

    const recent = await env.fpv_community
      .prepare(
        `SELECT COUNT(*) AS c FROM ratings
          WHERE ip_hash = ? AND spot_id = ?
            AND created_at > datetime('now','-1 day')`
      )
      .bind(ipHash, spotId)
      .first();

    if (recent && recent.c > 0) {
      return json(
        { ok: false, error: "You've already rated this spot today. Thanks though." },
        429
      );
    }

    await env.fpv_community
      .prepare(
        `INSERT INTO ratings (spot_id, seclusion, quiet, flying, ip_hash)
         VALUES (?, ?, ?, ?, ?)`
      )
      .bind(spotId, seclusion, quiet, flying, ipHash)
      .run();

    const agg = await env.fpv_community
      .prepare(
        `SELECT COUNT(*) AS n,
                AVG(seclusion) AS seclusion,
                AVG(quiet) AS quiet,
                AVG(flying) AS flying
           FROM ratings WHERE spot_id = ?`
      )
      .bind(spotId)
      .first();

    return json({
      ok: true,
      spot_id: spotId,
      aggregate: {
        n: agg.n,
        seclusion: Math.round(agg.seclusion * 10) / 10,
        quiet: Math.round(agg.quiet * 10) / 10,
        flying: Math.round(agg.flying * 10) / 10,
      },
    });
  } catch (err) {
    return json({ ok: false, error: "Could not save your rating." }, 500);
  }
}
