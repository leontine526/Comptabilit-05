
#!/usr/bin/env python
"""
Script pour démarrer l'application de manière robuste avec des vérifications préalables
"""
import os
import sys
import time
import logging
import subprocess
import traceback

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app_starter")

def ensure_database_url():
    """Vérifie que DATABASE_URL est définie"""
    if "DATABASE_URL" not in os.environ:
        db_url = "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
        os.environ["DATABASE_URL"] = db_url
        logger.info(f"DATABASE_URL définie: {db_url}")
    else:
        logger.info(f"DATABASE_URL déjà définie")
    return True

def ensure_logs_directory():
    """Assure que le répertoire logs existe"""
    if not os.path.exists("logs"):
        os.makedirs("logs")
        logger.info("Répertoire logs créé")
    return True

def check_db_connection():
    """Vérifie la connexion à la base de données"""
    try:
        # Exécuter test_db_connection.py s'il existe
        if os.path.exists("test_db_connection.py"):
            logger.info("Vérification de la connexion à la base de données...")
            result = subprocess.run([sys.executable, "test_db_connection.py"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            if result.returncode == 0:
                logger.info("Connexion à la base de données réussie")
                return True
            else:
                logger.error(f"Erreur de connexion à la base de données: {result.stderr}")
                return False
        
        # Plan B si le script n'existe pas
        logger.info("Tentative de connexion à la base de données...")
        # Importer depuis db_helper si disponible
        try:
            from db_helper import init_db_connection
            if init_db_connection():
                logger.info("Connexion à la base de données réussie via db_helper")
                return True
            else:
                logger.error("Échec de la connexion via db_helper")
                return False
        except ImportError:
            logger.warning("Module db_helper non trouvé")
            
            # Tenter une connexion directe avec SQLAlchemy
            try:
                from sqlalchemy import create_engine
                db_url = os.environ.get("DATABASE_URL")
                if db_url:
                    engine = create_engine(db_url)
                    with engine.connect() as conn:
                        logger.info("Connexion à la base de données réussie via SQLAlchemy")
                        return True
                else:
                    logger.error("DATABASE_URL n'est pas définie")
                    return False
            except Exception as e:
                logger.error(f"Erreur lors de la connexion à la base de données: {str(e)}")
                return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la connexion: {str(e)}")
        return False

def initialize_database():
    """Initialise la base de données"""
    try:
        if os.path.exists("db_initialize.py"):
            logger.info("Initialisation de la base de données...")
            result = subprocess.run([sys.executable, "db_initialize.py", "--retry", "3"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            if result.returncode == 0:
                logger.info("Initialisation de la base de données réussie")
                return True
            else:
                logger.error(f"Erreur d'initialisation de la base de données: {result.stderr}")
                return False
        else:
            logger.warning("Script db_initialize.py non trouvé, initialisation ignorée")
            return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        return False

def start_application():
    """Démarre l'application principale"""
    try:
        # Vérifier que main.py existe
        if not os.path.exists("main.py"):
            logger.error("Fichier main.py introuvable!")
            return False
        
        logger.info("Démarrage de l'application...")
        
        # Exécuter l'application
        process = subprocess.Popen([sys.executable, "main.py"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
        
        # Attendre un moment pour voir si l'application démarre correctement
        time.sleep(2)
        
        # Vérifier si le processus est toujours en cours d'exécution
        if process.poll() is None:
            logger.info("Application démarrée avec succès")
            
            # Rediriger les sorties standard et d'erreur vers les logs
            def log_output(stream, log_level):
                for line in stream:
                    if log_level == "INFO":
                        logger.info(line.strip())
                    else:
                        logger.error(line.strip())
            
            # Démarrer des threads pour capturer la sortie
            import threading
            threading.Thread(target=log_output, args=(process.stdout, "INFO"), daemon=True).start()
            threading.Thread(target=log_output, args=(process.stderr, "ERROR"), daemon=True).start()
            
            # Attendre que le processus se termine
            process.wait()
            
            # Vérifier le code de retour
            if process.returncode == 0:
                logger.info("Application terminée normalement")
                return True
            else:
                logger.error(f"Application terminée avec le code d'erreur {process.returncode}")
                return False
        else:
            # Récupérer les messages d'erreur
            stdout, stderr = process.communicate()
            logger.error(f"Application n'a pas démarré correctement: {stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Fonction principale"""
    print("\n" + "="*50)
    print(" DÉMARRAGE ROBUSTE DE L'APPLICATION ".center(50, "="))
    print("="*50 + "\n")
    
    try:
        # Vérifications préalables
        ensure_database_url()
        ensure_logs_directory()
        
        # Vérifier la connexion à la base de données
        if not check_db_connection():
            logger.error("Impossible de se connecter à la base de données")
            logger.info("Tentative de démarrage de l'application malgré l'erreur...")
        
        # Initialiser la base de données
        initialize_database()
        
        # Démarrer l'application
        start_application()
    
    except Exception as e:
        logger.error(f"Erreur critique lors du démarrage: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
