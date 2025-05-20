
from app import app, db
import logging
from models import *
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialiser la base de données avec tous les modèles"""
    try:
        with app.app_context():
            # Créer toutes les tables
            logger.info("Création des tables...")
            db.create_all()
            
            # Vérifier les tables créées
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Tables créées: {', '.join(tables)}")
            
            # Créer un utilisateur admin par défaut
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
                logger.info("Utilisateur admin créé avec succès")

            return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_database()
