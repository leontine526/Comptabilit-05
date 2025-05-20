import os
import logging
import sys
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupère l'URL de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("DATABASE_URL non définie. Assurez-vous qu'elle est correctement configurée dans .env ou les variables d'environnement.")

# Importe l'application Flask et l'instance SocketIO
try:
    from app import app, socketio
    logger.info("Application Flask et Socket.IO importés avec succès")
except Exception as e:
    logger.critical(f"Erreur critique lors de l'importation de l'application: {str(e)}")
    sys.exit(1)

# Affiche les informations sur la base de données
db_url = os.getenv("DATABASE_URL", "Non définie")
if db_url and db_url != "Non définie":
    # Masquer les informations sensibles dans les logs
    safe_url = db_url.split('@')[1] if '@' in db_url else 'Hidden for security'
    logger.info(f"Configuration de la base de données: {safe_url}")
    if "postgres" in db_url.lower():
        logger.info("Type de base de données: PostgreSQL (externe)")
    elif "sqlite" in db_url.lower():
        logger.info("Type de base de données: SQLite (locale)")
else:
    logger.warning("DATABASE_URL non définie, utilisation de la base de données SQLite locale par défaut")

# Initialisation de la base de données avec notre helper
try:
    from db_helper import init_db_connection
    # Tente d'établir la connexion à la base de données
    if init_db_connection():
        logger.info("Connexion à la base de données établie avec succès")
    else:
        logger.warning("Impossible d'établir une connexion à la base de données. L'application peut rencontrer des erreurs.")
except ImportError:
    logger.warning("Module db_helper non trouvé, la vérification de connexion à la base de données sera ignorée")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de la connexion à la base de données: {str(e)}")

# Importe les gestionnaires d'événements Socket.IO
try:
    import socket_events
    logger.info("Gestionnaires d'événements Socket.IO chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des gestionnaires Socket.IO: {str(e)}")

# Importer toutes les routes nécessaires
from routes import routes
app.register_blueprint(routes)
logger.info("Routes chargées avec succès")

# Importe les gestionnaires d'erreurs
try:
    import error_handlers
    logger.info("Gestionnaires d'erreurs chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des gestionnaires d'erreurs: {str(e)}")

# Point d'entrée pour Gunicorn avec Socket.IO
# L'application sera démarrée automatiquement avec Gunicorn 
# en utilisant le workflow configuré dans Replit
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Initialiser la base de données une seule fois
    try:
        from db_initialize import initialize_database
        with app.app_context():
            if not hasattr(app, 'db_initialized'):
                if initialize_database():
                    app.db_initialized = True
                    logger.info("Base de données initialisée avec succès")
                else:
                    logger.warning("Problème lors de l'initialisation de la base de données")
    except ImportError:
        logger.warning("Module db_initialize introuvable")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")

    try:
        logger.info("Démarrage du serveur Socket.IO")
        # Optimisation pour la production si l'environnement n'est pas de développement
        import os
        debug_mode = os.environ.get('FLASK_ENV') == 'development'
        
        # Configurer l'environnement Replit pour la production
        is_replit_prod = os.environ.get('REPL_SLUG') and not debug_mode
        
        # Choisir la configuration appropriée
        from config import config
        config_name = 'production' if is_replit_prod else 'development'
        logger.info(f"Utilisation de la configuration: {config_name}")
        app.config.from_object(config[config_name])

        # Utiliser gunicorn en production, eventlet sinon
        if os.environ.get('GUNICORN_WORKERS') or is_replit_prod:
            # Configuration pour production
            app.run(host='0.0.0.0', port=5000, debug=False)
        else:
            # Démarrage avec Eventlet pour Socket.IO en développement
            port = int(os.getenv('PORT', 5000))
            socketio.run(app, 
                        host='0.0.0.0',
                        port=port,
                        debug=debug_mode,
                        allow_unsafe_werkzeug=True,
                        log_output=True)
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du serveur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)