import os
import logging
import sqlite3

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_sqlite_uri():
    """Retourne l'URI de connexion à la base de données SQLite"""
    # Utiliser un fichier dans le répertoire courant
    base_dir = os.path.abspath(os.path.dirname(__file__))
    return f"sqlite:///{os.path.join(base_dir, 'smartohada.db')}"

def init_sqlite_db():
    """Initialise la base de données SQLite si elle n'existe pas déjà"""
    try:
        logger.info("Initialisation de la base de données SQLite...")
        # Vérifier si le fichier existe déjà
        base_dir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(base_dir, 'smartohada.db')

        # Si la base de données n'existe pas, on la crée
        # (La création effective des tables sera faite par SQLAlchemy)
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.close()
            logger.info(f"Base de données SQLite créée à {db_path}")

        logger.info("Base de données SQLite initialisée avec succès!")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données SQLite: {str(e)}")
        return False