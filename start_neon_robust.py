
#!/usr/bin/env python
"""
Script de démarrage robuste pour SmartOHADA avec base de données Neon
Gère les erreurs d'importation PyMuPDF
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

def patch_pymupdf_if_needed():
    """Patch PyMuPDF si le module frontend est manquant"""
    try:
        import fitz
        logger.info("✅ PyMuPDF importé avec succès")
        return True
    except ImportError as e:
        if "frontend" in str(e):
            logger.warning("⚠️ Erreur PyMuPDF détectée, création d'un patch...")
            
            # Créer un module frontend factice
            import sys
            import types
            
            # Créer un module frontend minimal
            frontend_module = types.ModuleType('frontend')
            frontend_module.__dict__.update({
                'Document': type('Document', (), {}),
                'Page': type('Page', (), {}),
                'Rect': type('Rect', (), {}),
                'Point': type('Point', (), {}),
            })
            sys.modules['frontend'] = frontend_module
            
            # Essayer d'importer à nouveau
            try:
                import fitz
                logger.info("✅ PyMuPDF patché avec succès")
                return True
            except Exception as e2:
                logger.error(f"❌ Échec du patch PyMuPDF: {e2}")
                return False
        else:
            logger.error(f"❌ Erreur PyMuPDF différente: {e}")
            return False

def patch_exercise_solver():
    """Patch le module exercise_solver pour éviter les erreurs PyMuPDF"""
    try:
        # Tenter d'importer exercise_solver normalement
        import exercise_solver
        logger.info("✅ Module exercise_solver importé avec succès")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Erreur exercise_solver: {e}")
        logger.info("Utilisation du module exercise_solver_dummy...")
        
        # Utiliser le module dummy à la place
        import exercise_solver_dummy
        sys.modules['exercise_solver'] = exercise_solver_dummy
        
        logger.info("✅ Module exercise_solver_dummy utilisé")
        return True

def main():
    """Démarre l'application avec la base de données Neon"""
    try:
        logger.info("=== DÉMARRAGE ROBUSTE SMARTOHADA AVEC NEON DB ===")
        
        # S'assurer que la variable d'environnement DATABASE_URL pointe vers Neon
        neon_url = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
        os.environ["DATABASE_URL"] = neon_url
        
        logger.info("Configuration de la base de données Neon...")
        
        # Créer les dossiers nécessaires
        for folder in ['logs', 'uploads', 'static/uploads']:
            os.makedirs(folder, exist_ok=True)
        
        # Patcher PyMuPDF si nécessaire
        logger.info("Vérification de PyMuPDF...")
        patch_pymupdf_if_needed()
        
        # Patcher exercise_solver si nécessaire
        logger.info("Vérification d'exercise_solver...")
        patch_exercise_solver()
        
        # Importer l'application principale
        logger.info("Importation de l'application...")
        from app import app, socketio
        
        # Importer les routes
        logger.info("Importation des routes...")
        import routes
        
        # Obtenir le port
        port = int(os.environ.get('PORT', 5000))
        
        logger.info(f"Démarrage de SmartOHADA sur le port {port} avec Neon DB")
        logger.info(f"Application disponible sur: http://0.0.0.0:{port}")
        
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
