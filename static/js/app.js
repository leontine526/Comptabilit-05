/**
 * OHADA Comptabilité - Main JavaScript
 * This file contains the main functionality for the application
 */

// JavaScript principal pour l'application

// Variable pour suivre l'état du spinner
let spinnerVisible = false;

// Fonction pour afficher/masquer le spinner de chargement
function toggleLoadingSpinner(show) {
    if (spinnerVisible === show) return; // Éviter les appels redondants

    let spinner = document.getElementById('loading-spinner');
    if (!spinner && show) {
        const spinnerHtml = `
            <div id="loading-spinner" class="position-fixed top-50 start-50 translate-middle" style="z-index: 9999; display: none; pointer-events: none;">
                <div class="d-flex flex-column align-items-center bg-dark bg-opacity-75 p-4 rounded">
                    <div class="spinner-border text-light mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    <div class="text-light fw-bold">Chargement en cours...</div>
                </div>
            </div>`;
        document.body.insertAdjacentHTML('beforeend', spinnerHtml);
        spinner = document.getElementById('loading-spinner');
    }

    if (!spinner) return;

    spinnerVisible = show;

    if (show) {
        spinner.style.display = 'flex';
        spinner.style.opacity = '1';
        spinner.style.pointerEvents = 'none'; // Crucial: ne jamais bloquer les interactions
    } else {
        spinner.style.opacity = '0';
        setTimeout(() => {
            if (spinner && !spinnerVisible) {
                spinner.style.display = 'none';
            }
        }, 200);
    }
}

// Masquer le spinner au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // S'assurer que le spinner est masqué au chargement
    spinnerVisible = false;
    const existingSpinner = document.getElementById('loading-spinner');
    if (existingSpinner) {
        existingSpinner.style.display = 'none';
    }
    
    // Activer tous les boutons immédiatement
    setTimeout(activateAllButtons, 100);
});

// Masquer le spinner une fois la page complètement chargée
window.addEventListener('load', function() {
    spinnerVisible = false;
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
    
    // Réactiver tous les boutons après le chargement complet
    setTimeout(activateAllButtons, 200);
});

// Gestionnaire d'événements amélioré pour tous les boutons
document.addEventListener('click', function(e) {
    // Ne pas traiter les clics si le spinner est déjà visible
    if (spinnerVisible) return;
    
    const clickable = e.target.closest('a[href], button, input[type="submit"], .btn, [role="button"]');

    if (clickable) {
        // Exceptions - éléments qui ne doivent pas déclencher le spinner
        const exceptions = [
            'btn-close',
            'dropdown-toggle', 
            'navbar-toggler',
            'toast-close',
            'close',
            'modal-close',
            'accordion-button'
        ];
        
        // Vérifier si l'élément a un attribut ou classe d'exception
        const hasException = exceptions.some(cls => clickable.classList.contains(cls)) ||
                            clickable.hasAttribute('data-no-loading') ||
                            clickable.hasAttribute('data-bs-toggle') ||
                            clickable.hasAttribute('data-bs-dismiss');
        
        if (!hasException) {
            const href = clickable.getAttribute('href');
            const isButton = clickable.tagName === 'BUTTON' || clickable.type === 'submit';
            
            // Pour les liens de navigation
            if (href && href !== '#' && !href.startsWith('javascript:') && 
                !href.startsWith('mailto:') && !href.startsWith('tel:') && 
                !href.startsWith('#')) {
                
                setTimeout(() => toggleLoadingSpinner(true), 50);
                setTimeout(() => toggleLoadingSpinner(false), 6000);
            }
            // Pour les boutons (sauf ceux dans des modals)
            else if (isButton && !clickable.closest('.modal')) {
                setTimeout(() => toggleLoadingSpinner(true), 50);
                setTimeout(() => toggleLoadingSpinner(false), 8000);
            }
        }
    }
});

