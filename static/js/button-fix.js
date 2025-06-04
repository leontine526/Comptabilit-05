(function() {
    'use strict';

    console.log('🔧 Initialisation du système d\'activation des boutons');

    // Configuration simplifiée
    const selectors = [
        'button',
        'a',
        '.btn',
        '[onclick]',
        '[data-bs-toggle]',
        '[role="button"]'
    ];

    function activateButtons() {
        let buttonCount = 0;

        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector + ':not([data-keep-disabled])');
            elements.forEach(element => {
                // Supprimer les attributs qui peuvent bloquer les clics
                element.removeAttribute('disabled');
                element.style.pointerEvents = 'auto';
                element.style.cursor = 'pointer';
                element.classList.remove('disabled');
                buttonCount++;
            });
        });

        if (buttonCount === 0) {
            console.log('🎯 Aucun bouton à activer - arrêt des vérifications périodiques');
            return false;
        }

        return true;
    }

    // Activation immédiate
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', activateButtons);
    } else {
        activateButtons();
    }

    // Activation périodique si nécessaire
    let checkInterval = setInterval(() => {
        if (!activateButtons()) {
            clearInterval(checkInterval);
        }
    }, 3000);

    // Observer les changements du DOM
    if (typeof MutationObserver !== 'undefined') {
        const observer = new MutationObserver(() => {
            activateButtons();
        });
        observer.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: true,
            attributeFilter: ['disabled', 'class', 'style']
        });
    }

    console.log('✅ Système d\'activation des boutons initialisé');

})();