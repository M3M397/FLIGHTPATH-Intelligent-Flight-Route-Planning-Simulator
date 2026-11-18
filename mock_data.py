"""FLIGHTPATH - airports, simulated environment and route planning.

Airport locations are real (approximate coordinates for Pakistan and major world hubs).
Everything else - routes, restricted zones, obstacles and weather - is simulated.
`plan_route()` uses the implemented A* algorithm to calculate optimized routes while
preserving the return shape consumed by app.py.

The simulated environment (weather, restricted airspace, obstacles) is defined once in
structured tables below (`_COUNTRY_ENV`, `_OCEAN_WEATHER`). The map markers, hover
popups and nearby-conditions panel read the same items via `all_env()`.
"""
