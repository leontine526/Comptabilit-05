
/**
 * Script spécialisé pour forcer l'activation de tous les boutons
 * Solution d'urgence pour les boutons non cliquables
 */

(function() {
    'use strict';

    function forceButtonActivation() {
        try {
            // Forcer l'activation de tous les éléments interactifs
            const selectors = [
                'button',
                'a',
                '.btn',
                'input[type="submit"]',
                'input[type="button"]',
                '[onclick]',
                '.nav-link',
                '.dropdown-toggle',
                '[data-bs-toggle]',
                '[role="button"]'
            ];

            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(element => {
                    if (!element.hasAttribute('data-keep-disabled')) {
                        // Supprimer les attributs qui peuvent bloquer
                        element.removeAttribute('disabled');
                        element.removeAttribute('readonly');
                        
                        // Forcer les styles
                        element.style.pointerEvents = 'auto';
                        element.style.cursor = 'pointer';
                        element.style.opacity = '1';
                        
                        // Supprimer les classes qui peuvent bloquer
                        element.classList.remove('disabled', 'pe-none');
                        
                        // S'assurer que les liens ont un href valide ou un gestionnaire de clic
                        if (element.tagName === 'A' && !element.href && !element.onclick && !element.getAttribute('onclick')) {
                            element.href = 'javascript:void(0)';
                        }
                    }
                });
            });

            // Forcer la réactivation des dropdowns Bootstrap
            if (typeof bootstrap !== 'undefined') {
                document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(dropdown => {
                    try {
                        new bootstrap.Dropdown(dropdown);
                    } catch (e) {
                        // Ignorer si déjà initialisé
                    }
                });
            }

            console.log('Activation forcée des boutons terminée');
        } catch (error) {
            console.error('Erreur lors de l\'activation forcée des boutons:', error);
        }
    }

    // Exécuter immédiatement
    forceButtonActivation();

    // Exécuter après le chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceButtonActivation);
    }

    // Exécuter après le chargement complet
    window.addEventListener('load', forceButtonActivation);

    // Exécuter périodiquement
    setInterval(forceButtonActivation, 3000);

    // Observer les mutations du DOM
    if (typeof MutationObserver !== 'undefined') {
        const observer = new MutationObserver(function(mutations) {
            let shouldCheck = false;
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    shouldCheck = true;
                }
            });
            if (shouldCheck) {
                setTimeout(forceButtonActivation, 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['disabled', 'class', 'style']
        });
    }

    // Exposer la fonction globalement
    window.forceButtonActivation = forceButtonActivation;
})();
