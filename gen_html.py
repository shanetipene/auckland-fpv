import json, os, html, re

OUT = os.path.expanduser("~/.hermes/workspace/fpv-auckland")
os.makedirs(OUT, exist_ok=True)

CENTRAL = {"Coyle Park","Monte Cecilia","Waiatarua","Stonefields","Panmure Basin","Pt England","Orakei Basin","Glendowie"}

def load(path):
    return json.load(open(path))

base = load("spots.json")
def _is_central(s):
    if s.get("region"):
        return s["region"] == "central"
    return s["short"] in CENTRAL

regions = {
 "central": [s for s in base if _is_central(s)],
 "east":    [s for s in base if not _is_central(s)],
 "west":    load("spots_west.json"),
 "north":   load("spots_north.json"),
 "south":   load("spots_south.json"),
}

# short -> (quietest time, quietest days, avoid)
QUIET = {
"Musick Point": ("Weekday 06:30-09:00","Mon-Thu","Sat-Sun 07:00-15:00 (golf + walkers)"),
"Waitawa": ("Weekday 08:00-11:00","Tue-Thu","Sat-Sun 09:00-15:00 (MTB shuttles)"),
"Kawakawa Bay": ("Weekday 06:30-09:00","Mon-Thu","Summer weekends 09:00-16:00 (boat ramp)"),
"Mangemangeroa": ("Weekday 08:00-11:00","Mon-Thu","Sat-Sun 10:00-14:00 (walkers)"),
"Sunkist Bay": ("Weekday 07:00-09:30","Mon-Fri","Summer weekends 10:00-16:00"),
"Monte Cecilia": ("Weekday 08:00-10:00","Tue-Thu","Sat-Sun (weddings and events)"),
"Eastern Beach": ("Weekday 06:30-09:00","Mon-Thu","Summer weekends after 09:30"),
"Omana": ("Weekday 08:00-10:30","Tue-Thu","Sat-Sun 10:00-15:00 (park visitors)"),
"Maraetai": ("Weekday 06:30-09:00","Mon-Thu","Summer weekends 10:00-17:00"),
"Pt England": ("Weekday 07:00-10:00","Tue-Fri","Sat 08:00-13:00 (sport), all Sunday"),
"Coyle Park": ("Weekday 07:00-09:00","Mon-Thu","Sat-Sun 10:00-15:00; summer sunsets"),
"Stonefields": ("Weekday 06:30-08:30","Tue-Thu","Weekends 09:00-16:00; weekdays 15:00-16:00"),
"Glendowie": ("Weekday 07:00-09:00","Tue-Thu","Sat 08:00-13:00 (sport)"),
"Whitford": ("Any weekday 08:00-16:00","Mon-Fri","Weekends (recreational forestry traffic)"),
"Waiatarua": ("Weekday 10:00-14:00","Mon-Fri","Daily 06:00-08:00 and 17:00-19:00 (dog rush)"),
"Panmure Basin": ("Weekday 06:00-08:00","Mon-Thu","Sat-Sun 09:00-17:00; weekday lunch"),
"Lloyd Elsmore": ("Weekday 09:00-15:00","Tue-Thu","Sat 08:00-14:00 (sport); weekday evenings"),
"Orakei Basin": ("Weekday 06:30-08:30","Mon-Thu","Weekends 09:00-16:00 (boardwalk busy)"),

"Laingholm": ("Weekday 09:00-15:00","Mon-Thu","Weekends 10:00-15:00"),
"Awhitu": ("Weekday 09:00-15:00","Tue-Thu","Sat-Sun 10:00-15:00 (park visitors)"),
"French Bay": ("Weekday 06:30-09:00","Mon-Thu","Summer weekends 10:00-17:00 (boats, swimmers)"),
"Lynfield Cove": ("Weekday 08:00-11:00","Mon-Fri","Weekends 10:00-14:00"),
"Waikowhai": ("Weekday 07:00-09:30","Mon-Thu","Sat-Sun 10:00-15:00; wharf fishermen early"),
"Titirangi Beach": ("Weekday 06:30-09:00","Mon-Thu","Summer weekends 10:00-16:00"),
"Blockhouse Bay": ("Weekday 07:00-09:00 or after 18:00","Mon-Thu","Sat-Sun 10:00-16:00"),
"Woodhill": ("Sun 07:00-10:00, or weekday after 17:00","Sun","Weekdays 06:00-16:00 (logging); Sat (4WD/MTB)"),
"Green Bay": ("Weekday 08:00-11:00","Mon-Fri","Weekends 10:00-15:00"),
"Parrs Park": ("Weekday 09:00-15:00","Tue-Fri","Sat 08:00-13:00 (sport)"),
"Olympic Park": ("Weekday 09:00-15:00","Tue-Thu","Weekday 16:00-20:00 (athletics); weekends"),

"Pakiri": ("Weekday 07:00-11:00","Mon-Thu","Summer weekends 10:00-16:00 (surfers)"),
"Leigh": ("Weekday 06:30-09:30","Mon-Thu","Summer weekends 09:00-16:00 (boats, divers)"),
"Mahurangi West": ("Weekday 08:00-11:00","Tue-Thu","Sat-Sun 10:00-15:00"),
"Algies Bay": ("Weekday 07:00-10:00","Mon-Thu","Summer weekends 10:00-16:00"),
"Sandspit": ("Weekday 08:00-10:30","Mon-Thu","Weekends 09:00-16:00 (ferry, boats)"),
"Omaha": ("Weekday 06:30-09:30","Mon-Thu","Summer weekends 09:00-17:00"),
"Wenderholm": ("Weekday 08:00-11:00","Tue-Thu","Sat-Sun 10:00-16:00 (picnic crowds)"),
"Puhoi": ("Weekday 07:00-09:30","Mon-Thu","Summer weekends 10:00-15:00 (kayakers)"),
"Waiwera": ("Weekday 07:00-10:00","Mon-Fri","Weekends 10:00-15:00"),
"Manly": ("Weekday 06:30-09:00","Mon-Thu","Summer weekends 09:30-16:00"),
"Stanmore Bay": ("Weekday 07:00-09:30","Mon-Thu","Weekends 09:00-16:00"),
"Tindalls": ("Weekday 07:00-09:30","Mon-Fri","Weekends 10:00-15:00"),
"Hatfields": ("Weekday 07:00-09:30","Mon-Fri","Weekends 10:00-15:00"),
"Orewa": ("Weekday 06:00-08:30","Tue-Thu","Sat-Sun 08:00-18:00 (busiest beach in the north)"),
"Browns Bay": ("Weekday 06:30-09:00 (daylight only)","Mon-Thu","Weekends 09:00-17:00; after dark (transit lane ends)"),
"Long Bay": ("Weekday 07:00-09:00","Mon-Thu","Weekends 10:00-16:00"),
"Devonport": ("Weekday 06:30-08:30","Mon-Thu","Weekends 09:00-17:00 (ferry crowds)"),

"Karioitahi": ("Weekday 07:00-10:00 (before thermals)","Mon-Thu","Weekends 09:00-16:00 (surfers); midday thermals bring paragliders"),
"Orere Point": ("Weekday 07:00-10:00","Mon-Thu","Summer weekends 09:00-16:00"),
"Waiau Pa": ("Weekday 08:00-11:00","Mon-Fri","Weekends 09:00-15:00 (wharf fishermen)"),
"Glenbrook": ("Weekday 09:00-15:00","Mon-Fri","Weekends 10:00-15:00"),
"Bombay": ("Any weekday 08:00-16:00","Tue-Fri","Weekend afternoons (SH1 traffic)"),
"Matakawau": ("Weekday 08:00-12:00","Mon-Thu","Weekends 10:00-15:00"),
"Clevedon": ("Weekday 08:00-11:00","Tue-Fri","Sat 08:00-13:00 (farmers market)"),
"Kingseat": ("Weekday 09:00-15:00","Mon-Fri","Weekends 10:00-15:00"),
"Clarks Beach": ("Weekday 07:00-10:00","Mon-Thu","Summer weekends 09:00-16:00 (boat ramp)"),
"Karaka": ("Weekday 08:00-16:00","Tue-Fri","Weekends (model aero club uses the danger area)"),
"Waiuku": ("Weekday 08:00-11:00","Mon-Thu","Weekends 10:00-15:00"),
"Pukekohe": ("Weekday 09:00-15:00","Tue-Thu","Sat morning (market, sport)"),
}

