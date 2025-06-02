
/**
 * Script pour s'assurer que tous les boutons restent opérationnels
 * Corrige les problèmes de boutons désactivés ou non-responsifs
 */

(function() {
    'use strict';

    // Fonction principale d'activation
    function ensureButtonsWork() {
        // 1. Réactiver tous les boutons
        document.querySelectorAll('button, input[type="submit"], input[type="button"]').forEach(button => {
            if (!button.hasAttribute('data-keep-disabled')) {
                button.disabled = false;
                button.style.pointerEvents = 'auto';
            }
        });

        // 2. S'assurer que les liens fonctionnent
        document.querySelectorAll('a').forEach(link => {
            if (link.href && !link.classList.contains('disabled')) {
                link.style.pointerEvents = 'auto';
            }
        });

        // 3. Réactiver les éléments avec la classe btn
        document.querySelectorAll('.btn').forEach(btn => {
            if (!btn.hasAttribute('data-keep-disabled')) {
                btn.disabled = false;
                btn.style.pointerEvents = 'auto';
                btn.classList.remove('disabled');
            }
        });

        // 4. S'assurer que les dropdowns fonctionnent
        document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(dropdown => {
            if (typeof bootstrap !== 'undefined') {
                try {
                    new bootstrap.Dropdown(dropdown);
                } catch (e) {
                    // Ignorer si déjà initialisé
                }
            }
        });
    }

    // Exécuter au chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureButtonsWork);
    } else {
        ensureButtonsWork();
    }

    // Exécuter périodiquement pour corriger les problèmes
    setInterval(ensureButtonsWork, 5000);

    // Exécuter après les erreurs Ajax
    document.addEventListener('ajaxComplete', ensureButtonsWork);

    // Observer les mutations DOM
    if (typeof MutationObserver !== 'undefined') {
        const observer = new MutationObserver(function(mutations) {
            let shouldCheck = false;
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    shouldCheck = true;
                }
            });
            if (shouldCheck) {
                setTimeout(ensureButtonsWork, 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Exposer la fonction globalement
    window.ensureButtonsWork = ensureButtonsWork;
})();
