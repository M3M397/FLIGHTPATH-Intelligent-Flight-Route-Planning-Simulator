"""FLIGHTPATH - reusable interface components (HTML/SVG builders + Streamlit helpers)."""
from __future__ import annotations

import base64
import html as _html
import math
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as stc

import mock_data as md
import world_data

# --------------------------------------------------------------------------
# Low-level helpers
# --------------------------------------------------------------------------
_LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 40">'
    '<path d="M2 37C14 22 30 12 62 3C49 10 42 14 36 20L47 22C39 24 34 27 30 33L26 26'
    'C18 28 10 32 2 37Z" fill="#985E6D"/></svg>'
)
LOGO_URI = "data:image/svg+xml;base64," + base64.b64encode(_LOGO_SVG.encode()).decode()


def flat(s: str) -> str:
    """Strip indentation/blank lines so Markdown never treats HTML as a code block."""
    return "".join(line.strip() for line in s.strip().splitlines())


def html(s: str) -> None:
    st.markdown(flat(s), unsafe_allow_html=True)


def load_css() -> None:
    css = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Chrome: sidebar + top bar
# --------------------------------------------------------------------------
NAV = [
    ("home", "Home", ":material/home:"),
    ("pilot", "Pilot Mode", ":material/flight:"),
    ("about", "About", ":material/info:"),
]


def sidebar(active: str, on_nav) -> None:
    with st.sidebar:
        html(f'<div class="fp-rail-logo"><img src="{LOGO_URI}" alt="FlightPath"></div>')
        for key, label, icon in NAV:
            st.button(label, key=f"nav_{key}", icon=icon,
                      type="primary" if active == key else "secondary",
                      on_click=on_nav, args=(key,))
        html('<div class="fp-rail-foot">Think Different.<br>Build Different.</div>')


def top_bar(mode_label: str) -> None:
    html(f"""
    <div class="fp-top">
      <div class="fp-brand">
        <img src="{LOGO_URI}" alt="">
        <div>
          <div class="fp-word">FLIGHT<b>PATH</b></div>
          <div class="fp-tag">Intelligent Flight Route Planning Simulator</div>
        </div>
      </div>
      <div class="fp-pill"><span class="fp-dot"></span>{_html.escape(mode_label)}</div>
    </div>""")


def card_title(text: str, number: int | None = None) -> None:
    num = f'<span class="fp-num">{number}</span>' if number else ""
    html(f'<div class="fp-cardtitle">{num}{_html.escape(text)}</div>')


# --------------------------------------------------------------------------
# Small HTML blocks
# --------------------------------------------------------------------------
def kv(label: str, value: str, tone: str = "") -> str:
    return f'<div class="fp-row"><div class="fp-k">{label}</div><div class="fp-v {tone}">{value}</div></div>'


def summary_card(dep: str, arr: str, km: float | None, time_txt: str | None, ready: bool, note: str) -> None:
    if ready:
        body = (kv("Route", f"{dep} → {arr}") + kv("Distance", md.fmt_km(km)) +
                kv("Estimated time", time_txt) + kv("Status", "✓ Route Ready", "ok"))
    else:
        body = (kv("Route", f"{dep} → {arr}") + kv("Distance", "—", "muted") +
                kv("Estimated time", "—", "muted") + kv("Status", "Awaiting search", "muted"))
    html(f'<div class="fp-h2">Route Summary</div><div class="fp-sum">{body}</div>'
         f'<div class="fp-note" style="margin-top:.4rem">{note}</div>')


def metrics_bar(items: list[tuple[str, str, str]]) -> None:
    cells = "".join(f'<div class="fp-metric"><div class="fp-k">{k}</div><div class="fp-v {t}">{v}</div></div>'
                    for k, v, t in items)
    html(f'<div class="fp-metrics">{cells}</div>')


def chips(labels: list[str], hot: bool = False) -> str:
    cls = "fp-chip hot" if hot else "fp-chip"
    return '<div class="fp-chips">' + "".join(f'<span class="{cls}">{_html.escape(l)}</span>' for l in labels) + "</div>"


