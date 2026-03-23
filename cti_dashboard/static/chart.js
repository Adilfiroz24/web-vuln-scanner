fetch('/data')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Malicious',
                        data: data.malicious,
                        borderColor: 'red',
                        backgroundColor: 'rgba(255,0,0,0.1)',
                        tension: 0.1
                    },
                    {
                        label: 'Benign',
                        data: data.benign,
                        borderColor: 'green',
                        backgroundColor: 'rgba(0,255,0,0.1)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });