// Socket.IO connection and event handlers
class SocketHandler {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.init();
    }

    init() {
        this.connect();
        
        // Auto-reconnect if connection drops
        setInterval(() => {
            if (!this.isConnected && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.connect();
            }
        }, 5000);
    }

    connect() {
        try {
            this.socket = io({
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: 1000
            });

            // Connection events
            this.socket.on('connect', () => {
                console.log('🔗 Connected to NIDS server');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.showConnectionStatus('connected');
                
                // Request initial stats
                this.socket.emit('request_stats');
            });

            this.socket.on('disconnect', () => {
                console.log('🔌 Disconnected from server');
                this.isConnected = false;
                this.showConnectionStatus('disconnected');
            });

            this.socket.on('reconnect_attempt', (attempt) => {
                console.log(`🔄 Reconnection attempt ${attempt}`);
                this.reconnectAttempts = attempt;
                this.showConnectionStatus('reconnecting');
            });

            this.socket.on('reconnect_failed', () => {
                console.error('❌ Failed to reconnect');
                this.showConnectionStatus('failed');
            });

            // Custom events
            this.socket.on('new_alert', (alertData) => {
                this.handleNewAlert(alertData);
            });

            this.socket.on('stats_update', (statsData) => {
                this.handleStatsUpdate(statsData);
            });

            this.socket.on('connected', (data) => {
                console.log('Server:', data.message);
            });

        } catch (error) {
            console.error('Socket connection error:', error);
        }
    }

    showConnectionStatus(status) {
        const statusElement = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-item span:last-child');
        
        if (!statusElement) return;

        switch(status) {
            case 'connected':
                statusElement.style.background = '#00ff88';
                statusElement.style.boxShadow = '0 0 10px #00ff88';
                statusText.textContent = 'System Online';
                break;
            case 'disconnected':
                statusElement.style.background = '#ff4444';
                statusElement.style.boxShadow = '0 0 10px #ff4444';
                statusText.textContent = 'System Offline';
                break;
            case 'reconnecting':
                statusElement.style.background = '#ffaa00';
                statusElement.style.boxShadow = '0 0 10px #ffaa00';
                statusText.textContent = 'Reconnecting...';
                break;
            case 'failed':
                statusElement.style.background = '#ff4444';
                statusElement.style.boxShadow = '0 0 10px #ff4444';
                statusText.textContent = 'Connection Failed';
                break;
        }
    }

    handleNewAlert(alertData) {
        console.log('🚨 New Alert:', alertData);
        
        // Show toast notification
        this.showAlertToast(alertData);
        
        // Update dashboard counters
        this.updateAlertCounters();
        
        // Refresh charts if on dashboard
        if (typeof window.updateCharts === 'function') {
            window.updateCharts();
        }
        
        // Play alert sound (optional)
        this.playAlertSound();
    }

    handleStatsUpdate(statsData) {
        // Update dashboard with new stats
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats(statsData);
        }
    }

    showAlertToast(alertData) {
        const toastContainer = document.getElementById('alert-toast-container');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `alert-toast ${alertData.category.toLowerCase().replace(' ', '-')}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        toast.innerHTML = `
            <div class="alert-header">
                <span class="alert-category">${alertData.category}</span>
                <span class="alert-time">${timestamp}</span>
            </div>
            <div class="alert-message">${alertData.message}</div>
            <div class="alert-ip">Source: ${alertData.src_ip} (${alertData.country})</div>
        `;

        toastContainer.appendChild(toast);

        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideInRight 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }
        }, 8000);

        // Limit to 5 toasts maximum
        const toasts = toastContainer.getElementsByClassName('alert-toast');
        if (toasts.length > 5) {
            toasts[0].remove();
        }
    }

    playAlertSound() {
        // Create a simple beep sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('Audio not supported');
        }
    }

    updateAlertCounters() {
        // This will be implemented in dashboard.js
        if (typeof window.refreshStats === 'function') {
            window.refreshStats();
        }
    }

    // Method to manually send events (for testing)
    emit(event, data) {
        if (this.socket && this.isConnected) {
            this.socket.emit(event, data);
        }
    }

    // Method to listen to events
    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback);
        }
    }
}

// Initialize socket handler when page loads
let socketHandler;
document.addEventListener('DOMContentLoaded', function() {
    socketHandler = new SocketHandler();
    window.socketHandler = socketHandler; // Make available globally
});