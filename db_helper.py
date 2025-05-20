"""
The code implements improved transaction management and recovery in database operations.
"""
import logging
import time
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, OperationalError, DisconnectionError
from app import db
from sqlalchemy import text

logger = logging.getLogger(__name__)

def safe_db_operation(max_retries=3):
    """Décorateur pour réessayer des opérations de base de données en cas d'erreur de connexion"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            last_error = None

            while retry_count < max_retries:
                try:
                    # Créer une nouvelle session si la session actuelle est en état d'erreur
                    if hasattr(db, 'session') and db.session.is_active:
                        session_status = "active"
                        try:
                            # Tester si la transaction est en état d'échec
                            db.session.execute(text("SELECT 1"))
                        except Exception:
                            session_status = "error"
                            db.session.rollback()
                            db.session.close()
                            db.create_scoped_session()

                    result = func(*args, **kwargs)
                    return result

                except (SQLAlchemyError, OperationalError) as e:
                    retry_count += 1
                    last_error = e

                    # S'assurer que la transaction est annulée proprement
                    try:
                        db.session.rollback()
                    except Exception:
                        pass

                    logger.warning(
                        f"Erreur de base de données dans {func.__name__}: {str(e)}. "
                        f"Tentative {retry_count}/{max_retries}."
                    )

                    # Si c'est la dernière tentative, réinitialiser la connexion
                    if retry_count == max_retries - 1:
                        logger.info("Tentative de réinitialisation de la connexion à la base de données...")
                        try:
                            db.session.close()
                            db.engine.dispose()
                        except Exception:
                            pass
                        init_db_connection()

                    # Temps d'attente exponentiel entre les tentatives
                    wait_time = 0.1 * (2 ** (retry_count - 1))
                    time.sleep(wait_time)

            # Si toutes les tentatives échouent, logger l'erreur et la relancer
            logger.error(
                f"Échec de l'opération {func.__name__} après {max_retries} tentatives. "
                f"Dernière erreur: {str(last_error)}"
            )
            raise last_error
        return wrapper
    return decorator

def init_db_connection():
    """Initialiser ou réinitialiser la connexion à la base de données"""
    from app import app, db
    import os
    from sqlalchemy.engine.url import make_url
    from sqlalchemy import create_engine, text
    import logging

    logger = logging.getLogger(__name__)
    max_attempts = 5  # Augmenter le nombre de tentatives
    attempt = 1
    connect_timeout = 10  # Augmenter le timeout de connexion

    # Forcer l'utilisation de l'URL PostgreSQL avec paramètres optimisés
    database_url = os.environ.get('DATABASE_URL', "postgresql://neondb_owner:npg_Crwao4WUkt5f@ep-spring-pond-a5upovj4-pooler.us-east-2.aws.neon.tech/neondb")
    # Ajouter les paramètres de connexion optimisés
    database_url += "?sslmode=require&connect_timeout=15&application_name=smartohada&keepalives=1&keepalives_idle=30&keepalives_interval=10&keepalives_count=5"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,  # Réduire la taille du pool
        "pool_recycle": 280,  # Recycler avant l'expiration du serveur (5 min)
        "pool_pre_ping": True,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_timeout": 30
    }

    with app.app_context():
        # Optimiser l'URL pour utiliser le connection pooler de Neon
        database_url = os.environ.get("DATABASE_URL")
        if database_url and 'neon.tech' in database_url:
            # Vérifier si l'URL utilise déjà le connection pooler
            if '-pooler' not in database_url:
                try:
                    url_obj = make_url(database_url)
                    host = url_obj.host
                    # Remplacer le host normal par la version pooler
                    pooler_host = host.replace('.', '-pooler.', 1)
                    new_url = database_url.replace(host, pooler_host)
                    logger.info(f"URL de base de données optimisée pour connection pooling")
                    # Mettre à jour l'URL dans l'application
                    app.config["SQLALCHEMY_DATABASE_URI"] = new_url
                except Exception as e:
                    logger.warning(f"Impossible d'optimiser l'URL pour le connection pooling: {str(e)}")
            else:
                logger.info("L'URL utilise déjà le connection pooler Neon")

        # S'assurer que les dossiers nécessaires existent
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('examples', exist_ok=True)

        while attempt <= max_attempts:
            try:
                # Réinitialiser le pool de connexions
                db.engine.dispose()

                # Essayer de faire une requête simple pour tester la connexion
                with db.engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    # Vérifier que la requête a bien retourné un résultat
                    if result.scalar() == 1:
                        logger.info("Connexion à la base de données établie avec succès")
                        return True
                    else:
                        logger.warning("La requête de test a retourné une valeur inattendue")
            except Exception as e:
                logger.warning(f"Tentative {attempt}/{max_attempts} de connexion à la base de données échouée: {str(e)}")

            # Incrémenter le compteur d'essais
            attempt += 1

            if attempt <= max_attempts:
                time.sleep(2)  # Attendre avant de réessayer

        logger.error(f"Impossible d'établir une connexion à la base de données après {max_attempts} tentatives")
        return False

def check_db_connection():
    """Vérifie si la connexion à la base de données est active"""
    from app import db

    try:
        # Exécuter une requête simple pour vérifier la connexion
        with db.engine.connect() as conn:
            conn.execute(db.text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {str(e)}")
        db.session.rollback()
        return False