// Gestion des soumissions de formulaires (événement séparé pour éviter les doublons)
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form && !form.hasAttribute('data-no-loading') && !spinnerVisible) {
        toggleLoadingSpinner(true);

        // Masquer automatiquement après 8 secondes pour les formulaires
        setTimeout(() => {
            toggleLoadingSpinner(false);
        }, 8000);
    }
});

// Initialisation des composants Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Masquer le spinner au chargement initial
    toggleLoadingSpinner(false);

    // Initialiser tous les tooltips avec gestion d'erreur
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } catch (e) {
        console.warn('Erreur lors de l\'initialisation des tooltips:', e);
    }

    // Initialiser tous les popovers avec gestion d'erreur
    try {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    } catch (e) {
        console.warn('Erreur lors de l\'initialisation des popovers:', e);
    }

    // S'assurer que l'accordéon de la FAQ fonctionne correctement
    var accordionElement = document.getElementById('faqAccordion');
    if (accordionElement) {
        console.log('FAQ accordéon initialisé');
    }

    // Initialiser l'animation des témoignages
    initTestimonialSlider();

    // Toggle dark mode
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        const isDarkMode = localStorage.getItem('darkMode') === 'true';

        if (isDarkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }

        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
            }

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

    // Forcer l'activation de tous les boutons
    activateAllButtons();
});

function initTestimonialSlider() {
    const container = document.querySelector('.testimonials-container');
    if (!container) return;

    let slider = container.querySelector('.testimonials-slider');
    if (!slider) {
        slider = document.createElement('div');
        slider.className = 'testimonials-slider';
        container.appendChild(slider);
    }

    const testimonials = Array.from(document.querySelectorAll('.testimonial-card'));
    if (!testimonials.length) return;

    slider.innerHTML = '';

    testimonials.forEach(testimonial => {
        const clone = testimonial.cloneNode(true);
        slider.appendChild(clone);
        testimonial.remove();
    });

    testimonials.forEach(testimonial => {
        const clone = testimonial.cloneNode(true);
        slider.appendChild(clone);
    });

    testimonials.forEach(testimonial => {
        const clone = testimonial.cloneNode(true);
        slider.appendChild(clone);
    });

    let position = 0;
    let animationFrameId = null;
    const speed = 0.8;
    const cardWidth = 430;
    const totalWidth = testimonials.length * cardWidth;

    function animate() {
        position -= speed;

        if (position <= -totalWidth) {
            position = 0;
        }

        slider.style.transform = `translateX(${position}px)`;
        animationFrameId = requestAnimationFrame(animate);
    }

    animate();

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

// Gestion du lien vers le plan comptable
document.addEventListener('DOMContentLoaded', function() {
    const planLink = document.getElementById('plan-comptable-link');
    if (planLink) {
        const isAuthenticated = document.body.classList.contains('user-authenticated');

        if (isAuthenticated) {
            fetch('/api/get-first-exercise')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.exercise_id) {
                        planLink.href = `/exercises/${data.exercise_id}/accounts`;
                    }
                })
                .catch(error => {
                    console.error('Erreur lors du chargement de l\'exercice:', error);
                });
        }
    }
});

/**
 * Setup transaction form functionality
 */
