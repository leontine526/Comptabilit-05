
#!/usr/bin/env python
"""
Script pour démarrer l'application SmartOHADA en utilisant SQLite
"""
import os
import logging
import sys
from db_sqlite_adapter import init_sqlite_db

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("sqlite_starter")

def start_app():
    """Démarre l'application avec SQLite"""
    try:
        # Créer les dossiers nécessaires
        os.makedirs("logs", exist_ok=True)
        os.makedirs("uploads", exist_ok=True)
        
        # Initialiser la base de données SQLite
        logger.info("Initialisation de la base de données SQLite...")
        if init_sqlite_db():
            logger.info("Base de données SQLite initialisée avec succès!")
        else:
            logger.warning("Problème lors de l'initialisation de la base de données SQLite.")
        
        # Démarrer l'application
        logger.info("Démarrage de l'application SmartOHADA avec SQLite...")
        os.environ["FLASK_ENV"] = "development"
        
        # Exécuter l'application
        os.system("python app_sqlite.py")
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        return False

if __name__ == "__main__":
    start_app()