def env_list(zones, obstacles, zones_enabled: bool) -> None:
    """Pilot Mode list: user-created objects + a one-line summary of the preset simulated environment."""
    rows = []
    for o in obstacles:
        rows.append(f'<div class="fp-env"><span>▲ Obstacle #{o["id"]}</span><span>{_html.escape(o.get("sector", "Custom"))}</span></div>')
    for z in zones:
        state = "" if zones_enabled else " · hidden"
        rows.append(f'<div class="fp-env"><span>▨ Restricted zone #{z["id"]}</span>'
                    f'<span>{z["sev"]} severity{state}</span></div>')
    if not rows:
        rows.append('<div class="fp-env"><span>No custom objects yet</span><span>use the buttons or the map</span></div>')
    countries = len(md._COUNTRY_ENV)
    ocean = sum(1 for w in md.ENV_WEATHER if w["country"] is None)
    html(f'<div class="fp-envlist">{"".join(rows)}</div>'
         f'<div class="fp-note">Preset simulated airspace: <b>{countries}</b> countries × (1 weather anomaly, 1 restricted zone, '
         f'1 obstacle) + <b>{ocean}</b> oceanic weather anomalies. Hover any symbol on the map for details.</div>')


def comparison_table(rows: list[tuple[str, str, str]], best_col: int | None) -> None:
    def cell(val, col):
        return f'<td class="best">{val}</td>' if best_col == col else f"<td>{val}</td>"
    body = "".join(f"<tr><td>{k}</td>{cell(a, 0)}{cell(b, 1)}</tr>" for k, a, b in rows)
    html(f'<table class="fp-table"><thead><tr><th></th><th>Direct route</th><th>Optimized route</th></tr></thead>'
         f'<tbody>{body}</tbody></table>')


def steps(current: int) -> None:
    labels = ["Initial route plotted", "Obstacle added across route", "Route blocked — recalculating", "Alternative route found"]
    out = []
    for i, l in enumerate(labels):
        cls = "active" if i == current else ("done" if i < current else "")
        mark = "✓" if i < current else str(i + 1)
        out.append(f'<div class="fp-step {cls}"><i>{mark}</i>{l}</div>')
    html(f'<div class="fp-steps">{"".join(out)}</div>')


def stat_cards(items: list[tuple[str, str, str]]) -> None:
    cells = "".join(f'<div><div class="fp-k">{k}</div><div class="fp-v {t}">{v}</div></div>' for k, v, t in items)
    html(f'<div class="fp-cards4">{cells}</div>')


# --------------------------------------------------------------------------
# Environment symbols (shared by the map, the legend and the nearby-conditions cards)
# --------------------------------------------------------------------------
_CLOUD = "M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"
_WX_PATHS = {
    "storm": '<path d="M6 16.326A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 .5 8.973"/><path d="m13 12-3 5h4l-3 5"/>',
    "rain": f'<path d="{_CLOUD}"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/>',
    "wind": '<path d="M12.8 19.6A2 2 0 1 0 14 16H2"/><path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/>',
    "fog": f'<path d="{_CLOUD}"/><path d="M16 17H7"/><path d="M17 21H9"/>',
}
_ICON_CACHE: dict[str, str] = {}


def _data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _hex_pts(cx, cy, r) -> str:
    return " ".join(f"{cx + r * math.cos(math.radians(60 * i + 30)):.2f},{cy + r * math.sin(math.radians(60 * i + 30)):.2f}" for i in range(6))


