
#!/usr/bin/env python
"""
Script de vérification rapide de l'état de l'application
"""
import os
import sys
import logging
import importlib

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_imports():
    """Vérifie les imports critiques"""
    critical_modules = [
        "flask", "flask_sqlalchemy", "flask_login", 
        "flask_socketio", "sqlalchemy"
    ]
    
    for module in critical_modules:
        try:
            importlib.import_module(module)
            logger.info(f"✅ Module {module} importé avec succès")
        except ImportError as e:
            logger.error(f"❌ Erreur lors de l'import du module {module}: {str(e)}")
            return False
    
    return True

def check_app():
    """Vérifie si l'application Flask peut être importée"""
    try:
        from app import app
        logger.info("✅ Application Flask importée avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import de l'application Flask: {str(e)}")
        return False

def check_templates():
    """Vérifie les templates critiques"""
    template_path = os.path.join("templates", "errors", "500.html")
    if os.path.exists(template_path):
        logger.info(f"✅ Template d'erreur 500 trouvé: {template_path}")
    else:
        logger.warning(f"⚠️ Template d'erreur 500 non trouvé: {template_path}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" VÉRIFICATION RAPIDE DE L'APPLICATION ".center(50, "="))
    print("="*50 + "\n")
    
    # Vérifier les imports
    if not check_imports():
        logger.error("❌ Problèmes avec les imports. Vérifiez les dépendances.")
    
    # Vérifier l'application
    if not check_app():
        logger.error("❌ Problèmes avec l'application Flask.")
    
    # Vérifier les templates
    check_templates()
    
    print("\nPour démarrer l'application après les corrections, exécutez:")
    print("python start_simple.py")
