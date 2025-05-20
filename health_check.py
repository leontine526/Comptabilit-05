
import logging
import sys
import os
import requests
import time
from sqlalchemy import create_engine, text

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database():
    """Vérifier la connexion à la base de données"""
    try:
        db_url = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_Crwao4WUkt5f@ep-spring-pond-a5upovj4-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("✅ Connexion à la base de données réussie")
                return True
        logger.error("❌ La requête de test à la base de données a échoué")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à la base de données: {str(e)}")
        return False

def check_web_server(url="http://localhost:5000/health"):
    """Vérifier si le serveur web répond"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Le serveur web répond correctement ({response.status_code})")
            return True
        logger.error(f"❌ Le serveur web répond avec un code d'erreur: {response.status_code}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du test du serveur web: {str(e)}")
        return False

def check_static_files():
    """Vérifier l'accès aux fichiers statiques"""
    try:
        static_url = "http://localhost:5000/static/css/main.css"
        response = requests.get(static_url, timeout=5)
        if response.status_code == 200:
            logger.info("✅ Les fichiers statiques sont accessibles")
            return True
        logger.error(f"❌ Erreur d'accès aux fichiers statiques: {response.status_code}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des fichiers statiques: {str(e)}")
        return False

def run_health_check():
    """Exécuter tous les contrôles de santé"""
    logger.info("🔍 Démarrage de la vérification de l'état de l'application...")
    
    db_status = check_database()
    web_status = check_web_server()
    static_status = check_static_files()
    
    all_checks_passed = db_status and web_status and static_status
    
    if all_checks_passed:
        logger.info("✅ Tous les contrôles sont passés avec succès!")
        return 0
    else:
        logger.error("❌ Certains contrôles ont échoué. L'application peut ne pas fonctionner correctement.")
        return 1

if __name__ == "__main__":
    sys.exit(run_health_check())
