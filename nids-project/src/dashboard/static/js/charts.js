class ChartManager {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        this.setupChartDefaults();
    }

    setupChartDefaults() {
        Chart.defaults.backgroundColor = 'rgba(0, 255, 255, 0.1)';
        Chart.defaults.borderColor = 'rgba(0, 255, 255, 0.3)';
        Chart.defaults.color = '#ffffff';
        Chart.defaults.font.family = "'Courier New', monospace";
    }

    createCategoriesChart(data) {
        const ctx = document.getElementById('categoriesChart')?.getContext('2d');
        if (!ctx) return;

        if (this.charts.categories) {
            this.charts.categories.destroy();
        }

        const colors = this.getCyberpunkColors(Object.keys(data).length);

        this.charts.categories = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: colors,
                    borderColor: colors.map(color => this.lightenColor(color, 0.3)),
                    borderWidth: 2,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#ffffff',
                            font: {
                                family: "'Courier New', monospace",
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10, 10, 10, 0.8)',
                        titleColor: '#00ffff',
                        bodyColor: '#ffffff',
                        borderColor: '#00ffff',
                        borderWidth: 1
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }

    createTimelineChart(data) {
        const ctx = document.getElementById('timelineChart')?.getContext('2d');
        if (!ctx) return;

        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }

        const labels = data.map(item => {
            const date = new Date(item.time);
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        });

        const counts = data.map(item => item.count);

        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Alerts',
                    data: counts,
                    borderColor: '#00ffff',
                    backgroundColor: 'rgba(0, 255, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#00ffff',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10, 10, 10, 0.8)',
                        titleColor: '#00ffff',
                        bodyColor: '#ffffff'
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#b0b0b0',
                            maxTicksLimit: 8
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#b0b0b0'
                        }
                    }
                }
            }
        });
    }

    createProtocolChart(data) {
        const ctx = document.getElementById('protocolChart')?.getContext('2d');
        if (!ctx) return;

        if (this.charts.protocol) {
            this.charts.protocol.destroy();
        }

        const colors = this.getCyberpunkColors(Object.keys(data).length);

        this.charts.protocol = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: colors,
                    borderColor: colors.map(color => this.lightenColor(color, 0.3)),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            font: {
                                size: 10
                            }
                        }
                    }
                }
            }
        });
    }

    updateCharts(statsData) {
        if (statsData.category_count) {
            this.createCategoriesChart(statsData.category_count);
        }
        
        if (statsData.alerts_over_time) {
            this.createTimelineChart(statsData.alerts_over_time);
        }
        
        if (statsData.protocol_distribution) {
            this.createProtocolChart(statsData.protocol_distribution);
        }
    }

    getCyberpunkColors(count) {
        const baseColors = [
            '#00ffff', '#ff00ff', '#ffff00', '#00ff88', 
            '#ff4444', '#ffaa00', '#8844ff', '#ff8844'
        ];
        
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        return colors;
    }

    lightenColor(color, factor) {
        return color.replace(/^#/, '').replace(/../g, 
            color => ('0' + Math.min(255, Math.max(0, parseInt(color, 16) + 255 * factor)).toString(16)).substr(-2)
        );
    }

    destroyAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

let chartManager;
function initializeCharts() {
    chartManager = new ChartManager();
    window.chartManager = chartManager;
}

function updateCharts() {
    if (chartManager) {
        fetch('/api/stats')
            .then(response => response.json())
            .then(statsData => {
                chartManager.updateCharts(statsData);
            })
            .catch(error => console.error('Error updating charts:', error));
    }
}

window.initializeCharts = initializeCharts;
window.updateCharts = updateCharts;