META = {
 "central": dict(title="Central Auckland", short="Central", blurb="Isthmus parks and harbour reserves, 10-21 minutes from the CBD. Airspace is clean except Orakei Basin."),
 "east":    dict(title="East Auckland", short="East", blurb="Bucklands Beach out to the Pohutukawa Coast. Clean airspace the whole way; two sites need a regional-park permit."),
 "west":    dict(title="West Auckland", short="West", blurb="The Manukau Harbour side. The Waitakere Ranges and the Whenuapai control zone take out most of the west, so these are what's left."),
 "north":   dict(title="North Auckland", short="North", blurb="Hibiscus Coast, Mahurangi and Matakana. The North Shore is locked up by the control zone - the good flying starts north of Silverdale."),
 "south":   dict(title="South Auckland", short="South", blurb="Franklin. The airport control zone plus four aerodrome buffers cover the entire urban south, so everything legal is rural or coastal."),
}
ORDER = ["central","east","north","west","south"]

STATUS_LABEL = {"clear":"Clean - no permit","permit":"Regional park - permit","restricted":"Restricted - cert / ATC / private"}
STATUS_CLASS = {"clear":"ok","permit":"permit","restricted":"warn"}

for key, spots in regions.items():
    spots.sort(key=lambda s: -s["fpv_score"])
    for i, s in enumerate(spots, 1):
        s["num"] = i

