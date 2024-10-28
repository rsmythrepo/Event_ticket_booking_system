document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-toggle="modal"]').forEach(button => {
        button.addEventListener('click', function () {
            const index = this.getAttribute('data-event-id');
            fetch(`/admin/event_sales/${index}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const ticketSalesLabels = data.ticket_sales_labels;
                    const ticketSalesData = data.ticket_sales_data;
                    const revenueData = data.revenue_data;
                    const ctxTickets = document.getElementById('ticketsChart' + index).getContext('2d');
                    const ticketsChart = new Chart(ctxTickets, {
                        type: 'line',
                        data: {
                            labels: ticketSalesLabels,
                            datasets: [{
                                label: 'Tickets Sold',
                                data: ticketSalesData,
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: {
                                    beginAtZero: true
                                },
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                    const ctxRevenue = document.getElementById('revenueChart' + index).getContext('2d');
                    const revenueChart = new Chart(ctxRevenue, {
                        type: 'line',
                        data: {
                            labels: ticketSalesLabels,
                            datasets: [{
                                label: 'Revenue Generated',
                                data: revenueData,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: {
                                    beginAtZero: true
                                },
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                })
                .catch(error => {
                    console.error('Error fetching event sales data:', error);
                });
        });
    });
});
