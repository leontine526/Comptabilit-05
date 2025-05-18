import os
import traceback
import logging
import json
from datetime import datetime
from flask import render_template, request, jsonify, current_app
from flask_login import current_user
from app import app
from sqlalchemy.exc import SQLAlchemyError

# Configuration du logger
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('logs/app.log'),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

@app.errorhandler(404)
def page_not_found(e):
    """Gestionnaire pour les erreurs 404 (Page non trouvée)"""
    # Log de base pour les 404
    logger.info(f"404 Page not found: {request.path} - User IP: {request.remote_addr}")

    return render_template('errors/404.html', 
                          requested_url=request.path), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Gestionnaire pour les erreurs 500 (Erreur interne)"""
    # Log détaillé pour les erreurs 500
    error_id = log_error(e, 500)

    # Vérifier le mode de débogage
    debug_mode = current_app.config.get('DEBUG', False)

    # En mode de production, masquer les détails de l'erreur
    if not debug_mode:
        return render_template('errors/500.html', 
                              error_id=error_id), 500

    # En mode de débogage, montrer plus de détails
    return render_template('errors/500.html',
                          error_id=error_id,
                          error_message=str(e),
                          traceback=traceback.format_exc()), 500

@app.errorhandler(403)
def forbidden(e):
    """Gestionnaire pour les erreurs 403 (Accès interdit)"""
    # Log l'erreur d'accès
    logger.warning(f"403 Forbidden access: {request.path} - User: {current_user.id if not current_user.is_anonymous else 'Anonymous'} - IP: {request.remote_addr}")

    return render_template('errors/403.html'), 403

@app.errorhandler(400)
def bad_request(e):
    """Gestionnaire pour les erreurs 400 (Requête incorrecte)"""
    # Log l'erreur de requête
    logger.info(f"400 Bad request: {request.path} - Data: {request.form or request.args or request.json}")

    return render_template('errors/400.html', error=str(e)), 400

@app.errorhandler(405)
def method_not_allowed(e):
    """Gestionnaire pour les erreurs 405 (Méthode non autorisée)"""
    # Log l'erreur de méthode
    logger.info(f"405 Method not allowed: {request.method} {request.path}")

    return render_template('errors/405.html', 
                          method=request.method,
                          allowed_methods=e.valid_methods), 405

@app.errorhandler(413)
def request_entity_too_large(e):
    """Gestionnaire pour les erreurs 413 (Entité trop grande)"""
    # Log l'erreur de taille
    logger.info(f"413 Request entity too large: {request.path} - Content-Length: {request.headers.get('Content-Length', 'Unknown')}")

    return render_template('errors/413.html'), 413

@app.errorhandler(429)
def too_many_requests(e):
    """Gestionnaire pour les erreurs 429 (Trop de requêtes)"""
    # Log l'erreur de rate limit
    logger.warning(f"429 Too many requests: {request.path} - User: {current_user.id if not current_user.is_anonymous else 'Anonymous'} - IP: {request.remote_addr}")

    return render_template('errors/429.html'), 429

# Gestionnaire spécifique pour les erreurs de base de données
@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    """Gestionnaire pour les erreurs de base de données"""
    # Annuler toute transaction en cours pour éviter les erreurs "transaction aborted"
    try:
        db.session.rollback()
        logger.info("Transaction en cours annulée avec succès")
    except Exception as rollback_error:
        logger.error(f"Erreur lors de l'annulation de la transaction: {str(rollback_error)}")
    
    # Log détaillé de l'erreur DB
    error_id = log_error(e, 'DB')

    # En mode de débogage, montrer plus de détails
    if current_app.config.get('DEBUG', False):
        return render_template('errors/db_error.html',
                              error_id=error_id,
                              error=str(e)), 500

    # En production, juste une erreur générique
    return render_template('errors/db_error.html',
                          error_id=error_id), 500

def log_error(error, code):
    """
    Log les détails de l'erreur dans le fichier de log
    Retourne un identifiant unique pour l'erreur
    """
    # Générer un ID unique pour cette erreur
    error_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(str(error)) % 10000}"

    # Collecter les détails de l'erreur
    error_details = {
        'error_id': error_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'error_code': code,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'route': request.path,
        'method': request.method,
        'args': dict(request.args),
        'form': sanitize_data(request.form),  # Masquer les données sensibles
        'json': sanitize_data(request.json) if request.is_json else None,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'user_id': current_user.id if not getattr(current_user, 'is_anonymous', True) else None,
        'referrer': request.referrer,
        'traceback': traceback.format_exc()
    }

    # Log l'erreur de manière structurée
    logger.error(f"Error {code} [{error_id}] on {request.path}: {str(error)}")
    logger.error(f"Error details: {json.dumps(error_details, default=str)}")

    # Log traceback complet
    logger.error(f"Traceback for [{error_id}]: {traceback.format_exc()}")

    return error_id

def sanitize_data(data):
    """Masque les données sensibles dans les formulaires et JSON"""
    if not data:
        return {}

    # Conversion en dict si c'est un objet de forme immutabledict
    if hasattr(data, 'to_dict'):
        data = data.to_dict()

    # Liste des mots-clés sensibles à masquer
    sensitive_keys = ['password', 'token', 'secret', 'key', 'auth', 'credential', 'pwd', 'pass']

    # Fonction pour déterminer si une clé est sensible
    def is_sensitive(key):
        return any(s in key.lower() for s in sensitive_keys)

    # Masquer les données sensibles
    sanitized = {}
    for key, value in data.items():
        if is_sensitive(key):
            sanitized[key] = '******'
        else:
            sanitized[key] = value

    return sanitized