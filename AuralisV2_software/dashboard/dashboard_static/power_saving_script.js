document.addEventListener('DOMContentLoaded', () => {
    // --- 1. SELECT ELEMENTS & DEFINE STATE ---
    let socket;
    const powerSaveButton = document.getElementById('openPowerSaveModalBtn');
    const powerControlWindow = document.getElementById('powerControlWindow');
    const closePowerControlBtn = document.getElementById('closePowerControlBtn');
    const streetListContainer = document.getElementById('street-power-list');
    const loaderBar = document.getElementById('power-saving-bar');
    const percentageText = document.getElementById('power-save-percentage');

    // --- 2. SOCKET.IO SETUP ---
    function initializeSocketIO() {
        try {
            socket = io();

            socket.on('connect', () => {
                console.log('Auralis Power Control connected to real-time server.');
            });

            socket.on('street_list_updated', () => {
                console.log('Received real-time notification: Street list has changed.');
                fetchAndUpdateUI(); 
                showNotification('Power saving status updated in real-time.', 'info');
            });
            
            socket.on('error', (data) => {
                console.error('Socket.IO Error:', data.message);
                showNotification(`Real-time update error: ${data.message}`, 'error');
            });
        } catch (e) {
            console.error("Socket.IO failed to initialize.", e);
            showNotification('Could not connect to the real-time server.', 'error');
        }
    }

    // --- 3. DYNAMIC RENDERING & CALCULATION ---
    function renderStreetList(streets) {
        if (!streetListContainer) return;
        streetListContainer.innerHTML = '';
        const streetItemsHTML = streets.map(street => {
            const isChecked = street.power_save_mode ? 'checked' : '';
            return `
                <div class="street-power-item" data-street-name="${street.name}">
                    <span class="street-item-name">${street.name}</span>
                    <label class="toggle-switch">
                        <input type="checkbox" ${isChecked}>
                        <span class="slider"></span>
                    </label>
                </div>
            `;
        }).join('');
        streetListContainer.innerHTML = streetItemsHTML;
    }
    
    function calculatePowerSavingPercentage(streets) {
        if (!streets || streets.length === 0) return 0;
        const enabledStreets = streets.filter(street => street.power_save_mode).length;
        return (enabledStreets / streets.length) * 100;
    }

    // --- 4. EVENT HANDLING & API CALLS ---
    powerSaveButton?.addEventListener('click', () => powerControlWindow.classList.add('is-open'));
    closePowerControlBtn?.addEventListener('click', () => powerControlWindow.classList.remove('is-open'));
    powerControlWindow?.addEventListener('click', (event) => {
        if (event.target === powerControlWindow) {
            powerControlWindow.classList.remove('is-open');
        }
    });

    async function updatePowerSaveState(streetName, isEnabled) {
        try {
            const encodedStreetName = encodeURIComponent(streetName);
            const response = await fetch(`/admin/street/${encodedStreetName}/power_save_mode`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ state: isEnabled }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update server.');
            }
            
            console.log(`Successfully requested update for ${streetName} to ${isEnabled}.`);

        } catch (error) {
            console.error('Error updating power save mode:', error);
            showNotification(`Error: ${error.message}`, 'error');
            fetchAndUpdateUI();
        }
    }

    streetListContainer?.addEventListener('change', (event) => {
        if (event.target.matches('input[type="checkbox"]')) {
            const streetItem = event.target.closest('.street-power-item');
            const streetName = streetItem.dataset.streetName;
            const isEnabled = event.target.checked;
            
            updatePowerSaveState(streetName, isEnabled);
        }
    });

    // --- 5. INITIALIZATION & DATA FETCHING ---
    async function fetchAndUpdateUI() {
        try {
            const response = await fetch('/streets/all_details');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const streetsData = await response.json(); 
            
            // This now correctly renders the list every time data is fetched.
            renderStreetList(streetsData);

            const percentage = calculatePowerSavingPercentage(streetsData);
            updatePowerSaving(percentage);

        } catch (error) {
            console.error("Failed to fetch or render street list:", error);
            if (streetListContainer) {
                streetListContainer.innerHTML = '<div class="error-message">Could not load street data.</div>';
            }
        }
    }

    async function initializePowerControls() {
        initializeSocketIO();
        await fetchAndUpdateUI();
    }
    
    initializePowerControls();

    // --- 6. HELPER FUNCTIONS ---
    const showNotification = window.showNotification || ((message, type) => console.log(`[${type}] ${message}`));

    function updatePowerSaving(targetPercentage, duration = 1500) {
        if (!loaderBar || !percentageText) return;
        const clampedTarget = Math.max(0, Math.min(100, targetPercentage));
        const startWidth = parseFloat(loaderBar.style.width) || 0;
        let startTime = null;

        function animationStep(currentTime) {
            if (!startTime) startTime = currentTime;
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            const currentPercentage = startWidth + (clampedTarget - startWidth) * progress;
            
            loaderBar.style.width = `${currentPercentage}%`;
            percentageText.textContent = `${Math.round(currentPercentage)}%`;
            
            if (progress < 1) {
                requestAnimationFrame(animationStep);
            }
        }
        requestAnimationFrame(animationStep);
    }
});