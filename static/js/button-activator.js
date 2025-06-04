// Script de support simplifié pour l'activation des boutons
(function() {
    'use strict';

    console.log('📱 Script de support button-activator chargé');

    // Simple activation des boutons sans interférence
    document.addEventListener('DOMContentLoaded', function() {
        // S'assurer que tous les boutons sont cliquables
        const allButtons = document.querySelectorAll('button, .btn, a[href], [role="button"]');
        allButtons.forEach(button => {
            button.style.pointerEvents = 'auto';
            button.removeAttribute('disabled');
        });
    });

})();