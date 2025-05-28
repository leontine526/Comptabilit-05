
#!/usr/bin/env python
"""
Script d'initialisation pour la nouvelle base de données Neon
"""
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

def initialize_new_neon_database():
    """Initialise la nouvelle base de données Neon avec toutes les tables"""
    logger.info("=== INITIALISATION DE LA NOUVELLE BASE DE DONNÉES NEON ===")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # URL de la nouvelle base de données Neon
    database_url = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    
    logger.info("Connexion à la nouvelle base de données Neon...")
    
    try:
        # Créer un moteur SQLAlchemy avec paramètres optimisés pour Neon
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=60,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 3
            }
        )
        
        # Tester la connexion
        logger.info("Test de connexion...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Connexion à la nouvelle base de données établie avec succès")
            else:
                logger.error("❌ La requête de test a échoué")
                return False
        
        # Vérifier les tables existantes
        logger.info("Vérification des tables existantes...")
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            logger.info(f"Tables existantes: {', '.join(existing_tables)}")
        else:
            logger.info("Aucune table n'existe, création des tables...")
        
        # Importer l'application Flask et créer les tables
        logger.info("Importation des modèles et création des tables...")
        
        # Temporairement définir la variable d'environnement
        os.environ["DATABASE_URL"] = database_url
        
        from app import app, db
        from models import User, Exercise, Account, Transaction, TransactionItem, Document
        from models import ExerciseExample, ExerciseSolution, Workgroup, Message, Note
        from models import Post, Comment, Like, Share, Story, StoryView, PrivateMessage
        from models import Notification, GroupConversation, GroupMessage, Poll, PollOption
        from models import PollVote, Event, EventAttendee
        
        with app.app_context():
            # Créer toutes les tables
            logger.info("Création de toutes les tables...")
            db.create_all()
            
            # Vérifier que les tables ont été créées
            inspector = inspect(engine)
            created_tables = inspector.get_table_names()
            
            if created_tables:
                logger.info(f"✅ Tables créées avec succès: {', '.join(sorted(created_tables))}")
                logger.info(f"Total: {len(created_tables)} tables créées")
            else:
                logger.error("❌ Échec de la création des tables")
                return False
            
            # Créer un utilisateur administrateur par défaut
            logger.info("Création de l'utilisateur administrateur...")
            try:
                admin = User.query.filter_by(username="admin").first()
                
                if not admin:
                    admin = User(
                        username="admin",
                        email="admin@smartohada.com",
                        full_name="Administrateur",
                        is_admin=True,
                        bio="Administrateur principal de SmartOHADA",
                        position="Administrateur Système"
                    )
                    admin.set_password("admin123")
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("✅ Utilisateur administrateur créé avec succès")
                    logger.info("   Username: admin")
                    logger.info("   Password: admin123")
                    logger.info("   Email: admin@smartohada.com")
                else:
                    logger.info("✅ Utilisateur administrateur existe déjà")
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors de la création de l'utilisateur admin: {str(e)}")
                return False
            
        logger.info("✅ Initialisation de la base de données terminée avec succès!")
        return True
                
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {str(e)}")
        traceback.print_exc()
        return False

def verify_database_setup():
    """Vérifie que la base de données est correctement configurée"""
    logger.info("\n=== VÉRIFICATION DE LA CONFIGURATION ===")
    
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            # Compter les utilisateurs
            user_count = User.query.count()
            logger.info(f"Nombre d'utilisateurs dans la base: {user_count}")
            
            # Lister les utilisateurs admin
            admins = User.query.filter_by(is_admin=True).all()
            logger.info(f"Administrateurs: {[admin.username for admin in admins]}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erreur de vérification: {str(e)}")
        return False

if __name__ == "__main__":
    success = initialize_new_neon_database()
    
    if success:
        logger.info("\n" + "="*50)
        logger.info("🎉 INITIALISATION RÉUSSIE!")
        logger.info("="*50)
        logger.info("Votre application est maintenant connectée à la nouvelle base de données Neon.")
        logger.info("Vous pouvez démarrer l'application avec le bouton Run.")
        logger.info("\nInformations de connexion admin:")
        logger.info("- Username: admin")
        logger.info("- Password: admin123")
        logger.info("- Email: admin@smartohada.com")
        
        # Vérification finale
        verify_database_setup()
        
        sys.exit(0)
    else:
        logger.error("\n" + "="*50)
        logger.error("❌ ÉCHEC DE L'INITIALISATION")
        logger.error("="*50)
        logger.error("Veuillez vérifier les logs ci-dessus pour plus de détails.")
        sys.exit(1)
