
import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_tables():
    """Vérifie l'état des tables dans la base de données"""
    print("=== VÉRIFICATION DES TABLES DE LA BASE DE DONNÉES ===")
    
    # Récupérer l'URL de la base de données
    database_url = os.environ.get("DATABASE_URL", 
                                "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
    
    try:
        # Créer le moteur SQLAlchemy
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=60,
            pool_pre_ping=True,
        )
        
        logger.info("Tentative de connexion à la base de données...")
        
        # Tester la connexion
        with engine.connect() as conn:
            # Vérifier si la connexion est active
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Connexion à la base de données établie avec succès!")
                
                # Vérifier si des tables existent
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                if tables:
                    logger.info(f"✅ {len(tables)} tables trouvées dans la base de données:")
                    for i, table in enumerate(tables, 1):
                        logger.info(f"  {i}. {table}")
                    
                    # Vérifier si les tables principales existent
                    required_tables = ['user', 'exercise', 'account', 'transaction', 'post']
                    missing_tables = [table for table in required_tables if table not in tables]
                    
                    if missing_tables:
                        logger.warning(f"⚠️ Tables requises manquantes: {', '.join(missing_tables)}")
                    else:
                        logger.info("✅ Toutes les tables requises existent")
                    
                    # Compter les enregistrements dans quelques tables
                    for table in ['user', 'exercise', 'post']:
                        if table in tables:
                            count = conn.execute(text(f"SELECT COUNT(*) FROM \"{table}\"")).fetchone()[0]
                            logger.info(f"Table '{table}': {count} enregistrements")
                else:
                    logger.warning("⚠️ Aucune table n'existe dans la base de données")
                    logger.info("La base de données est vide et doit être initialisée")
            
            return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification de la base de données: {str(e)}")
        return False

if __name__ == "__main__":
    if check_database_tables():
        print("\n✅ Vérification des tables de la base de données terminée")
        sys.exit(0)
    else:
        print("\n❌ La vérification des tables de la base de données a échoué")
        sys.exit(1)
