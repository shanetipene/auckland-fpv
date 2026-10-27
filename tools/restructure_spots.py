#!/usr/bin/env python3
"""Restructure the spot list so every entry is a real, walkable launch point.

- deletes spots that are village junctions, road verges or private farmland
- re-anchors four spots onto verified reserve/beach coordinates
- adds three verified regional-park / beach spots
- writes a specific `launch` line onto every surviving spot
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CBD = (-36.8489, 174.7652)
FILES = ("spots.json", "spots_north.json", "spots_west.json", "spots_south.json")

DELETE = {
    "Whitford", "Devonport", "Karaka", "Waiau Pa", "Clevedon", "Waiuku",
    "Bombay", "Kingseat", "Ararimu", "Pollok", "Ramarama", "Paerata",
    "Mauku", "Kohekohe", "Patumahoe", "Puni",
}

REANCHOR = {
    "Orewa": (-36.590260, 174.698306),
    "Puhoi": (-36.508550, 174.660930),
    "Mahurangi West": (-36.503800, 174.718800),
    "Pukekohe": (-37.206170, 174.902430),
}

LAUNCH = {
    # central
    "Coyle Park": "Car park inside Coyle Park off Point Chevalier Rd, then a 2 min walk to the grass above the cliff.",
    "Monte Cecilia": "Park at the Pah Homestead car park on Hillsborough Rd; fly from the open parkland south of the house.",
    "Waiatarua": "Car park off Grand Dr; set up on the mown grass beside the wetland.",
    "Stonefields": "Street parking on Stonefields Ave or College Rd; fly from the path edge at the old quarry floor.",
    "Panmure Basin": "Car park at the Basin View / Ireland Rd end; fly from the reserve grass on the northern shore of the lagoon.",
    "Pt England": "Grass car park off Point England Rd; fly from the open field facing the harbour.",
    "Orakei Basin": "Enter from Orakei Rd or Upland Rd; fly from the grass beside the boardwalk.",
    "Glendowie": "Park on Glendowie Rd or Riddell Rd; fly from the clifftop grass.",
    "Fearon Park": "Car park off Fearon Ave by the tennis courts; fly from the top field.",
    "Meola Reef": "Reserve entrance car park on Meola Rd; fly from the grass above the reef.",
    "Eric Armishaw": "Car park off Great North Rd, Waterview; fly from the reserve grass by the inlet.",
    "Western Springs": "Stadium-end car park off Motions Rd; fly from the grass beside the lake.",
    "Keith Hay Park": "Car park off Hillsborough Rd; fly from the edge of the sports fields.",
    # east
    "Musick Point": "Car park at the end of Musick Point Rd; 2 min walk to the grass above the harbour.",
    "Waitawa": "Road-end car parks on Waitawa Bay Rd; fly from the MTB trailhead clearing.",
    "Kawakawa Bay": "Boat ramp car park at the end of Kawakawa Bay Rd; fly from the beach reserve beside it.",
    "Maraetai": "Te Puru Park car park off Maraetai Dr; fly from the field above the beach.",
    "Mangemangeroa": "Somerville Rd entrance; walk the valley track about 10 min to the estuary boardwalk.",
    "Eastern Beach": "Car park on The Esplanade; fly from the sand at the northern end.",
    "Sunkist Bay": "End of Sunkist Bay Rd, Beachlands; fly from the beach reserve.",
    "Omana": "Car park on Omana Dr; fly from the beach reserve.",
    "Lloyd Elsmore": "Car park off Sir Lloyd Dr; fly from the edge of the sports fields.",
    "Cockle Bay": "Car park off Shelly Beach Parade; fly from the beach reserve.",
    "Shelly Park": "End of Sandspit Rd; fly from the estuary beach.",
    "Mellons Bay": "Car park off Bleakhouse Rd; fly from the beach.",
    "Howick Beach": "Car park at the end of Granger Rd; fly from the sand.",
    "Macleans Park": "Car park off Macleans Rd; fly from the top field.",
    "Umupuia": "Gravel car park at the end of Maraetai Coast Rd; fly from the beach.",
    "Duder": "Gate at the end of North Rd; walk 15 min to the beach, or fly from the open paddock by the car park.",
    # west
    "French Bay": "Car park at the end of Otitori Bay Rd; fly from the beach.",
    "Titirangi Beach": "End of Titirangi Beach Rd; fly from the sand beside the wharf.",
    "Laingholm": "Victory Rd is a no-exit road; fly from the beach at the end.",
    "Blockhouse Bay": "Reserve car park off Blockhouse Bay Rd; fly from the grass above the beach.",
    "Green Bay": "Beach reserve car park next to the shops on Green Bay Rd.",
    "Parrs Park": "Car park off Parrs Park Dr; fly from the edge of the sports fields.",
    "Olympic Park": "Car park off Portage Rd, New Lynn; fly from the stadium forecourt.",
    "Awhitu": "Awhitu Regional Park, end of Awhitu Rd; fly from the campground and beach car park.",
    "Woodhill": "Restall Rd forest access (commercial forest park, fee applies); fly from the trailhead clearing.",
    "Waikowhai": "Park on Waikowhai Rd; walk the track down to the wharf and fly from the foreshore.",
    "Lynfield Cove": "Park on The Avenue, Lynfield; walk the cove track to the beach.",
    "Ceramco Park": "Car park off Great North Rd, Glendene; fly from the sports fields.",
    "Wattle Bay": "Reserve at the end of Wattle Bay Rd; fly from the grass above the bay.",
    # north
    "Pakiri": "Beach access car park on Pakiri Rd; walk over the dunes to the sand.",
    "Leigh": "Wharf Rd, Leigh Harbour; fly from the wharf apron and grass beside it.",
    "Mahurangi West": "Opahi Bay car park off Mahurangi West Rd; fly from the reserve above the bay.",
    "Algies Bay": "Beach reserve car park at the end of Algies Bay Rd.",
    "Sandspit": "Marina car park at the end of Sandspit Rd.",
    "Omaha": "Car park at the north end of Omaha Dr; fly from the beach access.",
    "Wenderholm": "Main car park at the end of the Wenderholm access road; walk to the beach or the hill.",
    "Puhoi": "Puhoi Domain car park off Puhoi Rd; fly from the domain grass.",
    "Waiwera": "Beach reserve at the end of Waiwera Rd, beside the pools.",
    "Manly": "Big Manly Beach car park at the end of Manly Esplanade.",
    "Stanmore Bay": "Beach reserve car park off Brightside Rd; fly from the grass above the sand.",
    "Tindalls": "Car park at the end of Tindalls Beach Rd.",
    "Hatfields": "Beach reserve car park off Hatfields Beach Rd.",
    "Orewa": "Orewa Beach Reserve car park off Orewa Beach Rd; fly from the grass above the sand.",
    "Browns Bay": "Car park at the end of Beach Rd; fly from the sand.",
    "Long Bay": "Long Bay Regional Park main car park at the end of Beach Rd.",
    "Narrow Neck": "Car park off Old Lake Rd; fly from the beach reserve.",
    "Little Manly": "Park on Ngaio St, Manly; 2 min walk to the beach.",
    "Matakatia": "Matakatia Pde beach access; fly from the reserve.",
    "Arkles Bay": "Boat ramp car park off Arkles Strand.",
    "Army Bay": "Car park at the end of Whangaparaoa Rd.",
    "Shakespear": "Main gate car park inside Shakespear Regional Park (gate opens 6am).",
    "Scandrett": "Car park at the end of Scandrett Rd.",
    "Ti Point": "Reserve at the end of Ti Point Rd.",
    "Te Arai": "Gravel car park at Te Arai Point, end of Te Arai Point Rd.",
    # south
    "Karioitahi": "Surf club car park at the end of Karioitahi Rd.",
    "Orere Point": "Beach reserve at the end of Orere Point Rd.",
    "Clarks Beach": "Beach reserve and boat ramp car park off Clarks Beach Rd.",
    "Glenbrook": "End of Glenbrook Beach Rd; fly from the beach.",
    "Matakawau": "Awhitu Rd to Matakawau Point; fly from the reserve at the point.",
    "Pukekohe": "Bledisloe Park car park, Pukekohe; fly from the sports fields.",
}

ACCESS = {
    "Orewa": "Orewa Beach Reserve, Orewa Beach Rd, ~35 min from CBD. Beachfront car parks along the reserve.",
    "Puhoi": "Puhoi Domain, off Puhoi Rd, ~40 min from CBD. Park in the domain car park beside the sports fields.",
    "Mahurangi West": "Opahi Bay, Mahurangi West Rd off SH1, ~45 min from CBD. Car park at the bay.",
    "Pukekohe": "Bledisloe Park, Pukekohe, ~45 min from CBD. Car park off the park entrance.",
}

NEW = [
    {
        "region": "north", "name": "Martins Bay Beach", "short": "Martins Bay",
        "lat": -36.449645, "lon": 174.764318, "secl": 3.4, "traffic": 2.6, "fly": 3.2,
        "kind": "sheltered beach", "status": "clear",
        "land": "Council beach reserve",
        "access": "Martins Bay Rd, Mahurangi East, ~65 min from CBD. Beach car park at the end of the road.",
        "launch": "Beach car park at the end of Martins Bay Rd; fly from the sand at the southern end.",
        "best": "A sheltered east-facing beach with a holiday park at one end and open sand at the other. Good for low, fast passes along the waterline when the camp is quiet.",
        "hazards": "Holiday park and baches at the northern end, swimmers in summer, the beach narrows at high tide.",
        "note": "Airspace clean - nearest aerodrome Warkworth, 11.1 km. Stay south of the camp and keep clear of the rocky points.",
        "drive_min": 75, "drive_km": 64,
    },
    {
        "region": "south", "name": "Tapapakanga Regional Park", "short": "Tapapakanga",
        "lat": -36.980202, "lon": 175.258902, "secl": 4.2, "traffic": 1.2, "fly": 3.8,
        "kind": "coastal farm park", "status": "permit",
        "land": "Auckland Council regional park",
        "access": "Tapapakanga Regional Park, off Orere-Matingarahi Rd, ~1 h 15 from CBD. Gravel car park at the park entrance.",
        "launch": "Park entrance car park off Orere-Matingarahi Rd; fly from the open paddocks above the beach.",
        "best": "Farm parkland rolling down to a long Pohutukawa coast. Big open grass, almost nobody midweek, and a clean horizon out over the Firth.",
        "hazards": "Farm stock and electric fences, steep coastal drops, no shelter from the nor'west, poor phone coverage.",
        "note": "Regional park - drone use needs an Auckland Council permit. Airspace clean, nearest aerodrome 24 km.",
        "drive_min": 78, "drive_km": 82,
    },
    {
        "region": "south", "name": "Waharau Regional Park", "short": "Waharau",
        "lat": -37.039352, "lon": 175.294634, "secl": 4.4, "traffic": 0.6, "fly": 3.6,
        "kind": "bush + coast park", "status": "permit",
        "land": "Auckland Council regional park",
        "access": "Waharau Regional Park, off East Coast Rd, ~1 h 25 from CBD. Car park at the park entrance.",
        "launch": "Entrance car park off East Coast Rd; fly from the open grass between the road and the bush edge.",
        "best": "The quietest coast in Auckland - bush behind, the Firth in front, and often not another person there. Long sight lines north and south.",
        "hazards": "Dense bush limits recovery, steep drop to the water, isolated with no phone coverage, exposed to sea breeze.",
        "note": "Regional park - permit required for drone use. Airspace clean, nearest aerodrome 24.6 km.",
        "drive_min": 88, "drive_km": 90,
    },
]


def km(a, b, c, d):
    r = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def score(secl, traffic, fly, status):
    base = 1.0 + 0.8 * fly + 0.6 * secl + 0.4 * (5 - traffic)
    if status == "permit":
        base -= 1.0
    elif status == "restricted":
        base -= 1.5
    return round(max(0.0, min(10.0, base)), 1)


def main():
    removed = []
    for fn in FILES:
        path = os.path.join(ROOT, fn)
        data = json.load(open(path, encoding="utf-8"))
        keep = []
        for s in data:
            if s["short"] in DELETE:
                removed.append(s["short"])
                continue
            if s["short"] in REANCHOR:
                lat, lon = REANCHOR[s["short"]]
                s["lat"], s["lon"] = lat, lon
                s["maps_url"] = f"https://maps.google.com/?q={lat:.6f},{lon:.6f}"
                s["sv_url"] = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat:.6f},{lon:.6f}"
            if s["short"] in ACCESS:
                s["access"] = ACCESS[s["short"]]
            keep.append(s)
        json.dump(keep, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    by_file = {"north": "spots_north.json", "south": "spots_south.json"}
    for spec in NEW:
        spec = dict(spec)
        spec["dist_cbd_km"] = round(km(CBD[0], CBD[1], spec["lat"], spec["lon"]), 1)
        spec["fpv_score"] = score(spec["secl"], spec["traffic"], spec["fly"], spec["status"])
        spec["merit"] = spec["fpv_score"]
        spec["tier"] = 2
        spec["maps_url"] = f"https://maps.google.com/?q={spec['lat']:.6f},{spec['lon']:.6f}"
        spec["sv_url"] = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={spec['lat']:.6f},{spec['lon']:.6f}"
        path = os.path.join(ROOT, by_file[spec["region"]])
        data = json.load(open(path, encoding="utf-8"))
        data.append(spec)
        json.dump(data, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # launch lines
    missing, total = [], 0
    for fn in FILES:
        path = os.path.join(ROOT, fn)
        data = json.load(open(path, encoding="utf-8"))
        for s in data:
            total += 1
            if s["short"] in LAUNCH:
                s["launch"] = LAUNCH[s["short"]]
            else:
                missing.append(s["short"])
        json.dump(data, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"deleted {len(removed)}: {', '.join(sorted(removed))}")
    print(f"added {len(NEW)}; total now {total}")
    print("missing launch text:", missing or "none")


if __name__ == "__main__":
    main()
