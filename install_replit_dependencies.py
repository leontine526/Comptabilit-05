
#!/usr/bin/env python
"""
Script d'installation automatique des dépendances pour l'environnement Replit
"""
import subprocess
import sys
import logging
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("replit_installer")

def install_with_upm(packages):
    """Installe les packages avec UPM (recommandé pour Replit)"""
    logger.info("Installation des dépendances avec UPM...")
    
    for package in packages:
        try:
            logger.info(f"Installation de {package}...")
            subprocess.check_call(["upm", "add", package], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.PIPE)
            logger.info(f"✅ {package} installé avec succès")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Erreur UPM pour {package}, tentative avec pip...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"✅ {package} installé avec pip")
            except subprocess.CalledProcessError:
                logger.error(f"❌ Échec d'installation pour {package}")

def setup_nltk_data():
    """Configure les données NLTK"""
    logger.info("Configuration des données NLTK...")
    try:
        import nltk
        nltk.download('punkt', download_dir='./nltk_data', quiet=True)
        nltk.download('stopwords', download_dir='./nltk_data', quiet=True)
        logger.info("✅ Données NLTK configurées")
    except Exception as e:
        logger.error(f"❌ Erreur configuration NLTK: {e}")

def verify_installation():
    """Vérifie que les modules essentiels sont installés"""
    essential_modules = [
        "flask", "flask_login", "flask_sqlalchemy", "flask_socketio",
        "sqlalchemy", "dotenv", "werkzeug", "eventlet"
    ]
    
    logger.info("Vérification des modules essentiels...")
    missing = []
    
    for module in essential_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module} disponible")
        except ImportError:
            missing.append(module)
            logger.error(f"❌ {module} manquant")
    
    return len(missing) == 0

def main():
    """Fonction principale"""
    logger.info("=== INSTALLATION DES DÉPENDANCES REPLIT ===")
    
    # Créer les dossiers nécessaires
    os.makedirs("logs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("nltk_data", exist_ok=True)
    
    # Packages essentiels pour l'application
    essential_packages = [
        "flask==3.1.0",
        "flask-login==0.6.3", 
        "flask-sqlalchemy==3.1.1",
        "flask-socketio==5.5.1",
        "flask-wtf==1.2.2",
        "python-dotenv==1.1.0",
        "sqlalchemy==2.0.40",
        "eventlet==0.39.1",
        "werkzeug==2.3.8",
        "psycopg2-binary==2.9.10"
    ]
    
    # Installation avec UPM
    install_with_upm(essential_packages)
    
    # Configuration NLTK
    setup_nltk_data()
    
    # Vérification finale
    if verify_installation():
        logger.info("🎉 Toutes les dépendances essentielles sont installées!")
        logger.info("Vous pouvez maintenant démarrer l'application avec le bouton Run")
    else:
        logger.error("❌ Certaines dépendances sont encore manquantes")
        logger.info("Exécutez ce script à nouveau ou vérifiez manuellement")

if __name__ == "__main__":
    main()
