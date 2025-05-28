
#!/usr/bin/env python3
"""
Script de démarrage direct pour SmartOHADA avec SQLite
"""
import os
import logging
from app_sqlite import app
from db_sqlite_adapter import init_sqlite_db

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Démarre l'application avec SQLite"""
    try:
        logger.info("Démarrage de SmartOHADA avec SQLite...")
        
        # Initialiser la base de données SQLite
        if init_sqlite_db():
            logger.info("Base de données SQLite initialisée avec succès")
        else:
            logger.error("Échec de l'initialisation de la base de données SQLite")
            return
        
        # Obtenir le port
        port = int(os.environ.get("PORT", 5000))
        
        # Démarrer l'application
        logger.info(f"Démarrage de l'application sur le port {port}...")
        app.run(host="0.0.0.0", port=port, debug=True)
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {str(e)}")
        raise

if __name__ == "__main__":
    main()
