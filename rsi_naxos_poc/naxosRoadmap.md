# RoadSafetyInsights - Development Roadmap - End of July (DEADLINE)

**Project Definition:** A civic tech platform designed to visualize, track, and simulate road safety hazards and accident metrics, transitioning from a web-based proof-of-concept to a fully integrated cross-platform mobile application.

---

## Phase 1: Naxos MVP (Target: End of July)
*Focus: Finalizing the web-based simulation for live demonstration and television broadcast.*

- [x] **Core Map Integration:** Implement OpenStreetMap with OSRM routing for realistic vehicle tracking.
- [x] **Responsive UI:** Glassmorphism overlay with a mobile-responsive bottom sheet.
- [ ] **Sound Notifications (Push):** Integrate browser Web Audio API to trigger alert chimes when a vehicle enters a predefined hazard zone (`radius_meters`).
- [ ] **QR Scanner for Application:** Generate and deploy static QR codes pointing to the live URL to allow live audience interaction during presentations.

---

## Phase 2: Agency Portal & Web Expansion
*Focus: Expanding the web architecture to support multiple administrative users and preparing the data infrastructure.*

- [ ] **Recommended Agencies on Landing Page:** Update the main entry portal (`landing.html`) to highlight collaborating entities (e.g., Municipality of Volos, Hellenic Police).
- [ ] **Agency Login Portal:** Develop a secure backend authentication system (Node.js/Firebase) providing isolated, customized dashboard views for different departments.
- [ ] **Data Overlay (50/50 View):** Build a split-screen or toggle UI allowing agencies to compare live simulation routing against historical accident datasets simultaneously.

---

## Phase 3: Native Mobile Transition (Flutter)
*Focus: Porting the stabilized web application into a native cross-platform mobile app.*

- [ ] **Gradual WebApp -> Flutter Migration:** Rebuild the map view and UI components using `flutter_map` and Dart. Connect the app to the Phase 2 backend API.
- [ ] **Native Push Notifications:** Upgrade from web-based audio alerts to OS-level push notifications for hazard proximity.
- [ ] **VoiceMemo Integration (On/Off):** Utilize native device hardware capabilities to allow municipal workers or drivers to record and pin voice memos to specific geographic coordinates.

---

*Note: This roadmap is a living document. Timelines and features may shift based on external data access approvals and municipal deployment requirements.*
