
import os
import sys
import logging
import traceback
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """Tester la connexion à la base de données"""
    load_dotenv()  # Charger les variables d'environnement
    
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL n'est pas définie dans les variables d'environnement")
        return False
    
    logger.info(f"Test de connexion à: {database_url.split('@')[1] if '@' in database_url else 'URL masquée'}")
    
    try:
        # Créer un moteur SQLAlchemy
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )
        
        # Tester la connexion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Connexion à la base de données établie avec succès!")
                
                # Afficher les tables existantes
                tables_result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='public'
                    ORDER BY table_name;
                """))
                tables = [row[0] for row in tables_result]
                
                if tables:
                    logger.info(f"Tables existantes: {', '.join(tables)}")
                else:
                    logger.info("Aucune table n'existe encore dans cette base de données.")
                
                return True
            else:
                logger.error("❌ La requête de test a échoué")
                return False
    except Exception as e:
        logger.error(f"❌ Erreur de connexion: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n✅ La connexion à la base de données a réussi!")
        sys.exit(0)
    else:
        print("\n❌ La connexion à la base de données a échoué!")
        sys.exit(1)
