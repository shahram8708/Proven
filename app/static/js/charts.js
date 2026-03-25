/* ========================================
   Proven — Chart.js Radar Chart Helper
   ======================================== */

/**
 * Initialize a radar chart on a canvas element.
 * @param {string} canvasId - The id of the canvas element.
 * @param {object} data - { labels: [...], values: [...] }
 * @param {object} options - Optional overrides.
 */
function initRadarChart(canvasId, data, options) {
    var canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return null;

    var defaults = {
        labels: data.labels || ['Technical', 'Leadership', 'Strategic', 'Communication', 'Analytical'],
        values: data.values || [0, 0, 0, 0, 0],
        maxValue: data.max || 100,
        fillColor: 'rgba(15, 111, 94, 0.2)',
        borderColor: 'rgba(15, 111, 94, 1)',
        pointColor: 'rgba(15, 111, 94, 1)'
    };

    if (options) {
        Object.keys(options).forEach(function (key) {
            defaults[key] = options[key];
        });
    }

    return new Chart(canvas.getContext('2d'), {
        type: 'radar',
        data: {
            labels: defaults.labels,
            datasets: [{
                label: 'Skills',
                data: defaults.values,
                backgroundColor: defaults.fillColor,
                borderColor: defaults.borderColor,
                borderWidth: 2,
                pointBackgroundColor: defaults.pointColor,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: defaults.maxValue,
                    ticks: {
                        stepSize: defaults.maxValue / 5,
                        display: false
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.06)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.06)'
                    },
                    pointLabels: {
                        font: {
                            family: "'Inter', sans-serif",
                            size: 11,
                            weight: '600'
                        },
                        color: '#0f214f'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#0f214f',
                    titleFont: { family: "'Inter', sans-serif" },
                    bodyFont: { family: "'Inter', sans-serif" },
                    padding: 10,
                    cornerRadius: 6
                }
            }
        }
    });
}

/**
 * Initialize a comparison radar chart with two datasets.
 * @param {string} canvasId
 * @param {object} data1 - { label, values }
 * @param {object} data2 - { label, values }
 * @param {array} labels - dimension labels
 */
function initComparisonRadar(canvasId, data1, data2, labels) {
    var canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return null;

    return new Chart(canvas.getContext('2d'), {
        type: 'radar',
        data: {
            labels: labels || ['Technical', 'Leadership', 'Strategic', 'Communication', 'Analytical'],
            datasets: [
                {
                    label: data1.label || 'You',
                    data: data1.values,
                    backgroundColor: 'rgba(15, 111, 94, 0.2)',
                    borderColor: 'rgba(15, 111, 94, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(15, 111, 94, 1)',
                    pointRadius: 3
                },
                {
                    label: data2.label || 'Average',
                    data: data2.values,
                    backgroundColor: 'rgba(212, 168, 67, 0.15)',
                    borderColor: 'rgba(212, 168, 67, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(212, 168, 67, 1)',
                    pointRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: { display: false },
                    grid: { color: 'rgba(0, 0, 0, 0.06)' },
                    angleLines: { color: 'rgba(0, 0, 0, 0.06)' },
                    pointLabels: {
                        font: { family: "'Inter', sans-serif", size: 11, weight: '600' },
                        color: '#0f214f'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { family: "'Inter', sans-serif", size: 12 },
                        usePointStyle: true,
                        padding: 16
                    }
                }
            }
        }
    });
}
