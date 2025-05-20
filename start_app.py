
#!/usr/bin/env python
"""
Script simplifié pour démarrer l'application avec gestion des erreurs et fallbacks
"""
import os
import sys
import logging
import subprocess
import traceback

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app_starter")

# Ajouter .pythonlibs au PYTHONPATH
sys.path.insert(0, os.path.abspath(".pythonlibs"))

def set_database_url():
    """Configure l'URL de la base de données"""
    if "DATABASE_URL" not in os.environ:
        # Définir l'URL de la base de données Neon
        db_url = "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
        os.environ["DATABASE_URL"] = db_url
        logger.info(f"DATABASE_URL définie: {db_url}")
    return True

def start_app():
    """Démarre l'application principale"""
    try:
        # S'assurer que les dossiers nécessaires existent
        os.makedirs("logs", exist_ok=True)
        os.makedirs("uploads", exist_ok=True)
        
        # Définir l'URL de la base de données
        set_database_url()
        
        # Initialiser la base de données (optionnel)
        try:
            if os.path.exists("db_initialize.py"):
                logger.info("Initialisation de la base de données...")
                result = subprocess.run([sys.executable, "db_initialize.py", "--retry", "3"], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("Base de données initialisée avec succès!")
                else:
                    logger.warning(f"Problème lors de l'initialisation de la base de données: {result.stderr}")
        except Exception as e:
            logger.warning(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        
        # Démarrer l'application
        logger.info("Démarrage de l'application...")
        
        os.environ["FLASK_ENV"] = "development"
        os.environ["PORT"] = "5000"
        
        # Exécuter main.py
        process = subprocess.Popen([sys.executable, "main.py"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
        
        # Lire et afficher la sortie standard et d'erreur
        for line in process.stdout:
            print(line.strip())
        
        # Attendre que le processus se termine
        process.wait()
        
        # Vérifier le code de sortie
        if process.returncode == 0:
            logger.info("Application terminée avec succès!")
            return True
        else:
            # Récupérer les erreurs
            errors = process.stderr.read()
            logger.error(f"Application terminée avec erreur (code {process.returncode})")
            logger.error(f"Erreurs: {errors}")
            return False
    
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    start_app()
