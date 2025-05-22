
import os
import logging
import traceback
from flask import request, render_template, jsonify
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError
from app import db

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Enregistre tous les gestionnaires d'erreur pour l'application Flask"""

    @app.errorhandler(404)
    def page_not_found(e):
        """Gestionnaire pour les erreurs 404 (page non trouvée)"""
        logger.warning(f"Page non trouvée: {request.path}")

        # Vérifier si la requête attend du JSON 
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Page non trouvée", message=str(e)), 404

        return render_template('errors/404.html', error=str(e)), 404

    @app.errorhandler(403)
    def forbidden_error(e):
        """Gestionnaire pour les erreurs 403 (accès interdit)"""
        logger.warning(f"Accès interdit: {request.path}")

        # Vérifier si la requête attend du JSON
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Accès interdit", message=str(e)), 403

        return render_template('errors/403.html', error=str(e)), 403

    @app.errorhandler(400)
    def bad_request(e):
        """Gestionnaire pour les erreurs 400 (requête invalide)"""
        logger.warning(f"Requête invalide: {request.path}")

        # Vérifier si la requête attend du JSON
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Requête invalide", message=str(e)), 400

        return render_template('errors/400.html', error=str(e)), 400

    @app.errorhandler(500)
    def internal_server_error(e):
        """Gestionnaire pour les erreurs 500 (erreur interne du serveur)"""
        logger.error(f"Erreur 500: {str(e)}")
        logger.error(traceback.format_exc())

        # Essayer de faire un rollback sur la session SQLAlchemy
        try:
            db.session.rollback()
        except Exception:
            pass

        # Vérifier si la requête attend du JSON
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Erreur interne du serveur", message="Une erreur inattendue s'est produite"), 500

        return render_template('errors/500.html', error=str(e)), 500

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        """Gestionnaire pour les erreurs de base de données"""
        logger.error(f"Erreur de base de données: {str(e)}")
        logger.error(traceback.format_exc())

        # Essayer de faire un rollback sur la session SQLAlchemy si possible
        try:
            db.session.rollback()
            logger.info("Transaction annulée automatiquement après une erreur de base de données")
        except Exception as rollback_error:
            logger.error(f"Erreur lors de l'annulation de la transaction: {str(rollback_error)}")

        # Vérifier si la requête attend du JSON
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Erreur de base de données", 
                          message="Une erreur de connexion à la base de données s'est produite"), 500

        return render_template('errors/db_error.html', error=str(e)), 500

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Gestionnaire pour toutes les autres exceptions non gérées"""
        logger.error(f"Erreur non gérée: {str(e)}")
        logger.error(traceback.format_exc())

        # Essayer de faire un rollback sur la session SQLAlchemy
        try:
            db.session.rollback()
        except Exception:
            pass

        # Vérifier si l'environnement est en développement
        is_debug = os.environ.get('FLASK_ENV') == 'development'

        # Vérifier si la requête attend du JSON
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Erreur non gérée", 
                          message=str(e) if is_debug else "Une erreur inattendue s'est produite"), 500

        return render_template('errors/500.html', error=str(e) if is_debug else "Une erreur inattendue s'est produite"), 500
