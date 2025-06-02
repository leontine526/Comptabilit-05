
#!/usr/bin/env python
"""
Version optimisée ultra-rapide de SmartOHADA
- Chargement lazy des modules
- Cache optimisé
- Démarrage minimal
"""
import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor

# Configuration logging minimal
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Configuration rapide de l'environnement"""
    os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    os.environ["FLASK_ENV"] = "production"
    os.environ["WERKZEUG_RUN_MAIN"] = "true"

def create_dummy_modules():
    """Création rapide des modules factices"""
    import types
    import sys
    
    # PyMuPDF factice
    if 'fitz' not in sys.modules:
        fitz = types.ModuleType('fitz')
        fitz.open = lambda *args: type('Doc', (), {'page_count': 0, 'close': lambda: None})()
        sys.modules['fitz'] = fitz

def optimize_imports():
    """Optimise les imports pour la vitesse"""
    # Précharger les modules critiques seulement
    import flask
    import flask_login
    import flask_sqlalchemy
    import sqlalchemy
    
def download_nltk_background():
    """Télécharge NLTK en arrière-plan"""
    try:
        import nltk
        nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
        os.makedirs(nltk_data_dir, exist_ok=True)
        nltk.data.path.insert(0, nltk_data_dir)
        
        # Téléchargement silencieux en arrière-plan
        resources = ['punkt_tab', 'punkt', 'stopwords']
        for resource in resources:
            try:
                nltk.download(resource, download_dir=nltk_data_dir, quiet=True)
            except:
                pass
    except Exception:
        pass

def main():
    """Démarrage ultra-rapide"""
    start_time = time.time()
    print("🚀 Démarrage rapide SmartOHADA...")
    
    # 1. Configuration rapide
    setup_environment()
    create_dummy_modules()
    
    # 2. Téléchargement NLTK en arrière-plan
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(download_nltk_background)
    
    # 3. Imports optimisés
    optimize_imports()
    
    try:
        # 4. Import de l'app avec gestion d'erreur
        from app import app
        
        # 5. Désactiver le debug pour la vitesse
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # 6. Import des routes minimal
        try:
            import routes
        except Exception as e:
            print(f"⚠️ Erreur routes (ignorée): {e}")
        
        # 7. SocketIO optionnel pour vitesse
        try:
            from app import socketio
            use_socketio = True
        except:
            use_socketio = False
        
        port = int(os.environ.get('PORT', 5000))
        startup_time = time.time() - start_time
        print(f"✅ Démarré en {startup_time:.2f}s sur port {port}")
        
        # 8. Démarrage selon disponibilité
        if use_socketio:
            from app import socketio
            socketio.run(
                app,
                host='0.0.0.0',
                port=port,
                debug=False,
                use_reloader=False,
                log_output=False
            )
        else:
            app.run(
                host='0.0.0.0',
                port=port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        # Fallback vers SQLite si Postgres échoue
        print("🔄 Tentative avec SQLite...")
        try:
            import app_sqlite
            app_sqlite.main()
        except Exception as e2:
            print(f"❌ Échec total: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()
