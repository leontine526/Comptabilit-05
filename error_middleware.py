
from werkzeug.wrappers import Response
import traceback
import logging
from flask import Flask, render_template_string

# Configuration du logging
logger = logging.getLogger(__name__)

class ErrorMiddleware:
    """Middleware pour gérer les erreurs non capturées au niveau WSGI"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        """Méthode principale du middleware"""
        try:
            return self.app(environ, start_response)
        except Exception as e:
            logger.error(f"Erreur critique interceptée par le middleware: {str(e)}")
            logger.error(traceback.format_exc())
            return self.handle_exception(e, environ, start_response)
    
    def handle_exception(self, e, environ, start_response):
        """Gère une exception non capturée et renvoie une réponse d'erreur"""
        # Message d'erreur simple
        error_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erreur Système</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                .error-container { max-width: 800px; margin: 50px auto; padding: 20px; 
                                 border: 1px solid #ddd; border-radius: 5px; }
                h1 { color: #d9534f; }
                .message { margin: 20px 0; color: #333; }
                .details { margin-top: 30px; text-align: left; background: #f5f5f5; 
                         padding: 15px; border-radius: 5px; overflow-x: auto; }
                .back-link { margin-top: 30px; }
                .back-link a { color: #337ab7; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Erreur Système</h1>
                <div class="message">
                    Une erreur inattendue s'est produite. L'équipe technique a été notifiée.
                </div>
                <div class="back-link">
                    <a href="/">Retour à la page d'accueil</a>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Créer une réponse
        response_headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response('500 Internal Server Error', response_headers)
        return [error_html.encode('utf-8')]

def register_middleware(app):
    """Enregistre le middleware sur l'application Flask"""
    # Encapsuler l'application avec notre middleware de gestion d'erreurs
    return ErrorMiddleware(app)
