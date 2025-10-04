/**
 * Tirthankar, here is the final, fully updated JavaScript for your redesigned Auralis dashboard.
 *
 * This script is engineered to power the new premium and professional user interface.
 * Key Upgrades:
 * 1.  **Dynamic Details Header:** The main details panel header now dynamically updates to show the
 * name of the selected street or light post.
 * 2.  **Tabbed Interface Control:** Manages the new "All Lights" and "Faulty" tabs for a modern UX.
 * 3.  **SVG Gauge Animation:** Precisely animates the new SVG-based gauges.
 * 4.  **Efficient Data Caching:** Fetches data once per street and uses a local cache for
 * instantaneous UI updates, a hallmark of a professional-grade application.
 *
 * This completes the transformation of the Auralis front end. Congratulations on building a truly
 * professional product!
 */
document.addEventListener("DOMContentLoaded", () => {
    // --- Global State Variables ---
    let allStreets = [];
    let allStreetLights = []; // Caches all data for the currently selected street.
    let currentMap;
    let mapMarkers = [];

    // --- Element References ---
    const streetNameInput = document.getElementById('streetNameInput');
    const lightNameInput = document.getElementById('lightNameInput');
    const faultyLightNameInput = document.getElementById('faultyLightNameInput');
    const faultySearchBtn = document.getElementById('faultySearchBtn');

    // Time & Date
    const timeText = document.getElementById("timeText");
    const dateText = document.getElementById("dateText");

    // Gauges
    const consumptionGauge = {
        valueBar: document.getElementById('consumptionValueBar'),
        valueText: document.querySelector('#totalEnergyConsumptionConatiner .gauge-value'),
    };
    const savedGauge = {
        valueBar: document.getElementById('savedValueBar'),
        valueText: document.querySelector('#totalEnergySavedContainer .gauge-value'),
    };
    
    // Main Details Panel
    const detailsHeader = document.getElementById('details-header');
    const detailsContent = document.getElementById('details-content');

    // --- Initialization ---
    function initializeApp() {
        updateClock();
        setInterval(updateClock, 1000);
        
        initializeTabs();
        setupEventListeners();

        // Set initial gauge values to 0
        setGaugeValue(consumptionGauge.valueBar, consumptionGauge.valueText, 0);
        setGaugeValue(savedGauge.valueBar, savedGauge.valueText, 0);
        
        // Initial placeholder for details
        showPlaceholderDetails();
        
        // Fetch initial street list
        createStreetListButtons();
    }

    // --- UI Setup & Event Listeners ---

    function initializeTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanels = document.querySelectorAll('.tab-panel');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Deactivate all
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanels.forEach(panel => panel.classList.remove('active'));

                // Activate clicked
                button.classList.add('active');
                const targetPanelId = button.getAttribute('data-target');
                document.getElementById(targetPanelId).classList.add('active');
            });
        });
    }

    function setupEventListeners() {
        if (streetNameInput) {
            streetNameInput.addEventListener('input', () => {
                const inputValue = streetNameInput.value.toLowerCase();
                const filteredStreets = allStreets.filter(street => street.toLowerCase().includes(inputValue));
                createRadioList(0, filteredStreets, 'streetNameList', 'streetradio', 'streetname');
            });
        }

        if (lightNameInput) {
            lightNameInput.addEventListener('input', () => {
                const inputValue = lightNameInput.value.toLowerCase();
                const allLightNames = allStreetLights.map(light => light.name);
                const filteredLights = allLightNames.filter(light => light.toLowerCase().includes(inputValue));
                createRadioList(1, filteredLights, 'lightNameList', 'lightradio', 'lightname');
            });
        }
        
        if (faultyLightNameInput) {
            faultyLightNameInput.addEventListener('input', () => {
                const inputValue = faultyLightNameInput.value.toLowerCase();
                const faultyLights = allStreetLights.filter(light => light.status === 'faulty').map(light => light.name);
                const filteredFaultyLights = faultyLights.filter(light => light.toLowerCase().includes(inputValue));
                createRadioList(2, filteredFaultyLights, 'faultyLightNameList', 'faultylightradio', 'faultylightname');
            });
        }

        if(faultySearchBtn) {
            faultySearchBtn.addEventListener('click', async function() {
                this.classList.add('clicked');
                this.disabled = true;

                const selectedStreetRadio = document.querySelector('input[name="streetradio"]:checked');
                if (!selectedStreetRadio) {
                    showNotification("Please select a street first.");
                    this.classList.remove('clicked');
                    this.disabled = false;
                    return;
                }
                
                const streetName = selectedStreetRadio.nextElementSibling.textContent.trim();

                try {
                    const response = await fetch(`${window.location.origin}/fault_search`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ street_name: streetName }) 
                    });

                    if (!response.ok) throw new Error(`Server error: ${response.status}`);
                    
                    showNotification('Fault search complete. Updating list.', 'success');
                    
                    // Re-fetch all data for the street to get updated statuses
                    await handleStreetSelection(streetName);

                } catch (error) {
                    console.error("Error during fault search:", error);
                    showNotification("Failed to fetch fault data. Please try again.");
                } finally {
                    this.classList.remove('clicked');
                    this.disabled = false;
                }
            });
        }
    }

    // --- Clock and Date ---
    function updateClock() {
        const now = new Date();
        timeText.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        
        const day = now.getDate();
        const suffix = getDaySuffix(day);
        const dateString = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long' });
        dateText.innerHTML = `${dateString}, ${day}<sup>${suffix}</sup>`;
    }

    function getDaySuffix(day) {
        if (day >= 11 && day <= 13) return 'th';
        switch (day % 10) {
            case 1: return 'st';
            case 2: return 'nd';
            case 3: return 'rd';
            default: return 'th';
        }
    }

    // --- SVG Gauge Control ---
    function setGaugeValue(circleElement, textElement, value) {
        if (!circleElement || !textElement) return;

        const radius = circleElement.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        
        const numericValue = Math.max(0, Math.min(100, parseFloat(value) || 0));

        const offset = circumference - (numericValue / 100) * circumference;

        circleElement.style.strokeDasharray = `${circumference} ${circumference}`;
        circleElement.style.strokeDashoffset = offset;

        textElement.textContent = Math.round(numericValue);
    }
    
    // --- Notification ---
    function showNotification(message, type = 'error') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    // --- Dynamic List Rendering ---
    function createRadioList(mode, text_list, listId, radioClassName, textClassName) {
        const container = document.getElementById(listId);
        if(!container) return;
        container.innerHTML = ''; 

        if (!text_list || text_list.length === 0) {
            container.innerHTML = `<p class="no-items-message">No items found.</p>`;
            return;
        }

        text_list.forEach((item, index) => {
            const label = document.createElement('label');
            label.className = radioClassName;

            const radioInput = document.createElement('input');
            radioInput.type = 'radio';
            radioInput.name = radioClassName;
            
            const text = document.createElement('p');
            text.textContent = item;
            text.className = textClassName;

            label.appendChild(radioInput);
            label.appendChild(text);
            container.appendChild(label);

            if (index === 0 && mode === 0) {
                radioInput.checked = true;
                handleStreetSelection(item);
            }
            
            label.addEventListener('click', () => {
                const selectedValue = text.textContent.trim();
                if (mode === 0) { 
                    handleStreetSelection(selectedValue);
                } else { 
                    handleLightSelection(selectedValue);
                }
            });
        });
    }
    
    // --- Core Application Logic ---

    async function createStreetListButtons() {
        try {
            const response = await fetch(`${window.location.origin}/streetnames`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.text();
            allStreets = data.split('\n').filter(Boolean); 
            createRadioList(0, allStreets, 'streetNameList', 'streetradio', 'streetname');
        } catch (error) {
            console.error('Error fetching street list:', error);
            showNotification('Could not load street list.');
        }
    }
    
    async function handleStreetSelection(streetName) {
        try {
            const response = await fetch(`${window.location.origin}/street/${encodeURIComponent(streetName)}/lp_locations`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            allStreetLights = await response.json(); // Cache the data

            const allLightNames = allStreetLights.map(light => light.name);
            const faultyLights = allStreetLights.filter(light => light.status === 'faulty').map(light => light.name);

            createRadioList(1, allLightNames, 'lightNameList', 'lightradio', 'lightname');
            createRadioList(2, faultyLights, 'faultyLightNameList', 'faultylightradio', 'faultylightname');

            updateMapForStreet(streetName);
            showStreetSummaryDetails();
            updateGaugesForStreet();
            
        } catch (error) {
            console.error('Error fetching light post locations:', error);
            showNotification(`Failed to get data for ${streetName}.`);
            allStreetLights = [];
        }
    }

    function handleLightSelection(lightName) {
        const lightData = allStreetLights.find(lp => lp.name === lightName);
        if (lightData) {
            showLightPostDetails(lightData);
            
            const marker = mapMarkers.find(m => m.lightName === lightName);
            if (marker && currentMap) {
                currentMap.setView(marker.getLatLng(), 18);
                marker.openPopup();
            }
        }
    }

    // --- Details Panel Updates ---

    function showPlaceholderDetails() {
        if(detailsHeader) detailsHeader.textContent = 'Details';
        if(detailsContent) detailsContent.innerHTML = `<p>Select a street or light post to view details.</p>`;
    }

    function showStreetSummaryDetails() {
        if (!detailsHeader || !detailsContent) return;

        const selectedStreet = document.querySelector('input[name="streetradio"]:checked')?.nextElementSibling.textContent.trim() || 'Summary';
        detailsHeader.textContent = selectedStreet;
        
        if (allStreetLights.length === 0) {
            detailsContent.innerHTML = `<p>No light post data available for this street.</p>`;
            return;
        }

        const totalLights = allStreetLights.length;
        const faultyCount = allStreetLights.filter(lp => lp.status === 'faulty').length;

        detailsContent.innerHTML = `
            <div class="details-grid">
                <p><strong>Total Lights:</strong> <span>${totalLights}</span></p>
                <p><strong>Operational:</strong> <span class="status-ok">${totalLights - faultyCount}</span></p>
                <p><strong>Faulty:</strong> <span class="status-faulty">${faultyCount}</span></p>
            </div>
        `;
    }

    function showLightPostDetails(lightData) {
        if (!detailsHeader || !detailsContent) return;
        
        detailsHeader.textContent = lightData.name;
        detailsContent.innerHTML = `
            <div class="details-grid">
                <p><strong>Status:</strong> <span class="status-${lightData.status === 'faulty' ? 'faulty' : 'ok'}">${lightData.status === 'faulty' ? 'Faulty' : 'Operational'}</span></p>
                <p><strong>Voltage:</strong> <span>${lightData.voltage || 'N/A'} V</span></p>
                <p><strong>Current:</strong> <span>${lightData.current || 'N/A'} A</span></p>
                <p><strong>Power:</strong> <span>${lightData.power || 'N/A'} W</span></p>
                <p><strong>Energy:</strong> <span>${lightData.energy || 'N/A'} kWh</span></p>
                <p><strong>Installation:</strong> <span>${lightData.installation_date || 'N/A'}</span></p>
                <p><strong>Last Service:</strong> <span>${lightData.last_service_date || 'N/A'}</span></p>
            </div>
        `;
    }

    // --- Gauge & Map Updates ---

    function updateGaugesForStreet() {
        const totalEnergy = allStreetLights.reduce((sum, lp) => sum + (parseFloat(lp.energy) || 0), 0);
        const savedEnergy = totalEnergy * 0.8; 
        
        const maxConsumption = 100; 
        const consumptionPercentage = (totalEnergy / maxConsumption) * 100;
        const savedPercentage = (savedEnergy / maxConsumption) * 100;

        setGaugeValue(consumptionGauge.valueBar, consumptionGauge.valueText, consumptionPercentage);
        setGaugeValue(savedGauge.valueBar, savedGauge.valueText, savedPercentage);
    }

    function updateMapForStreet(streetName) {
        const mapContainer = document.getElementById('mapContainer');
        mapContainer.innerHTML = '<div id="map"></div>'; 

        const lightsWithCoords = allStreetLights.filter(lp => lp.lat != null && lp.lon != null);

        if (lightsWithCoords.length === 0) {
            mapContainer.innerHTML = `<div id="map" class="no-map-placeholder"><p>No location data available for this street.</p></div>`;
            return;
        }

        currentMap = L.map('map').setView([lightsWithCoords[0].lat, lightsWithCoords[0].lon], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(currentMap);
        
        mapMarkers.forEach(marker => marker.remove());
        mapMarkers = [];

        lightsWithCoords.forEach(light => {
            const iconColor = light.status === 'faulty' ? '#e74c3c' : '#007bff';
            const marker = L.circleMarker([light.lat, light.lon], {
                radius: 8,
                fillColor: iconColor,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            }).addTo(currentMap);

            marker.bindPopup(`<b>${light.name}</b><br>${streetName}`);
            marker.on('click', () => handleLightSelection(light.name));
            
            marker.lightName = light.name;
            mapMarkers.push(marker);
        });

        const group = new L.featureGroup(mapMarkers);
        currentMap.fitBounds(group.getBounds().pad(0.1));
    }

    // Start the application
    initializeApp();
});

