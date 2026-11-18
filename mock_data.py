"""FLIGHTPATH - airports, simulated environment and frontend stand-ins.

Airport LOCATIONS are real (approximate coordinates, Pakistan + major world hubs).
Everything else - routes, restricted zones, obstacles, weather - is SIMULATED.
`plan_route()` is a *frontend stand-in*: it draws smooth curves and nudges them
away from obstacles so the interface has something to show. It is NOT an A*
implementation. Integration point for the real engine: replace its body and
keep the same return shape.

The simulated environment (weather, restricted airspace, obstacles) is defined ONCE in
the structured tables below (`_COUNTRY_ENV`, `_OCEAN_WEATHER`). The map markers, the hover
popups and the "Nearby airspace conditions" panel all read the same items via `all_env()`.
"""
from __future__ import annotations

import math

# --------------------------------------------------------------------------
# Map canvas: equirectangular world map, lon -180..180 -> x 0..1000, lat 80..-58
# --------------------------------------------------------------------------
MAP_W = 1000.0
LAT_TOP, LAT_BOT = 80.0, -58.0
SCALE = MAP_W / 360.0                      # map units per degree
MAP_H = (LAT_TOP - LAT_BOT) * SCALE        # ~383
KM_PER_UNIT_EQ = 111.32 / SCALE            # km per map unit along the equator


def project(lat: float, lon: float) -> tuple[float, float]:
    return ((lon + 180.0) * SCALE, (LAT_TOP - lat) * SCALE)


def unproject(x: float, y: float) -> tuple[float, float]:
    return (LAT_TOP - y / SCALE, x / SCALE - 180.0)  # (lat, lon)


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(a))


# --------------------------------------------------------------------------
# Airports
# --------------------------------------------------------------------------
_RAW = [
    # code, name, city, lat, lon, group
    ("KHI", "Jinnah International", "Karachi", 24.9065, 67.1608, "PK"),
    ("LHE", "Allama Iqbal International", "Lahore", 31.5216, 74.4036, "PK"),
    ("ISB", "Islamabad International", "Islamabad", 33.5600, 72.8500, "PK"),
    ("PEW", "Bacha Khan International", "Peshawar", 33.9939, 71.5146, "PK"),
    ("UET", "Quetta International", "Quetta", 30.2514, 66.9378, "PK"),
    ("MUX", "Multan International", "Multan", 30.2032, 71.4191, "PK"),
    ("SKT", "Sialkot International", "Sialkot", 32.5356, 74.3639, "PK"),
    ("FSD", "Faisalabad International", "Faisalabad", 31.3650, 72.9948, "PK"),
    ("GWD", "Gwadar International", "Gwadar", 25.2333, 62.3294, "PK"),
    ("SKD", "Skardu International", "Skardu", 35.3355, 75.5360, "PK"),
    ("DXB", "Dubai International", "Dubai", 25.2532, 55.3657, "WORLD"),
    ("DOH", "Hamad International", "Doha", 25.2731, 51.6081, "WORLD"),
    ("JED", "King Abdulaziz International", "Jeddah", 21.6796, 39.1565, "WORLD"),
    ("IST", "Istanbul Airport", "Istanbul", 41.2753, 28.7519, "WORLD"),
    ("LHR", "Heathrow", "London", 51.4700, -0.4543, "WORLD"),
    ("FRA", "Frankfurt Airport", "Frankfurt", 50.0379, 8.5622, "WORLD"),
    ("JFK", "John F. Kennedy International", "New York", 40.6413, -73.7781, "WORLD"),
    ("LAX", "Los Angeles International", "Los Angeles", 33.9416, -118.4085, "WORLD"),
    ("PEK", "Beijing Capital International", "Beijing", 40.0801, 116.5846, "WORLD"),
    ("SIN", "Changi Airport", "Singapore", 1.3644, 103.9915, "WORLD"),
    ("SYD", "Kingsford Smith", "Sydney", -33.9399, 151.1753, "WORLD"),
    ("JNB", "O. R. Tambo International", "Johannesburg", -26.1337, 28.2420, "WORLD"),
]

