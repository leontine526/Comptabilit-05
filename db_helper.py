"""
Module pour la connexion et la gestion de la base de données
"""
import os
import logging
import time
import traceback
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app import db, app
from functools import wraps

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db_connection(max_retries=3, retry_delay=2):
    """Initialise la connexion à la base de données avec retry"""
    for attempt in range(1, max_retries + 1):
        try:
            # Utiliser un contexte d'application pour la connexion
            with app.app_context():
                # Exécuter une requête simple pour vérifier la connexion
                from sqlalchemy import text
                result = db.session.execute(text("SELECT 1")).scalar()
                db.session.commit()
                logger.info("Connexion à la base de données établie avec succès")
                return True
        except Exception as e:
            # En cas d'erreur, loguer et réessayer
            logger.warning(f"Tentative {attempt}/{max_retries} - Erreur: {str(e)}")

            if attempt < max_retries:
                # Attendre avant de réessayer
                time.sleep(retry_delay)
            else:
                # Échec après toutes les tentatives
                logger.error("Échec de la connexion après plusieurs tentatives")
                return False
    return False

def safe_db_operation(max_retries=3, retry_delay=2):
    """Décorateur pour exécuter des opérations de base de données de manière sécurisée"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    # Utiliser un contexte d'application
                    with app.app_context():
                        result = func(*args, **kwargs)
                        return result
                except OperationalError as e:
                    logger.warning(f"Opération DB échouée (tentative {attempt}/{max_retries}): {str(e)}")
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                        # Si nécessaire, reconnecter à la base de données
                        try:
                            db.session.rollback()
                        except:
                            pass
                    else:
                        logger.error(f"Échec définitif de l'opération DB après {max_retries} tentatives")
                        raise
                except Exception as e:
                    logger.error(f"Erreur non gérée: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Rollback de la session
                    try:
                        db.session.rollback()
                    except:
                        pass
                    raise
        return wrapper
    return decorator