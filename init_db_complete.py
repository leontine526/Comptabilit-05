
import os
import sys
import logging
import traceback
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialisation complète de la base de données"""
    logger.info("=== INITIALISATION COMPLÈTE DE LA BASE DE DONNÉES ===")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Récupérer l'URL de la base de données
    database_url = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
    
    if not database_url:
        logger.error("L'URL de la base de données n'est pas définie")
        return False
    
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
                logger.info("✅ Connexion à la base de données établie avec succès")
            else:
                logger.error("❌ La requête de test a échoué")
                return False
        
        # Importer les éléments nécessaires pour créer les tables
        # Cette importation est faite ici pour éviter les problèmes de dépendances circulaires
        try:
            from app import app, db
            from models import User
            
            with app.app_context():
                # Vérifier si des tables existent déjà
                inspector = inspect(engine)
                existing_tables = inspector.get_table_names()
                
                if existing_tables:
                    logger.info(f"Tables existantes: {', '.join(existing_tables)}")
                else:
                    logger.info("Aucune table n'existe encore, création des tables...")
                    
                    # Créer toutes les tables définies dans models.py
                    db.create_all()
                    
                    # Vérifier que les tables ont été créées
                    inspector = inspect(engine)
                    created_tables = inspector.get_table_names()
                    
                    if created_tables:
                        logger.info(f"Tables créées avec succès: {', '.join(created_tables)}")
                    else:
                        logger.error("Échec de la création des tables")
                        return False
                
                # Création d'un utilisateur administrateur par défaut
                admin = User.query.filter_by(username="admin").first()
                
                if not admin:
                    admin = User(
                        username="admin",
                        email="admin@smartohada.com",
                        full_name="Administrateur",
                        is_admin=True
                    )
                    admin.set_password("admin123")
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("✅ Utilisateur administrateur créé avec succès")
                
                logger.info("✅ Initialisation des tables terminée avec succès")
                
        except ImportError as e:
            logger.error(f"❌ Erreur d'importation: {str(e)}")
            traceback.print_exc()
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création des tables: {str(e)}")
            traceback.print_exc()
            return False
        
        return True
                
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if initialize_database():
        logger.info("✅ Initialisation de la base de données terminée avec succès")
        sys.exit(0)
    else:
        logger.error("❌ Échec de l'initialisation de la base de données")
        sys.exit(1)
