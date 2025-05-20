
"""
Script de diagnostic détaillé pour la connexion à la base de données
"""
import os
import logging
import sys
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/db_check.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Fonction principale de diagnostic"""
    logger.info("=== DIAGNOSTIC DÉTAILLÉ DE LA BASE DE DONNÉES ===")
    
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Récupération de l'URL de la base de données
    database_url = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
    
    if not database_url:
        logger.error("❌ DATABASE_URL n'est pas définie")
        return False
    
    # Extraction des informations de la base pour affichage sécurisé
    masked_url = database_url.replace(database_url.split('@')[0], "***HIDDEN***")
    logger.info(f"URL de la base de données: {masked_url}")
    
    # Test de connexion direct avec SQLAlchemy
    try:
        logger.info("Tentative de connexion avec SQLAlchemy...")
        engine = create_engine(
            database_url,
            echo=False,
            pool_size=1,
            pool_timeout=10,
            connect_args={"connect_timeout": 10}
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("✅ Connexion SQLAlchemy établie avec succès")
            else:
                logger.error("❌ La requête de test a retourné une valeur inattendue")
                return False
        
        # Inspection des tables
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if tables:
                logger.info(f"✅ Tables trouvées dans la base de données: {', '.join(tables)}")
            else:
                logger.warning("⚠️ Aucune table trouvée dans la base de données")
            
            # Vérification de quelques tables essentielles
            essential_tables = ["users", "exercises", "transactions"]
            missing_tables = [table for table in essential_tables if table not in tables]
            
            if missing_tables:
                logger.warning(f"⚠️ Tables essentielles manquantes: {', '.join(missing_tables)}")
            else:
                logger.info("✅ Toutes les tables essentielles sont présentes")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'inspection des tables: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur de connexion SQLAlchemy: {str(e)}")
        return False
    
    # Test avec la classe DBConnectionManager
    try:
        logger.info("Tentative avec DBConnectionManager...")
        
        # Import dynamique pour éviter les erreurs circulaires
        try:
            from db_connection_manager import db_manager
            
            db_manager.initialize(
                database_url,
                max_retries=2,
                retry_delay=1,
                pool_size=1
            )
            
            if db_manager.check_health():
                logger.info("✅ Connexion via DBConnectionManager établie avec succès")
            else:
                logger.error("❌ Échec de la vérification de santé avec DBConnectionManager")
                return False
                
        except ImportError:
            logger.error("❌ Module db_connection_manager non trouvé ou non importable")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur avec DBConnectionManager: {str(e)}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Erreur générale: {str(e)}")
        return False
    
    # Test avec l'application Flask
    try:
        logger.info("Vérification de la connexion dans le contexte Flask...")
        
        # Import dynamique pour éviter les erreurs circulaires
        try:
            from app import app, db
            
            with app.app_context():
                # Test de la connexion
                result = db.session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    logger.info("✅ Connexion dans le contexte Flask établie avec succès")
                else:
                    logger.error("❌ La requête de test dans Flask a retourné une valeur inattendue")
                    return False
                
        except ImportError as e:
            logger.error(f"❌ Erreur d'import pour les tests Flask: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur dans le contexte Flask: {str(e)}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Erreur générale lors des tests Flask: {str(e)}")
        return False
    
    logger.info("=== DIAGNOSTIC TERMINÉ AVEC SUCCÈS ===")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Diagnostic de la base de données terminé avec succès")
            sys.exit(0)
        else:
            print("\n❌ Des problèmes ont été détectés dans la connexion à la base de données")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Erreur critique dans le script de diagnostic: {str(e)}", exc_info=True)
        sys.exit(2)
