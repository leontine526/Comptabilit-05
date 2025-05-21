
"""
Point d'entrée WSGI pour l'application en production
Prend en charge l'initialisation et les configurations spécifiques au déploiement
"""
import os
from error_handlers import register_error_handlers
import sys
import logging
from logging.handlers import RotatingFileHandler

# Assure que le chemin de l'application est dans le PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configuration avancée du logging
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configuration du handler de fichier
file_handler = RotatingFileHandler('logs/application.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

# Configuration du handler de console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# Configuration du logger root
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Import de l'application
from main import app as application
from error_handlers import register_error_handlers

# Enregistrer les gestionnaires d'erreur
register_error_handlers(application)

# Initialisation des variables d'environnement de production
os.environ['FLASK_ENV'] = 'production'

# Ajout des middlewares de production
if not application.debug:
    # Compression Gzip pour améliorer les performances
    try:
        from flask_compress import Compress
        compress = Compress()
        compress.init_app(application)
        root_logger.info("Flask-Compress initialisé")
    except ImportError:
        root_logger.warning("Flask-Compress n'est pas installé, pas de compression Gzip")
    
    # Cache pour améliorer les performances
    try:
        from flask_caching import Cache
        cache = Cache(config={
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': 300
        })
        cache.init_app(application)
        root_logger.info("Flask-Cache initialisé")
    except ImportError:
        root_logger.warning("Flask-Cache n'est pas installé, pas de mise en cache")

# Gestion des erreurs non capturées
@application.errorhandler(500)
def internal_error(error):
    root_logger.error(f"Erreur 500 non gérée: {str(error)}")
    return "Une erreur interne s'est produite. Notre équipe a été notifiée.", 500

# Point d'entrée pour un serveur WSGI
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
