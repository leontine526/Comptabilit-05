(function() {
    'use strict';

    // Variable pour éviter les initialisations multiples
    let isInitialized = false;

    // Configuration centralisée
    const config = {
        selectors: [
            'button:not([data-keep-disabled])',
            'a:not([data-keep-disabled])',
            '.btn:not([data-keep-disabled])',
            '[onclick]:not([data-keep-disabled])',
            '[data-bs-toggle]:not([data-keep-disabled])',
            '[role="button"]:not([data-keep-disabled])'
        ],
        checkInterval: 5000, // Réduit à 5 secondes
        maxRetries: 3
    };

    let retryCount = 0;
    let intervalId = null;

    function activateButtons() {
        try {
            let activatedCount = 0;

            config.selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    // Vérifier si l'élément a besoin d'activation
                    const needsActivation = 
                        element.hasAttribute('disabled') ||
                        element.style.pointerEvents === 'none' ||
                        element.classList.contains('disabled');

                    if (needsActivation) {
                        // Activer l'élément
                        element.removeAttribute('disabled');
                        element.style.pointerEvents = 'auto';
                        element.style.cursor = 'pointer';
                        element.classList.remove('disabled');

                        // Ajouter les gestionnaires d'événements si nécessaire
                        if (!element.hasAttribute('data-event-attached')) {
                            element.addEventListener('click', function(e) {
                                // Empêcher la soumission multiple
                                if (this.classList.contains('btn-loading')) {
                                    e.preventDefault();
                                    return false;
                                }
                            });
                            element.setAttribute('data-event-attached', 'true');
                        }

                        activatedCount++;
                    }
                });
            });

            if (activatedCount > 0) {
                console.log(`✅ ${activatedCount} boutons activés`);
                retryCount = 0; // Reset du compteur si on a trouvé des boutons
            }

            return activatedCount;
        } catch (error) {
            console.error('❌ Erreur lors de l\'activation des boutons:', error);
            return 0;
        }
    }

    function initializeButtonActivation() {
        if (isInitialized) {
            return;
        }

        console.log('🔧 Initialisation du système d\'activation des boutons');

        // Activation initiale
        const initialCount = activateButtons();

        // Observer pour les changements DOM
        if (typeof MutationObserver !== 'undefined') {
            const observer = new MutationObserver(function(mutations) {
                let shouldCheck = false;

                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        // Vérifier si des boutons ont été ajoutés
                        for (let node of mutation.addedNodes) {
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                const hasButtons = config.selectors.some(selector => 
                                    node.matches && node.matches(selector) ||
                                    node.querySelector && node.querySelector(selector)
                                );
                                if (hasButtons) {
                                    shouldCheck = true;
                                    break;
                                }
                            }
                        }
                    }
                });

                if (shouldCheck) {
                    setTimeout(activateButtons, 100); // Délai pour laisser le DOM se stabiliser
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: false // On ne surveille que les ajouts/suppressions
            });
        }

        // Vérification périodique réduite
        intervalId = setInterval(function() {
            const activatedCount = activateButtons();

            if (activatedCount === 0) {
                retryCount++;
                if (retryCount >= config.maxRetries) {
                    console.log('🎯 Aucun bouton à activer - arrêt des vérifications périodiques');
                    clearInterval(intervalId);
                    intervalId = null;
                }
            }
        }, config.checkInterval);

        isInitialized = true;
        console.log('✅ Système d\'activation des boutons initialisé');
    }

    // Initialisation au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeButtonActivation);
    } else {
        initializeButtonActivation();
    }

    // Nettoyage lors du déchargement de la page
    window.addEventListener('beforeunload', function() {
        if (intervalId) {
            clearInterval(intervalId);
        }
    });

})();