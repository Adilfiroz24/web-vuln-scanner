class Dashboard {
    constructor() {
        this.stats = {};
        this.init();
    }

    init() {
        this.loadInitialData();
        this.setupEventListeners();
        this.startAutoRefresh();
        this.updateCurrentTime();
    }

    loadInitialData() {
        this.refreshStats();
        this.loadAlertsTable();
        this.loadAttackersList();
    }

    async refreshStats() {
        try {
            const response = await fetch('/api/stats');
            const statsData = await response.json();
            this.stats = statsData;
            this.updateDashboardStats(statsData);
        } catch (error) {
            console.error('Error refreshing stats:', error);
        }
    }

    updateDashboardStats(statsData) {
        this.stats = statsData;
        
        this.updateCounter('total-alerts', statsData.total_alerts || 0);
        this.updateCounter('port-scans', statsData.category_count?.['Port Scan'] || 0);
        this.updateCounter('syn-floods', statsData.category_count?.['SYN Flood'] || 0);
        this.updateCounter('brute-force', statsData.category_count?.['Brute Force'] || 0);
        this.updateCounter('anomalies', statsData.category_count?.['Anomaly'] || 0);
        
        const activeThreats = Object.values(statsData.category_count || {}).reduce((a, b) => a + b, 0);
        this.updateCounter('active-threats', activeThreats);
        
        this.updateAttackersList(statsData.top_attackers || []);
        
        if (window.chartManager) {
            chartManager.updateCharts(statsData);
        }
        
        if (window.attackMap && statsData.map_data) {
            attackMap.updateAttackMap(statsData.map_data);
        }
    }

    updateCounter(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            this.animateCounter(element, value);
        }
    }

    animateCounter(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const steps = 60;
        const stepValue = (targetValue - currentValue) / steps;
        let currentStep = 0;

        const timer = setInterval(() => {
            currentStep++;
            const newValue = Math.round(currentValue + (stepValue * currentStep));
            element.textContent = newValue.toLocaleString();

            if (currentStep >= steps) {
                element.textContent = targetValue.toLocaleString();
                clearInterval(timer);
            }
        }, duration / steps);
    }

    async loadAlertsTable() {
        try {
            const response = await fetch('/api/alerts?limit=50');
            const alerts = await response.json();
            this.renderAlertsTable(alerts);
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    renderAlertsTable(alerts) {
        const tableBody = document.querySelector('.alerts-table tbody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        alerts.forEach(alert => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${alert.id}</td>
                <td>
                    <span class="alert-badge ${alert.category.toLowerCase().replace(' ', '-')}">
                        ${alert.category}
                    </span>
                </td>
                <td>${alert.message}</td>
                <td>
                    <span class="ip-address">${alert.src_ip}</span>
                    <br>
                    <small class="country-flag">${alert.country}</small>
                </td>
                <td>${new Date(alert.timestamp).toLocaleString()}</td>
                <td>
                    <span class="severity-badge ${alert.severity || 'medium'}">
                        ${alert.severity || 'medium'}
                    </span>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }

    updateAttackersList(attackers) {
        const container = document.getElementById('attackers-list');
        if (!container) return;

        container.innerHTML = '';

        attackers.forEach(attacker => {
            const item = document.createElement('div');
            item.className = 'attacker-item';
            item.innerHTML = `
                <div class="attacker-info">
                    <div class="attacker-ip">${attacker.ip}</div>
                    <div class="attacker-country">${attacker.country}</div>
                </div>
                <div class="attacker-count">${attacker.count}</div>
            `;
            container.appendChild(item);
        });
    }

    loadAttackersList() {
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshStats();
                this.loadAlertsTable();
            });
        }

        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportAlerts();
            });
        }

        const refreshMapBtn = document.getElementById('refresh-map');
        if (refreshMapBtn) {
            refreshMapBtn.addEventListener('click', () => {
                if (window.attackMap) {
                    attackMap.updateAttackMap();
                }
            });
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.refreshStats();
        }, 30000);
    }

    updateCurrentTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const updateTime = () => {
                const now = new Date();
                timeElement.textContent = now.toLocaleTimeString('en-US', {
                    hour12: false,
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            };
            
            updateTime();
            setInterval(updateTime, 1000);
        }
    }

    async exportAlerts() {
        try {
            const response = await fetch('/api/export/alerts');
            const alerts = await response.json();
            
            const blob = new Blob([JSON.stringify(alerts, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `nids-alerts-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting alerts:', error);
            alert('Error exporting alerts. Please try again.');
        }
    }
}

let dashboard;
function initializeDashboard() {
    dashboard = new Dashboard();
    window.dashboard = dashboard;
}

function updateDashboardStats(statsData) {
    if (dashboard) {
        dashboard.updateDashboardStats(statsData);
    }
}

window.initializeDashboard = initializeDashboard;
window.updateDashboardStats = updateDashboardStats;