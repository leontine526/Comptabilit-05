
#!/usr/bin/env python
"""
Script de démarrage sécurisé avec installation automatique des dépendances
"""
import os
import sys
import logging
import subprocess

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_missing_package(package_name):
    """Installe un package manquant via UPM"""
    try:
        logger.info(f"Installation de {package_name}...")
        subprocess.check_call(["upm", "add", package_name])
        logger.info(f"✅ {package_name} installé avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'installation de {package_name}: {e}")
        return False

def check_and_fix_imports():
    """Vérifie et corrige les importations manquantes"""
    critical_packages = {
        "flask": "flask",
        "flask_login": "flask-login",
        "flask_sqlalchemy": "flask-sqlalchemy",
        "flask_socketio": "flask-socketio",
        "sqlalchemy": "sqlalchemy",
        "dotenv": "python-dotenv",
        "numpy": "numpy", 
        "sklearn": "scikit-learn",
        "fitz": "PyMuPDF",
        "werkzeug": "werkzeug",
        "eventlet": "eventlet"
    }
    
    missing_count = 0
    for module, package in critical_packages.items():
        try:
            __import__(module)
            logger.info(f"✅ Module {module} disponible")
        except ImportError:
            logger.warning(f"⚠️ Module {module} manquant, installation...")
            if install_missing_package(package):
                logger.info(f"✅ {module} installé avec succès")
            else:
                missing_count += 1
                logger.error(f"❌ Échec installation {module}")
    
    if missing_count > 0:
        logger.warning(f"⚠️ {missing_count} modules n'ont pas pu être installés automatiquement")
        logger.info("Exécution du script d'installation complet...")
        try:
            subprocess.check_call([sys.executable, "install_all_dependencies.py"])
        except Exception as e:
            logger.error(f"Échec du script d'installation: {e}")

def main():
    """Démarre l'application de manière sécurisée"""
    logger.info("=== DÉMARRAGE SÉCURISÉ SMARTOHADA ===")
    
    # Vérifier et installer les dépendances critiques
    check_and_fix_imports()
    
    # Configurer la base de données Neon
    neon_url = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    os.environ["DATABASE_URL"] = neon_url
    
    # Créer les dossiers nécessaires
    for folder in ['logs', 'uploads', 'static/uploads']:
        os.makedirs(folder, exist_ok=True)
    
    try:
        # Importer l'application
        logger.info("Importation de l'application...")
        from app import app, socketio
        
        # Importer les routes
        logger.info("Importation des routes...")
        import routes
        
        # Démarrer l'application
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Démarrage sur le port {port}")
        
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        logger.info("Tentative de correction automatique...")
        
        # Exécuter le script de correction des modules
        try:
            exec(open('fix_missing_modules.py').read())
        except Exception:
            pass
            
        sys.exit(1)

if __name__ == "__main__":
    main()
