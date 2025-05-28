#!/usr/bin/env python
"""
Point d'entrée principal pour l'application SmartOHADA
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

def main():
    """Fonction principale de démarrage"""
    try:
        logger.info("Démarrage de l'application SmartOHADA...")

        # Importer l'application depuis app.py
        from app_sqlite import app, socketio

        # Importer les routes après avoir créé l'application
        import routes

        # Obtenir le port depuis l'environnement
        port = int(os.environ.get('PORT', 5000))

        logger.info(f"Démarrage de SmartOHADA sur le port {port}")

        # Démarrer l'application avec SocketIO
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=True,
            allow_unsafe_werkzeug=True
        )

    except ImportError as e:
        logger.error(f"Erreur d'importation: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur de démarrage: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()