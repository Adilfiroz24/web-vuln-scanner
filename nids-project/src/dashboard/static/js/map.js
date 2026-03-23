class AttackMap {
    constructor() {
        this.map = null;
        this.markers = [];
        this.init();
    }

    init() {
        this.initializeMap();
        this.updateAttackMap();
        
        setInterval(() => {
            this.updateAttackMap();
        }, 30000);
    }

    initializeMap() {
        const mapElement = document.getElementById('attack-map');
        if (!mapElement) return;

        this.map = L.map('attack-map').setView([20, 0], 2);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            className: 'map-tiles'
        }).addTo(this.map);

        this.applyMapTheme();
    }

    applyMapTheme() {
        const style = document.createElement('style');
        style.textContent = `
            .map-tiles {
                filter: invert(1) hue-rotate(180deg) brightness(0.6) contrast(1.2) saturate(0.8);
            }
            .attack-marker {
                border: 2px solid #ff4444;
                border-radius: 50%;
                background: rgba(255, 68, 68, 0.3);
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.2); opacity: 0.7; }
                100% { transform: scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }

    async updateAttackMap() {
        try {
            const response = await fetch('/api/map-data');
            const mapData = await response.json();
            
            this.clearMarkers();
            this.addMarkers(mapData);
            this.fitMapToMarkers();
            
        } catch (error) {
            console.error('Error updating attack map:', error);
        }
    }

    clearMarkers() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    }

    addMarkers(mapData) {
        if (!mapData || mapData.length === 0) {
            this.showNoDataMessage();
            return;
        }

        mapData.forEach(location => {
            if (location.lat && location.lon) {
                const marker = this.createMarker(location);
                this.markers.push(marker);
                marker.addTo(this.map);
            }
        });
    }

    createMarker(location) {
        const severity = this.getSeverityColor(location.count);
        const icon = this.createCustomIcon(severity);
        
        const marker = L.marker([location.lat, location.lon], { icon: icon });
        
        const popupContent = `
            <div class="map-popup">
                <h4>🚨 Attack Detected</h4>
                <p><strong>IP:</strong> ${location.ip}</p>
                <p><strong>Country:</strong> ${location.country}</p>
                <p><strong>Category:</strong> ${location.category}</p>
                <p><strong>Attack Count:</strong> ${location.count}</p>
                <p><strong>Coordinates:</strong> ${location.lat.toFixed(2)}, ${location.lon.toFixed(2)}</p>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        
        marker.on('mouseover', function() {
            this.openPopup();
        });
        
        return marker;
    }

    createCustomIcon(severity) {
        return L.divIcon({
            className: 'attack-marker',
            html: `<div style="
                width: 20px; 
                height: 20px; 
                background: ${severity.color}; 
                border: 2px solid ${severity.border};
                border-radius: 50%;
                box-shadow: 0 0 10px ${severity.color};
            "></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
    }

    getSeverityColor(count) {
        if (count > 10) {
            return { color: '#ff4444', border: '#ff0000' };
        } else if (count > 5) {
            return { color: '#ffaa00', border: '#ff8800' };
        } else {
            return { color: '#ffff00', border: '#ffcc00' };
        }
    }

    fitMapToMarkers() {
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    showNoDataMessage() {
        const mapElement = document.getElementById('attack-map');
        if (mapElement) {
            mapElement.innerHTML = `
                <div style="
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    height: 100%; 
                    color: var(--text-secondary);
                    font-style: italic;
                    text-align: center;
                    padding: 20px;
                ">
                    <div>
                        <i class="fas fa-globe-americas" style="font-size: 48px; margin-bottom: 10px;"></i>
                        <p>No attack data available yet</p>
                        <p style="font-size: 12px;">Attack locations will appear here when detected</p>
                    </div>
                </div>
            `;
        }
    }
}

let attackMap;

function initializeAttackMap() {
    attackMap = new AttackMap();
}

function updateAttackMap() {
    if (attackMap) {
        attackMap.updateAttackMap();
    }
}

window.initializeAttackMap = initializeAttackMap;
window.updateAttackMap = updateAttackMap;