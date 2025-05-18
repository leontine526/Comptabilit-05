"""
Utilitaires pour gérer la connexion à la base de données et récupération d'erreurs
"""
import logging
import time
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, OperationalError, DisconnectionError
from app import db
from sqlalchemy import text

logger = logging.getLogger(__name__)

def safe_db_operation(max_retries=3, retry_delay=1):
    """
    Décorateur pour gérer en toute sécurité les opérations de base de données avec des tentatives de reconnexion

    Args:
        max_retries (int): Nombre maximum de tentatives de reconnexion
        retry_delay (int): Délai en secondes entre les tentatives
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_error = None

            while retries < max_retries:
                try:
                    # Exécute la fonction avec ses arguments
                    result = func(*args, **kwargs)
                    # Si on arrive ici, l'opération a réussi
                    return result
                except (OperationalError, DisconnectionError) as e:
                    # Erreurs de connexion, on peut réessayer
                    last_error = e
                    retries += 1
                    logger.warning(f"Erreur de connexion à la base de données: {str(e)}. Tentative {retries}/{max_retries}")

                    # Annuler toute transaction en cours
                    try:
                        db.session.rollback()
                    except Exception:
                        pass
                    
                    # Réinitialiser complètement la session
                    db.session.remove()
                    
                    # Si nécessaire, reconnecter le moteur de base de données
                    if "connection" in str(e).lower() or "timeout" in str(e).lower():
                        try:
                            db.engine.dispose()
                            logger.info("Moteur de base de données réinitialisé")
                        except Exception as dispose_error:
                            logger.error(f"Erreur lors de la réinitialisation du moteur: {str(dispose_error)}")

                    # Attendre avant de réessayer
                    time.sleep(retry_delay)
                except (SQLAlchemyError, DBAPIError) as e:
                    # Autres erreurs SQLAlchemy, on annule la transaction
                    last_error = e
                    logger.error(f"Erreur SQLAlchemy: {str(e)}")

                    # Toujours annuler la transaction en cours
                    try:
                        db.session.rollback()
                        logger.info("Transaction annulée avec succès")
                    except Exception as rollback_error:
                        logger.error(f"Erreur lors de l'annulation: {str(rollback_error)}")
                        # En cas d'erreur d'annulation, on réinitialise complètement la session
                        db.session.remove()
                        
                    # Si c'est une erreur de transaction avortée, on peut réessayer
                    if "current transaction is aborted" in str(e) or "inactive transaction" in str(e):
                        retries += 1
                        logger.warning(f"Transaction avortée, tentative de récupération {retries}/{max_retries}")
                        # Réinitialiser la session pour s'assurer d'avoir une transaction propre
                        db.session.remove()
                        time.sleep(retry_delay)
                    else:
                        # Pour les autres erreurs, on arrête et on remonte l'erreur
                        raise

            # Si on atteint ce point, c'est qu'on a dépassé le nombre de tentatives
            logger.error(f"Échec après {max_retries} tentatives. Dernière erreur: {str(last_error)}")
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