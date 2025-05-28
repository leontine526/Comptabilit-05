
#!/usr/bin/env python
"""
Script de démarrage robuste pour SmartOHADA
Gère automatiquement les erreurs courantes et lance l'application
"""
import os
import sys
import logging
import traceback

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configure l'environnement nécessaire"""
    try:
        # Créer les dossiers nécessaires
        os.makedirs('logs', exist_ok=True)
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('static/uploads', exist_ok=True)
        os.makedirs('instance', exist_ok=True)
        
        # Définir les variables d'environnement par défaut
        if not os.environ.get('DATABASE_URL'):
            os.environ['DATABASE_URL'] = 'sqlite:///smartohada.db'
            logger.info("DATABASE_URL définie sur SQLite")
        
        if not os.environ.get('FLASK_ENV'):
            os.environ['FLASK_ENV'] = 'development'
        
        if not os.environ.get('PORT'):
            os.environ['PORT'] = '5000'
            
        if not os.environ.get('SESSION_SECRET'):
            os.environ['SESSION_SECRET'] = 'dev_secret_key_change_in_production'
            
        logger.info("Environnement configuré avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de l'environnement: {e}")
        logger.error(traceback.format_exc())
        return False

def check_critical_files():
    """Vérifie la présence des fichiers critiques"""
    critical_files = [
        'app.py', 'main.py', 'models.py', 'routes.py',
        'templates/base.html', 'templates/index.html'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Fichiers critiques manquants: {missing_files}")
        return False
    
    logger.info("Tous les fichiers critiques sont présents")
    return True

def start_application():
    """Démarre l'application avec gestion d'erreurs robuste"""
    try:
        logger.info("=== DÉMARRAGE SMARTOHADA ===")
        
        # Vérifier l'environnement
        if not setup_environment():
            logger.error("Échec de la configuration de l'environnement")
            return False
        
        # Vérifier les fichiers critiques
        if not check_critical_files():
            logger.error("Fichiers critiques manquants")
            return False
        
        # Tenter le démarrage avec main.py
        logger.info("Tentative de démarrage avec main.py...")
        try:
            import main
            main.main()
            return True
        except Exception as e:
            logger.error(f"Erreur avec main.py: {e}")
            logger.error(traceback.format_exc())
            # Si c'est une erreur de logger, on essaie de la corriger
            if "logger" in str(e) and "not defined" in str(e):
                logger.error("Erreur de logger détectée dans main.py")
        
        # Fallback avec start_simple.py
        logger.info("Tentative de démarrage avec start_simple.py...")
        try:
            import start_simple
            start_simple.start_app_with_retry()
            return True
        except Exception as e:
            logger.error(f"Erreur avec start_simple.py: {e}")
            logger.error(traceback.format_exc())
        
        # Dernier recours : démarrage direct de l'app
        logger.info("Tentative de démarrage direct de l'application...")
        try:
            from app import app
            port = int(os.environ.get('PORT', 5000))
            app.run(host='0.0.0.0', port=port, debug=False)
            return True
        except Exception as e:
            logger.error(f"Erreur lors du démarrage direct: {e}")
            logger.error(traceback.format_exc())
        
        logger.error("Toutes les tentatives de démarrage ont échoué")
        return False
        
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
        return True
    except Exception as e:
        logger.error(f"Erreur critique lors du démarrage: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Point d'entrée principal"""
    success = start_application()
    
    if not success:
        print("\n" + "="*50)
        print(" ÉCHEC DU DÉMARRAGE ".center(50, "="))
        print("="*50)
        print("Recommandations:")
        print("1. Vérifiez les logs dans le dossier 'logs/'")
        print("2. Exécutez 'python error_diagnostics.py' pour un diagnostic complet")
        print("3. Vérifiez que tous les modules requis sont installés")
        print("4. Consultez le fichier README.md pour les instructions")
        sys.exit(1)
    else:
        logger.info("Application démarrée avec succès")

if __name__ == "__main__":
    main()
