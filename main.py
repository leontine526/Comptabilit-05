import os
from error_handlers import register_error_handlers
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
    # Enregistrer les gestionnaires d'erreur
    register_error_handlers(app)
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
try:
    # Importation explicite de la route principale pour s'assurer qu'elle est correctement enregistrée
    from routes import index
    # Puis importer toutes les autres routes
    from routes import about, welcome, health_check, login, logout, register, dashboard
    from routes import *
    logger.info("Routes chargées avec succès")
except ImportError as e:
    logger.error(f"Erreur lors du chargement des routes: {str(e)}")

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

    # Configuration du logging améliorée
    log_level = logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )

    # Initialiser le gestionnaire d'erreurs
    try:
        import error_interceptor
        if hasattr(error_interceptor, 'initialize'):
            error_interceptor.initialize()
        elif hasattr(error_interceptor, 'ErrorInterceptor'):
            error_interceptor.ErrorInterceptor.init_app(app)
        logger.info("Gestionnaire d'erreurs initialisé avec succès")
    except ImportError:
        logger.warning("Module error_interceptor non trouvé, les erreurs ne seront pas interceptées")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du gestionnaire d'erreurs: {str(e)}")

    # Initialiser la base de données une seule fois avec gestion d'erreurs robuste
    try:
        from db_initialize import initialize_database
        from db_helper import init_db_connection

        # Vérifier d'abord la connexion à la base de données
        if init_db_connection():
            logger.info("Connexion à la base de données établie avec succès")

            # Initialiser les tables si nécessaire
            with app.app_context():
                if not hasattr(app, 'db_initialized'):
                    if initialize_database():
                        app.db_initialized = True
                        logger.info("Base de données initialisée avec succès")
                    else:
                        logger.warning("Problème lors de l'initialisation de la base de données")
        else:
            logger.error("Impossible d'établir une connexion à la base de données. Vérifiez les paramètres de connexion.")
    except ImportError as e:
        logger.warning(f"Module manquant: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        logger.error(traceback.format_exc())

    # Démarrer le moniteur de performances
    try:
        from performance_monitor import start_monitoring
        performance_monitor = start_monitoring()
        logger.info("Moniteur de performances démarré avec succès")
    except ImportError:
        logger.warning("Module performance_monitor non trouvé, le monitoring ne sera pas activé")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du moniteur de performances: {str(e)}")

    # Vérification de l'état avant démarrage
    try:
        from health_check import check_database
        if not check_database():
            logger.warning("La vérification de la base de données a échoué. L'application peut ne pas fonctionner correctement.")
    except ImportError:
        logger.warning("Module health_check non trouvé, la vérification de l'état ne sera pas effectuée")
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état: {str(e)}")

    try:
        logger.info("Démarrage du serveur")
        # Optimisation pour la production si l'environnement n'est pas de développement
        import os
        debug_mode = os.environ.get('FLASK_ENV') == 'development'

        # Configurer l'environnement pour la production
        is_prod = os.environ.get('FLASK_ENV') == 'production'

        # Choisir la configuration appropriée
        from config import config
        config_name = 'production' if is_prod else 'development'
        logger.info(f"Utilisation de la configuration: {config_name}")
        app.config.from_object(config[config_name])

        # Déterminer le port
        port = int(os.getenv('PORT', 5000))

        # Utiliser gunicorn en production, eventlet sinon
        if is_prod:
            # Configuration pour production
            logger.info(f"Démarrage en mode production sur le port {port}")
            socketio.run(app, 
                        host='0.0.0.0',
                        port=port,
                        debug=False,
                        allow_unsafe_werkzeug=True)
        else:
            # Démarrage avec Eventlet pour Socket.IO en développement
            logger.info(f"Démarrage en mode développement sur le port {port}")
            from maintenance_mode import init_maintenance_mode

            # Initialiser le mode maintenance
            init_maintenance_mode(app)
            socketio.run(app, 
                        host='0.0.0.0',
                        port=port,
                        debug=debug_mode,
                        allow_unsafe_werkzeug=True,
                        log_output=True)
    except Exception as e:
        logger.error(f"Erreur critique lors du démarrage du serveur: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)