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
    import sys
    import types

    # Créer un module fitz factice complet
    try:
        import fitz
        logger.info("✅ PyMuPDF disponible")
    except ImportError as e:
        logger.info(f"Création du module fitz factice pour: {str(e)}")

        # Créer le module frontend manquant
        frontend_module = types.ModuleType('frontend')
        frontend_module.__dict__.update({
            'Document': type('Document', (), {}),
            'Page': type('Page', (), {}),
            'Rect': type('Rect', (), {}),
            'Point': type('Point', (), {}),
        })
        sys.modules['frontend'] = frontend_module

        # Créer le module fitz factice
        fitz_module = types.ModuleType('fitz')

        class DummyDocument:
            def __init__(self, *args, **kwargs):
                self.page_count = 0

            def __len__(self):
                return 0

            def __getitem__(self, index):
                raise IndexError("Document factice sans pages")

            def close(self):
                pass

        fitz_module.open = lambda *args, **kwargs: DummyDocument(*args, **kwargs)
        fitz_module.Document = DummyDocument
        sys.modules['fitz'] = fitz_module
        logger.info("✅ Module fitz factice créé")

    # Gérer eventlet
    try:
        import eventlet
        logger.info("✅ eventlet disponible")
    except ImportError:
        logger.info("Création du module eventlet factice")
        import threading
        import time

        eventlet_module = types.ModuleType('eventlet')
        eventlet_module.sleep = time.sleep
        eventlet_module.spawn = lambda func, *args, **kwargs: threading.Thread(target=func, args=args, kwargs=kwargs)
        sys.modules['eventlet'] = eventlet_module
        logger.info("✅ Module eventlet factice créé")

def check_dependencies():
    """Vérifie et configure les dépendances critiques"""
    required_modules = [
        'flask', 'flask_login', 'flask_sqlalchemy', 'flask_socketio',
        'sqlalchemy', 'werkzeug', 'PyMuPDF', 'eventlet'
    ]

    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module} disponible")
        except ImportError as e:
            logger.error(f"❌ {module} manquant: {e}")
            return False

    # Configuration NLTK
    import nltk
    import os
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    if os.path.exists(nltk_data_dir):
        nltk.data.path.insert(0, nltk_data_dir)
        logger.info(f"✅ NLTK configuré avec le dossier: {nltk_data_dir}")

    return True

def main():
    """Démarre l'application avec les packages disponibles"""
    logger.info("=== DÉMARRAGE MINIMAL SMARTOHADA ===")

    # Créer les dossiers nécessaires
    for folder in ['logs', 'uploads', 'static/uploads']:
        os.makedirs(folder, exist_ok=True)

    # Corriger PyMuPDF en premier
    try:
        from fix_pymupdf import fix_pymupdf
        fix_pymupdf()
    except Exception as e:
        logger.warning(f"Impossible d'appliquer le correctif PyMuPDF: {e}")

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