AIRPORTS: dict[str, dict] = {}
for code, name, city, lat, lon, grp in _RAW:
    x, y = project(lat, lon)
    AIRPORTS[code] = {"name": name, "city": city, "lat": lat, "lon": lon, "x": x, "y": y, "group": grp}


def airport_label(code: str) -> str:
    a = AIRPORTS[code]
    return f"{code} — {a['name']}, {a['city']}"


AIRPORT_CODES = list(AIRPORTS)

# --------------------------------------------------------------------------
# Simulated environment (NOT real restrictions or weather)
# --------------------------------------------------------------------------
SEVERITY_R = {"Low": 3.5, "Medium": 5.0, "High": 7.0}   # map units (~140 / 200 / 280 km)
SEVERITIES = list(SEVERITY_R)
OBSTACLE_R = 2.5

SECTORS = {
    "Sindh": project(26.0, 68.5),
    "Southern Punjab": project(29.5, 71.0),
    "Northern Punjab": project(32.5, 73.0),
    "Khyber Pakhtunkhwa": project(34.2, 71.8),
    "Balochistan": project(28.5, 65.0),
    "Gilgit-Baltistan": project(35.5, 75.0),
    "Arabian Sea": project(22.0, 64.0),
    "Persian Gulf": project(26.5, 52.0),
    "Central Asia": project(40.0, 67.0),
}

# --- Weather conditions: symbol key + hover/card description --------------------------
WX_CONDITIONS = {
    "Thunderstorm": ("storm", "Simulated storm activity affecting route cost."),
    "Heavy Rain": ("rain", "Simulated heavy rainfall reducing visibility along the corridor."),
    "Strong Winds": ("wind", "Simulated strong-wind band raising fuel burn and route cost."),
    "Fog": ("fog", "Simulated low-visibility fog layer affecting route cost."),
}
WX_RADIUS = {"Low": 2.6, "Moderate": 3.1, "High": 3.6}            # map units (~105-145 km)
ZONE_RADIUS = {"Low": 1.9, "Medium": 2.3, "High": 2.7}             # preset zones are small (~75-110 km)
ZONE_DESC = {
    "Low": "Simulated advisory flight region with light restrictions.",
    "Medium": "Simulated restricted flight region.",
    "High": "Simulated no-fly region; routes are planned around it.",
}
OBSTACLE_DESC = [
    "A simulated obstruction affecting the available route.",
    "Simulated high-terrain obstruction in the flight corridor.",
    "Simulated tall-structure cluster near the flight corridor.",
]

