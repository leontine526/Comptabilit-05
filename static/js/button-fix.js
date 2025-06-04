
(function() {
    'use strict';

    // Solution définitive pour les boutons non cliquables
    function forceButtonActivation() {
        // Sélecteurs très larges pour capturer tous les éléments interactifs
        const allInteractiveSelectors = [
            'button',
            'a',
            'input[type="submit"]',
            'input[type="button"]',
            '.btn',
            '.nav-link',
            '.dropdown-toggle',
            '.dropdown-item',
            '[onclick]',
            '[data-bs-toggle]',
            '[role="button"]',
            '.btn-primary',
            '.btn-secondary',
            '.btn-success',
            '.btn-danger',
            '.btn-warning',
            '.btn-info',
            '.btn-light',
            '.btn-dark',
            '.btn-outline-primary',
            '.btn-outline-secondary',
            '.btn-outline-success',
            '.btn-outline-danger',
            '.btn-outline-warning',
            '.btn-outline-info',
            '.btn-outline-light',
            '.btn-outline-dark'
        ];

        allInteractiveSelectors.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach(element => {
                    // Ne pas toucher aux éléments marqués comme devant rester désactivés
                    if (element.hasAttribute('data-keep-disabled') || 
                        element.hasAttribute('data-permanently-disabled')) {
                        return;
                    }

                    // Force l'activation complète
                    element.disabled = false;
                    element.removeAttribute('disabled');
                    
                    // Styles CSS forcés
                    element.style.pointerEvents = 'auto !important';
                    element.style.cursor = 'pointer !important';
                    element.style.opacity = '1 !important';
                    element.style.visibility = 'visible !important';
                    element.style.display = element.style.display || 'inline-block';
                    
                    // Supprimer toutes les classes qui peuvent désactiver
                    const disablingClasses = ['disabled', 'pe-none', 'pointer-events-none', 'btn-disabled'];
                    disablingClasses.forEach(cls => element.classList.remove(cls));
                    
                    // Pour les liens
                    if (element.tagName === 'A') {
                        if (!element.href && !element.onclick && !element.getAttribute('onclick')) {
                            element.href = 'javascript:void(0)';
                        }
                        element.removeAttribute('tabindex');
                    }

                    // Forcer l'ajout d'event listeners
                    if (!element.hasAttribute('data-clickable-forced')) {
                        element.setAttribute('data-clickable-forced', 'true');
                        
                        // Ajouter un gestionnaire de clic générique si aucun n'existe
                        if (!element.onclick && !element.getAttribute('onclick') && 
                            !element.href && element.type !== 'submit') {
                            element.addEventListener('click', function(e) {
                                // Ne rien faire, juste s'assurer que le clic est capturé
                                console.log('Clic capturé sur:', this);
                            });
                        }
                    }
                });
            } catch (error) {
                console.warn('Erreur lors de l\'activation du sélecteur', selector, ':', error);
            }
        });

        // Force l'activation de tous les formulaires
        document.querySelectorAll('form').forEach(form => {
            form.style.pointerEvents = 'auto !important';
            form.querySelectorAll('input, button, select, textarea').forEach(input => {
                if (!input.hasAttribute('data-keep-disabled')) {
                    input.disabled = false;
                    input.removeAttribute('disabled');
                    input.style.pointerEvents = 'auto !important';
                }
            });
        });
    }

    // Fonction pour injecter des styles CSS forcés
    function injectForceStyles() {
        const existingStyle = document.getElementById('force-button-styles');
        if (existingStyle) {
            existingStyle.remove();
        }

        const style = document.createElement('style');
        style.id = 'force-button-styles';
        style.textContent = `
            /* Force l'activation de tous les boutons */
            button:not([data-keep-disabled]),
            .btn:not([data-keep-disabled]),
            a:not([data-keep-disabled]),
            input[type="submit"]:not([data-keep-disabled]),
            input[type="button"]:not([data-keep-disabled]) {
                pointer-events: auto !important;
                cursor: pointer !important;
                opacity: 1 !important;
                visibility: visible !important;
            }
            
            /* Supprimer les états désactivés */
            .disabled:not([data-keep-disabled]),
            .pe-none:not([data-keep-disabled]) {
                pointer-events: auto !important;
                opacity: 1 !important;
            }
            
            /* Force les interactions sur les dropdowns */
            .dropdown-toggle:not([data-keep-disabled]),
            .dropdown-item:not([data-keep-disabled]) {
                pointer-events: auto !important;
                cursor: pointer !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Exécution immédiate et répétée
    function executeForceActivation() {
        injectForceStyles();
        forceButtonActivation();
    }

    // Exécution au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', executeForceActivation);
    } else {
        executeForceActivation();
    }

    // Exécution après le chargement complet
    window.addEventListener('load', executeForceActivation);

    // Exécution périodique agressive
    setInterval(executeForceActivation, 2000);

    // Observer très agressif pour les mutations DOM
    if (typeof MutationObserver !== 'undefined') {
        const observer = new MutationObserver(function() {
            setTimeout(executeForceActivation, 100);
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['disabled', 'class', 'style']
        });
    }

    // Réactivation après les erreurs
    window.addEventListener('error', function() {
        setTimeout(executeForceActivation, 500);
    });

    // Réactivation après les requêtes AJAX
    if (typeof $ !== 'undefined') {
        $(document).ajaxComplete(function() {
            setTimeout(executeForceActivation, 200);
        });
    }

    // Fonction de débogage améliorée
    window.debugButtonStates = function() {
        const all = document.querySelectorAll('button, a, .btn, input[type="submit"]');
        const disabled = document.querySelectorAll('[disabled], .disabled');
        
        console.log(`🔍 Total éléments interactifs: ${all.length}`);
        console.log(`❌ Éléments désactivés: ${disabled.length}`);
        
        disabled.forEach((el, i) => {
            console.log(`Désactivé ${i+1}:`, el, {
                disabled: el.disabled,
                classes: el.className,
                style: el.style.cssText,
                computed: window.getComputedStyle(el).pointerEvents
            });
        });
        
        return { total: all.length, disabled: disabled.length };
    };

    // Exposer la fonction globalement
    window.forceButtonActivation = executeForceActivation;
    
    console.log('🚀 Solution définitive d\'activation des boutons chargée');
})();
