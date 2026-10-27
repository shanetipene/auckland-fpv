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
"Glenbrook": ("Weekday 09:00-15:00","Mon-Fri","Weekends 10:00-15:00"),
"Matakawau": ("Weekday 08:00-12:00","Mon-Thu","Weekends 10:00-15:00"),
"Clarks Beach": ("Weekday 07:00-10:00","Mon-Thu","Summer weekends 09:00-16:00 (boat ramp)"),
"Pukekohe": ("Weekday 09:00-15:00","Tue-Thu","Sat morning (market, sport)"),
"Martins Bay": ("Weekday 06:30-09:30","Mon-Thu","Summer weekends and school holidays (holiday park)"),
"Tapapakanga": ("Any weekday","Tue-Thu","Summer weekends 10:00-16:00 (campers)"),
"Waharau": ("Any day, early","Mon-Thu","Almost never busy - the quietest coast in Auckland"),
}

META = {
 "central": dict(title="Central Auckland", short="Central", blurb="Isthmus parks and harbour reserves, 10-21 minutes from the CBD. Airspace is clean except Orakei Basin."),
 "east":    dict(title="East Auckland", short="East", blurb="Bucklands Beach out to the Pohutukawa Coast. Clean airspace the whole way; two sites need a regional-park permit."),
 "west":    dict(title="West Auckland", short="West", blurb="The Manukau Harbour side. The Waitakere Ranges and the Whenuapai control zone take out most of the west, so these are what's left."),
 "north":   dict(title="North Auckland", short="North", blurb="Hibiscus Coast, Mahurangi and Matakana. The North Shore is locked up by the control zone - the good flying starts north of Silverdale."),
 "south":   dict(title="South Auckland", short="South", blurb="Franklin. The airport control zone plus four aerodrome buffers cover the entire urban south, so everything legal is rural or coastal."),
}
ORDER = ["central","east","north","west","south"]

REGION_COLOUR = {
 "central": "#7cc4ff", "east": "#2fd28a", "north": "#f2b544",
 "west": "#b98bff", "south": "#ff7a90",
}

def _hull(points):
    """Convex hull (monotone chain). Points are (lon, lat)."""
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _buffered_hull(spots, factor=1.05):
    """Hull around a region's spots, nudged out from the centroid so the
    clickable area is a touch larger than the outermost pins."""
    h = _hull([(s["lon"], s["lat"]) for s in spots])
    if not h:
        return [], [0, 0]
    cx = sum(p[0] for p in h) / len(h)
    cy = sum(p[1] for p in h) / len(h)
    out = [[round(cx + (x - cx) * factor, 5), round(cy + (y - cy) * factor, 5)] for x, y in h]
    return out, [round(cx, 5), round(cy, 5)]


# screen-space nudge so the Central/East/West labels don't sit on top of each other
_LABEL_OFF = {
 "central": [0, -6], "east": [58, 16], "west": [-60, 16],
 "north": [0, 0], "south": [0, 0],
}

_map_regions = []
_map_spots = []
for _k in ORDER:
    _hull_pts, _centre = _buffered_hull(regions[_k])
    # label sits at the average of the region's spots, not the hull centroid:
    # hull centroids bunch up on the isthmus and overlap each other
    _sp = regions[_k]
    _centre = [round(sum(s["lon"] for s in _sp) / len(_sp), 5),
               round(sum(s["lat"] for s in _sp) / len(_sp), 5)]
    _map_regions.append({
        "key": _k, "name": META[_k]["short"], "n": len(regions[_k]),
        "colour": REGION_COLOUR[_k], "hull": _hull_pts, "c": _centre,
        "off": _LABEL_OFF[_k],
    })
    for _s in regions[_k]:
        _map_spots.append({
            "n": _s["short"], "la": round(_s["lat"], 5), "lo": round(_s["lon"], 5),
            "r": _k, "rn": META[_k]["short"], "sc": _s["fpv_score"],
            "id": re.sub(r"[^a-z0-9]+", "-", _s["short"].lower()).strip("-"),
        })

