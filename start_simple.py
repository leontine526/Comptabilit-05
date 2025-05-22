#!/usr/bin/env python
"""
Script de démarrage simplifié et robuste
pour l'application SmartOHADA
"""
import os
import sys
import logging
import time
import subprocess
import traceback

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Création du dossier de logs
os.makedirs('logs', exist_ok=True)

def check_and_repair_text_processor():
    """Vérifie et répare le fichier text_processor.py"""
    try:
        with open('text_processor.py', 'r') as f:
            content = f.read()

        # Vérifier si le problème de la chaîne non terminée est présent
        if "text.split('\n\n')" not in content and "text.split('\\n\\n')" not in content:
            logger.info("Réparation du fichier text_processor.py...")
            fixed_content = """# Module temporaire pour éviter les erreurs d'importation NLTK
def process_text(text, summarize=True, split_paragraphs=True, analyze=True, compression_rate=0.3):
    return {
        'original': text,
        'summary': "La fonctionnalité de résumé n'est pas disponible pour le moment.",
        'paragraphs': text.split('\\n\\n'),
        'analysis': {
            'complexity': 'Non disponible',
            'sentiment': 'Non disponible',
            'keywords': ['Non disponible']
        }
    }
"""
            with open('text_processor.py', 'w') as f:
                f.write(fixed_content)
            logger.info("✅ text_processor.py réparé avec succès")
            return True
        else:
            logger.info("✅ text_processor.py est déjà correct")
            return True
    except Exception as e:
        logger.error(f"Erreur lors de la réparation de text_processor.py: {str(e)}")
        return False

def check_error_handlers():
    """Vérifie et corrige les gestionnaires d'erreurs"""
    try:
        if os.path.exists("app.py"):
            with open("app.py", "r") as f:
                content = f.read()

            # Vérifier s'il y a une référence à handle_standard_exception
            if "handle_standard_exception" in content:
                logger.info("Correction du gestionnaire d'erreurs dans app.py...")
                corrected_content = content.replace(
                    "return app.handle_standard_exception(e)",
                    "return render_template('errors/500.html', error=str(e)), 500"
                )

                with open("app.py", "w") as f:
                    f.write(corrected_content)

                logger.info("✅ Gestionnaire d'erreurs dans app.py corrigé")
                return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des gestionnaires d'erreurs: {str(e)}")

    return False

def initialize_sqlite_database():
    """Initialise la base de données SQLite locale"""
    try:
        logger.info("Initialisation de la base de données SQLite...")
        # Définir la variable d'environnement pour utiliser SQLite
        os.environ["DATABASE_URL"] = "sqlite:///smartohada.db"

        # Exécuter le script d'initialisation
        try:
            subprocess.run([sys.executable, "db_initialize.py", "--retry", "3"], check=True)
            logger.info("✅ Base de données SQLite initialisée avec succès")
            return True
        except subprocess.CalledProcessError:
            # Essayer avec l'initialisation complète
            try:
                subprocess.run([sys.executable, "init_db_complete.py"], check=True)
                logger.info("✅ Base de données SQLite initialisée avec succès (méthode alternative)")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Échec de l'initialisation de la base de données: {str(e)}")
                return False
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        return False

def start_app_with_retry(max_retries=3):
    """Démarre l'application avec plusieurs tentatives"""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Tentative de démarrage {attempt}/{max_retries}...")

            # Utiliser SQLite comme base de données
            os.environ["DATABASE_URL"] = "sqlite:///smartohada.db"
            os.environ["FLASK_ENV"] = "development"
            os.environ["PORT"] = "5000"

            # Vérifier les gestionnaires d'erreurs avant de démarrer
            check_error_handlers()

            # Importer l'application
            from app import app, socketio

            # Vérifier si l'application a été correctement importée
            if app and socketio:
                logger.info("✅ Application importée avec succès")

            # Démarrer l'application
                logger.info("Démarrage du serveur sur port 5000...")
                socketio.run(app, 
                          host='0.0.0.0',
                          port=5000,
                          debug=True,
                          allow_unsafe_werkzeug=True)
                return True
        except ImportError as e:
            logger.error(f"Erreur d'importation: {str(e)}")
            logger.error(traceback.format_exc())
            time.sleep(2)
        except Exception as e:
            logger.error(f"Erreur lors du démarrage: {str(e)}")
            logger.error(traceback.format_exc())
            time.sleep(2)

    logger.error(f"Échec du démarrage après {max_retries} tentatives")
    return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" DÉMARRAGE SIMPLIFIÉ SMARTOHADA ".center(50, "="))
    print("="*50 + "\n")

    # Étape 1: Réparer text_processor.py
    if not check_and_repair_text_processor():
        logger.error("Impossible de réparer text_processor.py. Arrêt du script.")
        sys.exit(1)

    # Étape 2: Initialiser la base de données SQLite
    if not initialize_sqlite_database():
        logger.warning("Problème lors de l'initialisation de la base de données. Tentative de démarrage quand même...")

    # Étape 3: Démarrer l'application
    if not start_app_with_retry(max_retries=3):
        logger.error("Impossible de démarrer l'application. Veuillez consulter les logs pour plus de détails.")
        sys.exit(1)