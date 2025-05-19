from app import app, db
import logging
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialiser correctement la base de données avec tous les modèles"""
    try:
        with app.app_context():
            # Vérifier la configuration de la base de données
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            if 'neon.tech' in db_url:
                logger.info("Connexion à la base de données Neon PostgreSQL")
            else:
                logger.warning("URL de base de données non reconnue")

            logger.info("Initialisation de la base de données...")

            # Import tous les modèles pour s'assurer qu'ils sont enregistrés
            from models import User, Exercise, Account, Transaction, TransactionItem, Document
            from models import ExerciseExample, ExerciseSolution, Workgroup, Message
            from models import Note, Post, Comment, Like, Story, StoryView, Notification

            # Créer toutes les tables
            db.create_all()

            # Vérifier que les tables ont été créées
            engine = db.engine
            inspector = db.inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Tables créées: {', '.join(tables)}")

            logger.info("Base de données initialisée avec succès!")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL lors de l'initialisation de la base de données: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_database()