# FLIGHTPATH — Flight Route Planning Simulator

### Think Different. Build Different.

**FLIGHTPATH** is an interactive flight route planning simulator developed by **THE OUTLIERS** for SKYBER 2026 — Senior Build-a-Thon. It demonstrates how efficient flight routes can be calculated, evaluated and adjusted around simulated environmental hazards using the A* pathfinding algorithm.

---

## Project Overview

Flight route planning requires finding suitable routes between departure and destination while considering environmental conditions such as obstacles, restricted airspace and weather anomalies.

FLIGHTPATH provides a simulated environment where users can explore route planning through two operating modes. It calculates optimized routes, displays them on an interactive map and demonstrates how routes can change when environmental restrictions are introduced.

The project is designed as an educational prototype and does not provide real-world aviation navigation.

## Key Features

### 1. Passenger Mode
A simplified interface for users who want to find an optimized flight route.

- Select departure and destination airports.
- Calculate an optimized route.
- View the route on an interactive map.
- See simulated route distance and estimated travel time.
- View relevant environmental hazards around the selected route.

### 2. Pilot Mode
An advanced interface with additional route configuration and simulation controls.

- Configure departure and destination.
- Add manual waypoints.
- Select route preferences.
- Configure simulated flight parameters.
- Enable or disable restricted airspace.
- Add and remove simulated obstacles and restricted zones.
- Compare direct and optimized routes.

### 3. A* Pathfinding Algorithm
FLIGHTPATH uses the A* (A-star) pathfinding algorithm to calculate efficient routes.

The algorithm evaluates possible paths between the selected airports while considering simulated environmental restrictions.

Its purpose is to find a suitable route that avoids active obstacles and restricted zones while maintaining an efficient path.

### 4. Dynamic Route Recalculation
FLIGHTPATH demonstrates dynamic rerouting when environmental conditions affect an existing route.

**Demonstration workflow:**
1. Calculate an initial route.
2. Introduce a simulated obstacle or restricted zone.
3. Check whether the original route is affected.
4. Recalculate an alternative route using A*.
5. Display the alternative route on the map.

### 5. Route Hazard Explanation
This feature explains why an optimized route may be preferred over a direct route.

- Identifies simulated hazards intersecting the direct route.
- Highlights hazards avoided by the optimized route.
- Shows relevant environmental conditions near the optimized route.
- Reports when no clear optimized route is found.

It helps users understand the route-planning result rather than simply viewing a line on the map.

### 6. Interactive Map
The map provides a visual representation of the simulated flight environment.

It displays:
- Departure and destination airports.
- Direct and optimized routes.
- Alternative routes when rerouting occurs.
- Simulated obstacles.
- Restricted airspace.
- Weather anomalies.
- Relevant map information through interactive elements.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic and route planning |
| Streamlit | Application interface |
| HTML | Map component structure |
| CSS | Interface styling |
| JavaScript | Interactive map functionality |
| A* Algorithm | Route pathfinding |

## Project Structure

```text
FLIGHTPATH/
│
├── app.py
├── components.py
├── mock_data.py
├── world_data.py
├── styles.css
├── requirements.txt
├── README.md
│
└── map_component/
    └── index.html
```

### File Description

| File | Description |
|---|---|
| `app.py` | Main Streamlit application and application workflow |
| `components.py` | Reusable interface and map-related components |
| `mock_data.py` | Simulated airports, environmental data and route-planning logic |
| `world_data.py` | World map and geographical visualization data |
| `styles.css` | Application styling |
| `map_component/index.html` | Custom interactive map component |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

---

## Installation and Setup

### Prerequisites

- Python 3.9 or later
- pip package manager
- A code editor such as Visual Studio Code

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

### Step 2: Open the Project Directory

```bash
cd FLIGHTPATH
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser.

---

## How to Use FLIGHTPATH

### Passenger Mode

1. Open the application.
2. Select a departure airport.
3. Select a destination airport.
4. Click **Find Optimal Route**.
5. View the calculated route and simulated flight information.
6. Review the route hazard explanation.

### Pilot Mode

1. Open Pilot Mode.
2. Configure the route and available flight parameters.
3. Adjust simulated obstacles and restricted zones.
4. Calculate or compare routes.
5. Introduce an obstacle or restriction across the existing route.
6. Observe the alternative route generated through A*.
7. Review the route hazard explanation.

---

## Dynamic Rerouting Demonstration

The dynamic rerouting feature demonstrates how a route can be adjusted when environmental conditions change.

| Stage | System Behaviour |
|---|---|
| Initial Planning | Calculates an optimized route |
| Environmental Change | A simulated obstacle or restriction is introduced |
| Route Validation | Checks whether the existing route is affected |
| Recalculation | A* searches for an alternative route |
| Final Display | Shows the updated route on the interactive map |

---

## Simulated Data

FLIGHTPATH uses predefined simulated data for its demonstration.

The simulated environment includes:
- Airport locations.
- Environmental obstacles.
- Restricted airspace zones.
- Weather anomalies.
- Flight parameters.

No external aviation APIs, live weather services, real-time flight tracking or real-world aviation datasets are used.

The application is designed to operate locally without depending on external services.

---

## Limitations

FLIGHTPATH is an educational flight route planning simulator.

- It does not provide real-world flight navigation.
- Environmental information is simulated and predefined.
- Weather conditions are not obtained from live weather services.
- Flight speed, altitude and travel time are simulated.
- It is not connected to air traffic control systems.
- It is not certified for operational aviation use.

---

## AI Tools and Development Assistance

The team used AI tools as development assistants during the project.

| AI Tool | Purpose |
|---|---|
| ChatGPT | Research, brainstorming, project planning and technical guidance |
| Claude | Code generation and implementation assistance |
| ChatGPT and Claude | Debugging, error resolution and code refinement |

AI-generated suggestions and code were reviewed and integrated as part of the team's development process.

---

## Team THE OUTLIERS

**SKYBER 2026 — Senior Build-a-Thon**

| Team Member | Contribution |
|---|---|
| Muhammad Bazil Meraj | Research, brainstorming, frontend development and debugging |
| Shaikh Taha | Research, brainstorming, frontend development and debugging |
| Zainab Jameel | Research, brainstorming, backend development and algorithm implementation |
| Hareem Fatima | Research, brainstorming, backend development and algorithm implementation |

All four team members participated in research, brainstorming, problem analysis and solution planning.

---

## Acknowledgements

Developed for **SKYBER 2026 — Senior Build-a-Thon**, organized at Sir Syed University of Engineering & Technology (SSUET), Karachi.

**Team:** THE OUTLIERS

**Project:** FLIGHTPATH — Flight Route Planning Simulator

**Motto:** Think Different. Build Different.
