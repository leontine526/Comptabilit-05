/**
 * Script de support pour l'activation des boutons
 * Fonctionne en complément de button-fix.js
 */

(function() {
    'use strict';

    // Fonction légère de support
    function quickButtonCheck() {
        // Réactivation rapide des boutons critiques uniquement
        const criticalButtons = document.querySelectorAll('button[type="submit"], .btn-primary, .btn-success');
        criticalButtons.forEach(btn => {
            if (!btn.hasAttribute('data-keep-disabled')) {
                btn.disabled = false;
                btn.style.pointerEvents = 'auto';
            }
        });
    }

    // Exécution uniquement au chargement initial
    document.addEventListener('DOMContentLoaded', quickButtonCheck);

    console.log('📱 Script de support button-activator chargé');
})();