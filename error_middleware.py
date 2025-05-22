
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
                # Vérifier si c'est une erreur 404 (NotFound)
                status_code = 500
                error_template = 'errors/500.html'
                
                if hasattr(e, 'code') and e.code == 404:
                    status_code = 404
                    error_template = 'errors/404.html'
                
                # Créer une réponse d'erreur adaptée au type de requête
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Pour les requêtes API, renvoyer du JSON
                    response = jsonify({
                        'error': 'Page non trouvée' if status_code == 404 else 'Erreur serveur',
                        'message': str(e) if self.app.debug else ('La ressource demandée n\'existe pas' if status_code == 404 else 'Une erreur inattendue s\'est produite')
                    })
                    response.status_code = status_code
                else:
                    # Pour les requêtes HTML, renvoyer une page d'erreur
                    try:
                        html_response = render_template(error_template, 
                                                  error=str(e) if self.app.debug else ('La ressource demandée n\'existe pas' if status_code == 404 else 'Une erreur inattendue s\'est produite'))
                        response = self.app.make_response((html_response, status_code))
                    except Exception as template_error:
                        # Si le rendu du template échoue, envoyer une réponse simple
                        logger.error(f"Erreur de rendu du template d'erreur: {str(template_error)}")
                        error_message = 'Page non trouvée (404)' if status_code == 404 else 'Erreur serveur (500)'
                        response = self.app.make_response((error_message + ": " + 
                                             (str(e) if self.app.debug else 'Une erreur est survenue'), status_code))

                return response(environ, start_response)

def register_middleware(app):
    """Enregistre le middleware sur l'application Flask"""
    # Encapsuler l'application avec notre middleware de gestion d'erreurs
    return ErrorMiddleware(app)
