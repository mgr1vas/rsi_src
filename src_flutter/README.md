# RoadSafetyInsights (RSI) - Naxos Mobile Application

A cross-platform mobile implementation of the **Road Safety Insights (RSI) Naxos Proof of Concept (PoC)** built using the Flutter framework. This application ports the original static simulation logic into a responsive, native mobile ecosystem for iOS and Android devices.

The system parses localized hazard zones from geographic datasets, projects actual road navigation paths using real-world routing engine calculations, and actively triggers predictive audio-visual warnings when a user's coordinate path intersects hazardous roadway areas.

---

## 📱 Application Overview & Architecture

To support the migration from simulated navigation models to real-time physical sensor inputs, the project follows a decoupled, layered architectural pattern:

*   **`lib/models/`**: Defines strict, type-safe structures for handling geographic feature sets (GeoJSON) and local Naxos coordinate lookups.
*   **`lib/services/`**: Isolates data collection mechanics. It currently reads static local asset data and communicates with public OSRM mapping servers, making it easy to swap these endpoints for live IoT streams later without refactoring the UI layout.
*   **`lib/screens/`**: Houses the responsive user interface. Utilizes a full-screen mapping stack overlay layered with an edge-sliding drawer control panel to maximize visible map real estate on compact mobile screens.

---

## 🛠️ Project File Structure

```text
src_flutter/
│
├── assets/
│   └── data/
│       └── naxos_hazards.geojson       # Local municipal hazard zone data coordinates
│
├── pubspec.yaml                        # Third-party dependencies & asset declarations
│
└── lib/
    ├── main.dart                       # Global application execution entry point
    │
    ├── models/
    │   ├── hazard_model.dart           # Strict data parser for GeoJSON feature sets
    │   └── routes_data.dart            # Standard waypoint dataset maps for Naxos nodes
    │
    ├── services/
    │   ├── data_service.dart           # Local filesystem platform asset loader
    │   └── osrm_service.dart           # Real road trajectory generator querying OSRM APIs
    │
    └── screens/
        └── live_tracking_screen.dart   # Interactive full-screen map & responsive tracking dashboard
