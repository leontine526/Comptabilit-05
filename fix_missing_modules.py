#!/usr/bin/env python
"""
Script pour installer les modules manquants et corriger les dépendances
"""
import os
import sys
import subprocess
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("module_fixer")

def install_module(module_name):
    """Installe un module via upm dans Replit"""
    logger.info(f"Installation du module {module_name}...")
    try:
        # Utiliser upm au lieu de pip dans l'environnement Replit
        subprocess.check_call(["upm", "add", module_name])
        logger.info(f"✅ Module {module_name} installé avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'installation de {module_name}: {str(e)}")
        logger.info(f"Alternative: essai avec pip install --user")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", module_name])
            logger.info(f"✅ Module {module_name} installé avec succès via pip --user")
            return True
        except Exception as e2:
            logger.error(f"❌ Échec de l'installation alternative: {str(e2)}")
            return False

def check_and_install_modules():
    """Vérifie et installe les modules nécessaires"""
    required_modules = [
        "flask",
        "flask-login",
        "flask-sqlalchemy",
        "sqlalchemy",
        "flask-socketio",
        "python-dotenv",
        "xlsxwriter",
        "eventlet",
        "psycopg2-binary",
        "werkzeug",
        "pymongo",
        "reportlab",
        "pdfkit",
        "pytesseract",
        "nltk",
        "spacy",
        "numpy",
        "fitz"
    ]

    # Compter combien de modules sont manquants
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module.replace('-', '_').replace('.', '_'))
            logger.info(f"✓ Module {module} déjà installé")
        except ImportError:
            missing_modules.append(module)

    # Installer les modules manquants
    if missing_modules:
        logger.info(f"{len(missing_modules)} modules manquants trouvés: {', '.join(missing_modules)}")
        for module in missing_modules:
            # Mapping spécial pour certains modules
            if module == "fitz":
                install_module("PyMuPDF")
            else:
                install_module(module)
    else:
        logger.info("Tous les modules requis sont déjà installés")

    # Télécharger les données NLTK
    try:
        logger.info("Téléchargement des données NLTK...")
        subprocess.check_call([
            sys.executable, "-m", "nltk.downloader", 
            "punkt", "stopwords", "-d", "nltk_data"
        ])
        logger.info("✅ Données NLTK téléchargées avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors du téléchargement des données NLTK: {str(e)}")

def main():
    """Fonction principale"""
    logger.info("Vérification des modules requis...")
    check_and_install_modules()
    logger.info("Terminé! Vous pouvez maintenant exécuter l'application.")

if __name__ == "__main__":
    main()