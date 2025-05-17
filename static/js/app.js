/**
 * OHADA Comptabilité - Main JavaScript
 * This file contains the main functionality for the application
 */

// JavaScript principal pour l'application

// Initialiser les composants Bootstrap comme l'accordéon pour la FAQ
// Fonction pour afficher/masquer le spinner de chargement
function toggleLoadingSpinner(show) {
    const spinner = document.getElementById('loading-spinner');
    if (!spinner) {
        const spinnerHtml = `
            <div id="loading-spinner" class="position-fixed top-50 start-50 translate-middle" style="z-index: 9999; display: none;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <div class="mt-2 text-primary">Chargement en cours...</div>
            </div>`;
        document.body.insertAdjacentHTML('beforeend', spinnerHtml);
    }
    document.getElementById('loading-spinner').style.display = show ? 'block' : 'none';
}

// Intercepter tous les clics sur les liens et boutons
document.addEventListener('click', function(e) {
    const clickable = e.target.closest('a, button');
    if (clickable && !clickable.hasAttribute('data-no-loading') && !clickable.classList.contains('btn-close')) {
        if (!document.getElementById('loading-spinner')) {
            const spinnerHtml = `
                <div id="loading-spinner" class="position-fixed top-50 start-50 translate-middle" style="z-index: 9999; display: none;">
                    <div class="d-flex flex-column align-items-center bg-dark bg-opacity-75 p-3 rounded">
                        <div class="spinner-border text-light mb-2" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                        <div class="text-light">Chargement en cours...</div>
                    </div>
                </div>`;
            document.body.insertAdjacentHTML('beforeend', spinnerHtml);
        }
        document.getElementById('loading-spinner').style.display = 'block';
    }
});

// Masquer le spinner une fois la page chargée
window.addEventListener('load', function() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Masquer le spinner au chargement initial
    toggleLoadingSpinner(false);
    
    // Initialiser tous les tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialiser tous les popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // S'assurer que l'accordéon de la FAQ fonctionne correctement
    var accordionElement = document.getElementById('faqAccordion');
    if (accordionElement) {
        // L'accordéon est géré automatiquement par Bootstrap 5
        console.log('FAQ accordéon initialisé');
    }
});
// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser l'animation des témoignages
    initTestimonialSlider();

    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    function initTestimonialSlider() {
        const container = document.querySelector('.testimonials-container');
        if (!container) return;

        // Créer le conteneur du slider s'il n'existe pas déjà
        let slider = container.querySelector('.testimonials-slider');
        if (!slider) {
            slider = document.createElement('div');
            slider.className = 'testimonials-slider';
            container.appendChild(slider);
        }

        // Récupérer tous les témoignages
        const testimonials = Array.from(document.querySelectorAll('.testimonial-card'));
        if (!testimonials.length) return;

        // Vider le slider
        slider.innerHTML = '';

        // Ajouter les témoignages originaux
        testimonials.forEach(testimonial => {
            const clone = testimonial.cloneNode(true);
            slider.appendChild(clone);
            testimonial.remove(); // Supprimer l'original
        });

        // Ajouter des clones pour le défilement infini (doubler pour assurer la continuité)
        testimonials.forEach(testimonial => {
            const clone = testimonial.cloneNode(true);
            slider.appendChild(clone);
        });
        
        // Ajouter une troisième série pour garantir un défilement continu
        testimonials.forEach(testimonial => {
            const clone = testimonial.cloneNode(true);
            slider.appendChild(clone);
        });

        let position = 0;
        let animationFrameId = null;
        const speed = 0.8; // Vitesse optimale pour 10 témoignages
        const cardWidth = 430; // Largeur d'une carte + gap
        const totalWidth = testimonials.length * cardWidth;
        
        function animate() {
            position -= speed;
            
            // Réinitialiser position quand le premier groupe de cartes est complètement passé
            if (position <= -totalWidth) {
                // Reset position au début du second groupe
                position = 0;
            }
            
            slider.style.transform = `translateX(${position}px)`;
            animationFrameId = requestAnimationFrame(animate);
        }

        // Démarrer l'animation
        animate();

        // Gestion des événements de survol
        slider.addEventListener('mouseenter', () => {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        });

        slider.addEventListener('mouseleave', () => {
            if (!animationFrameId) {
                animate();
            }
        });
    }

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Toggle dark mode
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        // Check for saved dark mode preference
        const isDarkMode = localStorage.getItem('darkMode') === 'true';

        // Apply saved preference
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }

        // Toggle dark mode on change
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
            }

            // Update chart themes if charts exist
            if (typeof updateChartThemes === 'function') {
                updateChartThemes();
            }
        });
    }

    // Transaction form management
    setupTransactionForm();

    // Account select initialization for search
    initializeAccountSelect();

    // Initialize DataTables if available
    initializeDataTables();

    // Setup file upload preview
    setupFileUploadPreview();

    // Initialize exercise analysis
    initializeAnalysisCharts();
});

/**
 * Setup transaction form functionality
 * Handles dynamic addition of transaction lines and balance calculation
 */
