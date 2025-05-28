
#!/usr/bin/env python
"""
Script de démarrage direct pour SmartOHADA - Version simple
"""
import os
import sys

def main():
    """Démarrage direct de l'application"""
    print("=== DÉMARRAGE DIRECT SMARTOHADA ===")
    
    # Configurer les variables d'environnement
    os.environ.setdefault('DATABASE_URL', 'sqlite:///smartohada.db')
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('PORT', '5000')
    os.environ.setdefault('SESSION_SECRET', 'dev_secret_key')
    
    # Créer les dossiers nécessaires
    for folder in ['logs', 'uploads', 'static/uploads', 'instance']:
        os.makedirs(folder, exist_ok=True)
    
    try:
        print("Importation de l'application...")
        from app_sqlite import app, socketio
        
        print("Importation des routes...")
        import routes
        
        port = int(os.environ.get('PORT', 5000))
        print(f"Démarrage sur le port {port}")
        
        # Démarrer directement
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
