
// Script de support simplifié pour l'activation des boutons
(function() {
    'use strict';
    
    // Ce script ne fait que s'assurer que les boutons de formulaire fonctionnent
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📱 Script de support button-activator chargé');
        
        // Gestion spécifique des formulaires
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            submitButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    // Éviter la double soumission
                    if (this.classList.contains('btn-loading')) {
                        e.preventDefault();
                        return false;
                    }
                    
                    // Ajouter un indicateur de chargement
                    this.classList.add('btn-loading');
                    const originalText = this.textContent;
                    this.textContent = 'Chargement...';
                    
                    // Restaurer après un délai
                    setTimeout(() => {
                        this.classList.remove('btn-loading');
                        this.textContent = originalText;
                    }, 3000);
                });
            });
        });
    });
})();
