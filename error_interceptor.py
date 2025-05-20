
import traceback
import logging
from flask import render_template, request, jsonify
from app import app, db
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError

logger = logging.getLogger(__name__)

class ErrorInterceptor:
    @staticmethod
    def init_app(app):
        """Initialise l'intercepteur d'erreurs pour l'application Flask"""
        
        @app.errorhandler(Exception)
        def handle_exception(e):
            """Gestionnaire d'exceptions global"""
            # Essayer de faire un rollback de la session DB si nécessaire
            try:
                db.session.rollback()
            except:
                pass
                
            # Logger l'erreur avec des détails
            error_details = {
                'route': request.path,
                'method': request.method,
                'user_agent': request.user_agent.string,
                'referrer': request.referrer
            }
            
            logger.error(f"Exception non gérée: {str(e)}", exc_info=True, extra=error_details)
            
            # Si c'est une erreur API avec JSON attendu
            if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': False,
                    'error': 'Une erreur serveur est survenue',
                    'error_code': 'SERVER_ERROR'
                }), 500
                
            # Sinon renvoyer une page d'erreur HTML
            return render_template('errors/500.html', error_info={
                'message': str(e),
                'type': e.__class__.__name__
            }), 500
            
        @app.errorhandler(SQLAlchemyError)
        def handle_db_error(e):
            """Gestionnaire spécifique pour les erreurs de base de données"""
            try:
                db.session.rollback()
            except:
                pass
                
            # Tenter de reconnecter si c'est une erreur de connexion
            if isinstance(e, (OperationalError, DisconnectionError)):
                from db_helper import init_db_connection
                init_db_connection()
                
            logger.error(f"Erreur SQL: {str(e)}", exc_info=True)
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Une erreur de base de données est survenue',
                    'error_code': 'DATABASE_ERROR'
                }), 500
                
            return render_template('errors/db_error.html'), 500

# Initialiser l'intercepteur dans main.py
def initialize():
    ErrorInterceptor.init_app(app)
