# Auckland FPV Spots

**Live site:** https://auckland-fpv.pages.dev

A guide to 59 legally flyable FPV drone locations across Auckland, split into five regions: Central, East, North, West and South.

Every location was checked against live AirShare airspace data — control zones (CTR), 4 km aerodrome and helipad buffers, restricted areas, danger areas and VFR transit lanes — rather than copied from a "best drone spots" listicle. Sites inside a control zone are included only where a legitimate authorisation path exists, and are marked accordingly.

## What each spot carries

- **Seclusion** — how far you are from people, roads and buildings (5 = wilderness, 0 = crowded suburb)
- **Quiet** — foot traffic at the site (5 = empty, 0 = packed)
- **Flying** — how good the site actually is to fly: terrain, lines, sightlines, scenery
- **Overall score** — weighted toward flying quality and seclusion, with permit and authorisation requirements applied as a penalty
- **Quietest time / quietest days / avoid** — derived from what actually drives each site: boat ramps, golf tee times, Saturday sport, dog-walker rush hours, paraglider thermals, logging operations

## Status colours

| Colour | Meaning |
| --- | --- |
| Green | No permit required — standard Part 101 rules apply |
| Blue | Regional park — permit required from Auckland Council |
| Amber | Restricted — Part 101 certificate, ATC authorisation, aerodrome operator consent, or private land |

## Running it

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
```

The cards and all content work fully offline. The interactive map needs an internet connection for map tiles and the Leaflet CDN.

The plain HTML pages run on any static host — GitHub Pages, Netlify, S3 — with no build step. The live site runs on Cloudflare Pages with Pages Functions and a D1 database for community ratings and submissions, deployed with `./deploy-cloudflare.sh`.

The pages are generated: edit the spot JSON, then run `python3 gen_html.py`. Don't hand-edit the HTML.

## Community contributions

Anyone can suggest a spot from the nav button on any page. Suggestions land in a D1 queue and are reviewed once a day by an automated job that checks airspace, deduplicates and either adds the spot or rejects it with a reason.

Readers can also rate any spot (seclusion, quiet, flying). Displayed ratings are the community average blended with the editor rating, with the editor rating counting as one vote.

## Structure

```
index.html      landing page, links to the five regions
central.html    9 spots
east.html       10 spots
north.html      17 spots
west.html       11 spots
south.html      12 spots

gen_html.py          builds all six pages from the spot data
spots*.json          the source data — one file per region
assets/              shared CSS and JS for ratings and submissions
functions/api/       Pages Functions: ratings, rate, suggest
tools/airspace.py    point-in-polygon check against the AirShare layers
tools/apply_spot.py  geocode → airspace check → score → rebuild → deploy
tools/pin_audit      check_pins.py, pin_montage.py, nudge_onshore.py
```

Each region page is standalone: data is embedded as JSON, styling is inline, and the map is Leaflet with topographic, satellite and street basemaps.

## Before you fly

- Log the flight on AirShare — required on council land, and it is how you request ATC or aerodrome approval.
- Stay 30 m from people and dogs, 20 m from buildings, 50 m from playgrounds in use and infrastructure.
- Nothing over 2.5 kg on council land without council permission.
- FPV requires a spotter maintaining unaided visual line of sight — CAA position, not optional.
- September to March: stay 30 m off shorebirds on beaches, and do not take off within 100 m of them.
- Inside a control zone or 4 km ring, the recreational route is a Part 101 certificate plus approval, or a shielded operation.

## Accuracy

Airspace data was pulled from the AirShare advisories API in October 2026. Airspace, NOTAMs, council rules and park closures change — re-check the AirShare map on the day. This is a planning aid, not an authorisation.

Basemap imagery © Esri, Maxar, Earthstar Geographics. Airspace data © AirShare / Airways NZ.
