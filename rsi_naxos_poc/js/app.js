document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const startSelect = document.getElementById('start-point');
    const endSelect = document.getElementById('end-point');
    const startBtn = document.getElementById('start-btn');
    const resetBtn = document.getElementById('reset-btn');
    const statusText = document.getElementById('status-text');
    const systemStatus = document.getElementById('system-status');
    const routeNameDisplay = document.getElementById('route-name');
    const hazardDistance = document.getElementById('hazard-distance');
    
    const alertPopup = document.getElementById('alert-popup');
    const popupHazardName = document.getElementById('popup-hazard-name');
    const popupAction = document.getElementById('popup-action');

    // 1. Initialize Map centered on Greece
    const map = L.map('real-map', { zoomControl: false }).setView([38.5, 23.8], 6);
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // 2. Load Dark Theme Tiles (CARTO)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // 3. Database of City Nodes (Lat, Lng)
    const nodes = {
        "Athens": [37.9838, 23.7275],
        "Thessaloniki": [40.6401, 22.9444],
        "Patras": [38.2466, 21.7346],
        "Larissa": [39.6390, 22.4191],
        "Naxos": [37.1056, 25.3764]
    };

    // Plot Cities on Map
    for (const [city, coords] of Object.entries(nodes)) {
        L.circleMarker(coords, { color: '#3b82f6', radius: 6, fillColor: '#1e293b', fillOpacity: 1, weight: 2 }).addTo(map)
         .bindTooltip(city, { permanent: true, direction: 'right', className: 'city-label', offset: [5, 0] });
    }

    // 4. Predefined Routes Data
    const routesData = {
        "Athens-Thessaloniki": ["Athens", "Larissa", "Thessaloniki"],
        "Thessaloniki-Athens": ["Thessaloniki", "Larissa", "Athens"],
        "Athens-Patras": ["Athens", "Patras"],
        "Patras-Athens": ["Patras", "Athens"],
        "Athens-Naxos": ["Athens", "Naxos"]
    };

    // 5. Database of Hazards
    const globalHazards = [
        { name: "Highway Construction Zone", coords: [39.2, 22.8], radius: 25000, routes: ["Athens-Thessaloniki", "Thessaloniki-Athens"], action: "REDUCE SPEED 80KM/H" },
        { name: "Mountain Pass Blind Spots", coords: [38.6, 23.2], radius: 15000, routes: ["Athens-Thessaloniki", "Thessaloniki-Athens"], action: "CAUTION: LOW VISIBILITY" },
        { name: "Dangerous Crosswinds", coords: [38.1, 22.5], radius: 20000, routes: ["Athens-Patras", "Patras-Athens"], action: "TWO HANDS ON WHEEL" },
        { name: "High ATV Incident Zone", coords: [37.3, 24.5], radius: 30000, routes: ["Athens-Naxos"], action: "WATCH FOR TOURISTS" }
    ];

    let currentRouteLine = null;
    let activeHazardLayers = [];
    let vehicleMarker = null;
    let animationFrameId;

    function clearMap() {
        if (currentRouteLine) map.removeLayer(currentRouteLine);
        if (vehicleMarker) map.removeLayer(vehicleMarker);
        activeHazardLayers.forEach(layer => map.removeLayer(layer));
        activeHazardLayers = [];
        alertPopup.classList.add('hidden');
        cancelAnimationFrame(animationFrameId);
    }

    // Interpolation math to animate car along the line
    function animateVehicle(pathCoords, hazards) {
        let startTime = null;
        const duration = 6000; // Drive takes 6 seconds for demo purposes
        
        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = (timestamp - startTime) / duration;

            if (progress < 1) {
                // Calculate current position
                const index = Math.floor(progress * (pathCoords.length - 1));
                const nextIndex = Math.min(index + 1, pathCoords.length - 1);
                
                // Sub-progress between the two waypoints
                const segmentProgress = (progress * (pathCoords.length - 1)) % 1; 
                
                const lat = pathCoords[index][0] + (pathCoords[nextIndex][0] - pathCoords[index][0]) * segmentProgress;
                const lng = pathCoords[index][1] + (pathCoords[nextIndex][1] - pathCoords[index][1]) * segmentProgress;
                
                vehicleMarker.setLatLng([lat, lng]);

                // Check Hazards
                checkHazards([lat, lng], hazards);

                animationFrameId = requestAnimationFrame(step);
            } else {
                statusText.innerText = 'Destination Reached';
                systemStatus.className = 'status-indicator safe';
                hazardDistance.innerText = 'Trip Complete';
            }
        }
        animationFrameId = requestAnimationFrame(step);
    }

    function checkHazards(currentPos, hazards) {
        let alertTriggered = false;
        const currentLatLng = L.latLng(currentPos);

        hazards.forEach(hazard => {
            const distanceMeters = currentLatLng.distanceTo(hazard.coords);
            
            // If vehicle is inside the hazard radius
            if (distanceMeters < hazard.radius) {
                if (alertPopup.classList.contains('hidden')) {
                    alertPopup.classList.remove('hidden');
                    popupHazardName.innerText = hazard.name;
                    popupAction.innerText = hazard.action;
                }
                
                systemStatus.className = 'status-indicator danger';
                statusText.innerText = 'ALERT ACTIVE';
                hazardDistance.innerText = 'IN HAZARD ZONE';
                alertTriggered = true;
            }
        });

        if (!alertTriggered && !alertPopup.classList.contains('hidden')) {
            alertPopup.classList.add('hidden');
            systemStatus.className = 'status-indicator safe';
            statusText.innerText = 'Monitoring Active';
            hazardDistance.innerText = 'Scanning...';
        }
    }

    startBtn.addEventListener('click', () => {
        const start = startSelect.value;
        const end = endSelect.value;
        const routeKey = `${start}-${end}`;

        clearMap();

        if (start === end) {
            routeNameDisplay.innerText = "Invalid Route";
            return;
        }

        routeNameDisplay.innerText = `${start} to ${end}`;

        // Get Path Coordinates
        const pathCities = routesData[routeKey];
        if (!pathCities) return;
        const pathCoords = pathCities.map(city => nodes[city]);

        // Draw Line
        currentRouteLine = L.polyline(pathCoords, { color: '#3b82f6', weight: 4, dashArray: '10, 10', filter: 'drop-shadow(0 0 5px rgba(59,130,246,0.5))' }).addTo(map);
        map.fitBounds(currentRouteLine.getBounds(), { padding: [100, 100] });

        // Draw Hazards
        const activeHazards = globalHazards.filter(h => h.routes.includes(routeKey));
        activeHazards.forEach(hazard => {
            const circle = L.circle(hazard.coords, {
                color: '#ef4444',
                fillColor: '#ef4444',
                fillOpacity: 0.25,
                radius: hazard.radius,
                weight: 2,
                dashArray: '5, 5'
            }).addTo(map);
            activeHazardLayers.push(circle);
        });

        // Add Vehicle
        vehicleMarker = L.circleMarker(pathCoords[0], { color: '#fff', fillColor: '#3b82f6', fillOpacity: 1, radius: 8, weight: 3 }).addTo(map);
        
        systemStatus.className = 'status-indicator safe';
        statusText.innerText = 'Monitoring Active';
        hazardDistance.innerText = 'Scanning...';

        // Start Driving Animation after a brief pause
        setTimeout(() => animateVehicle(pathCoords, activeHazards), 800);
    });

    resetBtn.addEventListener('click', () => {
        clearMap();
        map.setView([38.5, 23.8], 6);
        routeNameDisplay.innerText = "Select route...";
        systemStatus.className = 'status-indicator safe';
        statusText.innerText = 'Ready to Monitor';
        hazardDistance.innerText = '-- to next threat';
        startSelect.value = "Athens";
        endSelect.value = "Naxos";
    });
});