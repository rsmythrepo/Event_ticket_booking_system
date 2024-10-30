function startSeatPolling(eventId, index) {
    setInterval(() => fetchAvailableSeats(eventId, index), 1000); // fetching every second
}

function fetchAvailableSeats(eventId, index) {
    fetch(`/admin/event_available_seats/${eventId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const seatContainer = document.getElementById(`seat-container${index}`);
            seatContainer.innerHTML = '';

            const cols = 7;
            const seats = data.seats;
            const seatCount = seats.length;
            const rows = Math.ceil(seatCount / cols);

            for (let row = 0; row < rows; row++) {
                const seatRow = document.createElement('div');
                seatRow.className = 'seat-row';

                for (let col = 0; col < cols; col++) {
                    const seatIndex = row * cols + col;
                    if (seatIndex < seatCount) {
                        const seat = seats[seatIndex];
                        const seatDiv = document.createElement('div');
                        seatDiv.className = 'seat';
                        seatDiv.setAttribute('data-seat-number', seat.seat_number);
                        seatDiv.style.margin = '5px';
                        seatDiv.style.cursor = seat.is_available ? 'pointer' : 'not-allowed';
                        seatDiv.style.opacity = seat.is_available ? '1' : '0.5';
                        seatDiv.onclick = seat.is_available ? function() { selectSeat(this); } : null;
                        seatDiv.disabled = !seat.is_available;

                        seatDiv.innerHTML = `<span>${seat.seat_number}</span>`;
                        seatRow.appendChild(seatDiv);
                    } else {
                        const emptySeatDiv = document.createElement('div');
                        emptySeatDiv.className = 'seat';
                        emptySeatDiv.style.margin = '5px';
                        emptySeatDiv.style.cursor = 'not-allowed';
                        emptySeatDiv.style.opacity = '0.3';
                        emptySeatDiv.innerHTML = '<span></span>';
                        seatRow.appendChild(emptySeatDiv);
                    }
                }
                seatContainer.appendChild(seatRow);
            }

            const availableSeatsCount = seats.filter(seat => seat.is_available).length;
            document.getElementById(`availableSeatsCount${index}`).textContent = availableSeatsCount;
        })
        .catch(error => console.error('Error fetching available seats:', error));
}
function initializeCharts() {
    const ticketSalesCtx = document.getElementById('ticketSalesChart').getContext('2d');
    const ticketSalesGradient = ticketSalesCtx.createLinearGradient(0, 0, 0, 400);
    ticketSalesGradient.addColorStop(0, 'rgba(54, 162, 235, 0.8)');
    ticketSalesGradient.addColorStop(1, 'rgba(75, 192, 192, 0.3)');

    const ticketSalesChart = new Chart(ticketSalesCtx, {
        type: 'line',
        data: {
            labels: ticketsSoldChartLabels,
            datasets: [{
                label: 'Tickets Sold',
                data: ticketsSoldChartData,
                backgroundColor: ticketSalesGradient,
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#333'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(54, 162, 235, 0.8)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(200, 200, 200, 0.3)',
                        borderDash: [5, 5]
                    },
                    ticks: {
                        color: '#666'
                    }
                }
            }
        }
    });

    const ctxRevenue = document.getElementById('revenueChart').getContext('2d');
    const gradientRevenue = ctxRevenue.createLinearGradient(0, 0, 0, 400);
    gradientRevenue.addColorStop(0, 'rgba(255, 99, 132, 0.8)');
    gradientRevenue.addColorStop(1, 'rgba(255, 159, 64, 0.3)');

    const revenueChart = new Chart(ctxRevenue, {
        type: 'line',
        data: {
            labels: revenueChartLabels,
            datasets: [{
                label: 'Revenue Generated',
                data: revenueChartData,
                backgroundColor: gradientRevenue,
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: 'rgba(255, 99, 132, 1)',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#333'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 99, 132, 0.8)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(200, 200, 200, 0.3)',
                        borderDash: [5, 5]
                    },
                    ticks: {
                        color: '#666'
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});
