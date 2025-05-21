
/**
 * Gestionnaire d'erreurs global pour l'application
 */
(function() {
    'use strict';
    
    // Capture des erreurs globales
    window.addEventListener('error', function(event) {
        handleJsError(event.error || event.message);
        return false;
    });
    
    // Capture des rejets de promesses
    window.addEventListener('unhandledrejection', function(event) {
        handleJsError(event.reason || 'Promesse rejetée non gérée');
        return false;
    });
    
    // Intercepte les erreurs AJAX
    $(document).ajaxError(function(event, jqXHR, settings, thrownError) {
        handleAjaxError(jqXHR, settings.url);
    });
    
    /**
     * Gère les erreurs JavaScript générales
     */
    function handleJsError(error) {
        console.error('Erreur JS:', error);
        
        // Afficher un message d'erreur convivial
        showErrorToast("Une erreur s'est produite. Veuillez rafraîchir la page.");
        
        // Envoyer l'erreur au serveur pour journalisation
        logErrorToServer({
            type: 'js_error',
            message: error.message || String(error),
            stack: error.stack,
            url: window.location.href,
            user_agent: navigator.userAgent
        });
    }
    
    /**
     * Gère les erreurs AJAX
     */
    function handleAjaxError(jqXHR, requestUrl) {
        // Détecter les erreurs de réseau ou de serveur
        if (jqXHR.status === 0) {
            showErrorToast("Impossible de se connecter au serveur. Vérifiez votre connexion.");
        } else if (jqXHR.status === 401) {
            showErrorToast("Votre session a expiré. Veuillez vous reconnecter.");
            setTimeout(function() {
                window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
            }, 2000);
        } else if (jqXHR.status === 404) {
            showErrorToast("La ressource demandée n'existe pas.");
        } else if (jqXHR.status === 500) {
            showErrorToast("Une erreur serveur s'est produite. Veuillez réessayer plus tard.");
        } else {
            showErrorToast("Une erreur s'est produite lors de la communication avec le serveur.");
        }
        
        // Journaliser l'erreur
        logErrorToServer({
            type: 'ajax_error',
            status: jqXHR.status,
            url: requestUrl,
            response: jqXHR.responseText,
            user_agent: navigator.userAgent
        });
    }
    
    /**
     * Affiche un message d'erreur à l'utilisateur
     */
    function showErrorToast(message) {
        // Si toastr est disponible
        if (typeof toastr !== 'undefined') {
            toastr.error(message, 'Erreur', {
                closeButton: true,
                timeOut: 5000,
                extendedTimeOut: 2000,
                progressBar: true
            });
            return;
        }
        
        // Fallback: créer un toast personnalisé
        var toast = document.createElement('div');
        toast.className = 'alert alert-danger alert-dismissible fade show error-toast';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = message + 
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        
        // Ajouter au DOM
        document.body.appendChild(toast);
        
        // Supprimer après 5 secondes
        setTimeout(function() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
    
    /**
     * Envoie l'erreur au serveur pour journalisation
     */
    function logErrorToServer(errorData) {
        // Envoyer l'erreur au serveur sans attendre de réponse
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/log-client-error', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(errorData));
    }
    
    // Ajouter un style CSS pour les toasts d'erreur
    var style = document.createElement('style');
    style.textContent = `
        .error-toast {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 350px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
    `;
    document.head.appendChild(style);Child(style);
})();
