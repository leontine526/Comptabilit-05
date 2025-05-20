
import os
import sys
import logging
import importlib
import traceback

print("=== DIAGNOSTIC DE L'APPLICATION SMARTOHADA ===")

# Configuration du logging pour le diagnostic
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnostic")

def check_module(module_name):
    """Vérifie si un module peut être importé"""
    try:
        importlib.import_module(module_name)
        logger.info(f"✅ Module {module_name} importé avec succès")
        return True
    except ImportError as e:
        logger.error(f"❌ Erreur d'importation du module {module_name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de l'importation de {module_name}: {str(e)}")
        return False

# Vérifier les modules critiques
critical_modules = ["flask", "sqlalchemy", "flask_login", "flask_sqlalchemy", "flask_socketio"]
for module in critical_modules:
    check_module(module)

# Vérifier les fichiers principaux de l'application
main_files = ["app.py", "main.py", "db_helper.py", "error_handlers.py", "error_interceptor.py", "wsgi.py"]
for file in main_files:
    if os.path.exists(file):
        logger.info(f"✅ Fichier {file} trouvé")
    else:
        logger.error(f"❌ Fichier {file} manquant")

# Vérifier la connexion à la base de données
try:
    from db_helper import init_db_connection
    if init_db_connection():
        logger.info("✅ Connexion à la base de données réussie")
    else:
        logger.error("❌ Échec de la connexion à la base de données")
except Exception as e:
    logger.error(f"❌ Erreur lors de la vérification de la base de données: {str(e)}")

# Vérifier les logs d'erreur
log_file = "logs/app.log"
if os.path.exists(log_file):
    logger.info(f"✅ Fichier de log trouvé: {log_file}")
    try:
        with open(log_file, 'r') as f:
            last_lines = f.readlines()[-20:]  # Lire les 20 dernières lignes
            error_count = sum(1 for line in last_lines if "ERROR" in line)
            logger.info(f"ℹ️ {error_count} erreurs trouvées dans les 20 dernières lignes du log")
            
            if error_count > 0:
                logger.info("Dernières erreurs dans le log:")
                for line in last_lines:
                    if "ERROR" in line:
                        print(f"  {line.strip()}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la lecture du fichier de log: {str(e)}")
else:
    logger.warning(f"⚠️ Fichier de log non trouvé: {log_file}")
    os.makedirs("logs", exist_ok=True)
    logger.info("✅ Dossier de logs créé")

print("\n=== RÉSUMÉ DU DIAGNOSTIC ===")
print("Veuillez vérifier les points suivants qui pourraient être à l'origine du crash:")
print("1. Format de logging incorrect dans app.py (%(message.s au lieu de %(message)s)")
print("2. Problème d'initialisation du gestionnaire d'erreurs dans main.py")
print("3. Problèmes potentiels de connexion à la base de données")
print("4. Vérifiez les logs pour plus de détails sur l'erreur spécifique")
print("\nExécutez python health_check.py pour vérifier l'état général de l'application")
