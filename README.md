# FLIGHTPATH — Flight Route Planning Simulator

**Think Different. Build Different.**

A software-based flight route planning simulator developed by **THE OUTLIERS** for SKYBER 2026 — Senior Build-a-Thon at Sir Syed University of Engineering & Technology (SSUET), Karachi.

---

## About the Project

FlightPath is a flight route planning simulator designed to demonstrate how efficient flight routes can be calculated while considering simulated obstacles, restricted airspace and weather conditions.

A direct route between two airports may not always be suitable when environmental restrictions are present. FlightPath addresses this challenge by using the *A (A-star) pathfinding algorithm*\* to find alternative routes around simulated hazards.

The project provides two operating modes: Passenger Mode and Pilot Mode.

## Features

### 1. Passenger Mode

Designed for a simple route-planning experience.

- Select departure and destination airports.
- Calculate an optimized route.
- View the calculated route on an interactive map.
- View simulated route distance and estimated travel time.
- Consider simulated environmental hazards.

### 2. Pilot Mode

Provides additional controls for route configuration and simulation.

- Configure manual waypoints.
- Select route preferences.
- Adjust simulated flight parameters.
- Enable or disable restricted airspace.
- Add and remove simulated obstacles.
- Add and remove restricted zones.
- Observe route changes when environmental conditions change.

### 3. A\* Pathfinding Algorithm

FlightPath uses A\* to search for a route between selected coordinates.

The algorithm:

- Evaluates possible movement paths.
- Uses a heuristic to estimate the remaining distance to the destination.
- Avoids simulated obstacles and active restricted zones.
- Finds an alternative route when the original path becomes unavailable.
- Supports route planning through intermediate waypoints.

Both Passenger Mode and Pilot Mode use the same underlying route-planning engine.

### 4. Interactive Map

- Visualizes departure and destination points.
- Displays calculated flight routes.
- Shows simulated obstacles and restricted zones.
- Supports map interaction, zooming and panning.
- Displays relevant environmental information.

---

## Technology Stack

| Technology    | Purpose                                     |
| ------------- | ------------------------------------------- |
| Python        | Core application logic and pathfinding      |
| Streamlit     | Web application framework                   |
| HTML          | Interactive map component                   |
| CSS           | User interface styling                      |
| JavaScript    | Map interaction and Streamlit communication |
| A\* Algorithm | Route pathfinding and optimization          |

## Project Structure

```text
FLIGHTPATH/
│
├── app.py                  # Main Streamlit application
├── components.py           # Reusable interface and map components
├── mock_data.py            # Simulated airport and environment data
├── world_data.py           # World map geometry and geographic data
├── styles.css              # Application styling
│
├── map_component/
│   └── index.html           # Interactive HTML/JavaScript map
│
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Installation and Setup

### Prerequisites

- Python 3.9 or later
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

### Step 2: Navigate to the Project Directory

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

The application will open in your default browser. If it does not, open the local URL displayed in your terminal.

---

## How It Works

The basic route-planning workflow is:

1. The user selects a departure and destination airport.
2. The application retrieves their simulated coordinates.
3. The route planner receives the coordinates and active environmental restrictions.
4. A\* searches for a valid path while avoiding blocked areas.
5. The application displays the resulting route on the interactive map.
6. When an obstacle or restricted zone changes, the route can be recalculated.

### Dynamic Rerouting Demonstration

One of FlightPath's key demonstrations is dynamic rerouting:

1. Calculate an initial route.
2. Introduce a simulated obstacle or restricted zone across the route.
3. Detect that the original route is blocked.
4. Run the A\* pathfinding algorithm again.
5. Display the alternative route.

---

## Data and Simulation

FlightPath uses predefined, simulated data for its demonstration.

- Airport coordinates
- Simulated obstacles
- Restricted airspace zones
- Weather anomalies
- Flight parameters

The project does not depend on live aviation APIs, external weather services or real-world aviation datasets.

This offline-friendly approach allows the prototype to operate using its local project data.

## Limitations

- Environmental conditions are simulated rather than live.
- Airport information is predefined.
- Flight distance and travel time are estimates based on simulated assumptions.
- Aircraft physics and real-world flight regulations are not modeled.
- The application is not connected to air traffic control systems.
- The prototype is intended for educational demonstration, not actual flight navigation.

---

## AI Tools and Development Assistance

AI tools were used during project development and are disclosed below.

| Tool               | Usage                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------- |
| ChatGPT            | Project management, prompt preparation, research, brainstorming and technical guidance |
| Claude             | Code generation and implementation assistance                                          |
| ChatGPT and Claude | Debugging, troubleshooting and code refinement                                         |

The team reviewed and integrated the AI-assisted work during development.

## Team THE OUTLIERS

All team members participated in research, brainstorming, problem analysis and solution planning.

| Team Member          | Contributions                                    |
| -------------------- | ------------------------------------------------ |
| Muhammad Bazil Meraj | Frontend development and debugging               |
| Shaikh Taha          | Frontend development and debugging               |
| Zainab Jameel        | Backend development and algorithm implementation |
| Hareem Fatima        | Backend development and algorithm implementation |

**Team:** THE OUTLIERS
**Event:** SKYBER 2026 — Senior Build-a-Thon
**Track:** Space, Flight and Communications
**Institution:** Sir Syed University of Engineering & Technology (SSUET), Karachi

---

## Acknowledgements

Developed as part of SKYBER 2026 Senior Build-a-Thon.

**FLIGHTPATH — Smarter Routes Through Intelligent Pathfinding.**

*Think Different. Build Different.*
