
import os
import sys
import logging
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to PostgreSQL database specified in DATABASE_URL."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get database URL from environment variables
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL is not defined in environment variables")
        return False
    
    logger.info(f"Tentative de connexion à la base de données: {database_url.split('@')[1]}")
    
    # Test with psycopg2
    try:
        logger.info("Test de connexion avec psycopg2...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        logger.info(f"Connexion réussie! Version PostgreSQL: {version}")
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur de connexion avec psycopg2: {str(e)}")
        return False
    
    # Test with SQLAlchemy
    try:
        logger.info("Test de connexion avec SQLAlchemy...")
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info(f"Connexion SQLAlchemy réussie: {result.fetchone()}")
    except Exception as e:
        logger.error(f"Erreur de connexion avec SQLAlchemy: {str(e)}")
        return False
    
    logger.info("Tests de connexion à la base de données réussis!")
    return True

if __name__ == "__main__":
    success = test_connection()
    print("Script de test de connexion à la base de données terminé avec succès!" if success 
          else "Échec du test de connexion à la base de données.")
    sys.exit(0 if success else 1)
