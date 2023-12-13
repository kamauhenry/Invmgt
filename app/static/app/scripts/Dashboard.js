document.addEventListener('DOMContentLoaded', function () {
    function getRandomPastelColor() {
        var hue = Math.floor(Math.random() * 360);
        var pastel = 'hsl(' + hue + ', 100%, 80%)';
        return pastel;
    }
    var barColors = PieData.data.map(() => getRandomPastelColor());
    var barchart = new Chart(
        document.getElementById('barchart').getContext('2d'),
        {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Total Usage',
                    data: chartData.series[0].data,
                    backgroundColor: barColors,
                    borderColor: barColors,
                    borderWidth: 1,
                    hoverOffset: 10,
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            },
            
        }
    );

    // Generate random colors for pie chart
    var pieColors = PieData.data.map(() => getRandomPastelColor());

    var piechart = new Chart(
        document.getElementById('piechart').getContext('2d'),
        {
            type: 'pie',
            data: {
                labels: PieData.labels,
                datasets: [{
                    data: PieData.data,
                    backgroundColor: pieColors,
                    hoverOffset: 25,  // Add a slight hover effect
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                    },
                    title: {
                        display: true,
                        text: 'Inventory Items',
                        font: {
                            size: 30,
                        }
                    }
                },
                tooltips: {
                    callbacks: {
                        label: function (tooltipItem, data) {
                            var dataset = data.datasets[tooltipItem.datasetIndex];
                            var total = dataset.data.reduce(function (previousValue, currentValue) {
                                return previousValue + currentValue;
                            });
                            var currentValue = dataset.data[tooltipItem.index];
                            var percentage = Math.floor(((currentValue / total) * 100) + 0.5);
                            return PieData.labels[tooltipItem.index] + ': ' + currentValue + ' (' + percentage + '%)';
                        }
                    }
                }
            },
        }
    );
});
