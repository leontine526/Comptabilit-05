
#!/usr/bin/env python
"""
Script de démarrage propre pour SmartOHADA
"""
import os
import sys
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_and_fix_common_issues():
    """Vérifie et corrige les problèmes courants"""
    logger.info("Vérification des problèmes courants...")
    
    # Créer les dossiers nécessaires
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    
    # Définir les variables d'environnement par défaut
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///smartohada.db'
        logger.info("DATABASE_URL définie sur SQLite")
    
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    if not os.environ.get('PORT'):
        os.environ['PORT'] = '5000'

def start_application():
    """Démarre l'application principale"""
    try:
        logger.info("Démarrage de l'application...")
        
        # Import direct au lieu d'exec
        import main
        main.main()
        
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur de démarrage: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.info("Tentative avec start_simple.py...")
        try:
            import start_simple
            start_simple.start_app_with_retry()
        except Exception as fallback_error:
            logger.error(f"Échec du fallback: {fallback_error}")
            import traceback
            logger.error(traceback.format_exc())
            sys.exit(1)

if __name__ == "__main__":
    print("=== DÉMARRAGE PROPRE SMARTOHADA ===")
    check_and_fix_common_issues()
    start_application()