# --- Structured environment: EXACTLY one weather anomaly, one restricted zone and one
# obstacle per represented country.  (lat, lon, ...) -> positions are approximate and
# deliberately kept well away from the airports so no airport is ever enclosed.
# country: {"wx": (lat, lon, condition, severity, region),
#           "rz": (lat, lon, severity, region),
#           "ob": (lat, lon, region)}
_COUNTRY_ENV = {
    "Pakistan":     {"wx": (28.5, 69.5, "Fog", "Moderate", "Upper Sindh plains"),
                     "rz": (27.0, 65.0, "High", "Southern Balochistan"),
                     "ob": (27.5, 68.0, "Kirthar range")},
    "India":        {"wx": (18.5, 74.5, "Heavy Rain", "High", "Western Ghats"),
                     "rz": (27.5, 76.5, "Medium", "Northern plains"),
                     "ob": (13.5, 78.0, "Southern plateau")},
    "Afghanistan":  {"wx": (36.5, 70.5, "Strong Winds", "Moderate", "Hindu Kush"),
                     "rz": (32.8, 63.0, "Medium", "Southern Afghanistan"),
                     "ob": (34.2, 62.0, "Western Afghanistan")},
    "Iran":         {"wx": (30.5, 58.0, "Strong Winds", "Low", "Eastern Iran"),
                     "rz": (29.3, 53.3, "Medium", "Southern Iran"),
                     "ob": (35.8, 50.5, "Northern Iran")},
    "Saudi Arabia": {"wx": (28.5, 40.5, "Strong Winds", "Moderate", "Northern Saudi Arabia"),
                     "rz": (19.5, 48.5, "Low", "Empty Quarter"),
                     "ob": (27.5, 44.5, "Central Saudi Arabia")},
    "Turkey":       {"wx": (38.5, 42.5, "Thunderstorm", "Moderate", "Eastern Anatolia"),
                     "rz": (37.5, 38.5, "Medium", "Southeastern Turkey"),
                     "ob": (40.2, 38.5, "Black Sea highlands")},
    "Kazakhstan":   {"wx": (50.5, 77.0, "Strong Winds", "Low", "Eastern steppe"),
                     "rz": (45.5, 59.5, "Medium", "Aral region"),
                     "ob": (49.5, 55.5, "Western Kazakhstan")},
    "China":        {"wx": (28.5, 105.5, "Heavy Rain", "Moderate", "Southwestern China"),
                     "rz": (42.5, 91.0, "High", "Xinjiang"),
                     "ob": (31.5, 91.5, "Tibetan Plateau")},
    "Russia":       {"wx": (66.0, 70.0, "Strong Winds", "Moderate", "Western Siberia"),
                     "rz": (58.5, 125.0, "Low", "Eastern Siberia"),
                     "ob": (56.0, 40.0, "European Russia")},
    "Egypt":        {"wx": (30.3, 27.0, "Fog", "Low", "Western Desert coast"),
                     "rz": (23.5, 32.5, "Medium", "Southern Egypt"),
                     "ob": (24.5, 26.5, "Western Desert")},
    "South Africa": {"wx": (-30.5, 30.0, "Heavy Rain", "Moderate", "KwaZulu-Natal"),
                     "rz": (-33.2, 22.5, "Low", "Southern coast"),
                     "ob": (-25.0, 21.5, "Kalahari region")},
    "United States": {"wx": (33.0, -90.0, "Thunderstorm", "High", "Southern plains"),
                      "rz": (44.0, -110.0, "Medium", "Northern Rockies"),
                      "ob": (36.5, -108.5, "Colorado Plateau")},
    "Brazil":       {"wx": (-3.5, -60.0, "Heavy Rain", "Moderate", "Amazon basin"),
                     "rz": (-18.0, -47.5, "Low", "Central Brazil"),
                     "ob": (-8.0, -39.5, "Northeastern Brazil")},
    "Australia":    {"wx": (-17.5, 131.0, "Thunderstorm", "Moderate", "Northern Territory"),
                     "rz": (-28.5, 122.5, "Medium", "Western Australia"),
                     "ob": (-31.5, 141.5, "Southeastern Australia")},
}

# Oceanic weather anomalies (separate from the country-based ones; no ocean zones/obstacles)
_OCEAN_WEATHER = [
    (23.2, 63.8, "Thunderstorm", "Moderate", "Arabian Sea"),
    (14.0, 88.5, "Heavy Rain", "Moderate", "Bay of Bengal"),
    (-12.0, 80.0, "Thunderstorm", "Low", "Indian Ocean"),
    (47.5, -35.0, "Strong Winds", "High", "North Atlantic"),
    (38.0, -150.0, "Fog", "Low", "North Pacific"),
    (-20.0, -15.0, "Heavy Rain", "Low", "South Atlantic"),
    (-37.0, 160.0, "Strong Winds", "Moderate", "Tasman Sea"),
]


def _item(id_, kind, lat, lon, r, location, severity, description, *, condition=None, status=None,
          country=None, custom=False):
    x, y = project(lat, lon)
    return {"id": id_, "kind": kind, "lat": lat, "lon": lon, "x": x, "y": y, "r": r,
            "location": location, "severity": severity, "description": description,
            "condition": condition, "status": status, "country": country, "custom": custom,
            "icon": WX_CONDITIONS[condition][0] if condition else None}


