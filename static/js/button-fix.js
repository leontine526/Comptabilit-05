
(function() {
    'use strict';

    // Variable pour éviter les exécutions multiples
    let isActivating = false;
    let lastActivation = 0;
    const ACTIVATION_COOLDOWN = 100; // ms

    // Fonction principale d'activation des boutons
    function ensureAllButtonsActive() {
        // Éviter les exécutions trop rapprochées
        const now = Date.now();
        if (isActivating || (now - lastActivation < ACTIVATION_COOLDOWN)) {
            return;
        }

        isActivating = true;
        lastActivation = now;

        try {
            // Sélecteurs pour tous les éléments interactifs
            const selectors = [
                'button',
                'a',
                '.btn',
                'input[type="submit"]',
                'input[type="button"]',
                '[onclick]',
                '[data-bs-toggle]',
                '[role="button"]',
                '.nav-link',
                '.dropdown-toggle',
                '.dropdown-item'
            ];
            
            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(element => {
                    // Ne pas toucher aux éléments explicitement marqués comme devant rester désactivés
                    if (element.hasAttribute('data-keep-disabled') || 
                        element.hasAttribute('data-permanently-disabled')) {
                        return;
                    }

                    // Réactiver l'élément
                    element.removeAttribute('disabled');
                    element.style.pointerEvents = 'auto';
                    element.style.cursor = 'pointer';
                    element.style.opacity = '1';
                    element.classList.remove('disabled', 'pe-none');

                    // Cas spéciaux pour les liens
                    if (element.tagName === 'A') {
                        // S'assurer que les liens ont un href ou un gestionnaire de clic
                        if (!element.href && !element.onclick && !element.getAttribute('onclick')) {
                            element.href = 'javascript:void(0)';
                        }
                        // Supprimer tabindex négatif
                        if (element.tabIndex < 0) {
                            element.removeAttribute('tabindex');
                        }
                    }

                    // Réinitialiser les dropdowns Bootstrap si nécessaire
                    if (element.hasAttribute('data-bs-toggle') && element.getAttribute('data-bs-toggle') === 'dropdown') {
                        if (typeof bootstrap !== 'undefined') {
                            try {
                                // Éviter les erreurs de réinitialisation
                                if (!element._dropdown) {
                                    new bootstrap.Dropdown(element);
                                }
                            } catch (e) {
                                // Ignorer les erreurs de Bootstrap
                            }
                        }
                    }
                });
            });

            console.log('✅ Activation des boutons terminée avec succès');
        } catch (error) {
            console.error('❌ Erreur lors de l\'activation des boutons:', error);
        } finally {
            isActivating = false;
        }
    }

    // Fonction de débogage
    function debugButtonStates() {
        const allInteractive = document.querySelectorAll('button, a, input[type="submit"], .btn');
        const disabled = document.querySelectorAll('button:disabled, input:disabled, .disabled');
        
        console.log(`Debug: ${allInteractive.length} éléments interactifs, ${disabled.length} désactivés`);
        
        disabled.forEach((el, i) => {
            console.log(`Élément désactivé ${i + 1}:`, el, {
                disabled: el.disabled,
                classes: el.className,
                style: el.style.pointerEvents
            });
        });
    }

    // Initialisation immédiate si le DOM est déjà prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureAllButtonsActive);
    } else {
        ensureAllButtonsActive();
    }

    // Exécution après le chargement complet
    window.addEventListener('load', ensureAllButtonsActive);

    // Réactivation périodique (moins fréquente)
    setInterval(ensureAllButtonsActive, 5000);

    // Observer les mutations DOM avec throttling
    if (typeof MutationObserver !== 'undefined') {
        let mutationTimeout;
        const observer = new MutationObserver(function(mutations) {
            // Vérifier si des changements significatifs ont eu lieu
            let hasSignificantChanges = false;
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Vérifier si des boutons ont été ajoutés
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // Element node
                            if (node.matches && (
                                node.matches('button, a, .btn, input[type="submit"]') ||
                                node.querySelector('button, a, .btn, input[type="submit"]')
                            )) {
                                hasSignificantChanges = true;
                            }
                        }
                    });
                }
                if (mutation.type === 'attributes' && 
                    ['disabled', 'class', 'style'].includes(mutation.attributeName)) {
                    hasSignificantChanges = true;
                }
            });

            if (hasSignificantChanges) {
                clearTimeout(mutationTimeout);
                mutationTimeout = setTimeout(ensureAllButtonsActive, 200);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['disabled', 'class', 'style', 'tabindex']
        });
    }

    // Gestion des erreurs JavaScript
    window.addEventListener('error', function(e) {
        console.warn('Erreur JavaScript détectée, réactivation des boutons dans 1s');
        setTimeout(ensureAllButtonsActive, 1000);
    });

    // Réactivation après les requêtes AJAX
    if (typeof $ !== 'undefined') {
        $(document).ajaxComplete(function() {
            setTimeout(ensureAllButtonsActive, 100);
        });
    }

    // Exposer les fonctions globalement pour le débogage
    window.ensureAllButtonsActive = ensureAllButtonsActive;
    window.debugButtonStates = debugButtonStates;
    
    console.log('🔧 Script d\'activation des boutons initialisé');
})();
