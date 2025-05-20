
import os
import sys
import logging
import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_new_connection():
    """Tester la connexion à la nouvelle base de données"""
    # Nouvelle URL de base de données
    database_url = "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    
    logger.info("Test de connexion à la nouvelle base de données")
    
    try:
        # Créer un moteur SQLAlchemy
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=60,
            pool_pre_ping=True,
        )
        
        # Tester la connexion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Connexion à la nouvelle base de données établie avec succès!")
                
                # Vérifier si des tables existent
                try:
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
                except Exception as e:
                    logger.error(f"Erreur lors de la vérification des tables: {str(e)}")
                
                return True
            else:
                logger.error("❌ La requête de test a échoué")
                return False
    except SQLAlchemyError as e:
        logger.error(f"❌ Erreur SQLAlchemy: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        logger.error(f"❌ Erreur de connexion: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_new_connection():
        print("\n✅ La connexion à la nouvelle base de données a réussi!")
        sys.exit(0)
    else:
        print("\n❌ La connexion à la nouvelle base de données a échoué!")
        sys.exit(1)
