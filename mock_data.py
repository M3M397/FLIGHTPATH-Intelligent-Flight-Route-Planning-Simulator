"""FLIGHTPATH - airports, simulated environment and frontend stand-ins.

Airport LOCATIONS are real (approximate coordinates, Pakistan + major world hubs).
Everything else - routes, restricted zones, obstacles, weather - is SIMULATED.
`plan_route()` is a *frontend stand-in*: it draws smooth curves and nudges them
away from obstacles so the interface has something to show. It is NOT an A*
implementation. Integration point for the real engine: replace its body and
keep the same return shape.
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

WEATHER = [
    {"x": project(22.5, 68.5)[0], "y": project(22.5, 68.5)[1], "r": 7.0, "kind": "storm"},
    {"x": project(35.0, 70.0)[0], "y": project(35.0, 70.0)[1], "r": 6.0, "kind": "cloud"},
    {"x": project(27.0, 47.0)[0], "y": project(27.0, 47.0)[1], "r": 9.0, "kind": "storm"},
    {"x": project(45.0, -40.0)[0], "y": project(45.0, -40.0)[1], "r": 14.0, "kind": "storm"},
]

_z = project(31.0, 65.0)
_o = project(28.5, 74.3)
DEFAULT_ZONES = [{"id": 1, "x": _z[0], "y": _z[1], "r": SEVERITY_R["Medium"], "sev": "Medium", "sector": "Demo zone"}]
DEFAULT_OBSTACLES = [{"id": 2, "x": _o[0], "y": _o[1], "sector": "Demo obstacle"}]

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
        out += [{"x": z["x"], "y": z["y"], "r": z["r"] + 1.0} for z in zones]
    out += [{"x": o["x"], "y": o["y"], "r": OBSTACLE_R + 0.8} for o in obstacles]
    if weather:
        out += [{"x": w["x"], "y": w["y"], "r": w["r"]} for w in weather]
    return out


DEFAULT_BEND = 0.06
_BEND_CANDIDATES = sorted(
    [0.30, 0.22, 0.14, 0.06, -0.02, -0.10, -0.18, -0.26, -0.34, -0.42],
    key=lambda b: abs(b - DEFAULT_BEND),
)


def plan_route(points, blockers):
    """FRONTEND STAND-IN (not A*). See module docstring."""
    direct, optimized = [], []
    for p0, p1 in zip(points, points[1:]):
        d = (p0, _control(p0, p1, DEFAULT_BEND), p1)
        direct.append(d)
        best, best_clear = d, _min_clearance([d], blockers)
        if best_clear < 0:
            for b in _BEND_CANDIDATES:
                cand = (p0, _control(p0, p1, b), p1)
                clear = _min_clearance([cand], blockers)
                if clear >= 0:
                    best, best_clear = cand, clear
                    break
                if clear > best_clear:
                    best, best_clear = cand, clear
        optimized.append(best)
    return {
        "direct_segments": direct,
        "optimized_segments": optimized,
        "direct_km": segments_length_km(direct),
        "optimized_km": segments_length_km(optimized),
        "direct_blocked": _min_clearance(direct, blockers) < 0,
        "optimized_clear": _min_clearance(optimized, blockers) >= 0,
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
