"""FLIGHTPATH - Intelligent Flight Route Planning Simulator (frontend prototype).

Run with:  streamlit run app.py

All route data is simulated. `mock_data.plan_route()` is a frontend stand-in and
is the single place where the shared A* engine should be plugged in later.
"""
from __future__ import annotations

import copy
import math
import time

import streamlit as st

import components as ui
import mock_data as md

st.set_page_config(page_title="FLIGHTPATH", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------
DEFAULTS = dict(
    page="home", dep="KHI", arr="ISB", route_found=False,
    waypoints=[], route_type="Shortest Distance", max_dist=8000, route_pref="Optimized Route",
    zones_enabled=True, zones=copy.deepcopy(md.DEFAULT_ZONES), obstacles=copy.deepcopy(md.DEFAULT_OBSTACLES),
    next_id=10, severity="Medium", sector="Sindh",
    cruise_alt=35000, aircraft="Commercial", max_alt=41000, speed=850,
    compare=False, stage=0, click_mode="Off", last_click=0,
)
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, copy.deepcopy(v))
ss = st.session_state


def norm(v):
    """Always keep airport CODES (never display labels) in state."""
    return str(v).split(" — ")[0].strip()


for _k in ("dep", "arr", "w_dep", "w_arr"):
    if _k in ss:
        ss[_k] = norm(ss[_k])
ss.waypoints = [norm(w) for w in ss.waypoints if norm(w) in md.AIRPORTS]
if ss.sector not in md.SECTORS:
    ss.sector = "Sindh"
if ss.dep not in md.AIRPORTS:
    ss.dep = "KHI"
if ss.arr not in md.AIRPORTS:
    ss.arr = "ISB"


def bind(widget, key: str, label: str, after=None, **kw):
    """Widget whose value lives in a canonical session key, so it survives page switches."""
    wk = f"w_{key}"
    if wk not in ss:
        ss[wk] = ss[key]

    def _cb():
        ss[key] = ss[wk]
        if after:
            after()
    return widget(label, key=wk, on_change=_cb, **kw)


def go(page: str) -> None:
    ss.page = page


# ---- callbacks ----
def _route_changed():
    ss.route_found = False
    ss.compare = False
    ss.stage = 0


def find_route():
    if ss.dep == ss.arr:
        st.toast("Departure and destination must be different.")
        return
    ss.route_found = True


def _env_count(sector: str) -> int:
    return sum(1 for o in ss.obstacles + ss.zones if o.get("sector") == sector)


