/**
 * OHADA Comptabilité - Chart Configuration
 * This file contains configuration for Chart.js charts used in the application
 */

// Set default Chart.js options
if (typeof Chart !== 'undefined') {
    // Set default font family
    Chart.defaults.font.family = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";
    
    // Set default colors
    Chart.defaults.color = '#666';
    
    // Custom OHADA color palette
    const ohadaColors = {
        primary: '#4472C4',
        secondary: '#70AD47',
        warning: '#ED7D31',
        danger: '#C00000',
        info: '#5B9BD5',
        success: '#548235',
        dark: '#2F528F',
        light: '#D9E1F2'
    };
    
    // Check if dark mode is active
    function isDarkMode() {
        return document.body.classList.contains('dark-mode');
    }
    
    // Update chart themes based on dark mode
    function applyChartTheme() {
        if (isDarkMode()) {
            Chart.defaults.color = '#fff';
            Chart.defaults.borderColor = '#555';
        } else {
            Chart.defaults.color = '#666';
            Chart.defaults.borderColor = '#ddd';
        }
        
        // Update all existing charts
        if (Chart.instances) {
            Chart.instances.forEach(chart => {
                chart.update();
            });
        }
    }
    
    // Create financial health gauge chart
    function createFinancialHealthGauge(elementId, score) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        function getScoreColor(value) {
            if (value >= 75) return ohadaColors.success;
            if (value >= 50) return ohadaColors.warning;
            if (value >= 25) return '#FF9800'; // Orange
            return ohadaColors.danger;
        }
        
        // Create doughnut chart as gauge
        const chart = new Chart(element, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [
                        getScoreColor(score),
                        '#e9ecef'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '80%',
                circumference: 180,
                rotation: 270,
                plugins: {
                    tooltip: {
                        enabled: false
                    },
                    legend: {
                        display: false
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: false
                }
            }
        });
        
        // Add score text in the middle
        const ctx = element.getContext('2d');
        ctx.font = 'bold 24px "Segoe UI"';
        ctx.fillStyle = getScoreColor(score);
        ctx.textAlign = 'center';
        ctx.fillText(score.toFixed(0), element.width / 2, element.height * 0.8);
        
        ctx.font = '12px "Segoe UI"';
        ctx.fillStyle = isDarkMode() ? '#fff' : '#666';
        ctx.fillText('Score de santé', element.width / 2, element.height * 0.9);
        
        return chart;
    }
    
    // Create income and expenses chart
    function createIncomeExpensesChart(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        return new Chart(element, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Produits',
                        data: data.income || [],
                        backgroundColor: ohadaColors.success,
                        borderColor: '#548235',
                        borderWidth: 1
                    },
                    {
                        label: 'Charges',
                        data: data.expenses || [],
                        backgroundColor: ohadaColors.warning,
                        borderColor: '#C55A11',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString('fr-FR') + ' XOF';
                            }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Produits et Charges'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                label += ': ' + context.parsed.y.toLocaleString('fr-FR') + ' XOF';
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Create balance sheet chart
    function createBalanceSheetChart(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        return new Chart(element, {
            type: 'pie',
            data: {
                labels: ['Actif', 'Passif', 'Capitaux Propres'],
                datasets: [{
                    data: [
                        data.assets || 0,
                        data.liabilities || 0,
                        data.equity || 0
                    ],
                    backgroundColor: [
                        ohadaColors.primary,
                        ohadaColors.warning,
                        ohadaColors.success
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Structure du Bilan'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed.toLocaleString('fr-FR') + ' XOF';
                                const percentage = context.parsed / context.dataset.data.reduce((a, b) => a + b, 0) * 100;
                                return `${label}: ${value} (${percentage.toFixed(1)}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Create financial ratios chart
    function createFinancialRatiosChart(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        return new Chart(element, {
            type: 'radar',
            data: {
                labels: [
                    'Liquidité',
                    'Solvabilité',
                    'Rentabilité',
                    'Rotation des actifs',
                    'Marge bénéficiaire'
                ],
                datasets: [{
                    label: 'Ratios financiers',
                    data: [
                        data.liquidityRatio || 0,
                        data.solvencyRatio || 0,
                        data.profitabilityRatio || 0,
                        data.assetTurnoverRatio || 0,
                        data.profitMargin || 0
                    ],
                    backgroundColor: 'rgba(68, 114, 196, 0.2)',
                    borderColor: ohadaColors.primary,
                    pointBackgroundColor: ohadaColors.primary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: ohadaColors.primary
                },
                {
                    label: 'Référence du secteur',
                    data: [2, 1, 0.15, 1, 0.1], // Example industry benchmarks
                    backgroundColor: 'rgba(112, 173, 71, 0.2)',
                    borderColor: ohadaColors.success,
                    pointBackgroundColor: ohadaColors.success,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: ohadaColors.success
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        min: 0,
                        ticks: {
                            stepSize: 0.5
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Ratios Financiers'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                label += ': ' + context.raw.toFixed(2);
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Create account distribution chart
    function createAccountDistributionChart(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        return new Chart(element, {
            type: 'polarArea',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: [
                        ohadaColors.primary,
                        ohadaColors.success,
                        ohadaColors.warning,
                        ohadaColors.danger,
                        ohadaColors.info,
                        '#9C27B0', // Purple
                        '#607D8B', // Blue Grey
                        '#795548'  // Brown
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Répartition des Comptes'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw.toLocaleString('fr-FR') + ' XOF';
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = (context.raw / total * 100).toFixed(1) + '%';
                                return `${label}: ${value} (${percentage})`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Create transaction trend chart
    function createTransactionTrendChart(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        return new Chart(element, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Nombre de transactions',
                    data: data.counts || [],
                    borderColor: ohadaColors.primary,
                    backgroundColor: 'rgba(68, 114, 196, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Tendance des Transactions'
                    }
                }
            }
        });
    }
    
    // Export chart functions
    window.ohadaCharts = {
        createFinancialHealthGauge,
        createIncomeExpensesChart,
        createBalanceSheetChart,
        createFinancialRatiosChart,
        createAccountDistributionChart,
        createTransactionTrendChart,
        applyChartTheme,
        colors: ohadaColors
    };
    
    // Apply theme on initial load
    applyChartTheme();
    
    // Listen for dark mode changes
    document.addEventListener('DOMContentLoaded', function() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('change', applyChartTheme);
        }
    });
}