def icon_uri(name: str) -> str:
    """Small, consistent FlightPath-styled icons as <img>-safe data URIs (Streamlit-markdown friendly)."""
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]
    W = 'xmlns="http://www.w3.org/2000/svg"'
    if name in _WX_PATHS:
        svg = (f'<svg {W} viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" '
               f'stroke-linecap="round" stroke-linejoin="round">{_WX_PATHS[name]}</svg>')
    elif name == "obstacle":
        svg = (f'<svg {W} viewBox="0 0 24 24"><polygon points="12,3 21.5,20 2.5,20" fill="#192231" stroke="#fff" stroke-width="1.8" '
               f'stroke-linejoin="round"/><text x="12" y="17" text-anchor="middle" font-size="11" font-weight="700" fill="#fff" '
               f'font-family="Montserrat,Arial,sans-serif">!</text></svg>')
    elif name == "zone":
        svg = (f'<svg {W} viewBox="0 0 24 24"><defs><pattern id="h" width="4" height="4" patternUnits="userSpaceOnUse" '
               f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="#D98BA0" stroke-width="1.2"/></pattern></defs>'
               f'<polygon points="{_hex_pts(12, 12, 9.5)}" fill="rgba(152,94,109,.25)" stroke="#D98BA0" stroke-width="1.6"/>'
               f'<polygon points="{_hex_pts(12, 12, 9.5)}" fill="url(#h)" opacity=".6"/></svg>')
    elif name in ("dep", "arr"):
        fill = "#192231" if name == "dep" else "#985E6D"
        svg = (f'<svg {W} viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="#fff" stroke-opacity=".28"/>'
               f'<circle cx="12" cy="12" r="5.5" fill="{fill}" stroke="#fff" stroke-width="2.6"/></svg>')
    elif name == "waypoint":
        svg = (f'<svg {W} viewBox="0 0 24 24"><rect x="7" y="7" width="10" height="10" transform="rotate(45 12 12)" '
               f'fill="#192231" stroke="#fff" stroke-width="2.2"/></svg>')
    elif name == "route":
        svg = (f'<svg {W} viewBox="0 0 32 24"><line x1="3" y1="12" x2="29" y2="12" stroke="#E2A3B3" stroke-opacity=".35" stroke-width="9" stroke-linecap="round"/>'
               f'<line x1="3" y1="12" x2="29" y2="12" stroke="#985E6D" stroke-width="4" stroke-linecap="round"/></svg>')
    elif name == "alt":
        svg = (f'<svg {W} viewBox="0 0 32 24"><line x1="3" y1="12" x2="29" y2="12" stroke="#fff" stroke-opacity=".8" stroke-width="2.4" '
               f'stroke-dasharray="5 4.5" stroke-linecap="round"/></svg>')
    elif name == "weather":   # shaded region + symbol badge
        svg = (f'<svg {W} viewBox="0 0 24 24"><defs><radialGradient id="g"><stop offset="0" stop-color="#E6C6D0" stop-opacity=".8"/>'
               f'<stop offset=".6" stop-color="#985E6D" stop-opacity=".45"/><stop offset="1" stop-color="#985E6D" stop-opacity="0"/></radialGradient></defs>'
               f'<circle cx="12" cy="12" r="11.5" fill="url(#g)"/><circle cx="12" cy="12" r="7" fill="#192231" fill-opacity=".92" stroke="#985E6D" stroke-width="1.3"/>'
               f'<g transform="translate(5.5,5.5) scale(.55)" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{_WX_PATHS["storm"]}</g></svg>')
    else:
        svg = f'<svg {W} viewBox="0 0 24 24"/>'
    _ICON_CACHE[name] = _data_uri(svg)
    return _ICON_CACHE[name]


def _item_icon(it) -> str:
    return icon_uri(it["icon"] if it["kind"] == "weather" else it["kind"])


def tip_html(it) -> str:
    """Hover-popup markup for one environment item (same data that drives its map marker)."""
    e = _html.escape
    row = lambda k, v: f'<div class="tr"><span>{e(k)}</span>{e(str(v))}</div>'
    if it["kind"] == "obstacle":
        head, rows = "Simulated Obstacle", [row("ID", it["id"]), row("Location", it["location"])]
        rows += [f'<div class="td">{e(it["description"])}</div>', row("Status", it["status"])]
    elif it["kind"] == "zone":
        head, rows = "Restricted Airspace", [row("ID", it["id"]), row("Location", it["location"]), row("Severity", it["severity"])]
        rows += [f'<div class="td">{e(it["description"])}</div>', row("Status", it["status"])]
    else:
        head, rows = "Weather Anomaly", [row("ID", it["id"]), row("Location", it["location"]),
                                         row("Condition", it["condition"]), row("Severity", it["severity"])]
        rows += [f'<div class="td">{e(it["description"])}</div>']
    return f'<div class="th">{e(head)}</div>' + "".join(rows)


# --------------------------------------------------------------------------
# Home: map legend + nearby airspace conditions
# --------------------------------------------------------------------------
_LEGEND = [("dep", "Departure Airport"), ("arr", "Destination Airport"), ("route", "Flight Route"),
           ("alt", "Alternative Route"), ("obstacle", "Obstacle"), ("zone", "Restricted Airspace"),
           ("weather", "Weather Anomaly"), ("waypoint", "Waypoint")]


