
#!/usr/bin/env python
"""
Script pour vérifier que toutes les dépendances sont installées et fonctionnelles
"""
import sys
import importlib
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("requirements_checker")

# Liste des modules requis
REQUIRED_MODULES = [
    "flask",
    "flask_login",
    "flask_sqlalchemy",
    "sqlalchemy",
    "flask_socketio",
    "flask_wtf",
    "python_dotenv", 
    "xlsxwriter",
    "eventlet",
    "psycopg2",
    "werkzeug"
]

def check_module(module_name):
    """Vérifie si un module est installé"""
    try:
        # Normaliser le nom du module pour l'importation
        import_name = module_name.replace("-", "_")
        importlib.import_module(import_name)
        logger.info(f"✅ Module {module_name} installé avec succès")
        return True
    except ImportError as e:
        logger.error(f"❌ Module {module_name} non installé ou non fonctionnel: {str(e)}")
        return False

def main():
    """Fonction principale"""
    logger.info("Vérification des modules requis...")
    
    all_modules_installed = True
    
    for module in REQUIRED_MODULES:
        if not check_module(module):
            all_modules_installed = False
    
    if all_modules_installed:
        logger.info("✅ Tous les modules requis sont installés et fonctionnels!")
        return 0
    else:
        logger.error("❌ Certains modules requis ne sont pas installés ou fonctionnels.")
        logger.info("Exécutez 'pip install -r requirements.txt' pour installer les modules manquants.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
