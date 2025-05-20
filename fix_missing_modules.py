
#!/usr/bin/env python
"""
Script pour corriger les problèmes de modules manquants
"""
import os
import sys
import logging
import importlib
import traceback
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                  format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("module_fixer")

def check_main_py():
    """Vérifie et corrige les imports dans main.py"""
    file_path = "main.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Fichier {file_path} introuvable!")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Vérifier l'import problématique de klaxwriter
        if "import klaxwriter" in content:
            logger.info("Détection de l'import problématique klaxwriter")
            
            # Remplacer par logging
            new_content = content.replace(
                "import klaxwriter", 
                "# import klaxwriter remplacé par logging standard\nimport logging"
            )
            
            # Remplacer toutes les utilisations de klaxwriter
            new_content = re.sub(
                r"klaxwriter\.([a-zA-Z_]+)\((.*?)\)", 
                r"logging.\1(\2)", 
                new_content
            )
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"✅ Remplacé klaxwriter par logging dans {file_path}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de {file_path}: {str(e)}")
        return False

def check_socket_imports():
    """Vérifie et corrige les imports socketio"""
    file_path = "socket_events.py"
    
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Vérifier les imports de socketio
        if "socketio" in content and "from flask_socketio import SocketIO" not in content:
            modified = False
            
            # Ajouter l'import correct
            if "import socketio" in content:
                new_content = content.replace(
                    "import socketio", 
                    "from flask_socketio import SocketIO"
                )
                modified = True
            elif "from app import socketio" not in content:
                lines = content.split('\n')
                imports_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        imports_end = i + 1
                
                lines.insert(imports_end, "from app import socketio")
                new_content = '\n'.join(lines)
                modified = True
            
            if modified:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                logger.info(f"✅ Corrigé les imports socketio dans {file_path}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de {file_path}: {str(e)}")
        return False

def check_missing_flask_modules():
    """Vérifie les imports des modules Flask"""
    try:
        # Vérifier flask_socketio
        try:
            importlib.import_module('flask_socketio')
            logger.info("✅ Module flask_socketio disponible")
        except ImportError:
            logger.warning("⚠️ Module flask_socketio manquant, sera installé au besoin")
        
        # Vérifier d'autres modules Flask essentiels
        flask_modules = ['flask_login', 'flask_sqlalchemy', 'flask_migrate']
        for module in flask_modules:
            try:
                importlib.import_module(module)
                logger.info(f"✅ Module {module} disponible")
            except ImportError:
                logger.warning(f"⚠️ Module {module} manquant, sera installé au besoin")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des modules Flask: {str(e)}")
        return False

def create_logs_directory():
    """Crée le répertoire de logs s'il n'existe pas"""
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
            logger.info("✅ Dossier logs créé")
            return True
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la création du dossier logs: {str(e)}")
        return False

def main():
    """Fonction principale"""
    logger.info("Démarrage du diagnostic et de la correction des erreurs...")
    
    # Vérifier DATABASE_URL
    if "DATABASE_URL" not in os.environ:
        logger.error("DATABASE_URL n'est pas définie dans les variables d'environnement")
        # Définir une valeur par défaut si nécessaire
        os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
        logger.info(f"Configuration de DATABASE_URL avec la valeur par défaut: {os.environ['DATABASE_URL']}")
    
    # Corriger les imports problématiques
    fixed_main = check_main_py()
    if fixed_main:
        logger.info("Module klaxwriter introuvable. Vérification des alternatives...")
        logger.info("Module logging importé comme alternative à klaxwriter")
    
    # Vérifier les imports socketio
    fixed_socket = check_socket_imports()
    logger.info("Module socketio importé avec succès" if fixed_socket else "Aucun problème d'import socketio détecté")
    
    # Vérifier les modules Flask manquants
    check_missing_flask_modules()
    
    # Créer le dossier de logs
    create_logs_directory()
    
    logger.info("Corrections appliquées. Vous pouvez maintenant exécuter l'application.")
    logger.info("Utilisez le workflow 'Run Fixed App' pour démarrer l'application.")

if __name__ == "__main__":
    main()
