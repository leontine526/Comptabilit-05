
import os
import sys
import logging
import traceback
from app import app, db
from sqlalchemy import text
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_new_database():
    """Initialiser la nouvelle base de données avec les tables nécessaires"""
    load_dotenv()
    
    logger.info("Initialisation de la nouvelle base de données...")
    
    try:
        with app.app_context():
            # Vérifier que nous pouvons nous connecter à la nouvelle base de données
            logger.info("Test de connexion à la base de données...")
            db.engine.connect()
            logger.info("Connexion établie avec succès")
            
            # Créer toutes les tables
            logger.info("Création des tables...")
            db.create_all()
            logger.info("Tables créées avec succès")
            
            # Vérifier quelles tables ont été créées
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            logger.info(f"Tables créées: {', '.join(tables)}")
            
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Traceback: {traceback_str}")
        return False

if __name__ == "__main__":
    if initialize_new_database():
        logger.info("Base de données initialisée avec succès")
    else:
        logger.error("Échec de l'initialisation de la base de données")
        sys.exit(1)