KIND = {
"Laingholm":"harbour inlet","Awhitu":"wild coast","French Bay":"bush + harbour beach","Lynfield Cove":"sheltered cove",
"Waikowhai":"bush + wharf","Titirangi Beach":"beach + wharf","Blockhouse Bay":"clifftop + beach","Woodhill":"dunes + forest",
"Green Bay":"sheltered beach","Parrs Park":"open park","Olympic Park":"sports park",
"Pakiri":"ocean beach + dunes","Leigh":"harbour + surf beach","Mahurangi West":"harbour bays","Algies Bay":"quiet bay",
"Sandspit":"estuary + marina","Omaha":"white sand beach","Wenderholm":"bush + river mouth","Puhoi":"river valley",
"Waiwera":"river mouth beach","Manly":"sheltered beach","Stanmore Bay":"beach + park","Tindalls":"small bay",
"Hatfields":"beach + estuary","Orewa":"long beach","Browns Bay":"beach + reef","Long Bay":"long beach + cliffs",
"Devonport":"clifftop + harbour",
"Karioitahi":"black sand surf beach","Orere Point":"rocky coast","Waiau Pa":"harbour wharf","Glenbrook":"quiet harbour beach",
"Bombay":"hill country","Matakawau":"harbour point","Clevedon":"rural river valley","Kingseat":"village + open fields",
"Clarks Beach":"harbour beach","Karaka":"rural + sports park","Waiuku":"estuary + town","Pukekohe":"town parks",
}

for key, spots in regions.items():
    spots.sort(key=lambda s: -s["fpv_score"])
    for i, s in enumerate(spots, 1):
        s["num"] = i
        s["id"] = re.sub(r"[^a-z0-9]+", "-", s["short"].lower()).strip("-")
        if not s.get("kind"):
            s["kind"] = KIND.get(s["short"], "")
        t = QUIET.get(s["short"])
        if t:
            s["quiet_time"], s["quiet_days"], s["avoid"] = t
        elif not all(s.get(k) for k in ("quiet_time", "quiet_days", "avoid")):
            raise SystemExit("missing quiet data: " + s["short"])

