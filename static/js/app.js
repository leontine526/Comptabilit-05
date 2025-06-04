// Script principal de l'application - version simplifiée sans spinner
(function() {
    'use strict';

    console.log('🔧 Script principal de l\'application initialisé');

    // Fonctions utilitaires
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Initialize DataTables if available
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

    // Initialisation au chargement du DOM
    document.addEventListener('DOMContentLoaded', function() {

        // Gestion des accordéons FAQ
        const accordions = document.querySelectorAll('.accordion-button');
        if (accordions.length > 0) {
            console.log('FAQ accordéon initialisé');
        }

        // Gestion des tooltips Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // Gestion des modales
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
            modalTriggerList.forEach(function(trigger) {
                trigger.addEventListener('click', function(e) {
                    const target = this.getAttribute('data-bs-target');
                    if (target) {
                        const modal = new bootstrap.Modal(document.querySelector(target));
                        modal.show();
                    }
                });
            });
        }

        console.log('✅ Application initialisée avec succès');

        // Initialize DataTables if available
        initializeDataTables();

        // Setup file upload preview
        setupFileUploadPreview();

        // Initialize exercise analysis
        initializeAnalysisCharts();

        // Transaction form management
        setupTransactionForm();

        // Account select initialization for search
        initializeAccountSelect();
    });

    console.log('📱 Script principal app.js chargé (version simplifiée)');

})();