def _place():
    cx, cy = md.SECTORS[ss.sector]
    n = _env_count(ss.sector)
    return cx + 2.0 * (n % 3), cy + 1.6 * (n % 3) + 1.2 * (n // 3)


def add_obstacle():
    if len(ss.obstacles) >= 6:
        st.toast("Obstacle limit reached (6). Remove one first.")
        return
    x, y = _place()
    ss.obstacles.append({"id": ss.next_id, "x": x, "y": y, "sector": ss.sector})
    ss.next_id += 1
    ss.stage = 0


def remove_obstacle():
    if ss.obstacles:
        ss.obstacles.pop()
        ss.stage = 0
    else:
        st.toast("No obstacles to remove.")


def add_zone():
    if len(ss.zones) >= 5:
        st.toast("Restricted-zone limit reached (5). Remove one first.")
        return
    x, y = _place()
    r = md.SEVERITY_R[ss.severity]
    ss.zones.append({"id": ss.next_id, "x": x, "y": y, "r": r, "sev": ss.severity, "sector": ss.sector})
    ss.next_id += 1
    ss.stage = 0


def remove_zone():
    if ss.zones:
        ss.zones.pop()
        ss.stage = 0
    else:
        st.toast("No restricted zones to remove.")


def add_waypoint():
    choice = ss.get("wp_choice")
    if choice and choice not in ss.waypoints and len(ss.waypoints) < 4:
        ss.waypoints.append(choice)
        _route_changed()
    elif len(ss.waypoints) >= 4:
        st.toast("Waypoint limit reached (4).")


def remove_waypoint():
    if ss.waypoints:
        ss.waypoints.pop()
        _route_changed()


CLICK_MODES = ["Off", "Place obstacle", "Place restricted zone", "Remove nearest object"]


def handle_click(click):
    """Apply a map click (from the interactive component) to the simulated environment."""
    if not click or click.get("t") == ss.last_click or ss.click_mode == "Off":
        return
    ss.last_click = click["t"]
    x, y, mode = int(click["x"]), int(click["y"]), ss.click_mode
    if mode == "Place obstacle":
        if len(ss.obstacles) >= 6:
            st.toast("Obstacle limit reached (6).")
        else:
            ss.obstacles.append({"id": ss.next_id, "x": x, "y": y, "sector": "Map click"}); ss.next_id += 1
    elif mode == "Place restricted zone":
        if len(ss.zones) >= 5:
            st.toast("Restricted-zone limit reached (5).")
        else:
            r = md.SEVERITY_R[ss.severity]
            ss.zones.append({"id": ss.next_id, "x": x, "y": y, "r": r, "sev": ss.severity, "sector": "Map click"}); ss.next_id += 1
    else:
        cands = [(math.dist((x, y), (o["x"], o["y"])) - md.OBSTACLE_R, "o", o) for o in ss.obstacles]
        cands += [(math.dist((x, y), (z["x"], z["y"])) - z["r"], "z", z) for z in ss.zones]
        if cands:
            d, kind, obj = min(cands, key=lambda t: t[0])
            if d < 3.0:
                (ss.obstacles if kind == "o" else ss.zones).remove(obj)
            else:
                st.toast("No object near that point.")
    ss.stage = 0
    st.rerun()


def toggle_compare():
    ss.compare = not ss.compare


def on_aircraft():
    spec = md.AIRCRAFT[ss.aircraft]
    ss.speed, ss.max_alt = spec["speed"], spec["max_alt"]
    ss.w_speed, ss.w_max_alt = spec["speed"], spec["max_alt"]
    ss.cruise_alt = min(ss.cruise_alt, spec["max_alt"])
    ss.w_cruise_alt = ss.cruise_alt


def reset_demo():
    ss.stage = 0


# --------------------------------------------------------------------------
# Shared computations
# --------------------------------------------------------------------------
def xy(code):
    a = md.AIRPORTS[norm(code)]
    return (a["x"], a["y"])


def env_blockers(weather: bool = False):
    return md.blockers_for(ss.zones, ss.obstacles, ss.zones_enabled, md.WEATHER if weather else None)


def map_env():
    return dict(zones=ss.zones, obstacles=ss.obstacles, zones_enabled=ss.zones_enabled)


TIME_FACTOR = {"Shortest Distance": 1.0, "Fastest Time": 0.97, "Fuel Efficient": 1.05, "Weather Avoidance": 1.0}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def page_home():
    ui.top_bar("Passenger Mode")
    left, center, right = st.columns([1.0, 2.9, 1.0], gap="medium")

    with left:
        with st.container(key="card_plan"):
            ui.html("""<div class="fp-h1">Plan Your Flight</div>
            <p class="fp-sub">Welcome aboard. Choose a Pakistani or international airport for your departure and destination, and FlightPath will show you a simulated route.</p>""")
            bind(st.selectbox, "dep", "Departure", after=_route_changed, options=md.AIRPORT_CODES, format_func=md.airport_label)
            bind(st.selectbox, "arr", "Destination", after=_route_changed, options=md.AIRPORT_CODES, format_func=md.airport_label)
            if ss.dep == ss.arr:
                st.warning("Departure and destination must be different.")
            st.button("Find Optimal Route", type="primary", on_click=find_route, key="find_route")

    pts = [xy(ss.dep), xy(ss.arr)]
    plan = md.plan_route(pts, env_blockers()) if ss.dep != ss.arr else None
    found = (
    ss.route_found
    and plan is not None
    and plan["optimized_clear"]
)
    # dashed line = the straight path the optimized route had to avoid (only when they differ)
    alt = plan["direct_segments"] if found and plan["direct_km"] != plan["optimized_km"] else None

    with center:
        ui.render_map(ui.build_map(**map_env(), dep=ss.dep, arr=ss.arr, original=alt,
                                   active=plan["optimized_segments"] if found else None), height=500, key="map_home")
        ui.legend_strip()

    with right:
        with st.container(key="card_summary"):
            km = plan["optimized_km"] if found else None
            ui.summary_card(ss.dep, ss.arr, km, md.fmt_time(km, ss.speed) if found else None, found,
                            "Simulated demonstration data. Not for navigation." if found
                            else "Select Find Optimal Route to see your simulated route.")

    # Hidden until the passenger has searched for a route
    if found:
        assessed = md.assess_route(plan["optimized_segments"],
                                   md.all_env(ss.zones, ss.obstacles, ss.zones_enabled), plan["direct_segments"])
        with st.container(key="card_nearby"):
            ui.nearby_section(assessed)


def page_pilot():
    ui.top_bar("Pilot Mode · Advanced Flight Planning")
    ui.html("""<div class="fp-h1">Pilot Mode</div>
    <p class="fp-sub">Configure the route, shape the simulated airspace and tune flight parameters. All values are simulated planning inputs.</p>""")

    left, right = st.columns([1.0, 2.1], gap="medium")

    # ---------------- Controls ----------------
    with left:
        with st.container(key="card_route"):
            ui.card_title("Route Configuration", 1)
            c1, c2 = st.columns(2)
            with c1:
                bind(st.selectbox, "dep", "Departure", after=_route_changed, options=md.AIRPORT_CODES)
            with c2:
                bind(st.selectbox, "arr", "Destination", after=_route_changed, options=md.AIRPORT_CODES)
            if ss.dep == ss.arr:
                st.warning("Departure and destination must be different.")
            avail = [c for c in md.AIRPORT_CODES if c not in (ss.dep, ss.arr) and c not in ss.waypoints]
            st.selectbox("Waypoint (optional)", avail, key="wp_choice", format_func=md.airport_label)
            b1, b2 = st.columns(2)
            b1.button("Add Waypoint", on_click=add_waypoint, key="wp_add")
            b2.button("Remove Last", on_click=remove_waypoint, key="wp_rm")
            ui.html(ui.chips(ss.waypoints, hot=True) if ss.waypoints
                    else '<div class="fp-note">No waypoints — direct departure to destination.</div>')
            bind(st.selectbox, "route_type", "Preferred route type", options=md.ROUTE_TYPES)
            bind(st.slider, "max_dist", "Maximum route distance (km)", min_value=500, max_value=20000, step=100)
            bind(st.radio, "route_pref", "Route shown", options=["Direct Route", "Optimized Route"], horizontal=True)
            st.button("Hide Comparison" if ss.compare else "Compare Routes", on_click=toggle_compare, key="cmp")

        with st.container(key="card_airspace"):
            ui.card_title("Airspace Restrictions", 2)
            bind(st.toggle, "zones_enabled", "Simulated restricted zones")
            s1, s2 = st.columns(2)
            with s1:
                bind(st.selectbox, "sector", "Placement sector", options=list(md.SECTORS))
            with s2:
                bind(st.selectbox, "severity", "Zone severity", options=md.SEVERITIES)
            bind(st.radio, "click_mode", "Map click action", options=CLICK_MODES, horizontal=True)
            a1, a2 = st.columns(2)
            a1.button("Add Obstacle", on_click=add_obstacle, key="ob_add")
            a2.button("Remove Obstacle", on_click=remove_obstacle, key="ob_rm")
            a3, a4 = st.columns(2)
            a3.button("Add Restricted Zone", on_click=add_zone, key="z_add")
            a4.button("Remove Restricted Zone", on_click=remove_zone, key="z_rm")
            ui.env_list(ss.zones, ss.obstacles, ss.zones_enabled)

        with st.container(key="card_params"):
            ui.card_title("Flight Parameters", 3)
            p1, p2 = st.columns(2)
            with p1:
                bind(st.slider, "cruise_alt", "Cruising altitude (ft)", min_value=5000, max_value=45000, step=1000)
            with p2:
                bind(st.selectbox, "aircraft", "Aircraft category", after=on_aircraft, options=list(md.AIRCRAFT))
            p3, p4 = st.columns(2)
            with p3:
                bind(st.number_input, "max_alt", "Max permitted altitude (ft)", min_value=10000, max_value=50000, step=1000)
            with p4:
                bind(st.slider, "speed", "Flight speed (km/h)", min_value=200, max_value=1000, step=10)
            if ss.cruise_alt > ss.max_alt:
                st.warning("Cruising altitude exceeds the maximum permitted altitude.")

    # ---------------- Map + results ----------------
    valid = ss.dep != ss.arr
    plan = None
    if valid:
        pts = [xy(ss.dep)] + [xy(w) for w in ss.waypoints] + [xy(ss.arr)]
        plan = md.plan_route(pts, env_blockers(weather=ss.route_type == "Weather Avoidance"))

    hint = None if ss.click_mode == "Off" else f"Click the map: {ss.click_mode}"
    with right:
        if plan:
            direct = ss.route_pref == "Direct Route"
            segs = plan["direct_segments"] if direct else plan["optimized_segments"]
            km = plan["direct_km"] if direct else plan["optimized_km"]
            differs = plan["direct_km"] != plan["optimized_km"]
            original = plan["direct_segments"] if (not direct and differs) else None
            if direct:
                status, tone = ("Blocked", "warn") if plan["direct_blocked"] else ("✓ Direct", "ok")
            else:
                status, tone = ("✓ Optimized", "ok") if plan["optimized_clear"] else ("No clear path", "warn")
            if km > ss.max_dist:
                status, tone = "Over distance limit", "warn"
            tf = TIME_FACTOR[ss.route_type]
            handle_click(ui.render_map(ui.build_map(**map_env(), dep=ss.dep, arr=ss.arr, waypoints=ss.waypoints,
                                                    active=segs, original=original, legend=True, hint=hint),
                                       height=470, key="map_pilot", clickable=ss.click_mode != "Off"))
            ui.metrics_bar([("Distance", md.fmt_km(km), ""), ("Flight time", md.fmt_time(km * tf, ss.speed), ""),
                            ("Status", status, tone), ("Route type", ss.route_type, "")])
            ui.html(f'<div class="fp-note">Cruise <b>{ss.cruise_alt:,} ft</b> · {ss.aircraft} · <b>{ss.speed} km/h</b>'
                    f' · max altitude {ss.max_alt:,} ft · simulated values</div>')
            if ss.compare:
                with st.container(key="card_compare"):
                    ui.card_title("Route Comparison")
                    d_km, o_km = plan["direct_km"], plan["optimized_km"]
                    delta = o_km - d_km
                    ui.comparison_table([
                        ("Distance", md.fmt_km(d_km), md.fmt_km(o_km)),
                        ("Flight time", md.fmt_time(d_km * tf, ss.speed), md.fmt_time(o_km * tf, ss.speed)),
                        ("Airspace", "Crosses restrictions" if plan["direct_blocked"] else "Clear",
                         "Clear" if plan["optimized_clear"] else "Unavoidable conflict"),
                        ("Difference", "—", f"{delta:+,.0f} km" if abs(delta) > 0.5 else "Same path"),
                    ], best_col=1 if plan["direct_blocked"] else None)
        else:
            handle_click(ui.render_map(ui.build_map(**map_env(), dep=ss.dep, arr=ss.arr, waypoints=ss.waypoints, legend=True, hint=hint),
                                       height=470, key="map_pilot", clickable=ss.click_mode != "Off"))
            st.info("Choose two different airports to plan a route.")

    page_reroute_demo()


def page_reroute_demo():
    with st.container(key="card_reroute"):
        ui.html("""<div class="fp-h2">Dynamic Rerouting Demonstration</div>
        <p class="fp-sub">A simulated blockage appears across the initial route and the display switches to an illustrative alternative.
        This is a frontend demonstration — no pathfinding algorithm is running yet.</p>""")
        if ss.dep == ss.arr:
            st.info("Choose two different airports to run the demonstration.")
            return

        pts = [xy(ss.dep), xy(ss.arr)]
        base = md.plan_route(pts, env_blockers())
        initial = base["optimized_segments"]
        mx, my = md.route_midpoint(initial)
        chord = math.dist(pts[0], pts[1])
        block = {"x": mx, "y": my, "r": 0.11 * chord}
        alt_plan = md.plan_route(pts, env_blockers() + [{"x": mx, "y": my, "r": 0.17 * chord}])
        alt = alt_plan["optimized_segments"]
        alt_ok = alt_plan["optimized_clear"]
        km0, km1 = base["optimized_km"], alt_plan["optimized_km"]

        col_map, col_ctl = st.columns([2.3, 1.0], gap="medium")
        ph_map = col_map.empty()
        with col_ctl:
            ph_steps = st.empty()
            run = st.button("Run Rerouting Demo", type="primary", key="demo_run")
            st.button("Reset Demo", on_click=reset_demo, key="demo_reset")
            ui.html('<div class="fp-note">Uses the current departure, destination and airspace. Waypoints are ignored here.</div>')

        def draw(stage: int):
            kw = dict(**map_env(), dep=ss.dep, arr=ss.arr)
            if stage == 0:
                m = ui.build_map(**kw, active=initial, active_style="white")
                stats = [("Distance", md.fmt_km(km0), ""), ("Flight time", md.fmt_time(km0, ss.speed), ""),
                         ("Status", "✓ Route clear", "ok"), ("Route change", "—", "muted")]
            elif stage == 1:
                m = ui.build_map(**kw, original=initial, extra_zone=block, banner=("blocked", "ROUTE BLOCKED"))
                stats = [("Distance", md.fmt_km(km0), ""), ("Flight time", md.fmt_time(km0, ss.speed), ""),
                         ("Status", "Blocked", "warn"), ("Route change", "—", "muted")]
            elif stage == 2:
                m = ui.build_map(**kw, original=initial, extra_zone=block, banner=("recalc", "RECALCULATING ROUTE"))
                stats = [("Distance", "Calculating…", "muted"), ("Flight time", "Calculating…", "muted"),
                         ("Status", "Recalculating", "muted"), ("Route change", "—", "muted")]
            else:
                if alt_ok:
                    m = ui.build_map(**kw, original=initial, extra_zone=block, active=alt, toast="ALTERNATIVE ROUTE FOUND")
                    d = km1 - km0
                    stats = [("Distance", md.fmt_km(km1), ""), ("Flight time", md.fmt_time(km1, ss.speed), ""),
                             ("Status", "✓ Rerouted", "ok"), ("Route change", f"{d:+,.0f} km ({d / km0 * 100:+.1f}%)", "warn")]
                else:
                    m = ui.build_map(**kw, original=initial, extra_zone=block, banner=("blocked", "NO CLEAR ALTERNATIVE (DEMO)"))
                    stats = [("Distance", "—", "muted"), ("Flight time", "—", "muted"),
                             ("Status", "No clear path", "warn"), ("Route change", "—", "muted")]
            with ph_map.container():
                ss.draw_n = ss.get("draw_n", 0) + 1
                ui.render_map(m, height=440, key=f"map_demo_{ss.draw_n}")
                ui.stat_cards(stats)
            with ph_steps.container():
                ui.steps(stage)

        if run:
            for stage, pause in ((0, 0.9), (1, 1.5), (2, 1.7)):
                ss.stage = stage
                draw(stage)
                time.sleep(pause)
            ss.stage = 3
        draw(ss.stage)


def page_about():
    ui.top_bar("About FlightPath")
    with st.container(key="card_about_intro"):
        ui.html("""<div class="fp-h1">About FlightPath</div>
        <p class="fp-sub" style="max-width:780px">FlightPath is an educational flight route planning simulator developed as a software-based
        demonstration of intelligent route planning using simulated airspace conditions.</p>""")

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with st.container(key="card_about_pax"):
            ui.html("""<div class="fp-h2">How to use · Passenger Mode</div><ol class="fp-ol">
            <li>Enter departure location.</li><li>Enter destination.</li><li>Click Find Optimal Route.</li>
            <li>Review the simulated route and results.</li></ol>""")
    with c2:
        with st.container(key="card_about_pilot"):
            ui.html("""<div class="fp-h2">How to use · Pilot Mode</div><ol class="fp-ol">
            <li>Configure the route.</li><li>Manage simulated obstacles and restricted zones.</li>
            <li>Adjust simulated flight parameters.</li><li>Explore dynamic rerouting.</li></ol>""")

    with st.container(key="card_about_tech"):
        ui.html("""<div class="fp-h2">Technology</div><div class="fp-tech" style="margin-top:.6rem">
        <span>Python</span><span>Streamlit</span><span>HTML</span><span>CSS</span><span class="core">A* Pathfinding Algorithm</span></div>
        <p class="fp-note" style="margin-top:.8rem">The A* engine is planned core technology. This frontend currently runs on simulated demonstration data.</p>""")

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        with st.container(key="card_about_limits"):
            ui.html("""<div class="fp-h2">Project Limitations</div>
            <p class="fp-sub" style="margin-top:.5rem">Airport locations are real (approximate coordinates), but routes, restricted zones, obstacles and weather are simulated and do not reflect real Pakistani or international airspace. FlightPath uses simulated or hardcoded data. It does not connect to real aviation systems,
            live weather services or air traffic control.</p>
            <p class="fp-sub">It is an educational prototype and is not certified for real-world flight navigation or operational aviation use.</p>""")
    with c4:
        with st.container(key="card_about_credits"):
            members = ""
            if md.TEAM_MEMBERS:
                members = "<dt>Members</dt><dd>" + ", ".join(md.TEAM_MEMBERS) + "</dd>"
            ui.html(f"""<div class="fp-h2">Credits</div><dl class="fp-dl" style="margin-top:.7rem">
            <dt>Project</dt><dd>FlightPath</dd><dt>Team</dt><dd>{md.TEAM_NAME}</dd>{members}
            <dt>Event</dt><dd>SKYBER 2026 — Senior Build-a-Thon</dd>
            <dt>Institution</dt><dd>Sir Syed University of Engineering &amp; Technology (SSUET)</dd></dl>""")
    ui.html('<div class="fp-motto">Think Different. Build Different.</div>')


# --------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------
ui.load_css()
ui.sidebar(ss.page, go)
{"home": page_home, "pilot": page_pilot, "about": page_about}[ss.page]()