def legend_strip() -> None:
    cells = "".join(f'<div class="fp-lg"><img src="{icon_uri(k)}" alt="">{t}</div>' for k, t in _LEGEND)
    html(f'<div class="fp-legend"><div class="fp-legend-title">Map legend</div><div class="fp-legend-grid">{cells}</div></div>')


_REL_ORDER = {"affects": 0, "near": 1}


def _rel_text(r) -> tuple[str, str, str]:
    km = int(round(r["clearance_km"], -1))
    if r["relation"] == "affects":
        return "affects", "Affects route", "The simulated route passes through this condition."
    if r["detour"]:
        return "near", "Near route", f"Route adjusts around it · about {km:,} km clearance."
    return "near", "Near route", f"Located near the simulated route · about {km:,} km away."


def nearby_section(assessed: list[dict], max_cards: int = 9) -> None:
    e = _html.escape
    rel = sorted((r for r in assessed if r["relation"] in _REL_ORDER), key=lambda r: (_REL_ORDER[r["relation"]], r["clearance_km"]))
    n_aff = sum(r["relation"] == "affects" for r in rel)
    n_near = len(rel) - n_aff
    n_clear = len(assessed) - len(rel)
    head = '<div class="fp-h2 fp-caps">Nearby Airspace Conditions</div>'
    stats = (f'<div class="fp-chips" style="margin:.5rem 0 .2rem"><span class="fp-chip hot">{n_aff} affecting the route</span>'
             f'<span class="fp-chip">{n_near} near the route</span><span class="fp-chip">{n_clear} not relevant</span></div>')
    if not rel:
        body = ('<div class="fp-nempty">No significant simulated anomalies detected near this route.</div>')
    else:
        cards = []
        for r in rel[:max_cards]:
            cls, tag, txt = _rel_text(r)
            if r["kind"] == "weather":
                title, sev = f'{r["condition"]} — {r["location"]}', f'{r["severity"]} severity'
            elif r["kind"] == "zone":
                title, sev = f'Restricted Zone — {r["location"]}', f'{r["severity"]} severity'
            else:
                title, sev = f'Simulated Obstacle — {r["location"]}', r["status"]
            cards.append(
                f'<div class="fp-ncard {cls}"><div class="fp-nhead"><img src="{_item_icon(r)}" alt="">'
                f'<div class="fp-ntitle">{e(title)}</div></div>'
                f'<div class="fp-nsev">{e(sev)} · <span>{e(r["id"])}</span></div>'
                f'<div class="fp-ndesc">{e(r["description"])}</div>'
                f'<div class="fp-nrel"><b class="{cls}">{tag}</b>{e(txt)}</div></div>')
        extra = len(rel) - max_cards
        more = f'<div class="fp-note" style="margin-top:.5rem">+ {extra} more simulated condition(s) near this route.</div>' if extra > 0 else ""
        body = f'<div class="fp-ngrid">{"".join(cards)}</div>{more}'
    note = (f'<div class="fp-note" style="margin-top:.7rem">Proximity rule: <b>affects</b> = the route passes through the item; '
            f'<b>near</b> = within {int(md.NEAR_KM)} km of the route; anything farther is not listed. '
            f'Simulated demonstration data — not real aviation hazard detection.</div>')
    html(head + stats + body + note)


# --------------------------------------------------------------------------
# Map (SVG inside an iframe so the full document - fonts, patterns, animation -
# renders exactly as designed, independent of Streamlit's markdown sanitiser)
# --------------------------------------------------------------------------
def _path(segments) -> str:
    x0, y0 = segments[0][0]
    d = f"M{x0:.2f},{y0:.2f}"
    for _, (cx, cy), (x1, y1) in segments:
        d += f" Q{cx:.2f},{cy:.2f} {x1:.2f},{y1:.2f}"
    return d


