
#!/usr/bin/env python
"""
Script pour installer les dépendances essentielles de manière sécurisée
"""
import os
import sys
import logging
import subprocess
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dependency_installer")

def install_package(package):
    """Installe un package avec UPM de manière sécurisée"""
    logger.info(f"Installation de {package}...")
    
    try:
        subprocess.check_call(["upm", "add", package])
        logger.info(f"✅ {package} installé avec succès!")
        return True
    except subprocess.CalledProcessError:
        logger.warning(f"❌ Échec de l'installation de {package} avec upm")
        try:
            # Alternative installation method
            os.makedirs(".pythonlibs", exist_ok=True)
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                  "--target=.pythonlibs", package])
            logger.info(f"✅ {package} installé avec méthode alternative!")
            return True
        except subprocess.CalledProcessError:
            logger.error(f"❌ Échec de l'installation alternative de {package}")
            return False

# Liste des packages essentiels
ESSENTIAL_PACKAGES = [
    "flask-wtf",
    "flask-login",
    "flask-sqlalchemy",
    "eventlet",
    "sqlalchemy",
    "pymysql",
    "python-dotenv",
    "flask-socketio",
    "psycopg2-binary"
]

def main():
    """Fonction principale"""
    logger.info("Démarrage de l'installation des dépendances essentielles...")
    
    # Créer le dossier .pythonlibs s'il n'existe pas
    os.makedirs(".pythonlibs", exist_ok=True)
    
    # Ajouter .pythonlibs au PYTHONPATH
    sys.path.insert(0, os.path.abspath(".pythonlibs"))
    
    # Installer les packages essentiels
    success_count = 0
    for package in ESSENTIAL_PACKAGES:
        if install_package(package):
            success_count += 1
    
    # Afficher le résultat
    if success_count == len(ESSENTIAL_PACKAGES):
        logger.info("✅ Toutes les dépendances essentielles ont été installées!")
    else:
        logger.warning(f"⚠️ {success_count}/{len(ESSENTIAL_PACKAGES)} dépendances installées.")
    
    logger.info("Installation terminée.")

if __name__ == "__main__":
    main()