MAPDATA = json.dumps({"regions": _map_regions, "spots": _map_spots}, ensure_ascii=False)

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
        <div class="launch"><span>Launch from</span>{html.escape(s.get('launch') or s.get('access',''))}</div>
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
.launch{{background:rgba(124,196,255,.07);border:1px solid rgba(124,196,255,.22);border-left:3px solid #7cc4ff;border-radius:10px;padding:10px 12px;margin:12px 0 4px;font-size:13.5px;line-height:1.45;color:var(--fg)}}
.launch span{{display:block;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:#7cc4ff;font-weight:700;margin-bottom:3px}}
.card{{scroll-margin-top:86px}}
.card.flash{{animation:spotflash 1.9s ease}}
@keyframes spotflash{{0%{{box-shadow:0 0 0 0 rgba(124,196,255,0)}}12%{{box-shadow:0 0 0 3px rgba(124,196,255,.95)}}70%{{box-shadow:0 0 0 3px rgba(124,196,255,.75)}}100%{{box-shadow:0 0 0 3px rgba(124,196,255,0)}}}}
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
    <div><b>Where to fly from.</b> Every marker sits on the actual launch point — the car park, beach access, reserve entrance or road end you drive to — and every card states exactly where to set up once you're there. Pins are accurate to the access point, not to the metre; if a gate is locked or a beach access is closed, use the nearest public entrance and stay inside the reserve or beach boundary. Names are the official or most widely used name; local signage and iwi names may differ.</div>
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
function jumpToSpot(id) {{
  const card = document.querySelector('.card[data-spot="' + id + '"]');
  if (!card) return;
  const y = Math.max(0, window.scrollY + card.getBoundingClientRect().top - 74);
  window.scrollTo({{top: y, behavior: 'smooth'}});
  setTimeout(() => {{ if (Math.abs(window.scrollY - y) > 8) window.scrollTo(0, y); }}, 420);
  card.classList.remove('flash');
  void card.offsetWidth;
  card.classList.add('flash');
  setTimeout(() => card.classList.remove('flash'), 1900);
}}
for (const s of SPOTS) {{
  const icon = L.divIcon({{className:'', iconSize:[27,27], iconAnchor:[13.5,13.5],
    html:`<div style="width:27px;height:27px;border-radius:50%;background:${{COL[s.status]}};color:#fff;font:800 12.5px/27px -apple-system,Segoe UI,Roboto,sans-serif;text-align:center;box-shadow:0 0 0 3px rgba(255,255,255,.92),0 4px 12px rgba(0,0,0,.55)">${{s.num}}</div>`}});
  const m = L.marker([s.lat, s.lon], {{icon}}).addTo(map);
  m.bindPopup(`<b>${{s.num}}. ${{s.name}}</b><br>${{s.fpv_score}}/10 &middot; ${{s.drive_min}} min from CBD<br>
    <span style="color:#555">Quietest:</span> ${{s.quiet_time}}<br>
    <span style="color:#555">Days:</span> ${{s.quiet_days}}<br>
    <a href="${{s.maps_url}}" target="_blank" rel="noopener">Google Maps</a>`);
  m.on('click', () => jumpToSpot(s.id));
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
if (location.hash.indexOf('#spot-') === 0) {{
  const wanted = location.hash.slice(6);
  setTimeout(() => jumpToSpot(wanted), 400);
}}
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

# index map: all 59 spots plus one clickable shape per region
MAPJS = """
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const A = __DATA__;
const map = L.map('allmap', {scrollWheelZoom: true, zoomSnap: 0.25});
const topo = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {maxZoom:19, attribution:'Basemap &copy; Esri, HERE, Garmin, OpenStreetMap'}).addTo(map);
const imagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {maxZoom:19, attribution:'Imagery &copy; Esri, Maxar'});
const streets = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19, attribution:'&copy; OpenStreetMap'});
L.control.layers({'Topographic': topo, 'Satellite': imagery, 'Streets': streets}).addTo(map);

const bounds = [];
A.regions.forEach(r => {
  const poly = L.polygon(r.hull.map(p => [p[1], p[0]]), {
    color: r.colour, weight: 2, dashArray: '5 5',
    fillColor: r.colour, fillOpacity: 0.16
  }).addTo(map);
  poly.bindTooltip(r.name + ' — ' + r.n + ' spots · click to open', {sticky: true});
  poly.on('mouseover', () => poly.setStyle({fillOpacity: 0.26, weight: 3}));
  poly.on('mouseout', () => poly.setStyle({fillOpacity: 0.16, weight: 2}));
  poly.on('click', () => { window.location.href = r.key + '.html'; });

  L.marker([r.c[1], r.c[0]], {
    icon: L.divIcon({className: 'rlabel', html: '<span style="transform:translate(calc(-50% + ' + r.off[0] + 'px), calc(-50% + ' + r.off[1] + 'px))">' + r.name + ' &rarr;</span>', iconSize: [0, 0]}),
    keyboard: false
  }).addTo(map)
    .on('click', () => { window.location.href = r.key + '.html'; })
    .bindTooltip('Open ' + r.name + ' Auckland');
});

A.spots.forEach(s => {
  bounds.push([s.la, s.lo]);
  const reg = A.regions.find(r => r.key === s.r) || {colour: '#7cc4ff'};
  L.circleMarker([s.la, s.lo], {radius: 5, weight: 1, color: '#0b0e13', fillColor: reg.colour, fillOpacity: 0.95})
    .addTo(map)
    .bindPopup('<b>' + s.n + '</b><br>' + s.sc + '/10 &middot; <a href="' + s.r + '.html#spot-' + s.id + '">' + s.rn + ' Auckland &rarr;</a>');
});

map.fitBounds(bounds, {padding: [34, 34]});
</script>
""".replace("__DATA__", MAPDATA)

RULES = """
<section class="rules">
  <h2>Rules and regulations</h2>
  <p>Every spot here assumes you are flying under Part 101. These are the three rule sets that decide where you can legally launch, and each one can override the others.</p>
  <a class="rlink" href="https://www.aviation.govt.nz/drones" target="_blank" rel="noopener">
    <span class="who">CAA</span>
    <span><b>Drone rules and pilot requirements</b><small>Part 101 and Part 102, pilot registration and competency, airspace classes, 120 m ceiling, and the FPV and night-flying conditions. This is the rule set everything else sits on top of.</small></span>
  </a>
  <a class="rlink" href="https://www.aucklandcouncil.govt.nz/en/parks-recreation/get-outdoors/drones-unmanned-aerial-vehicles.html" target="_blank" rel="noopener">
    <span class="who">Auckland Council</span>
    <span><b>Council rules and guidelines</b><small>Where you can and can't fly on council land, the regional park permit process, the 2.5 kg limit without council permission, and the code of conduct for flying over parks and reserves.</small></span>
  </a>
  <a class="rlink" href="https://www.doc.govt.nz/get-involved/apply-for-permits/all-permissions/drone-use-on-conservation-land/" target="_blank" rel="noopener">
    <span class="who">DOC</span>
    <span><b>Department of Conservation rules</b><small>Public conservation land needs a concession (permit) to take off, land or hover. Also the wildlife separation rules: 100 m to take off near wildlife, 50 m in flight, and 150 m from marine mammals.</small></span>
  </a>
</section>
"""

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
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
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
.sechead{{font-size:22px;margin:26px 0 4px}}
.leghint{{color:var(--dim);font-size:14px;margin:0 0 12px}}
#allmap{{height:520px;border-radius:16px;border:1px solid var(--line);margin:0 0 34px;z-index:1;background:#0b0e13}}
.rlabel{{background:none;border:0}}
.rlabel span{{display:inline-block;position:absolute;left:0;top:0;width:max-content;transform:translate(-50%,-50%);background:rgba(11,14,19,.9);border:1px solid var(--line);color:#fff;font:700 12px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding:7px 11px;border-radius:999px;white-space:nowrap;box-shadow:0 2px 10px rgba(0,0,0,.45)}}
.rules{{border-top:1px solid var(--line);padding:38px 0 20px;margin-top:10px}}
.rules h2{{font-size:22px;margin:0 0 8px}}
.rules p{{color:var(--dim);font-size:14px;margin:0 0 20px;max-width:760px}}
.rlink{{display:flex;gap:16px;text-decoration:none;color:inherit;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:12px;transition:.15s}}
.rlink:hover{{border-color:#3a4757;transform:translateY(-1px)}}
.rlink b{{display:block;font-size:16px;margin-bottom:3px}}
.rlink small{{color:var(--dim);font-size:13px;line-height:1.55;display:block}}
.rlink .who{{color:#7cc4ff;font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;min-width:132px;padding-top:3px}}
@media (max-width:640px){{#allmap{{height:400px}} .rlink{{flex-direction:column;gap:6px}}}}
footer{{border-top:1px solid var(--line);padding:24px 0 60px;color:#6b7889;font-size:13px}}
</style></head><body><div class="wrap">
<header>
  <h1>Auckland <span>FPV</span> spots</h1>
  <p>{total} locations across five regions, each checked against live AirShare airspace data - control zones, 4 km aerodrome buffers, restricted areas and VFR transit lanes. Every spot carries a seclusion, quiet and flying rating (all higher = better), plus the quietest time and days to go.</p>
</header>
<h2 class="sechead">Auckland at a glance</h2>
<p class="leghint">All {total} spots, coloured by region. Click one of the five regions to open it.</p>
<div id="allmap"></div>
<div class="grid">
{''.join(rows)}
</div>
{RULES}
<footer>Scores are 0-10 and weighted toward flying quality and seclusion, with permit/authorisation requirements applied as a penalty. Numbers restart at 1 in each region. Airspace data: AirShare / Airways NZ, October 2026. Always re-check NOTAMs and the AirShare map on the day.</footer>
</div>
{MAPJS}
</body></html>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)
print("wrote index")
print("OUT:", OUT)
