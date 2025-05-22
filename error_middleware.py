from flask import request, jsonify, render_template
import traceback
import logging
import sys

logger = logging.getLogger(__name__)

class ErrorMiddleware:
    """Middleware Flask pour gérer les erreurs de manière centralisée"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """Méthode appelée pour chaque requête"""
        try:
            # Traiter la requête normalement
            return self.app(environ, start_response)
        except Exception as e:
            # Capturer toutes les exceptions non gérées
            logger.error(f"Erreur non gérée dans le middleware: {str(e)}")
            logger.error(traceback.format_exc())

            # Créer un contexte d'application Flask pour pouvoir utiliser ses fonctionnalités
            with self.app.request_context(environ):
                # Créer une réponse d'erreur adaptée au type de requête
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Pour les requêtes API, renvoyer du JSON
                    response = jsonify({
                        'error': 'Erreur serveur',
                        'message': str(e) if self.app.debug else 'Une erreur inattendue s\'est produite'
                    })
                    response.status_code = 500
                else:
                    # Pour les requêtes HTML, renvoyer une page d'erreur
                    try:
                        response = render_template('errors/500.html', 
                                                  error=str(e) if self.app.debug else 'Une erreur inattendue s\'est produite')
                        status = 500
                    except Exception as template_error:
                        # Si le rendu du template échoue, envoyer une réponse simple
                        logger.error(f"Erreur de rendu du template d'erreur: {str(template_error)}")
                        response = "Erreur serveur 500: " + (str(e) if self.app.debug else 'Une erreur inattendue s\'est produite')
                        status = 500

                return response(environ, start_response)

def register_middleware(app):
    """Enregistre le middleware sur l'application Flask"""
    # Encapsuler l'application avec notre middleware de gestion d'erreurs
    return ErrorMiddleware(app)