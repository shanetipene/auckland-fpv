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

export async function onRequestGet({ env }) {
  try {
    const { results } = await env.fpv_community
      .prepare(
        `SELECT spot_id,
                COUNT(*) AS n,
                AVG(seclusion) AS seclusion,
                AVG(quiet) AS quiet,
                AVG(flying) AS flying
           FROM ratings
          GROUP BY spot_id`
      )
      .all();

    const out = {};
    for (const r of results || []) {
      out[r.spot_id] = {
        n: r.n,
        seclusion: Math.round(r.seclusion * 10) / 10,
        quiet: Math.round(r.quiet * 10) / 10,
        flying: Math.round(r.flying * 10) / 10,
      };
    }
    return json({ ok: true, ratings: out }, 200, { "cache-control": "public, max-age=60" });
  } catch (err) {
    return json({ ok: false, error: "Could not load ratings." }, 500);
  }
}