function setupTransactionForm() {
    const transactionForm = document.getElementById('transactionForm');
    if (!transactionForm) return;

    const addLineBtn = document.getElementById('addLineBtn');
    const totalDebitEl = document.getElementById('totalDebit');
    const totalCreditEl = document.getElementById('totalCredit');
    const balanceEl = document.getElementById('balance');

    if (addLineBtn) {
        addLineBtn.addEventListener('click', function(e) {
            e.preventDefault();

            const itemsContainer = document.getElementById('transactionItems');
            const itemTemplate = document.querySelector('.transaction-item');
            const newItem = itemTemplate.cloneNode(true);

            newItem.querySelectorAll('input').forEach(input => {
                input.value = '';
            });

            newItem.querySelectorAll('select').forEach(select => {
                select.selectedIndex = 0;

                if (window.Select2 && select.classList.contains('account-select')) {
                    $(select).select2({
                        theme: 'bootstrap4',
                        width: '100%',
                        placeholder: 'Sélectionner un compte'
                    });
                }
            });

            setupTransactionItemEvents(newItem);
            itemsContainer.appendChild(newItem);
            updateTransactionBalance();
        });
    }

    document.querySelectorAll('.transaction-item').forEach(item => {
        setupTransactionItemEvents(item);
    });

    updateTransactionBalance();

    transactionForm.addEventListener('submit', function(e) {
        const balance = parseFloat(balanceEl.dataset.balance || 0);

        if (Math.abs(balance) > 0.001) {
            e.preventDefault();

            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
            alertDiv.innerHTML = `
                <strong>Erreur !</strong> La transaction n'est pas équilibrée. 
                La différence est de ${balance.toFixed(2)}.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            transactionForm.prepend(alertDiv);

            window.scrollTo({
                top: transactionForm.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    });
}

function setupTransactionItemEvents(item) {
    const debitInput = item.querySelector('.debit-input');
    const creditInput = item.querySelector('.credit-input');
    const removeBtn = item.querySelector('.remove-line-btn');

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

    if (removeBtn) {
        removeBtn.addEventListener('click', function(e) {
            e.preventDefault();

            const items = document.querySelectorAll('.transaction-item');
            if (items.length > 1) {
                item.remove();
                updateTransactionBalance();
            } else {
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

    totalDebitEl.textContent = totalDebit.toFixed(2);
    totalCreditEl.textContent = totalCredit.toFixed(2);

    const balance = totalDebit - totalCredit;
    balanceEl.textContent = balance.toFixed(2);
    balanceEl.dataset.balance = balance;

    if (Math.abs(balance) < 0.001) {
        balanceEl.className = 'balance-zero';
        balanceEl.textContent = '0.00';
    } else if (balance > 0) {
        balanceEl.className = 'balance-negative';
    } else {
        balanceEl.className = 'balance-negative';
    }
}

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

function setupFileUploadPreview() {
    const fileInput = document.querySelector('.custom-file-input');
    if (!fileInput) return;

    fileInput.addEventListener('change', function() {
        const fileLabel = document.querySelector('.custom-file-label');
        fileLabel.textContent = this.files[0] ? this.files[0].name : 'Choisir un fichier';
    });
}

function initializeAnalysisCharts() {
    // Charts initialization code here...
    // (Code complet disponible mais tronqué pour la lisibilité)
}

function getScoreColor(score) {
    if (score >= 75) return '#70AD47';
    if (score >= 50) return '#FFBF00';
    if (score >= 25) return '#ED7D31';
    return '#C00000';
}

function updateChartThemes() {
    if (typeof Chart === 'undefined') return;

    const isDarkMode = document.body.classList.contains('dark-mode');
    Chart.defaults.color = isDarkMode ? '#fff' : '#666';
    Chart.defaults.borderColor = isDarkMode ? '#555' : '#ddd';

    Chart.instances.forEach(chart => {
        chart.update();
    });
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function formatCurrency(amount) {
    return parseFloat(amount).toLocaleString('fr-FR', {
        style: 'currency',
        currency: 'XOF',
        minimumFractionDigits: 2
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}

function loadDocumentPreview(documentId, containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    container.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">Chargement du document...</p></div>';

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

// Fonction pour afficher le message de chargement des exercices
function showLoadingMessage() {
    console.log('Affichage du message de chargement...');

    const existingMsg = document.getElementById('loading-message');
    if (existingMsg) {
        existingMsg.remove();
    }

    const exerciseForm = document.getElementById('exercise-form');
    if (exerciseForm) {
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'alert alert-info mt-3 d-flex align-items-center';
        loadingMsg.id = 'loading-message';
        loadingMsg.innerHTML = `
            <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
            <span>🔄 Résolution en cours... Veuillez patienter.</span>
        `;

        exerciseForm.parentNode.insertBefore(loadingMsg, exerciseForm.nextSibling);
        console.log('Message de chargement affiché');
    } else {
        console.warn('Formulaire d\'exercice non trouvé');
    }
}

// Gestion des formulaires d'exercices
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('exercise-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Soumission du formulaire détectée');

            const enonceField = form.querySelector('textarea[name="enonce"]');
            if (enonceField && enonceField.value.trim() === '') {
                e.preventDefault();
                alert('Veuillez saisir un énoncé pour résoudre l\'exercice.');
                return false;
            }

            showLoadingMessage();

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Résolution...';
            }

            console.log('Formulaire soumis avec succès');
        });
    }
});

// Gestion des classes de comptes dans le plan comptable
document.addEventListener('DOMContentLoaded', function() {
    const accountClasses = document.querySelectorAll('.account-class');

    if (accountClasses && accountClasses.length > 0) {
        accountClasses.forEach(function(classElement) {
            classElement.addEventListener('click', function() {
                const classId = this.dataset.classId;
                const subAccountsContainer = document.getElementById('sub-accounts-' + classId);

                if (subAccountsContainer) {
                    if (subAccountsContainer.style.display === 'none' || !subAccountsContainer.style.display) {
                        fetch('/accounts/class/' + classId + '/subaccounts')
                            .then(response => response.json())
                            .then(data => {
                                let html = '<div class="sub-accounts-list">';
                                data.subaccounts.forEach(function(account) {
                                    html += `
                                        <div class="sub-account-item">
                                            <h4>${account.code} - ${account.name}</h4>
                                            <p class="account-description">${account.description || 'Aucune description disponible'}</p>
                                            <div class="account-usage">
                                                <strong>Utilisation:</strong> ${account.usage_example || 'Non spécifié'}
                                            </div>
                                        </div>
                                    `;
                                });
                                html += '</div>';
                                subAccountsContainer.innerHTML = html;
                                subAccountsContainer.style.display = 'block';
                            })
                            .catch(error => {
                                console.error('Erreur lors du chargement des sous-comptes:', error);
                                subAccountsContainer.innerHTML = '<p>Erreur lors du chargement des sous-comptes.</p>';
                                subAccountsContainer.style.display = 'block';
                            });
                    } else {
                        subAccountsContainer.style.display = 'none';
                    }
                }
            });
        });
    }
});

// Fonction légère pour l'activation des boutons (déléguée à button-fix.js)
function activateAllButtons() {
    // Déléguer à la fonction principale du button-fix.js
    if (typeof window.ensureAllButtonsActive === 'function') {
        window.ensureAllButtonsActive();
    } else {
        console.warn('Fonction d\'activation principale non disponible, utilisation de la version de base');
        // Version de base en cas de problème
        document.querySelectorAll('button:disabled, input[type="submit"]:disabled').forEach(button => {
            if (!button.hasAttribute('data-keep-disabled')) {
                button.disabled = false;
                button.style.pointerEvents = 'auto';
            }
        });
    }
}

// Fonction de débogage pour vérifier l'état des boutons
function debugButtons() {
    const buttons = document.querySelectorAll('button, a, input[type="submit"]');
    console.log(`Total d'éléments interactifs trouvés: ${buttons.length}`);
    
    const disabled = document.querySelectorAll('button:disabled, input[type="submit"]:disabled');
    console.log(`Éléments désactivés: ${disabled.length}`);
    
    disabled.forEach((el, index) => {
        console.log(`Élément désactivé ${index + 1}:`, el);
    });
    
    return {
        total: buttons.length,
        disabled: disabled.length,
        active: buttons.length - disabled.length
    };
}

// Exposer la fonction de débogage globalement
window.debugButtons = debugButtons;
window.activateAllButtons = activateAllButtons;
