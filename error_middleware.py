
import traceback
import logging
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class ErrorMiddleware:
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception as e:
            # Log l'erreur
            logger.error(f"Erreur non gérée: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Créer une réponse d'erreur
            response = self.handle_exception(e)
            return response(environ, start_response)
    
    def handle_exception(self, e):
        """Convertit l'exception en une réponse appropriée"""
        if isinstance(e, HTTPException):
            # Gestion des erreurs HTTP (404, 403, etc.)
            return self.app.make_response((
                render_template('errors/generic.html', 
                               error_code=e.code,
                               error_name=e.name,
                               error_description=e.description),
                e.code
            ))
        elif isinstance(e, SQLAlchemyError):
            # Gestion des erreurs de base de données
            from app import db
            db.session.rollback()  # Annuler la transaction en cours
            return self.app.make_response((
                render_template('errors/db_error.html',
                               error_message="Une erreur de base de données s'est produite."),
                500
            ))
        else:
            # Autres exceptions
            return self.app.make_response((
                render_template('errors/500.html',
                               error_message="Une erreur inattendue s'est produite."),
                500
            ))
