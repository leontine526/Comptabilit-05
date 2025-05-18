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
    from app import app
    max_attempts = 5
    attempt = 1

    with app.app_context():
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
        # Test the connection with a simple query
        db.session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {str(e)}")
        return False