def cards_html(spots):
    out = []
    for s in spots:
        bars = ""
        for key, label, val in (("seclusion", "Seclusion", s["secl"]), ("quiet", "Quiet", 5 - s["traffic"]), ("flying", "Flying", s["fly"])):
            pct = val / 5 * 100
            # all three bars read higher = better; amber when a site is genuinely busy
            tone = "bad" if key == "quiet" and val <= 2 else "good"
            bars += (f'<div class="bar" data-metric="{key}" data-editorial="{val}">'
                     f'<span>{label}</span><div class="track"><i class="{tone}" style="width:{pct:.0f}%"></i></div>'
                     f'<b>{val}</b></div>')
        out.append(f'''
      <article class="card" data-status="{s['status']}" data-spot="{s['id']}">
        <div class="cardhead">
          <div class="num {STATUS_CLASS[s['status']]}">{s['num']}</div>
          <div class="titles">
            <h3>{html.escape(s['name'])}</h3>
            <div class="meta">{s['drive_min']} min from CBD &middot; {s['drive_km']} km &middot; {html.escape(s['kind'])}</div>
          </div>
          <div class="score"><strong>{s['fpv_score']}</strong><span>/10</span></div>
        </div>
        <div class="badges"><span class="badge {STATUS_CLASS[s['status']]}">{STATUS_LABEL[s['status']]}</span></div>
        <div class="bars">{bars}</div>
        <div class="quiet">
          <div><span>Quietest time</span><b>{html.escape(s['quiet_time'])}</b></div>
          <div><span>Quietest days</span><b>{html.escape(s['quiet_days'])}</b></div>
          <div class="avoid"><span>Avoid</span><b>{html.escape(s['avoid'])}</b></div>
        </div>
        <p class="best"><strong>Best for:</strong> {html.escape(s['best'])}</p>
        <p class="haz"><strong>Hazards:</strong> {html.escape(s['hazards'])}</p>
        <p class="note">{html.escape(s['note'])}</p>
        <div class="community" hidden><span class="cnote"></span></div>
        <div class="ratebox">
          <button class="ratebtn" type="button">Rate this spot</button>
          <form class="rateform" hidden>
            <label><span>Seclusion</span><input type="range" name="seclusion" min="0" max="5" step="0.5" value="{s['secl']}"><output>{s['secl']}</output></label>
            <label><span>Quiet</span><input type="range" name="quiet" min="0" max="5" step="0.5" value="{5 - s['traffic']}"><output>{5 - s['traffic']}</output></label>
            <label><span>Flying</span><input type="range" name="flying" min="0" max="5" step="0.5" value="{s['fly']}"><output>{s['fly']}</output></label>
            <div class="row"><button type="submit">Submit rating</button></div>
          </form>
          <p class="ratemsg" role="status"></p>
        </div>
        <div class="links">
          <a href="{s['maps_url']}" target="_blank" rel="noopener">Open in Google Maps</a>
          <span class="coords">{s['lat']:.5f}, {s['lon']:.5f}</span>
        </div>
      </article>''')
    return "\n".join(out)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} FPV spots - Auckland</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root{{--bg:#0b0e13;--panel:#131820;--panel2:#0f141b;--line:#232c39;--txt:#e8eef6;--dim:#94a3b4;--ok:#1fb35a;--permit:#2f6fd0;--warn:#e08a00;--bad:#e5484d}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--txt);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
a{{color:#7cc4ff}}
.wrap{{max-width:1280px;margin:0 auto;padding:0 20px}}
nav{{position:sticky;top:0;z-index:1000;background:rgba(11,14,19,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
nav .wrap{{display:flex;gap:6px;align-items:center;height:56px;overflow-x:auto}}
nav .brand{{font-weight:800;letter-spacing:.3px;margin-right:10px;white-space:nowrap}}
nav .brand span{{color:var(--ok)}}
nav a{{padding:8px 12px;border-radius:8px;text-decoration:none;color:var(--dim);font-size:14px;font-weight:600;white-space:nowrap}}
nav a:hover{{background:#1a212b;color:#fff}}
nav a.on{{background:#1e2836;color:#fff}}
header.hero{{padding:44px 0 26px}}
header.hero h1{{margin:0 0 8px;font-size:clamp(26px,4vw,40px);letter-spacing:-.5px}}
header.hero p{{margin:0;color:var(--dim);max-width:820px}}
.statline{{display:flex;gap:22px;flex-wrap:wrap;margin-top:18px;color:var(--dim);font-size:14px}}
.statline b{{color:#fff}}
#map{{height:540px;border-radius:16px;border:1px solid var(--line);margin:8px 0 10px;z-index:1}}
.leaflet-popup-content{{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}}
.leaflet-popup-content b{{font-size:15px}}
.filters{{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 6px}}
.chip{{border:1px solid var(--line);background:var(--panel);color:var(--dim);padding:8px 14px;border-radius:999px;font-size:14px;font-weight:600;cursor:pointer}}
.chip.on{{background:#e8eef6;color:#0b0e13;border-color:#e8eef6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:18px;padding:16px 0 40px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px}}
.cardhead{{display:flex;gap:12px;align-items:flex-start}}
.num{{width:38px;height:38px;flex:0 0 38px;border-radius:50%;display:grid;place-items:center;font-weight:800;color:#fff;font-size:17px}}
.num.ok{{background:var(--ok)}} .num.permit{{background:var(--permit)}} .num.warn{{background:var(--warn)}}
.titles{{min-width:0}}.titles h3{{margin:0;font-size:19px;letter-spacing:-.2px;overflow-wrap:anywhere}}
.meta{{color:var(--dim);font-size:13px}}
.score{{margin-left:auto;text-align:right;line-height:1;padding-left:10px;flex:0 0 auto}}
.score strong{{font-size:24px}} .score span{{color:var(--dim);font-size:13px}}
.badges{{margin:12px 0 6px}}
.badge{{display:inline-block;font-size:12px;font-weight:700;padding:4px 10px;border-radius:999px;border:1px solid}}
.badge.ok{{color:#7ee2a8;border-color:#1c6b3f;background:#10241a}}
.badge.permit{{color:#9dc0ff;border-color:#234d8a;background:#101a2b}}
.badge.warn{{color:#ffc978;border-color:#7a4f10;background:#241a0d}}
.bars{{display:grid;gap:6px;margin:12px 0}}
.bar{{display:grid;grid-template-columns:92px 1fr 22px;gap:10px;align-items:center;font-size:13px;color:var(--dim)}}
.bar b{{color:#fff;text-align:right}}
.track{{height:6px;background:#1d2632;border-radius:999px;overflow:hidden}}
.track i{{display:block;height:100%;border-radius:999px}}
.track i.good{{background:var(--ok)}} .track i.bad{{background:var(--warn)}}
.quiet{{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:12px 0;display:grid;gap:6px;font-size:14px}}
.quiet div{{display:grid;grid-template-columns:120px 1fr;gap:8px}}
.quiet span{{color:var(--dim);font-size:13px}}
.quiet b{{font-weight:600}}
.quiet .avoid b{{color:#ffb4a2}}
p{{margin:10px 0;font-size:14.5px;color:#c9d4e1}}
p strong{{color:#fff}}
.note{{color:var(--dim);font-size:13.5px;border-left:2px solid var(--line);padding-left:12px}}
.links{{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font-size:13px}}
.coords{{color:#5f6c7d;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
section.rules{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px;margin:6px 0 40px}}
section.rules h2{{margin:0 0 10px;font-size:20px}}
section.rules li{{margin:6px 0;color:#c9d4e1;font-size:14.5px}}
footer{{border-top:1px solid var(--line);padding:22px 0 40px;color:#6b7889;font-size:13px}}
@media (max-width:640px){{#map{{height:400px}}.grid{{grid-template-columns:1fr}}.quiet div{{grid-template-columns:1fr}}}}
</style>
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<nav><div class="wrap">
  <div class="brand">AKL <span>FPV</span></div>
  {navlinks}
  <button class="navcta" id="suggestBtn" type="button">+ Suggest a spot</button>
</div></nav>

<div class="wrap">
  <header class="hero">
    <h1>{title} - FPV spots</h1>
    <p>{blurb}</p>
    <div class="statline">
      <div><b>{count}</b> spots</div>
      <div><b>{clean}</b> no permit</div>
      <div><b>{permit}</b> regional park</div>
      <div><b>{restricted}</b> restricted</div>
      <div>Airspace checked against live AirShare data, Oct 2026</div>
    </div>
  </header>

  <div id="map"></div>

  <div class="pinsnote">
    <div><b>About the pins and the names.</b> Each marker is a <b>reference point, not the launch spot</b> — usually the nearest car park, reserve entrance or road end, so it can sit 100–300 m from where you'll actually stand. Names are the official or most widely used name for the place; local signage, iwi names and some map apps differ, and a few spots go by more than one name. Navigate to the pin, then walk the last bit.</div>
  </div>

  <div class="filters">
    <button class="chip on" data-f="all">All spots</button>
    <button class="chip" data-f="clear">No permit</button>
    <button class="chip" data-f="permit">Regional park</button>
    <button class="chip" data-f="restricted">Restricted</button>
  </div>

  <main class="grid" id="cards">
{cards}
  </main>

  <section class="rules">
    <h2>Before you fly</h2>
    <ul>
      <li>Log the flight on AirShare - required on council land, and it's how you request ATC or aerodrome approval.</li>
      <li>Stay 30 m from people and dogs, 20 m from buildings, 50 m from playgrounds in use and infrastructure.</li>
      <li>Nothing over 2.5 kg on council land without council permission.</li>
      <li>FPV needs a spotter maintaining unaided line of sight - that's the CAA position, not optional.</li>
      <li>Sept-March: stay 30 m off shorebirds on beaches, and don't take off within 100 m of them.</li>
      <li>Inside a control zone or 4 km ring, the only recreational route is a Part 101 certificate plus approval - or a shielded operation.</li>
    </ul>
  </section>

  <footer>
    {title} &middot; {count} spots &middot; numbers are ranked within this region by overall score.
    Scores weight flying quality and seclusion; read the sub-scores for your own priorities.
    Basemap imagery &copy; Esri, Maxar, Earthstar Geographics. Airspace data &copy; AirShare / Airways NZ.
  </footer>
</div>

<dialog id="suggestModal" aria-labelledby="smodalTitle">
  <div class="smodal">
    <h2 id="smodalTitle">Suggest a spot</h2>
    <p class="sub">Reviewed once a day. Airspace, access and legality get checked before anything is added, so include anything you know about getting in.</p>
    <form id="suggestForm">
      <label class="field"><span>Spot name</span><input name="name" maxlength="90" required placeholder="e.g. Kaiaua Point"></label>
      <div class="grid2">
        <label class="field"><span>Region</span>
          <select name="region" required>
            <option value="">Choose…</option>
            <option value="central">Central</option>
            <option value="east">East</option>
            <option value="north">North</option>
            <option value="west">West</option>
            <option value="south">South</option>
          </select>
        </label>
        <label class="field"><span>Google Maps link (optional)</span><input name="maps_url" placeholder="https://maps.app.goo.gl/…"></label>
      </div>
      <div class="grid2">
        <label class="field"><span>Latitude</span><input name="lat" id="fLat" type="number" step="any" required placeholder="-36.84890"></label>
        <label class="field"><span>Longitude</span><input name="lon" id="fLon" type="number" step="any" required placeholder="174.76520"></label>
      </div>
      <div class="row"><button type="button" class="ghost" id="geoBtn">Use my location</button><span class="smsg" id="geoHint">Or paste a Maps link above and we'll pull the coordinates.</span></div>
      <label class="field"><span>Access</span><textarea name="access" maxlength="500" placeholder="Parking, track, gate, land owner, tide…"></textarea></label>
      <label class="field"><span>Why is it good?</span><textarea name="why" maxlength="1200" required placeholder="What makes it worth flying? Terrain, lines, sightlines, what's around."></textarea></label>
      <label class="field"><span>Hazards</span><textarea name="hazards" maxlength="500" placeholder="Powerlines, wind, people, wildlife, airspace…"></textarea></label>
      <label class="field"><span>Your name or handle (optional)</span><input name="submitter" maxlength="90"></label>
      <label class="hp"><span>Website</span><input name="website" tabindex="-1" autocomplete="off"></label>
      <div class="sactions">
        <button type="submit">Send for review</button>
        <button type="button" class="ghost" id="closeModal">Cancel</button>
      </div>
      <p class="smsg" id="suggestMsg" role="status"></p>
    </form>
  </div>
</dialog>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const SPOTS = {data};
const COL = {{clear:"#1fb35a", permit:"#2f6fd0", restricted:"#e08a00"}};
const map = L.map('map', {{scrollWheelZoom:true}});
const topo = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{{z}}/{{y}}/{{x}}', {{maxZoom:19, attribution:'Basemap &copy; Esri, HERE, Garmin, OpenStreetMap'}}).addTo(map);
const imagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{maxZoom:19, attribution:'Imagery &copy; Esri, Maxar'}});
const labels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}', {{maxZoom:19, opacity:0.9}});
const satellite = L.layerGroup([imagery, labels]);
const streets = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom:19, attribution:'&copy; OpenStreetMap'}});
L.control.layers({{"Topographic": topo, "Satellite": satellite, "Streets": streets}}, null, {{position:'topright'}}).addTo(map);
L.control.scale({{imperial:false, position:'bottomleft'}}).addTo(map);

const markers = {{}};
const bounds = [];
for (const s of SPOTS) {{
  const icon = L.divIcon({{className:'', iconSize:[27,27], iconAnchor:[13.5,13.5],
    html:`<div style="width:27px;height:27px;border-radius:50%;background:${{COL[s.status]}};color:#fff;font:800 12.5px/27px -apple-system,Segoe UI,Roboto,sans-serif;text-align:center;box-shadow:0 0 0 3px rgba(255,255,255,.92),0 4px 12px rgba(0,0,0,.55)">${{s.num}}</div>`}});
  const m = L.marker([s.lat, s.lon], {{icon}}).addTo(map);
  m.bindPopup(`<b>${{s.num}}. ${{s.name}}</b><br>${{s.fpv_score}}/10 &middot; ${{s.drive_min}} min from CBD<br>
    <span style="color:#555">Quietest:</span> ${{s.quiet_time}}<br>
    <span style="color:#555">Days:</span> ${{s.quiet_days}}<br>
    <a href="${{s.maps_url}}" target="_blank" rel="noopener">Google Maps</a>`);
  markers[s.num] = m;
  bounds.push([s.lat, s.lon]);
}}
if (bounds.length) map.fitBounds(bounds, {{padding:[40,40]}});

document.querySelectorAll('.chip').forEach(chip => {{
  chip.addEventListener('click', () => {{
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('on'));
    chip.classList.add('on');
    const f = chip.dataset.f;
    document.querySelectorAll('.card').forEach(c => {{
      c.style.display = (f === 'all' || c.dataset.status === f) ? '' : 'none';
    }});
    for (const s of SPOTS) {{
      const show = (f === 'all' || s.status === f);
      if (show) markers[s.num].addTo(map); else map.removeLayer(markers[s.num]);
    }}
  }});
}});
</script>
<script src="assets/site.js"></script>
</body></html>"""

def nav(current):
    parts = ['<a href="index.html">Index</a>']
    for k in ORDER:
        cls = ' class="on"' if k == current else ''
        parts.append(f'<a href="{k}.html"{cls}>{META[k]["short"]}</a>')
    return "\n  ".join(parts)

for key, spots in regions.items():
    m = META[key]
    counts = {st: sum(1 for s in spots if s["status"] == st) for st in ("clear","permit","restricted")}
    page = PAGE.format(
        title=m["title"], blurb=m["blurb"], navlinks=nav(key),
        count=len(spots), clean=counts["clear"], permit=counts["permit"], restricted=counts["restricted"],
        cards=cards_html(spots), data=json.dumps(spots, ensure_ascii=False),
    )
    open(os.path.join(OUT, f"{key}.html"), "w", encoding="utf-8").write(page)
    print("wrote", key, len(spots), "spots", len(page), "bytes")

# index
total = sum(len(v) for v in regions.values())
rows = []
for k in ORDER:
    sp = regions[k]
    top = sp[0]
    rows.append(f'''<a class="region" href="{k}.html">
      <div class="rhead"><h2>{META[k]["title"]}</h2><span class="pill">{len(sp)} spots</span></div>
      <p>{html.escape(META[k]["blurb"])}</p>
      <div class="rfoot"><span>Top pick: <b>{html.escape(top["short"])}</b> ({top["fpv_score"]}/10)</span><span class="go">Open &rarr;</span></div>
    </a>''')

index = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auckland FPV spots</title>
<style>
:root{{--bg:#0b0e13;--panel:#131820;--line:#232c39;--txt:#e8eef6;--dim:#94a3b4;--ok:#1fb35a}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--txt);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 20px}}
header{{padding:70px 0 30px}}
h1{{margin:0 0 10px;font-size:clamp(30px,5vw,48px);letter-spacing:-1px}}
h1 span{{color:var(--ok)}}
header p{{color:var(--dim);max-width:760px;margin:0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px;padding:20px 0 60px}}
.region{{display:flex;flex-direction:column;text-decoration:none;color:inherit;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px;transition:.15s}}
.region:hover{{border-color:#3a4757;transform:translateY(-2px)}}
.rhead{{display:flex;align-items:center;justify-content:space-between;gap:10px}}
.rhead h2{{margin:0;font-size:21px}}
.pill{{font-size:12px;font-weight:700;color:var(--dim);border:1px solid var(--line);padding:3px 10px;border-radius:999px}}
.region p{{color:var(--dim);font-size:14px;margin:10px 0 16px;flex:1}}
.rfoot{{display:flex;justify-content:space-between;font-size:13px;color:var(--dim);border-top:1px solid var(--line);padding-top:12px;margin-top:auto}}
.rfoot b{{color:#fff}}
.go{{color:#7cc4ff;font-weight:700}}
footer{{border-top:1px solid var(--line);padding:24px 0 60px;color:#6b7889;font-size:13px}}
</style></head><body><div class="wrap">
<header>
  <h1>Auckland <span>FPV</span> spots</h1>
  <p>{total} locations across five regions, each checked against live AirShare airspace data - control zones, 4 km aerodrome buffers, restricted areas and VFR transit lanes. Every spot carries a seclusion, quiet and flying rating (all higher = better), plus the quietest time and days to go.</p>
</header>
<div class="grid">
{''.join(rows)}
</div>
<footer>Scores are 0-10 and weighted toward flying quality and seclusion, with permit/authorisation requirements applied as a penalty. Numbers restart at 1 in each region. Airspace data: AirShare / Airways NZ, October 2026. Always re-check NOTAMs and the AirShare map on the day.</footer>
</div></body></html>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)
print("wrote index")
print("OUT:", OUT)