function setupTransactionForm() {
    const transactionForm = document.getElementById('transactionForm');
    if (!transactionForm) return;

    const addLineBtn = document.getElementById('addLineBtn');
    const totalDebitEl = document.getElementById('totalDebit');
    const totalCreditEl = document.getElementById('totalCredit');
    const balanceEl = document.getElementById('balance');

    // Handle adding new transaction lines
    if (addLineBtn) {
        addLineBtn.addEventListener('click', function(e) {
            e.preventDefault();

            const itemsContainer = document.getElementById('transactionItems');
            const itemTemplate = document.querySelector('.transaction-item');
            const newItem = itemTemplate.cloneNode(true);

            // Clear input values
            newItem.querySelectorAll('input').forEach(input => {
                input.value = '';
            });

            // Reset select values
            newItem.querySelectorAll('select').forEach(select => {
                select.selectedIndex = 0;

                // Reinitialize Select2 if used
                if (window.Select2 && select.classList.contains('account-select')) {
                    $(select).select2({
                        theme: 'bootstrap4',
                        width: '100%',
                        placeholder: 'Sélectionner un compte'
                    });
                }
            });

            // Set up event handlers for the new row
            setupTransactionItemEvents(newItem);

            // Add the new item to the container
            itemsContainer.appendChild(newItem);

            // Update transaction balance
            updateTransactionBalance();
        });
    }

    // Setup event handlers for existing transaction items
    document.querySelectorAll('.transaction-item').forEach(item => {
        setupTransactionItemEvents(item);
    });

    // Update initial transaction balance
    updateTransactionBalance();

    // Handle form submission
    transactionForm.addEventListener('submit', function(e) {
        // Check if the transaction is balanced
        const balance = parseFloat(balanceEl.dataset.balance || 0);

        if (Math.abs(balance) > 0.001) {
            e.preventDefault();

            // Show error alert
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
            alertDiv.innerHTML = `
                <strong>Erreur !</strong> La transaction n'est pas équilibrée. 
                La différence est de ${balance.toFixed(2)}.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            transactionForm.prepend(alertDiv);

            // Scroll to top of form
            window.scrollTo({
                top: transactionForm.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    });
}

/**
 * Set up event handlers for a transaction item row
 */
function setupTransactionItemEvents(item) {
    const debitInput = item.querySelector('.debit-input');
    const creditInput = item.querySelector('.credit-input');
    const removeBtn = item.querySelector('.remove-line-btn');

    // Handle debit/credit mutual exclusivity
    if (debitInput && creditInput) {
        debitInput.addEventListener('input', function() {
            if (parseFloat(this.value) > 0) {
                creditInput.value = '';
            }
            updateTransactionBalance();
        });

        creditInput.addEventListener('input', function() {
            if (parseFloat(this.value) > 0) {
                debitInput.value = '';
            }
            updateTransactionBalance();
        });
    }

    // Handle remove button
    if (removeBtn) {
        removeBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Only remove if there are multiple items
            const items = document.querySelectorAll('.transaction-item');
            if (items.length > 1) {
                item.remove();
                updateTransactionBalance();
            } else {
                // Just clear the inputs
                item.querySelectorAll('input').forEach(input => {
                    input.value = '';
                });

                item.querySelectorAll('select').forEach(select => {
                    select.selectedIndex = 0;
                });

                updateTransactionBalance();
            }
        });
    }
}

/**
 * Update transaction balance calculations
 */
function updateTransactionBalance() {
    const items = document.querySelectorAll('.transaction-item');
    const totalDebitEl = document.getElementById('totalDebit');
    const totalCreditEl = document.getElementById('totalCredit');
    const balanceEl = document.getElementById('balance');

    if (!totalDebitEl || !totalCreditEl || !balanceEl) return;

    let totalDebit = 0;
    let totalCredit = 0;

    items.forEach(item => {
        const debitInput = item.querySelector('.debit-input');
        const creditInput = item.querySelector('.credit-input');

        if (debitInput && debitInput.value) {
            totalDebit += parseFloat(debitInput.value) || 0;
        }

        if (creditInput && creditInput.value) {
            totalCredit += parseFloat(creditInput.value) || 0;
        }
    });

    // Update display
    totalDebitEl.textContent = totalDebit.toFixed(2);
    totalCreditEl.textContent = totalCredit.toFixed(2);

    // Calculate balance
    const balance = totalDebit - totalCredit;
    balanceEl.textContent = balance.toFixed(2);
    balanceEl.dataset.balance = balance;

    // Apply styling based on balance
    if (Math.abs(balance) < 0.001) {
        balanceEl.className = 'balance-zero';
        balanceEl.textContent = '0.00';
    } else if (balance > 0) {
        balanceEl.className = 'balance-negative';
    } else {
        balanceEl.className = 'balance-negative';
    }
}

/**
 * Ensure AI section is visible with animation
 */
document.addEventListener('DOMContentLoaded', function() {
    const aiSection = document.getElementById('ai-section');
    if (aiSection) {
        // Add animation class after a short delay
        setTimeout(() => {
            aiSection.classList.add('animated-section');
            aiSection.style.opacity = '1';
            aiSection.style.transform = 'translateY(0)';
        }, 500);
    }
});

/**
 * Initialize account select elements for searching
 */
function initializeAccountSelect() {
    if (typeof $ === 'undefined' || typeof $.fn.select2 === 'undefined') return;

    $('.account-select').each(function() {
        $(this).select2({
            theme: 'bootstrap4',
            width: '100%',
            placeholder: 'Sélectionner un compte',
            ajax: {
                url: '/api/accounts/search',
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        q: params.term || ''
                    };
                },
                processResults: function(data) {
                    return {
                        results: data.results
                    };
                },
                cache: true
            },
            minimumInputLength: 1
        });
    });
}

/**
 * Initialize DataTables if available
 */
function initializeDataTables() {
    if (typeof $ === 'undefined' || typeof $.fn.DataTable === 'undefined') return;

    $('.datatable').each(function() {
        $(this).DataTable({
            responsive: true,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.10.25/i18n/French.json'
            },
            pageLength: 10,
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Tous"]],
            dom: 'Bfrtip',
            buttons: [
                'copy', 'excel', 'pdf', 'print'
            ]
        });
    });
}

/**
 * Setup file upload preview
 */
function setupFileUploadPreview() {
    const fileInput = document.querySelector('.custom-file-input');
    if (!fileInput) return;

    fileInput.addEventListener('change', function() {
        const fileLabel = document.querySelector('.custom-file-label');
        fileLabel.textContent = this.files[0] ? this.files[0].name : 'Choisir un fichier';
    });
}

/**
 * Initialize analysis charts
 */
function initializeAnalysisCharts() {
    // Financial health gauge chart
    const healthGaugeEl = document.getElementById('financialHealthGauge');
    if (healthGaugeEl && typeof Chart !== 'undefined') {
        const score = parseFloat(healthGaugeEl.dataset.score || 0);

        new Chart(healthGaugeEl, {
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
        const scoreText = document.createElement('div');
        scoreText.className = 'position-absolute start-50 top-100 translate-middle';
        scoreText.style.marginTop = '-40px';
        scoreText.innerHTML = `
            <div class="text-center">
                <h3 class="mb-0" style="color: ${getScoreColor(score)}">${score.toFixed(0)}</h3>
                <small class="text-muted">Score de santé</small>
            </div>
        `;

        healthGaugeEl.parentNode.appendChild(scoreText);
    }

    // Income & expenses chart
    const incomeExpensesChartEl = document.getElementById('incomeExpensesChart');
    if (incomeExpensesChartEl && typeof Chart !== 'undefined') {
        const data = JSON.parse(incomeExpensesChartEl.dataset.chartdata || '{}');

        new Chart(incomeExpensesChartEl, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Produits',
                        data: data.income || [],
                        backgroundColor: '#70AD47',
                        borderColor: '#548235',
                        borderWidth: 1
                    },
                    {
                        label: 'Charges',
                        data: data.expenses || [],
                        backgroundColor: '#ED7D31',
                        borderColor: '#C55A11',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
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

    // Balance sheet chart
    const balanceSheetChartEl = document.getElementById('balanceSheetChart');
    if (balanceSheetChartEl && typeof Chart !== 'undefined') {
        const data = JSON.parse(balanceSheetChartEl.dataset.chartdata || '{}');

        new Chart(balanceSheetChartEl, {
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
                        '#4472C4',
                        '#ED7D31',
                        '#70AD47'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
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
}

/**
 * Get color based on score value
 */
function getScoreColor(score) {
    if (score >= 75) return '#70AD47'; // Green
    if (score >= 50) return '#FFBF00'; // Yellow
    if (score >= 25) return '#ED7D31'; // Orange
    return '#C00000'; // Red
}

/**
 * Update chart themes based on dark mode
 */
function updateChartThemes() {
    if (typeof Chart === 'undefined') return;

    const isDarkMode = document.body.classList.contains('dark-mode');

    Chart.defaults.color = isDarkMode ? '#fff' : '#666';
    Chart.defaults.borderColor = isDarkMode ? '#555' : '#ddd';

    // Update all charts
    Chart.instances.forEach(chart => {
        chart.update();
    });
}

/**
 * Confirm action with dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Format currency value
 */
function formatCurrency(amount) {
    return parseFloat(amount).toLocaleString('fr-FR', {
        style: 'currency',
        currency: 'XOF',
        minimumFractionDigits: 2
    });
}

/**
 * Format date value
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}

/**
 * Load document preview
 */
function loadDocumentPreview(documentId, containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    // Show loading indicator
    container.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">Chargement du document...</p></div>';

    // Fetch document preview
    fetch(`/documents/${documentId}/preview`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du chargement du document');
            }
            return response.text();
        })
        .then(html => {
            container.innerHTML = html;
        })
        .catch(error => {
            container.innerHTML = `<div class="alert alert-danger m-3">
                <i class="feather-alert-circle"></i> ${error.message}
            </div>`;
        });
}