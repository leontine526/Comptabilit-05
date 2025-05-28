
#!/usr/bin/env python
"""
Script de démarrage pour SmartOHADA avec base de données Neon
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

def main():
    """Démarre l'application avec la base de données Neon"""
    try:
        logger.info("=== DÉMARRAGE SMARTOHADA AVEC NEON DB ===")
        
        # S'assurer que la variable d'environnement DATABASE_URL pointe vers Neon
        neon_url = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
        os.environ["DATABASE_URL"] = neon_url
        
        logger.info("Configuration de la base de données Neon...")
        
        # Créer les dossiers nécessaires
        for folder in ['logs', 'uploads', 'static/uploads']:
            os.makedirs(folder, exist_ok=True)
        
        # Importer l'application principale
        logger.info("Importation de l'application...")
        from app import app, socketio
        
        # Importer les routes
        logger.info("Importation des routes...")
        import routes
        
        # Obtenir le port
        port = int(os.environ.get('PORT', 5000))
        
        logger.info(f"Démarrage de SmartOHADA sur le port {port} avec Neon DB")
        logger.info("Application disponible sur: https://0.0.0.0:{port}")
        
        # Démarrer l'application avec SocketIO
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
