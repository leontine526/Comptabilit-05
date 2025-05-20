import os
import sys
import logging
import traceback
import time
import importlib
import subprocess

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Vérifie et configure l'environnement"""
    # Vérifier si DATABASE_URL est définie
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        database_url = "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
        os.environ["DATABASE_URL"] = database_url
        logger.info(f"DATABASE_URL définie: {database_url}")
    else:
        logger.info(f"DATABASE_URL définie: {database_url}")

    # Vérifier les modules requis dans l'application
    logger.info("Vérification des modules requis...")
    required_modules = [
        "flask", "flask_login", "flask_sqlalchemy", "sqlalchemy", 
        "flask_socketio", "flask_wtf", "dotenv", "xlsxwriter", "eventlet"
    ]

    missing_modules = []
    for module in required_modules:
        try:
            # Normaliser le nom du module pour l'importation
            import_name = module.replace("-", "_")
            importlib.import_module(import_name)
            logger.info(f"✅ Module {module} disponible")
        except ImportError:
            logger.warning(f"❌ Module {module} non disponible")
            missing_modules.append(module)

    if missing_modules:
        logger.warning(f"Modules manquants: {', '.join(missing_modules)}")
        logger.info("L'application pourrait ne pas fonctionner correctement.")

    return True

def test_database_connection():
    """Teste la connexion à la base de données"""
    logger.info("Vérification de la connexion à la base de données...")

    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(os.environ.get('DATABASE_URL'))
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Connexion à la base de données réussie")
                return True
            else:
                logger.error("Test de connexion à la base de données échoué")
                return False
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def initialize_database():
    """Initialise la base de données"""
    logger.info("Initialisation de la base de données...")

    try:
        subprocess.check_call([sys.executable, "db_initialize.py", "--retry", "3"])
        logger.info("Initialisation de la base de données réussie")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Échec de l'initialisation de la base de données: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def patch_nltk_import():
    """Corrige temporairement l'importation de NLTK dans les routes"""
    logger.info("Application d'un patch temporaire pour l'importation de NLTK...")
    try:
        # Créer un module stub pour text_processor.py
        if os.path.exists("text_processor.py"):
            with open("text_processor_original.py", "w") as backup_file:
                with open("text_processor.py", "r") as original_file:
                    backup_file.write(original_file.read())

            with open("text_processor.py", "w") as f:
                f.write("""
# Module temporaire pour éviter les erreurs d'importation NLTK
def process_text(text, summarize=True, split_paragraphs=True, analyze=True, compression_rate=0.3):
    return {
        'original': text,
        'summary': "La fonctionnalité de résumé n'est pas disponible pour le moment.",
        'paragraphs': text.split('\n\n'),
        'analysis': {
            'complexity': 'Non disponible',
            'sentiment': 'Non disponible',
            'keywords': ['Non disponible']
        }
    }
""")
            logger.info("✅ Patch temporaire appliqué pour text_processor.py")
        else:
            logger.warning("❌ Fichier text_processor.py non trouvé, le patch ne peut pas être appliqué")
    except Exception as e:
        logger.error(f"Erreur lors de l'application du patch temporaire: {str(e)}")

def start_application():
    """Démarre l'application"""
    logger.info("Démarrage de l'application...")

    # Appliquer un patch temporaire pour éviter les erreurs d'importation
    patch_nltk_import()

    try:
        # Démarrer l'application directement dans le processus actuel
        import main
        return True
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        logger.error(traceback.format_exc())

        # Analyser l'erreur pour fournir plus d'informations
        error_str = str(e)
        if "ModuleNotFoundError" in error_str:
            module_name = error_str.split("'")[1] if "'" in error_str else error_str
            logger.error(f"Module manquant: {module_name}")
            logger.info(f"Suggestion: Utilisez 'pip install {module_name}' ou ajoutez-le à requirements.txt")

        return False

def main():
    """Fonction principale"""
    print("==================================================")
    print("======= DÉMARRAGE ROBUSTE DE L'APPLICATION =======")
    print("==================================================")
    print("")

    # Étape 1: Vérifier et configurer l'environnement
    check_environment()

    # Étape 2: Tester la connexion à la base de données
    db_ok = test_database_connection()
    if not db_ok:
        logger.warning("Problèmes de connexion à la base de données détectés")

    # Étape 3: Initialiser la base de données
    db_init_ok = initialize_database()
    if not db_init_ok:
        logger.warning("Problèmes lors de l'initialisation de la base de données")

    # Étape 4: Démarrer l'application
    try:
        app_ok = start_application()

        if not app_ok:
            logger.error("Échec du démarrage de l'application")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application arrêtée par l'utilisateur")
        sys.exit(0)

if __name__ == "__main__":
    main()