document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const startSelect = document.getElementById('start-point');
    const endSelect = document.getElementById('end-point');
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');
    const statusText = document.getElementById('status-text');
    const systemStatus = document.getElementById('system-status');
    const routeNameDisplay = document.getElementById('route-name');
    const alertPopup = document.getElementById('alert-popup');
    
    // Tabs Elements
    const btnTabLive = document.getElementById('btn-tab-live');
    const btnTabStats = document.getElementById('btn-tab-stats');
    const tabLive = document.getElementById('tab-live');
    const tabStats = document.getElementById('tab-stats');

    // 1. Initialize Map
    const map = L.map('real-map', { 
        zoomControl: false,
        minZoom: 11, 
        maxBounds: [[36.9000, 25.3000], [37.2500, 25.6500]]
    }).setView([37.0800, 25.4500], 12);
    
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    }).addTo(map);

    // 2. Load Hazards IMMEDIATELY
    let globalHazards = [];
    fetch('naxos_hazards.geojson')
        .then(res => {
            if (!res.ok) throw new Error("File not found");
            return res.json();
        })
        .then(data => {
            globalHazards = data.features;
            globalHazards.forEach(hazard => {
                const coords = [hazard.geometry.coordinates[1], hazard.geometry.coordinates[0]];
                L.circle(coords, { 
                    color: '#f97316',
                    fillColor: '#f97316', 
                    fillOpacity: 0.35, 
                    radius: hazard.properties.radius_meters, weight: 2, dashArray: '5, 5'
                }).addTo(map);
            });
        }).catch(err => console.error("Error loading hazards on boot: ", err));

    // 3. THE MASTER ROUTES DATABASE
    const routesData = {
        // --- CHORA (PORT) ---
        "Chora-AgiosProkopios": [[37.1004, 25.3775], [37.0850, 25.3650], [37.0750, 25.3550]],
        "Chora-Plaka": [[37.1004, 25.3775], [37.0750, 25.3550], [37.0500, 25.3650], [37.0350, 25.3750]],
        "Chora-Halki": [[37.1004, 25.3775], [37.0850, 25.4050], [37.0650, 25.4500]],
        "Chora-Filoti": [[37.1004, 25.3775], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965]],
        "Chora-Apiranthos": [[37.1004, 25.3775], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965], [37.0600, 25.5100], [37.0720, 25.5200]],
        "Chora-Moutsouna": [[37.1004, 25.3775], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965], [37.0600, 25.5100], [37.0720, 25.5200], [37.0750, 25.5500], [37.0780, 25.5840]],
        "Chora-Koronos": [[37.1004, 25.3775], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965], [37.0600, 25.5100], [37.0720, 25.5200], [37.0900, 25.5250], [37.1140, 25.5320]],
        "Chora-Apollonas": [[37.1004, 25.3775], [37.1200, 25.4200], [37.1600, 25.5000], [37.1850, 25.5500]],

        // --- AGIOS PROKOPIOS ---
        "AgiosProkopios-Chora": [[37.0750, 25.3550], [37.0850, 25.3650], [37.1004, 25.3775]],
        "AgiosProkopios-Plaka": [[37.0750, 25.3550], [37.0500, 25.3650], [37.0350, 25.3750]],
        "AgiosProkopios-Halki": [[37.0750, 25.3550], [37.0850, 25.3650], [37.1004, 25.3775], [37.0850, 25.4050], [37.0650, 25.4500]],
        "AgiosProkopios-Filoti": [[37.0750, 25.3550], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965]],
        "AgiosProkopios-Apiranthos": [[37.0750, 25.3550], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965], [37.0600, 25.5100], [37.0720, 25.5200]],
        "AgiosProkopios-Moutsouna": [[37.0750, 25.3550], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965], [37.0750, 25.5500], [37.0780, 25.5840]],
        "AgiosProkopios-Koronos": [[37.0750, 25.3550], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965], [37.1140, 25.5320]],
        "AgiosProkopios-Apollonas": [[37.0750, 25.3550], [37.0850, 25.4050], [37.0650, 25.4500], [37.1850, 25.5500]],

        // --- PLAKA ---
        "Plaka-Chora": [[37.0350, 25.3750], [37.0500, 25.3650], [37.0750, 25.3550], [37.1004, 25.3775]],
        "Plaka-AgiosProkopios": [[37.0350, 25.3750], [37.0500, 25.3650], [37.0750, 25.3550]],
        "Plaka-Halki": [[37.0350, 25.3750], [37.0600, 25.3800], [37.0650, 25.4500]],
        "Plaka-Filoti": [[37.0350, 25.3750], [37.0600, 25.3800], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965]],
        "Plaka-Apiranthos": [[37.0350, 25.3750], [37.0600, 25.3800], [37.0850, 25.4050], [37.0650, 25.4500], [37.0520, 25.4965], [37.0720, 25.5200]],
        "Plaka-Moutsouna": [[37.0350, 25.3750], [37.0600, 25.3800], [37.0850, 25.4050], [37.0780, 25.5840]],
        "Plaka-Koronos": [[37.0350, 25.3750], [37.1140, 25.5320]],
        "Plaka-Apollonas": [[37.0350, 25.3750], [37.1850, 25.5500]],

        // --- HALKI ---
        "Halki-Chora": [[37.0650, 25.4500], [37.0850, 25.4050], [37.1004, 25.3775]],
        "Halki-AgiosProkopios": [[37.0650, 25.4500], [37.0750, 25.3550]],
        "Halki-Plaka": [[37.0650, 25.4500], [37.0350, 25.3750]],
        "Halki-Filoti": [[37.0650, 25.4500], [37.0520, 25.4965]],
        "Halki-Apiranthos": [[37.0650, 25.4500], [37.0520, 25.4965], [37.0720, 25.5200]],
        "Halki-Moutsouna": [[37.0650, 25.4500], [37.0520, 25.4965], [37.0780, 25.5840]],
        "Halki-Koronos": [[37.0650, 25.4500], [37.1140, 25.5320]],
        "Halki-Apollonas": [[37.0650, 25.4500], [37.1850, 25.5500]],

        // --- FILOTI ---
        "Filoti-Chora": [[37.0520, 25.4965], [37.0650, 25.4500], [37.0850, 25.4050], [37.1004, 25.3775]],
        "Filoti-AgiosProkopios": [[37.0520, 25.4965], [37.0750, 25.3550]],
        "Filoti-Plaka": [[37.0520, 25.4965], [37.0350, 25.3750]],
        "Filoti-Halki": [[37.0520, 25.4965], [37.0650, 25.4500]],
        "Filoti-Apiranthos": [[37.0520, 25.4965], [37.0600, 25.5100], [37.0720, 25.5200]],
        "Filoti-Moutsouna": [[37.0520, 25.4965], [37.0780, 25.5840]],
        "Filoti-Koronos": [[37.0520, 25.4965], [37.1140, 25.5320]],
        "Filoti-Apollonas": [[37.0520, 25.4965], [37.1850, 25.5500]],

        // --- APIRANTHOS ---
        "Apiranthos-Chora": [[37.0720, 25.5200], [37.0520, 25.4965], [37.1004, 25.3775]],
        "Apiranthos-AgiosProkopios": [[37.0720, 25.5200], [37.0750, 25.3550]],
        "Apiranthos-Plaka": [[37.0720, 25.5200], [37.0350, 25.3750]],
        "Apiranthos-Halki": [[37.0720, 25.5200], [37.0650, 25.4500]],
        "Apiranthos-Filoti": [[37.0720, 25.5200], [37.0520, 25.4965]],
        "Apiranthos-Moutsouna": [[37.0720, 25.5200], [37.0780, 25.5840]],
        "Apiranthos-Koronos": [[37.0720, 25.5200], [37.1140, 25.5320]],
        "Apiranthos-Apollonas": [[37.0720, 25.5200], [37.1850, 25.5500]],

        // --- MOUTSOUNA ---
        "Moutsouna-Chora": [[37.0780, 25.5840], [37.1004, 25.3775]],
        "Moutsouna-AgiosProkopios": [[37.0780, 25.5840], [37.0750, 25.3550]],
        "Moutsouna-Plaka": [[37.0780, 25.5840], [37.0350, 25.3750]],
        "Moutsouna-Halki": [[37.0780, 25.5840], [37.0650, 25.4500]],
        "Moutsouna-Filoti": [[37.0780, 25.5840], [37.0520, 25.4965]],
        "Moutsouna-Apiranthos": [[37.0780, 25.5840], [37.0720, 25.5200]],
        "Moutsouna-Koronos": [[37.0780, 25.5840], [37.1140, 25.5320]],
        "Moutsouna-Apollonas": [[37.0780, 25.5840], [37.1850, 25.5500]],

        // --- KORONOS ---
        "Koronos-Chora": [[37.1140, 25.5320], [37.1004, 25.3775]],
        "Koronos-AgiosProkopios": [[37.1140, 25.5320], [37.0750, 25.3550]],
        "Koronos-Plaka": [[37.1140, 25.5320], [37.0350, 25.3750]],
        "Koronos-Halki": [[37.1140, 25.5320], [37.0650, 25.4500]],
        "Koronos-Filoti": [[37.1140, 25.5320], [37.0520, 25.4965]],
        "Koronos-Apiranthos": [[37.1140, 25.5320], [37.0720, 25.5200]],
        "Koronos-Moutsouna": [[37.1140, 25.5320], [37.0780, 25.5840]],
        "Koronos-Apollonas": [[37.1140, 25.5320], [37.1850, 25.5500]],

        // --- APOLLONAS ---
        "Apollonas-Chora": [[37.1850, 25.5500], [37.1004, 25.3775]],
        "Apollonas-AgiosProkopios": [[37.1850, 25.5500], [37.0750, 25.3550]],
        "Apollonas-Plaka": [[37.1850, 25.5500], [37.0350, 25.3750]],
        "Apollonas-Halki": [[37.1850, 25.5500], [37.0650, 25.4500]],
        "Apollonas-Filoti": [[37.1850, 25.5500], [37.0520, 25.4965]],
        "Apollonas-Apiranthos": [[37.1850, 25.5500], [37.0720, 25.5200]],
        "Apollonas-Moutsouna": [[37.1850, 25.5500], [37.0780, 25.5840]],
        "Apollonas-Koronos": [[37.1850, 25.5500], [37.1140, 25.5320]]
    };

    let currentRouteLine = null;
    let vehicleMarker = null;
    let animationFrameId;
    
    let isPaused = false;
    let savedProgress = 0;
    let currentAnimationStartTime = null;

    btnTabLive.addEventListener('click', () => {
        btnTabLive.classList.add('active'); btnTabStats.classList.remove('active');
        tabLive.classList.remove('hidden'); tabLive.classList.add('active-tab');
        tabStats.classList.add('hidden'); tabStats.classList.remove('active-tab');
    });
    btnTabStats.addEventListener('click', () => {
        btnTabStats.classList.add('active'); btnTabLive.classList.remove('active');
        tabStats.classList.remove('hidden'); tabStats.classList.add('active-tab');
        tabLive.classList.add('hidden'); tabLive.classList.remove('active-tab');
    });

    pauseBtn.addEventListener('click', () => {
        isPaused = !isPaused;
        if (isPaused) {
            pauseBtn.innerText = 'Συνέχιση Προσομοίωσης';
            pauseBtn.style.backgroundColor = '#f97316'; 
            pauseBtn.style.color = '#fff';
            statusText.innerText = 'Σε Παύση - Ανάλυση Δεδομένων';
        } else {
            pauseBtn.innerText = 'Παύση Προσομοίωσης';
            pauseBtn.style.backgroundColor = 'transparent';
            pauseBtn.style.color = '#ea580c';
            statusText.innerText = 'Ενεργό - Σε παρακολούθηση';
            currentAnimationStartTime = null; 
        }
    });

    document.getElementById('btn-understand').addEventListener('click', () => {
        alertPopup.classList.add('hidden');
    });

    function clearMap() {
        if (currentRouteLine) map.removeLayer(currentRouteLine);
        if (vehicleMarker) map.removeLayer(vehicleMarker);
        alertPopup.classList.add('hidden');
        cancelAnimationFrame(animationFrameId);
        pauseBtn.classList.add('hidden');
        isPaused = false;
    }

    function animateVehicle(pathCoords, hazards) {
        currentAnimationStartTime = null;
        savedProgress = 0;
        isPaused = false;
        
        pauseBtn.classList.remove('hidden');
        pauseBtn.innerText = 'Παύση Προσομοίωσης';
        pauseBtn.style.backgroundColor = 'transparent';
        pauseBtn.style.color = '#ea580c'; 

        const duration = 18000; 
        
        function step(timestamp) {
            if (isPaused) {
                currentAnimationStartTime = null; 
                animationFrameId = requestAnimationFrame(step);
                return;
            }

            if (!currentAnimationStartTime) {
                currentAnimationStartTime = timestamp - (savedProgress * duration);
            }

            const progress = (timestamp - currentAnimationStartTime) / duration;
            savedProgress = progress;

            if (progress < 1) {
                const index = Math.floor(progress * (pathCoords.length - 1));
                const nextIndex = Math.min(index + 1, pathCoords.length - 1);
                const segmentProgress = (progress * (pathCoords.length - 1)) % 1; 
                
                const lat = pathCoords[index][0] + (pathCoords[nextIndex][0] - pathCoords[index][0]) * segmentProgress;
                const lng = pathCoords[index][1] + (pathCoords[nextIndex][1] - pathCoords[index][1]) * segmentProgress;
                
                vehicleMarker.setLatLng([lat, lng]);
                checkHazards([lat, lng], hazards);
                animationFrameId = requestAnimationFrame(step);
            } else {
                statusText.innerText = 'Ολοκλήρωση Διαδρομής';
                systemStatus.className = 'status-indicator safe';
                pauseBtn.classList.add('hidden');
            }
        }
        animationFrameId = requestAnimationFrame(step);
    }

    function checkHazards(currentPos, hazards) {
        let alertTriggered = false;
        const currentLatLng = L.latLng(currentPos);

        hazards.forEach(hazard => {
            const hazardLatLng = L.latLng([hazard.geometry.coordinates[1], hazard.geometry.coordinates[0]]);
            const distanceMeters = currentLatLng.distanceTo(hazardLatLng);
            
            if (distanceMeters < hazard.properties.radius_meters) {
                if (alertPopup.classList.contains('hidden')) {
                    alertPopup.classList.remove('hidden');
                    document.getElementById('popup-hazard-name').innerText = hazard.properties.hazard_type;
                    document.getElementById('popup-weather').innerText = hazard.properties.weather_factor;
                    document.getElementById('popup-total').innerText = hazard.properties.total_accidents;
                    document.getElementById('popup-recent').innerText = hazard.properties.recent_accidents;
                    // Removed the assignment to the popup-action ID
                }
                
                if (!isPaused) {
                    systemStatus.className = 'status-indicator danger';
                    statusText.innerText = 'ΚΙΝΔΥΝΟΣ - ΕΝΕΡΓΗ ΕΙΔΟΠΟΙΗΣΗ';
                }
                alertTriggered = true;
            }
        });

        if (!alertTriggered && !alertPopup.classList.contains('hidden')) {
            alertPopup.classList.add('hidden');
            if (!isPaused) {
                systemStatus.className = 'status-indicator safe';
                statusText.innerText = 'Ενεργό - Σε παρακολούθηση';
            }
        }
    }

    startBtn.addEventListener('click', () => {
        clearMap();

        const start = startSelect.value;
        const end = endSelect.value;
        const routeKey = `${start}-${end}`;

        if (start === end) {
            routeNameDisplay.innerText = "Αδύνατη δρομολόγηση.";
            return;
        }

        if (!routesData[routeKey]) {
            routeNameDisplay.innerText = "Διαδρομή εκτός χάρτη.";
            return;
        }

        systemStatus.className = 'status-indicator safe';
        statusText.innerText = 'Υπολογισμός Δεδομένων...';
        routeNameDisplay.innerText = `${startSelect.options[startSelect.selectedIndex].text} -> ${endSelect.options[endSelect.selectedIndex].text}`;
        
        setTimeout(() => {
            const routePath = routesData[routeKey];
            
            currentRouteLine = L.polyline(routePath, { color: '#0284c7', weight: 4, dashArray: '10, 10' }).addTo(map);
            
            map.fitBounds(currentRouteLine.getBounds(), { 
                paddingTopLeft: [400, 50], 
                paddingBottomRight: [50, 50] 
            });

            vehicleMarker = L.circleMarker(routePath[0], { color: '#fff', fillColor: '#38bdf8', fillOpacity: 1, radius: 8, weight: 3 }).addTo(map);
            
            statusText.innerText = 'Ενεργό - Σε παρακολούθηση';
            
            setTimeout(() => animateVehicle(routePath, globalHazards), 800);

        }, 800);
    });

    resetBtn.addEventListener('click', () => {
        clearMap();
        map.setView([37.0800, 25.4500], 12);
        routeNameDisplay.innerText = "Επιλέξτε διαδρομή...";
        systemStatus.className = 'status-indicator safe';
        statusText.innerText = 'Ενεργό - Σε παρακολούθηση';
    });
});