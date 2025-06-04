
/**
 * Script de support minimal pour l'activation des boutons
 */

(function() {
    'use strict';

    // Fonction de support très simple
    function quickActivation() {
        // Activation rapide des boutons critiques seulement
        document.querySelectorAll('button[disabled], input[disabled]').forEach(btn => {
            if (!btn.hasAttribute('data-keep-disabled')) {
                btn.disabled = false;
            }
        });
    }

    // Exécution unique au chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', quickActivation);
    } else {
        quickActivation();
    }

    console.log('🔧 Script de support minimal chargé');
})();