def _build_env():
    """Built ONCE at import (module cache) - Streamlit reruns never duplicate anomalies."""
    wx, rz, ob = [], [], []
    for country, e in _COUNTRY_ENV.items():
        lat, lon, cond, sev, region = e["wx"]
        wx.append(_item(f"WX-{len(wx) + 1:02d}", "weather", lat, lon, WX_RADIUS[sev], f"{region}, {country}",
                        sev, WX_CONDITIONS[cond][1], condition=cond, country=country))
        lat, lon, sev, region = e["rz"]
        rz.append(_item(f"RZ-{len(rz) + 1:02d}", "zone", lat, lon, ZONE_RADIUS[sev], f"{region}, {country}",
                        sev, ZONE_DESC[sev], status="Active", country=country))
        lat, lon, region = e["ob"]
        ob.append(_item(f"OBS-{len(ob) + 1:02d}", "obstacle", lat, lon, OBSTACLE_R, f"{region}, {country}",
                        None, OBSTACLE_DESC[len(ob) % len(OBSTACLE_DESC)], status="Active", country=country))
    for lat, lon, cond, sev, region in _OCEAN_WEATHER:
        wx.append(_item(f"WX-{len(wx) + 1:02d}", "weather", lat, lon, WX_RADIUS[sev] + 0.6, region, sev,
                        WX_CONDITIONS[cond][1], condition=cond))
    # integrity check: one of each per represented country, ocean weather has no country
    for c in _COUNTRY_ENV:
        assert sum(1 for i in wx if i["country"] == c) == 1
        assert sum(1 for i in rz if i["country"] == c) == 1
        assert sum(1 for i in ob if i["country"] == c) == 1
    return wx, rz, ob


ENV_WEATHER, ENV_ZONES, ENV_OBSTACLES = _build_env()
WEATHER = [{"x": w["x"], "y": w["y"], "r": w["r"], "kind": w["icon"]} for w in ENV_WEATHER]  # for routing

# User-editable layer (Pilot Mode add/remove + map clicks). Starts empty: the preset
# environment above is the default scenery.
DEFAULT_ZONES: list[dict] = []
DEFAULT_OBSTACLES: list[dict] = []

# Country names drawn on the map (approximate interior anchor points, single typography)
COUNTRY_LABELS = [
    ("Canada", 59.0, -100.0), ("United States", 39.5, -98.0), ("Mexico", 23.5, -102.0),
    ("Colombia", 3.5, -73.0), ("Peru", -9.5, -74.5), ("Brazil", -10.5, -53.0), ("Argentina", -37.0, -65.0),
    ("United Kingdom", 54.2, -2.5), ("France", 46.7, 2.5), ("Spain", 40.0, -3.5), ("Germany", 51.0, 10.3),
    ("Ukraine", 49.0, 32.0), ("Sweden", 62.5, 15.5), ("Turkey", 39.0, 34.5), ("Russia", 62.0, 95.0),
    ("Kazakhstan", 48.0, 67.0), ("Mongolia", 46.8, 103.0), ("China", 35.5, 103.0), ("Japan", 36.5, 138.0),
    ("Egypt", 26.5, 29.8), ("Saudi Arabia", 24.0, 44.5), ("Iran", 32.8, 53.5), ("Afghanistan", 34.0, 66.5),
    ("Pakistan", 30.4, 69.2), ("India", 22.5, 81.0), ("Thailand", 15.3, 101.0), ("Indonesia", -2.0, 114.0),
    ("Australia", -25.5, 134.0), ("Algeria", 28.0, 2.5), ("Libya", 27.0, 17.5), ("Mali", 17.0, -3.5),
    ("Chad", 15.5, 18.5), ("Sudan", 15.5, 29.5), ("Nigeria", 9.5, 8.5), ("Ethiopia", 8.5, 39.5),
    ("DR Congo", -2.0, 23.5), ("South Africa", -29.5, 24.5),
]

