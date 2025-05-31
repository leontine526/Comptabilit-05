
#!/usr/bin/env python
"""
Script de démarrage minimal utilisant uniquement les packages disponibles
"""
import os
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_critical_imports():
    """Vérifie les imports critiques sans tentative d'installation"""
    critical_modules = [
        "flask",
        "flask_login", 
        "flask_sqlalchemy",
        "flask_socketio",
        "sqlalchemy",
        "werkzeug"
    ]
    
    missing = []
    for module in critical_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module} disponible")
        except ImportError:
            missing.append(module)
            logger.error(f"❌ {module} manquant")
    
    return len(missing) == 0

def create_dummy_modules():
    """Crée des modules factices pour les dépendances optionnelles manquantes"""
    
    # Module factice pour fitz/PyMuPDF
    fitz_dummy = """
class fitz:
    @staticmethod
    def open(*args, **kwargs):
        raise ImportError("PyMuPDF non disponible - fonctionnalité PDF désactivée")
    
    class Document:
        def __init__(self):
            pass
"""
    
    # Module factice pour eventlet
    eventlet_dummy = """
import threading
import time

class eventlet:
    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)
    
    @staticmethod  
    def spawn(func, *args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
"""
    
    try:
        import fitz
    except ImportError:
        exec(fitz_dummy, globals())
        logger.info("✅ Module fitz factice créé")
    
    try:
        import eventlet
    except ImportError:
        exec(eventlet_dummy, globals())
        logger.info("✅ Module eventlet factice créé")

def main():
    """Démarre l'application avec les packages disponibles"""
    logger.info("=== DÉMARRAGE MINIMAL SMARTOHADA ===")
    
    # Créer les dossiers nécessaires
    for folder in ['logs', 'uploads', 'static/uploads']:
        os.makedirs(folder, exist_ok=True)
    
    # Vérifier les imports critiques
    if not check_critical_imports():
        logger.error("Des modules critiques sont manquants. Impossible de démarrer.")
        sys.exit(1)
    
    # Créer les modules factices pour les dépendances optionnelles
    create_dummy_modules()
    
    # Configuration de la base de données
    neon_url = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    os.environ["DATABASE_URL"] = neon_url
    
    try:
        # Importer l'application
        logger.info("Importation de l'application...")
        from app import app
        
        # Essayer d'importer socketio, sinon utiliser l'app Flask standard
        try:
            from app import socketio
            logger.info("SocketIO disponible")
            use_socketio = True
        except ImportError:
            logger.warning("SocketIO non disponible, utilisation de Flask standard")
            socketio = None
            use_socketio = False
        
        # Importer les routes
        logger.info("Importation des routes...")
        import routes
        
        # Démarrer l'application
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Démarrage sur le port {port}")
        
        if use_socketio and socketio:
            socketio.run(
                app,
                host='0.0.0.0',
                port=port,
                debug=False,
                allow_unsafe_werkzeug=True
            )
        else:
            app.run(
                host='0.0.0.0',
                port=port,
                debug=False
            )
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        logger.info("Essayez de vérifier votre fichier pyproject.toml")
        sys.exit(1)

if __name__ == "__main__":
    main()