def _hex(x, y, r) -> str:
    pts = [(x + r * math.cos(math.radians(60 * i + 30)), y + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    return " ".join(f"{px:.2f},{py:.2f}" for px, py in pts)


_SEV_OPACITY = {"Low": 0.55, "Medium": 0.8, "High": 1.0}
_ASPECT = 2.0          # assumed frame width/height used to size markers
_REF_PX = 900.0        # assumed frame width in px

_MAP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@200;300;400;600;700&display=swap');
*{box-sizing:border-box} html,body{margin:0;height:100%;background:transparent;overflow:hidden;font-family:'Montserrat','Segoe UI',sans-serif}
.wrap{position:relative;width:100%;height:__H__px;border-radius:18px;overflow:hidden;border:1px solid rgba(255,255,255,.3);background:#18202F;user-select:none}
svg{width:100%;height:100%;display:block}
.banner{position:absolute;top:14px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:10px;padding:10px 22px;border-radius:12px;
 font-weight:700;font-size:13px;letter-spacing:.1em;color:#fff;border:1px solid rgba(255,255,255,.35);white-space:nowrap}
.banner.blocked{background:rgba(152,94,109,.92)}
.banner.recalc{background:rgba(73,78,107,.95)}
.banner.recalc .spin{width:12px;height:12px;border-radius:50%;border:2px solid rgba(255,255,255,.35);border-top-color:#fff;animation:sp 1s linear infinite}
.toast{position:absolute;top:14px;right:14px;padding:10px 16px;border-radius:12px;background:rgba(25,34,49,.94);border:1px solid rgba(255,255,255,.3);
 font-weight:700;font-size:11px;letter-spacing:.1em;color:#fff;display:flex;gap:8px;align-items:center}
.toast b{color:#8CC7A8}
.legend{position:absolute;left:14px;top:14px;padding:10px 14px;border-radius:12px;background:rgba(25,34,49,.82);border:1px solid rgba(255,255,255,.25);
 font-size:10.5px;letter-spacing:.06em;color:rgba(255,255,255,.9);display:flex;flex-direction:column;gap:7px}
.legend div{display:flex;align-items:center;gap:9px}
.sw{width:26px;height:0;border-top:2px solid #fff;flex:none}
.sw.dash{border-top:2px dashed rgba(255,255,255,.75)} .sw.alt{border-top:3px solid #985E6D}
.sw.zone{height:12px;border:1px solid #D98BA0;background:repeating-linear-gradient(45deg,rgba(217,139,160,.9) 0 2px,transparent 2px 5px)}
.sw.wx{height:12px;border:0;border-radius:6px;background:radial-gradient(circle,rgba(255,255,255,.7),rgba(152,94,109,.4))}
.sw.ob{width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-bottom:12px solid #fff;border-top:0}
.zoom{position:absolute;right:14px;bottom:44px;display:flex;flex-direction:column;gap:6px}
.zoom button{min-width:34px;height:34px;padding:0 8px;border-radius:10px;border:1px solid rgba(255,255,255,.35);background:rgba(25,34,49,.88);color:#fff;font:700 15px 'Montserrat',sans-serif;cursor:pointer}
.zoom button.w{font-size:10px;letter-spacing:.08em}
.zoom button:hover{background:#985E6D;border-color:#985E6D}
.hint{position:absolute;left:50%;bottom:44px;transform:translateX(-50%);padding:7px 16px;border-radius:999px;background:rgba(152,94,109,.9);border:1px solid rgba(255,255,255,.35);font-size:11px;font-weight:600;letter-spacing:.08em;color:#fff;pointer-events:none;white-space:nowrap}
.scale{position:absolute;left:16px;bottom:12px;color:rgba(255,255,255,.85);font-size:10px;letter-spacing:.08em;pointer-events:none}
.scale .bar{height:6px;border:1.5px solid rgba(255,255,255,.85);border-top:0;width:100px;margin-bottom:3px}
.cap{position:absolute;right:14px;bottom:10px;font-size:9.5px;font-weight:300;letter-spacing:.12em;color:rgba(255,255,255,.6);text-transform:uppercase}
.cn{pointer-events:none;font-weight:400}
.env:hover{filter:brightness(1.3)}
@keyframes sp{to{transform:rotate(360deg)}}
"""


def _fit(points, pad=0.32, min_w=30.0):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    px, py = max((x1 - x0) * pad, 4.0), max((y1 - y0) * pad, 4.0)
    x0, x1, y0, y1 = x0 - px, x1 + px, y0 - py, y1 + py
    vbw = max(x1 - x0, (y1 - y0) * _ASPECT, min_w)
    return (x0, y0, x1, y1), vbw


def build_map(
    *,
    zones=(), obstacles=(), zones_enabled=True,
    dep: str, arr: str, waypoints=(),
    active=None, active_style="sunset",
    original=None,
    extra_zone=None,
    banner: tuple[str, str] | None = None,
    toast: str | None = None,
    legend: bool = False,
    hint: str | None = None,
) -> str:
    A = md.AIRPORTS
    # ---- view fitted to the route; k = map units per (reference) screen pixel
    fit_pts = [(A[c]["x"], A[c]["y"]) for c in (dep, arr, *waypoints)]
    for segs in (active, original):
        for seg in segs or []:
            fit_pts += md.sample(seg, 12)
    if extra_zone:
        fit_pts += [(extra_zone["x"] + dx * extra_zone["r"], extra_zone["y"] + dy * extra_zone["r"]) for dx in (-1, 1) for dy in (-1, 1)]
    box, vbw = _fit(fit_pts)
    k = vbw / _REF_PX
    cy_lat = md.unproject((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)[0]
    km_per_unit = md.KM_PER_UNIT_EQ * max(math.cos(math.radians(cy_lat)), 0.2)

    NS = 'vector-effect="non-scaling-stroke"'
    svg = [f"""<svg viewBox="0 0 {md.MAP_W:.0f} {md.MAP_H:.1f}" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="land" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{md.MAP_H:.1f}"><stop offset="0" stop-color="#3B4260"/><stop offset="1" stop-color="#2A3148"/></linearGradient>
      <pattern id="hatch" width="{7 * k:.3f}" height="{7 * k:.3f}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="{7 * k:.3f}" stroke="#D98BA0" stroke-width="{2 * k:.3f}"/></pattern>
      <radialGradient id="storm"><stop offset="0" stop-color="#E6C6D0" stop-opacity=".75"/><stop offset=".55" stop-color="#985E6D" stop-opacity=".45"/><stop offset="1" stop-color="#985E6D" stop-opacity="0"/></radialGradient>
      <radialGradient id="cloud"><stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset=".6" stop-color="#C9BEC4" stop-opacity=".3"/><stop offset="1" stop-color="#98878F" stop-opacity="0"/></radialGradient>
      <filter id="blur" primitiveUnits="objectBoundingBox" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.05"/></filter>
    </defs>
    <rect x="-200" y="-200" width="1400" height="800" fill="#18202F"/>"""]
    for lon in range(-180, 181, 10):
        x = (lon + 180) * md.SCALE
        svg.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{md.MAP_H:.1f}" stroke="#fff" stroke-opacity=".05" stroke-width="1" {NS}/>')
    for lat in range(-50, 81, 10):
        y = (md.LAT_TOP - lat) * md.SCALE
        svg.append(f'<line x1="0" y1="{y:.1f}" x2="{md.MAP_W:.0f}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".05" stroke-width="1" {NS}/>')
    # All countries - including Pakistan, whose polygon is stored separately - use the SAME fill and border style.
    land = 'fill="url(#land)" stroke="#fff" stroke-opacity=".2" stroke-width="0.8" stroke-linejoin="round"'
    svg.append(f'<path d="{world_data.WORLD_PATH}" {land} {NS}/>')
    svg.append(f'<path d="{world_data.PAKISTAN_PATH}" {land} {NS}/>')
    for name, la, lo in md.COUNTRY_LABELS:
        lx, ly = md.project(la, lo)
        svg.append(f'<text class="cn" x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" font-size="{8.4 * k:.3f}" letter-spacing="{1.3 * k:.3f}" '
                   f'fill="#C7BAC1" fill-opacity=".7" stroke="#18202F" stroke-opacity=".6" stroke-width="{2.4 * k:.3f}" '
                   f'stroke-linejoin="round" paint-order="stroke">{_html.escape(name.upper())}</text>')

    def zone(z, sev="High"):
        op = _SEV_OPACITY.get(sev, .8)
        pts = _hex(z["x"], z["y"], z["r"])
        return (f'<polygon points="{pts}" fill="rgba(152,94,109,.18)" stroke="#D98BA0" stroke-width="1.6" stroke-opacity="{op}" {NS}/>'
                f'<polygon points="{pts}" fill="url(#hatch)" opacity="{op * .55:.2f}"/>')

    # Every item below comes from md.all_env(): the marker and its hover popup share one record.
    for it in md.all_env(zones, obstacles, zones_enabled):
        x, y, tip = it["x"], it["y"], _html.escape(tip_html(it), quote=True)
        if it["kind"] == "weather":
            glow = "storm" if it["icon"] in ("storm", "rain") else "cloud"
            s_ = 15 * k / 24
            svg.append(
                f'<g class="env" data-tip="{tip}">'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{it["r"]}" fill="url(#{glow})" filter="url(#blur)"/>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{it["r"] * .8:.2f}" fill="none" stroke="#E7B9C4" stroke-opacity=".3" stroke-width="1" stroke-dasharray="3 3" {NS}/>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{10 * k:.3f}" fill="#192231" fill-opacity=".92" stroke="#985E6D" stroke-width="1.4" {NS}/>'
                f'<g transform="translate({x - 12 * s_:.3f},{y - 12 * s_:.3f}) scale({s_:.4f})" fill="none" stroke="#fff" stroke-width="2.1" '
                f'stroke-linecap="round" stroke-linejoin="round">{_WX_PATHS[it["icon"]]}</g>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{max(it["r"] * .7, 11 * k):.3f}" fill="transparent"/></g>')
        elif it["kind"] == "zone":
            svg.append(f'<g class="env" data-tip="{tip}">{zone(it, it["severity"])}</g>')
        else:
            h = 9 * k
            svg.append(
                f'<g class="env" data-tip="{tip}"><polygon points="{x:.2f},{y - h:.2f} {x + h * .95:.2f},{y + h * .75:.2f} {x - h * .95:.2f},{y + h * .75:.2f}" '
                f'fill="#192231" fill-opacity=".9" stroke="#fff" stroke-width="1.6" stroke-linejoin="round" {NS}/>'
                f'<text x="{x:.2f}" y="{y + h * .5:.2f}" text-anchor="middle" font-size="{h * .9:.3f}" font-weight="700" fill="#fff">!</text>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{h * 1.4:.3f}" fill="transparent"/></g>')
    if extra_zone:
        blk = _html.escape('<div class="th">Simulated Blockage</div><div class="tr"><span>Status</span>Active</div>'
                           '<div class="td">Temporary simulated blockage used by the rerouting demonstration.</div>', quote=True)
        svg.append(f'<g class="env" data-tip="{blk}">{zone(extra_zone, "High")}</g>')
        svg.append(f'<text x="{extra_zone["x"]:.2f}" y="{extra_zone["y"] + 4 * k:.2f}" text-anchor="middle" font-size="{11 * k:.3f}" font-weight="700" letter-spacing="{1.5 * k:.3f}" fill="#fff" pointer-events="none">BLOCKED</text>')
    if original:
        svg.append(f'<path d="{_path(original)}" fill="none" stroke="#fff" stroke-opacity=".65" stroke-width="2.4" stroke-dasharray="7 7" stroke-linecap="round" pointer-events="none" {NS}/>')
    if active:
        color = "#985E6D" if active_style == "sunset" else "#FFFFFF"
        if active_style == "sunset":
            svg.append(f'<path d="{_path(active)}" fill="none" stroke="#E2A3B3" stroke-opacity=".3" stroke-width="10" stroke-linecap="round" pointer-events="none" {NS}/>')
        svg.append(f'<path d="{_path(active)}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" pointer-events="none" {NS}/>')
    keep = {dep, arr, *waypoints}
    for code, a in A.items():
        if code in keep:
            continue
        svg.append(f'<circle cx="{a["x"]:.2f}" cy="{a["y"]:.2f}" r="{3.5 * k:.3f}" fill="#98878F" fill-opacity=".95"/>'
                   f'<text x="{a["x"]:.2f}" y="{a["y"] + 16 * k:.2f}" text-anchor="middle" font-size="{9.5 * k:.3f}" font-weight="400" letter-spacing="{1.6 * k:.3f}" fill="#B9AAB2">{code}</text>')
    for code in waypoints:
        a = A[code]; s = 6 * k
        svg.append(f'<rect x="{a["x"] - s:.2f}" y="{a["y"] - s:.2f}" width="{2 * s:.2f}" height="{2 * s:.2f}" transform="rotate(45 {a["x"]:.2f} {a["y"]:.2f})" fill="#192231" stroke="#fff" stroke-width="2" {NS}/>'
                   f'<text x="{a["x"]:.2f}" y="{a["y"] + 24 * k:.2f}" text-anchor="middle" font-size="{11 * k:.3f}" font-weight="600" letter-spacing="{2 * k:.3f}" fill="#fff">{code}</text>')
    if active:
        mx, my = md.route_midpoint(active)
        ang = md.route_heading_deg(active)
        svg.append(f'<g pointer-events="none" transform="translate({mx:.2f},{my:.2f}) rotate({ang:.1f}) scale({0.9 * k:.4f})">'
                   '<path d="M16 0L-4-4L-10-15L-14-15L-9-3L-16-3L-18-8L-21-8L-19 0L-21 8L-18 8L-16 3L-9 3L-14 15L-10 15L-4 4Z" fill="#fff" stroke="#192231" stroke-width="1.2"/></g>')
    for code, fill in ((dep, "#192231"), (arr, "#985E6D")):          # departure = Evening, destination = Sunset
        a = A[code]
        svg.append(f'<circle cx="{a["x"]:.2f}" cy="{a["y"]:.2f}" r="{13 * k:.3f}" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="1" pointer-events="none" {NS}/>'
                   f'<circle cx="{a["x"]:.2f}" cy="{a["y"]:.2f}" r="{7 * k:.3f}" fill="{fill}" stroke="#fff" stroke-width="3" pointer-events="none" {NS}/>'
                   f'<text x="{a["x"]:.2f}" y="{a["y"] + 30 * k:.2f}" text-anchor="middle" font-size="{15 * k:.3f}" font-weight="700" letter-spacing="{2.5 * k:.3f}" fill="#fff" pointer-events="none">{code}</text>')
    svg.append("</svg>")

    overlays = ""
    if banner:
        tone, text = banner
        icon = '<span class="spin"></span>' if tone == "recalc" else "⚠"
        overlays += f'<div class="banner {tone}">{icon}{_html.escape(text)}</div>'
    if toast:
        overlays += f'<div class="toast"><b>✓</b>{_html.escape(toast)}</div>'
    if legend:
        overlays += ('<div class="legend">'
                     '<div><span class="sw dash"></span>Original Route</div>'
                     '<div><span class="sw alt"></span>Active / Alternative Route</div>'
                     '<div><span class="sw zone"></span>Restricted Zone (demo)</div>'
                     '<div><span class="sw wx"></span>Weather Area</div>'
                     '<div><span class="sw ob"></span>Obstacle (demo)</div></div>')
    overlays += ('<div class="zoom"><button data-z="in" title="Zoom in">+</button><button data-z="out" title="Zoom out">−</button>'
                 '<button data-z="reset" title="Fit route">⟲</button><button class="w" data-z="world" title="Whole world">WORLD</button></div>')
    if hint:
        overlays += f'<div class="hint">{_html.escape(hint)}</div>'
    overlays += '<div class="scale"><div class="bar"></div><span class="lbl"></span></div>'
    overlays += '<div class="cap">Simulated routes · scroll to zoom · drag to pan</div>'
    data = (f'data-box="{box[0]:.2f},{box[1]:.2f},{box[2]:.2f},{box[3]:.2f}" data-kmunit="{km_per_unit:.4f}" '
            f'data-full="{md.MAP_W:.0f},{md.MAP_H:.2f}"')
    return f'<style>{_MAP_CSS}</style><div class="wrap" {data}>{"".join(svg)}{overlays}</div>'


_map_component = stc.declare_component("flightpath_map", path=str(Path(__file__).parent / "map_component"))


def render_map(map_html: str, height: int = 430, key: str = "map", clickable: bool = False):
    """Interactive map (local Streamlit component). Returns {"x","y","t"} after a click when clickable."""
    return _map_component(html=map_html.replace("__H__", str(height)), height=height,
                          clickable=clickable, key=key, default=None)