# Obstacle / zone tooltip fallbacks for user-created objects
_USER_ZONE_DESC = "User-defined simulated restricted flight region."
_USER_OB_DESC = "User-defined simulated obstruction affecting the available route."


def all_env(zones=(), obstacles=(), zones_enabled: bool = True) -> list[dict]:
    """Every simulated environment item currently on the map (preset + user-created).

    Single source of truth for map markers, hover popups and nearby-conditions analysis.
    """
    items = list(ENV_WEATHER)
    if zones_enabled:
        items += ENV_ZONES
    items += ENV_OBSTACLES
    for z in zones:
        if not zones_enabled:
            break
        lat, lon = unproject(z["x"], z["y"])
        items.append(_item(f"RZ-U{z['id']:02d}", "zone", lat, lon, z["r"], z.get("sector", "Custom location"),
                           z["sev"], _USER_ZONE_DESC, status="Active", custom=True))
    for o in obstacles:
        lat, lon = unproject(o["x"], o["y"])
        items.append(_item(f"OBS-U{o['id']:02d}", "obstacle", lat, lon, OBSTACLE_R,
                           o.get("sector", "Custom location"), None, _USER_OB_DESC, status="Active", custom=True))
    return items


# --- Route proximity rule (frontend mock) ----------------------------------------------
# For each item we take the shortest geographic distance from the drawn route to the item's
# centre and subtract the item's own footprint radius -> "edge clearance".
#   edge clearance <= 0 km          -> AFFECTS the route (route passes through it)
#   0 < clearance <= NEAR_KM        -> NEAR the route (inside the route corridor)
#   clearance > NEAR_KM             -> not relevant (never listed)
NEAR_KM = 300.0


def assess_route(segments, items, direct_segments=None) -> list[dict]:
    """Classify simulated items relative to a route. Simulation only - not hazard detection."""
    def pts_of(segs):
        return [unproject(*p) for seg in segs for p in sample(seg, 60)]

    pts = pts_of(segments)
    direct_pts = pts_of(direct_segments) if direct_segments else None

    def clearance(plist, it):
        foot = it["r"] * KM_PER_UNIT_EQ * max(math.cos(math.radians(it["lat"])), 0.2)
        return min(haversine_km(la, lo, it["lat"], it["lon"]) for la, lo in plist) - foot

    out = []
    for it in items:
        edge = clearance(pts, it)
        rel = "affects" if edge <= 0 else "near" if edge <= NEAR_KM else "clear"
        detour = bool(direct_pts) and rel != "affects" and clearance(direct_pts, it) <= 0
        out.append({**it, "relation": rel, "clearance_km": max(edge, 0.0), "detour": detour})
    return out


ROUTE_TYPES = ["Shortest Distance", "Fastest Time", "Fuel Efficient", "Weather Avoidance"]
AIRCRAFT = {
    "Commercial": {"speed": 850, "max_alt": 41000},
    "Private Jet": {"speed": 780, "max_alt": 45000},
    "Turboprop": {"speed": 520, "max_alt": 31000},
    "Light Aircraft": {"speed": 300, "max_alt": 14000},
}

TEAM_NAME = "THE OUTLIERS"
TEAM_MEMBERS: list[str] = []  # add member names here when ready


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------
def _quad_point(seg, t):
    (x0, y0), (cx, cy), (x1, y1) = seg
    u = 1 - t
    return (u * u * x0 + 2 * u * t * cx + t * t * x1, u * u * y0 + 2 * u * t * cy + t * t * y1)


def sample(seg, n=48):
    return [_quad_point(seg, i / n) for i in range(n + 1)]


