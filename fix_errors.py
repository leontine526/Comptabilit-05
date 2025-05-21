
#!/usr/bin/env python
"""
Script pour corriger les erreurs système et améliorer la robustesse de l'application
"""
import os
import sys
import logging
import traceback
from flask import render_template

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def fix_flask_error_handlers():
    """Corrige le gestionnaire d'erreur dans app.py"""
    try:
        logger.info("Vérification du gestionnaire d'erreurs dans app.py...")
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Vérifier s'il y a une erreur de référence à handle_standard_exception
        if "handle_standard_exception" in content and "render_template" not in content:
            logger.info("Correction du gestionnaire d'erreurs dans app.py...")
            
            # Vérifier si l'import de render_template est manquant
            if "from flask import Flask" in content and "render_template" not in content[:content.find("app = Flask")]:
                # Ajouter render_template à l'import
                content = content.replace(
                    "from flask import Flask",
                    "from flask import Flask, render_template"
                )
            
            # Corriger le gestionnaire d'erreurs
            content = content.replace(
                "def handle_exception(e):",
                """def handle_exception(e):
    \"\"\"Gestionnaire global d'exceptions\"\"\"
    # Tentative d'annulation de toute transaction en cours
    try:
        db.session.rollback()
    except:
        pass
        
    # Laisser les autres gestionnaires d'erreurs traiter l'exception
    return render_template('errors/500.html', error=str(e)), 500"""
            )
            
            # Écrire le fichier corrigé
            with open("app.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("✅ Gestionnaire d'erreurs dans app.py corrigé")
            return True
        else:
            logger.info("✅ Gestionnaire d'erreurs dans app.py semble correct")
            return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction du gestionnaire d'erreurs: {str(e)}")
        return False

def fix_error_middleware():
    """Vérifie et corrige le middleware d'erreur"""
    try:
        logger.info("Vérification du middleware d'erreur...")
        if not os.path.exists("error_middleware.py"):
            logger.warning("⚠️ Fichier error_middleware.py non trouvé")
            return False
        
        with open("error_middleware.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Vérifier si le middleware est correctement configuré
        if "import traceback" not in content:
            logger.info("Ajout de l'import traceback manquant...")
            content = "import traceback\n" + content
        
        # S'assurer que le middleware enregistre correctement les erreurs
        if "logger.error(traceback.format_exc())" not in content:
            # Améliorer la journalisation des erreurs
            content = content.replace(
                "logger.error(f\"Erreur critique interceptée par le middleware: {str(e)}\")",
                "logger.error(f\"Erreur critique interceptée par le middleware: {str(e)}\")\n            logger.error(traceback.format_exc())"
            )
        
        # Écrire le fichier corrigé
        with open("error_middleware.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info("✅ Middleware d'erreur corrigé")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction du middleware d'erreur: {str(e)}")
        return False

def create_error_template_if_missing():
    """Crée les templates d'erreur s'ils sont manquants"""
    try:
        logger.info("Vérification des templates d'erreur...")
        error_template_dir = os.path.join("templates", "errors")
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(error_template_dir):
            os.makedirs(error_template_dir)
            logger.info(f"✅ Dossier {error_template_dir} créé")
        
        # Liste des templates d'erreur à vérifier
        error_templates = {
            "500.html": """{% extends 'base.html' %}

{% block title %}Erreur Système{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm mt-5">
                <div class="card-header bg-danger text-white">
                    <h3 class="mb-0">Erreur Système</h3>
                </div>
                <div class="card-body">
                    <div class="text-center mb-4">
                        <i class="fas fa-exclamation-triangle fa-4x text-danger mb-3"></i>
                        <h4>Une erreur inattendue s'est produite</h4>
                        <p class="text-muted">L'équipe technique a été notifiée.</p>
                    </div>
                    
                    {% if error %}
                    <div class="alert alert-secondary">
                        <strong>Détails de l'erreur:</strong> {{ error }}
                    </div>
                    {% endif %}
                    
                    <div class="mt-4">
                        <p>Vous pouvez essayer de:</p>
                        <ul>
                            <li>Rafraîchir la page</li>
                            <li>Revenir à la <a href="/">page d'accueil</a></li>
                            <li>Vous <a href="/logout">déconnecter</a> puis vous reconnecter</li>
                        </ul>
                    </div>
                </div>
                <div class="card-footer">
                    <a href="/" class="btn btn-primary">Retour à l'accueil</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",
            "404.html": """{% extends 'base.html' %}

{% block title %}Page non trouvée{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm mt-5">
                <div class="card-header bg-warning">
                    <h3 class="mb-0">Page non trouvée</h3>
                </div>
                <div class="card-body">
                    <div class="text-center mb-4">
                        <i class="fas fa-search fa-4x text-warning mb-3"></i>
                        <h4>La page que vous recherchez n'existe pas</h4>
                        <p class="text-muted">L'URL que vous avez demandée n'a pas été trouvée sur ce serveur.</p>
                    </div>
                    
                    <div class="alert alert-info">
                        <strong>URL demandée:</strong> {{ request.path }}
                    </div>
                    
                    <div class="mt-4">
                        <p>Vous pouvez essayer de:</p>
                        <ul>
                            <li>Vérifier l'URL</li>
                            <li>Revenir à la <a href="/">page d'accueil</a></li>
                            <li>Utiliser la barre de recherche pour trouver ce que vous cherchez</li>
                        </ul>
                    </div>
                </div>
                <div class="card-footer">
                    <a href="/" class="btn btn-primary">Retour à l'accueil</a>
                    <a href="javascript:history.back()" class="btn btn-secondary">Page précédente</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",
            "db_error.html": """{% extends 'base.html' %}

{% block title %}Erreur de base de données{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm mt-5">
                <div class="card-header bg-danger text-white">
                    <h3 class="mb-0">Erreur de base de données</h3>
                </div>
                <div class="card-body">
                    <div class="text-center mb-4">
                        <i class="fas fa-database fa-4x text-danger mb-3"></i>
                        <h4>Problème de connexion à la base de données</h4>
                        <p class="text-muted">L'équipe technique a été notifiée.</p>
                    </div>
                    
                    {% if error %}
                    <div class="alert alert-secondary">
                        <strong>Détails de l'erreur:</strong> {{ error }}
                    </div>
                    {% endif %}
                    
                    <div class="mt-4">
                        <p>Ce problème peut être temporaire. Vous pouvez essayer de:</p>
                        <ul>
                            <li>Rafraîchir la page dans quelques instants</li>
                            <li>Revenir à la <a href="/">page d'accueil</a></li>
                        </ul>
                    </div>
                </div>
                <div class="card-footer">
                    <a href="/" class="btn btn-primary">Retour à l'accueil</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
        }
        
        # Créer les templates manquants
        for template_name, template_content in error_templates.items():
            template_path = os.path.join(error_template_dir, template_name)
            if not os.path.exists(template_path):
                with open(template_path, "w", encoding="utf-8") as f:
                    f.write(template_content)
                logger.info(f"✅ Template {template_name} créé")
            else:
                logger.info(f"✅ Template {template_name} existe déjà")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des templates d'erreur: {str(e)}")
        return False

def ensure_js_error_handler():
    """S'assure que le gestionnaire d'erreurs JavaScript est correctement chargé"""
    try:
        error_handler_path = os.path.join("static", "js", "error-handler.js")
        
        if os.path.exists(error_handler_path):
            # Vérifier que le fichier est complet
            with open(error_handler_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "document.head.append" in content and not "document.head.appendChild(style);" in content:
                # Réparer le fichier incomplet
                logger.info("Réparation du fichier error-handler.js...")
                
                # Récupérer les 3 morceaux du fichier
                part1_content = ""
                part2_content = ""
                part3_content = ""
                
                try:
                    with open(os.path.join("static", "js", "error-handler.js"), "r", encoding="utf-8") as f:
                        part1_content = f.read()
                except:
                    pass
                
                try:
                    with open(os.path.join("static", "js", "error-handler-2.js"), "r", encoding="utf-8") as f:
                        part2_content = f.read()
                except:
                    pass
                
                try:
                    with open(os.path.join("static", "js", "error-handler-3.js"), "r", encoding="utf-8") as f:
                        part3_content = f.read()
                except:
                    pass
                
                # Créer le fichier complet
                complete_content = """/**
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
            showErrorToast("Impossible de se connecter au serveur. Vérifiez votre connexion Internet.");
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
    document.head.appendChild(style);
})();
"""
                
                # Écrire le fichier complet
                with open(error_handler_path, "w", encoding="utf-8") as f:
                    f.write(complete_content)
                
                logger.info("✅ Fichier error-handler.js réparé")
        else:
            # Créer le fichier s'il n'existe pas
            logger.info("Création du fichier error-handler.js...")
            os.makedirs(os.path.dirname(error_handler_path), exist_ok=True)
            
            with open(error_handler_path, "w", encoding="utf-8") as f:
                f.write("""/**
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
            showErrorToast("Impossible de se connecter au serveur. Vérifiez votre connexion Internet.");
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
    document.head.appendChild(style);
})();
""")
            
            logger.info("✅ Fichier error-handler.js créé")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la gestion du fichier error-handler.js: {str(e)}")
        return False

def fix_error_handlers_registration():
    """Vérifie et corrige l'enregistrement des gestionnaires d'erreur"""
    try:
        logger.info("Vérification de l'enregistrement des gestionnaires d'erreur...")
        
        # Vérifier si le fichier error_handlers.py existe
        if not os.path.exists("error_handlers.py"):
            logger.warning("⚠️ Fichier error_handlers.py non trouvé")
            return False
        
        # Vérifier si les gestionnaires sont correctement importés dans main.py
        if os.path.exists("main.py"):
            with open("main.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Vérifier si l'import et l'enregistrement sont présents
            if "from error_handlers import register_error_handlers" not in content or "register_error_handlers(app)" not in content:
                logger.info("Ajout de l'enregistrement des gestionnaires d'erreur dans main.py...")
                
                # Ajouter l'import si nécessaire
                if "from error_handlers import register_error_handlers" not in content:
                    import_pos = content.find("import ")
                    if import_pos > -1:
                        next_line_pos = content.find("\n", import_pos)
                        content = content[:next_line_pos+1] + "from error_handlers import register_error_handlers\n" + content[next_line_pos+1:]
                
                # Ajouter l'enregistrement si nécessaire
                if "register_error_handlers(app)" not in content:
                    if "app = create_app()" in content:
                        pos = content.find("app = create_app()") + len("app = create_app()")
                        content = content[:pos] + "\n# Enregistrer les gestionnaires d'erreur\nregister_error_handlers(app)" + content[pos:]
                    elif "from app import app" in content:
                        pos = content.find("from app import app") + len("from app import app")
                        content = content[:pos] + "\n# Enregistrer les gestionnaires d'erreur\nregister_error_handlers(app)" + content[pos:]
                
                # Écrire le fichier mis à jour
                with open("main.py", "w", encoding="utf-8") as f:
                    f.write(content)
                
                logger.info("✅ Enregistrement des gestionnaires d'erreur ajouté dans main.py")
        
        # Vérifier si les gestionnaires sont correctement importés dans wsgi.py
        if os.path.exists("wsgi.py"):
            with open("wsgi.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Vérifier si l'import et l'enregistrement sont présents
            if "from error_handlers import register_error_handlers" not in content or "register_error_handlers(application)" not in content:
                logger.info("Ajout de l'enregistrement des gestionnaires d'erreur dans wsgi.py...")
                
                # Ajouter l'import si nécessaire
                if "from error_handlers import register_error_handlers" not in content:
                    import_pos = content.find("import ")
                    if import_pos > -1:
                        next_line_pos = content.find("\n", import_pos)
                        content = content[:next_line_pos+1] + "from error_handlers import register_error_handlers\n" + content[next_line_pos+1:]
                
                # Ajouter l'enregistrement si nécessaire
                if "register_error_handlers(application)" not in content and "application = " in content:
                    pos = content.find("application = ")
                    line_end = content.find("\n", pos)
                    content = content[:line_end+1] + "\n# Enregistrer les gestionnaires d'erreur\nregister_error_handlers(application)\n" + content[line_end+1:]
                
                # Écrire le fichier mis à jour
                with open("wsgi.py", "w", encoding="utf-8") as f:
                    f.write(content)
                
                logger.info("✅ Enregistrement des gestionnaires d'erreur ajouté dans wsgi.py")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction de l'enregistrement des gestionnaires d'erreur: {str(e)}")
        return False

def run_fixes():
    """Exécute toutes les corrections"""
    print("\n" + "="*50)
    print(" CORRECTION DES ERREURS SYSTÈME ".center(50, "="))
    print("="*50 + "\n")
    
    # Étape 1: Corriger le gestionnaire d'erreur dans app.py
    fix_flask_error_handlers()
    
    # Étape 2: Vérifier et corriger le middleware d'erreur
    fix_error_middleware()
    
    # Étape 3: Créer les templates d'erreur s'ils sont manquants
    create_error_template_if_missing()
    
    # Étape 4: S'assurer que le gestionnaire d'erreurs JavaScript est correctement chargé
    ensure_js_error_handler()
    
    # Étape 5: Corriger l'enregistrement des gestionnaires d'erreur
    fix_error_handlers_registration()
    
    print("\n" + "="*50)
    print(" CORRECTIONS TERMINÉES ".center(50, "="))
    print("="*50 + "\n")
    
    print("Pour redémarrer l'application avec les corrections, exécutez:")
    print("python start_simple.py")

if __name__ == "__main__":
    run_fixes()
