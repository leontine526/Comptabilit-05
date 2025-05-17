
import os
from dotenv import load_dotenv
import psycopg2
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get database connection string
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    logger.error("DATABASE_URL environment variable not set!")
    exit(1)

# Masquer les informations sensibles dans les logs
safe_url = db_url.split('@')[1] if '@' in db_url else 'Hidden for security'
logger.info(f"Tentative de connexion à la base de données: {safe_url}")

try:
    # Test direct connection with psycopg2
    logger.info("Test de connexion avec psycopg2...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    logger.info(f"Connexion réussie! Version PostgreSQL: {version[0]}")
    cur.close()
    conn.close()
    
    # Test connection with SQLAlchemy
    logger.info("Test de connexion avec SQLAlchemy...")
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        logger.info(f"Connexion SQLAlchemy réussie: {result.fetchone()}")
    
    logger.info("Tests de connexion à la base de données réussis!")
    
except Exception as e:
    logger.error(f"Erreur de connexion à la base de données: {str(e)}")
    exit(1)

if __name__ == "__main__":
    print("Script de test de connexion à la base de données terminé avec succès.")