def _control(p0, p1, bend):
    """bend>0 arcs north, bend<0 arcs south (fraction of chord length)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy) or 1.0
    nx, ny = dy / length, -dx / length
    if ny > 0:
        nx, ny = -nx, -ny
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    return (mx + nx * bend * length, my + ny * bend * length)


def segments_length_km(segments) -> float:
    """Real geographic length of the drawn curve (haversine along the samples)."""
    total = 0.0
    for seg in segments:
        pts = [unproject(*p) for p in sample(seg)]
        total += sum(haversine_km(*pts[i], *pts[i + 1]) for i in range(len(pts) - 1))
    return total


def _min_clearance(segments, blockers):
    if not blockers:
        return 1e9
    worst = 1e9
    for seg in segments:
        for p in sample(seg):
            for b in blockers:
                worst = min(worst, math.dist(p, (b["x"], b["y"])) - b["r"])
    return worst


def blockers_for(zones, obstacles, zones_enabled=True, weather=None):
    out = []
    if zones_enabled:
        out += [{"x": z["x"], "y": z["y"], "r": z["r"] + 1.0} for z in list(zones) + ENV_ZONES]
    out += [{"x": o["x"], "y": o["y"], "r": OBSTACLE_R + 0.8} for o in list(obstacles) + ENV_OBSTACLES]
    if weather:
        out += [{"x": w["x"], "y": w["y"], "r": w["r"]} for w in weather]
    return out


DEFAULT_BEND = 0.06
_BEND_CANDIDATES = sorted(
    [0.30, 0.22, 0.14, 0.06, -0.02, -0.10, -0.18, -0.26, -0.34, -0.42],
    key=lambda b: abs(b - DEFAULT_BEND),
)



def _point_segment_distance(px, py, ax, ay, bx, by):
    """Shortest distance from a point to a line segment."""
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy

    if length_sq == 0:
        return math.hypot(px - ax, py - ay)

    t = ((px - ax) * dx + (py - ay) * dy) / length_sq
    t = max(0.0, min(1.0, t))

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    return math.hypot(px - closest_x, py - closest_y)


def _is_blocked(x, y, blockers, clearance=0.5):
    """Check whether a grid point falls inside a simulated hazard."""
    for b in blockers:
        radius = b["r"] + clearance
        if math.hypot(x - b["x"], y - b["y"]) <= radius:
            return True
    return False


def _segment_is_clear(a, b, blockers):
    """Check whether a straight line between two points avoids hazards."""
    for hazard in blockers:
        distance = _point_segment_distance(
            hazard["x"], hazard["y"],
            a[0], a[1], b[0], b[1]
        )

        if distance <= hazard["r"] + 0.5:
            return False

    return True


def _astar_leg(start, goal, blockers, step=1.5):
    """
    A* search between two map coordinates.

    Uses an 8-direction grid and Euclidean distance as its heuristic.
    Returns a list of map coordinates, or None if no route is found.
    """
    import heapq

    sx, sy = start
    gx, gy = goal

    # A* grid bounds around this leg and its hazards.
    chord = math.hypot(gx - sx, gy - sy)
    largest_radius = max(
        (b["r"] for b in blockers),
        default=0
    )
    margin = max(20.0, chord * 0.25, largest_radius * 2.0)

    min_x = min(sx, gx) - margin
    max_x = max(sx, gx) + margin
    min_y = min(sy, gy) - margin
    max_y = max(sy, gy) + margin

    def to_cell(point):
        return (
            round((point[0] - min_x) / step),
            round((point[1] - min_y) / step)
        )

    def to_point(cell):
        return (
            min_x + cell[0] * step,
            min_y + cell[1] * step
        )

    start_cell = to_cell(start)
    goal_cell = to_cell(goal)

    width = int((max_x - min_x) / step) + 2
    height = int((max_y - min_y) / step) + 2

    def inside(cell):
        return (
            0 <= cell[0] < width
            and 0 <= cell[1] < height
        )

    def blocked(cell):
        if cell == start_cell or cell == goal_cell:
            return False

        x, y = to_point(cell)
        return _is_blocked(x, y, blockers)

    # The eight possible movement directions.
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    def heuristic(cell):
        x, y = to_point(cell)
        return math.hypot(gx - x, gy - y)

    open_heap = []
    heapq.heappush(open_heap, (heuristic(start_cell), 0, start_cell))

    came_from = {}
    g_score = {start_cell: 0.0}
    closed = set()

    while open_heap:
        _, current_cost, current = heapq.heappop(open_heap)

        if current in closed:
            continue

        if current == goal_cell:
            # Reconstruct the path.
            cells = [current]

            while current in came_from:
                current = came_from[current]
                cells.append(current)

            cells.reverse()

            path = [start]
            path.extend(to_point(c) for c in cells[1:-1])
            path.append(goal)

            # Remove unnecessary intermediate points where a direct
            # line is clear. This makes the displayed route smoother.
            simplified = [path[0]]
            anchor = 0

            while anchor < len(path) - 1:
                next_index = len(path) - 1

                while next_index > anchor + 1:
                    if _segment_is_clear(
                        path[anchor],
                        path[next_index],
                        blockers
                    ):
                        break
                    next_index -= 1

                simplified.append(path[next_index])
                anchor = next_index

            return simplified

        closed.add(current)

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if not inside(neighbor) or neighbor in closed:
                continue

            if blocked(neighbor):
                continue

            # Prevent diagonal movement through blocked corners.
            if dx != 0 and dy != 0:
                side_a = (current[0] + dx, current[1])
                side_b = (current[0], current[1] + dy)

                if blocked(side_a) or blocked(side_b):
                    continue

            move_cost = step * (
                math.sqrt(2) if dx != 0 and dy != 0 else 1
            )

            tentative_g = current_cost + move_cost

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(
                    open_heap,
                    (f_score, tentative_g, neighbor)
                )

    # No valid path could be found.
    return None


def _points_to_segments(points):
    """Convert route coordinates into the segment format used by the map."""
    segments = []

    for p0, p1 in zip(points, points[1:]):
        midpoint = (
            (p0[0] + p1[0]) / 2,
            (p0[1] + p1[1]) / 2
        )
        segments.append((p0, midpoint, p1))

    return segments


def plan_route(points, blockers):
    """
    Plan a route using A* for every leg between departure,
    optional waypoints and destination.

    Keeps the existing return format so app.py can use it.
    """
    direct_segments = []

    for p0, p1 in zip(points, points[1:]):
        control = _control(p0, p1, DEFAULT_BEND)
        direct_segments.append((p0, control, p1))

    direct_blocked = _min_clearance(
        direct_segments, blockers
    ) < 0

    optimized_points = []
    route_found = True

    for start, goal in zip(points, points[1:]):
        leg = _astar_leg(start, goal, blockers)

        if leg is None:
            route_found = False
            break

        if optimized_points:
            optimized_points.extend(leg[1:])
        else:
            optimized_points.extend(leg)

    if route_found:
        optimized_segments = _points_to_segments(optimized_points)
        optimized_clear = (
            _min_clearance(optimized_segments, blockers) >= 0
        )
    else:
        optimized_segments = []
        optimized_clear = False

    return {
        "direct_segments": direct_segments,
        "optimized_segments": optimized_segments,
        "direct_km": segments_length_km(direct_segments),
        "optimized_km": (
            segments_length_km(optimized_segments)
            if optimized_clear else 0.0
        ),
        "direct_blocked": direct_blocked,
        "optimized_clear": optimized_clear,
    }



def route_midpoint(segments):
    return _quad_point(segments[len(segments) // 2], 0.5)


def route_heading_deg(segments):
    (x0, y0), _, (x1, y1) = segments[len(segments) // 2]
    return math.degrees(math.atan2(y1 - y0, x1 - x0))


def fmt_km(km):
    return f"{round(km):,} km"


def fmt_time(km, speed_kmh):
    hours = km / max(speed_kmh, 1)
    h, m = int(hours), int(round((hours - int(hours)) * 60))
    if m == 60:
        h, m = h + 1, 0
    return f"≈ {h}h {m:02d}m"
