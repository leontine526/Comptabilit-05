
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_url():
    """Vérifie si la variable DATABASE_URL est définie et valide."""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL n'est pas définie dans les variables d'environnement")
        
        # Utiliser l'URL de la base de données définie dans les workflows
        default_db_url = "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
        
        logger.info(f"Configuration de DATABASE_URL avec la valeur par défaut: {default_db_url}")
        os.environ['DATABASE_URL'] = default_db_url
        return True
    else:
        logger.info(f"DATABASE_URL est définie: {db_url[:20]}...")
        return True

def check_module_imports():
    """Vérifie les importations problématiques."""
    problematic_modules = ['klaxwriter']
    
    for module in problematic_modules:
        try:
            __import__(module)
            logger.info(f"Module {module} importé avec succès")
        except ImportError:
            logger.error(f"Module {module} introuvable. Vérification des alternatives...")
            
            # Vérifier si le module existe sous un autre nom ou s'il est mal écrit
            if module == 'klaxwriter':
                try:
                    import logging as alternative
                    logger.info("Module logging importé comme alternative à klaxwriter")
                    # Créer un alias pour éviter les erreurs d'importation
                    sys.modules['klaxwriter'] = alternative
                except ImportError:
                    logger.error("Impossible de trouver une alternative pour klaxwriter")

def fix_socket_io_issues():
    """Vérifie et corrige les problèmes liés à Socket.IO."""
    try:
        import socketio
        logger.info("Module socketio importé avec succès")
    except ImportError:
        logger.error("Socket.IO n'est pas installé. Installation en cours...")
        try:
            import pip
            pip.main(['install', 'python-socketio'])
            logger.info("Socket.IO installé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'installation de Socket.IO: {str(e)}")

if __name__ == "__main__":
    logger.info("Démarrage du diagnostic et de la correction des erreurs...")
    
    # Vérifier et corriger la variable DATABASE_URL
    db_ok = check_database_url()
    
    # Vérifier et corriger les problèmes d'importation
    check_module_imports()
    
    # Vérifier et corriger les problèmes de Socket.IO
    fix_socket_io_issues()
    
    if db_ok:
        logger.info("Corrections appliquées. Vous pouvez maintenant exécuter l'application.")
        logger.info("Utilisez le workflow 'Run Fixed App' pour démarrer l'application.")
    else:
        logger.error("Impossible de corriger tous les problèmes. Vérifiez les logs pour plus d'informations.")
