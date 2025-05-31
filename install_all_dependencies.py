
#!/usr/bin/env python
"""
Script d'installation complète des dépendances pour SmartOHADA
"""
import os
import sys
import subprocess
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dependency_installer")

def install_with_upm(package):
    """Installe un package avec UPM"""
    try:
        logger.info(f"Installation de {package} avec UPM...")
        subprocess.check_call(["upm", "add", package], timeout=120)
        logger.info(f"✅ {package} installé avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Échec UPM pour {package}: {e}")
        return False

def install_with_pip(package):
    """Installe un package avec pip en fallback"""
    try:
        logger.info(f"Installation de {package} avec pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package], timeout=120)
        logger.info(f"✅ {package} installé avec pip")
        return True
    except Exception as e:
        logger.error(f"❌ Échec pip pour {package}: {e}")
        return False

def main():
    """Installation complète des dépendances"""
    logger.info("=== INSTALLATION COMPLÈTE DES DÉPENDANCES ===")
    
    # Dépendances critiques dans l'ordre d'importance
    critical_packages = [
        "flask",
        "flask-login", 
        "flask-sqlalchemy",
        "flask-socketio",
        "flask-wtf",
        "sqlalchemy",
        "python-dotenv",
        "werkzeug",
        "eventlet",
        "psycopg2-binary"
    ]
    
    # Dépendances pour l'analyse et ML
    ml_packages = [
        "numpy",
        "scikit-learn",
        "nltk",
        "PyMuPDF"
    ]
    
    # Dépendances utilitaires
    utility_packages = [
        "xlsxwriter",
        "reportlab",
        "requests",
        "pymongo"
    ]
    
    all_packages = critical_packages + ml_packages + utility_packages
    
    success_count = 0
    failed_packages = []
    
    for package in all_packages:
        logger.info(f"--- Installation de {package} ---")
        
        # Essayer d'abord avec UPM
        if install_with_upm(package):
            success_count += 1
        # Si UPM échoue, essayer avec pip
        elif install_with_pip(package):
            success_count += 1
        else:
            failed_packages.append(package)
    
    # Résumé final
    logger.info(f"\n=== RÉSUMÉ DE L'INSTALLATION ===")
    logger.info(f"✅ Packages installés: {success_count}/{len(all_packages)}")
    
    if failed_packages:
        logger.warning(f"❌ Packages échoués: {', '.join(failed_packages)}")
    else:
        logger.info("🎉 Toutes les dépendances ont été installées avec succès!")
    
    # Installation des données NLTK
    try:
        logger.info("Installation des données NLTK...")
        subprocess.check_call([sys.executable, "-c", 
            "import nltk; nltk.download('punkt', download_dir='nltk_data'); nltk.download('stopwords', download_dir='nltk_data')"],
            timeout=60)
        logger.info("✅ Données NLTK installées")
    except Exception as e:
        logger.warning(f"⚠️ Échec installation données NLTK: {e}")

if __name__ == "__main__":
    main()
