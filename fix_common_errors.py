
#!/usr/bin/env python
"""
Script pour corriger automatiquement les erreurs courantes dans l'application SmartOHADA
"""
import os
import sys
import logging
import traceback
import re
import shutil
import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fix_errors")

class ErrorFixer:
    def __init__(self):
        self.fixed_issues = []
        self.failed_fixes = []
        
        # Créer le dossier de backup s'il n'existe pas
        os.makedirs("backups", exist_ok=True)
    
    def backup_file(self, file_path):
        """Crée une sauvegarde du fichier avant modification"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = os.path.join("backups", timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            logger.info(f"Sauvegarde créée: {backup_path}")
            return True
        
        return False
    
    def fix_logging_format(self):
        """Corrige le format de logging incorrect dans app.py"""
        file_path = "app.py"
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ Fichier {file_path} non trouvé")
                self.failed_fixes.append(f"Correction du format de logging dans {file_path}")
                return False
            
            # Créer une sauvegarde
            self.backup_file(file_path)
            
            # Lire le contenu du fichier
            with open(file_path, "r") as f:
                content = f.read()
            
            # Corriger le format de logging
            if "%(message.s" in content:
                corrected_content = content.replace("%(message.s", "%(message)s")
                
                # Écrire le contenu corrigé
                with open(file_path, "w") as f:
                    f.write(corrected_content)
                
                logger.info(f"✅ Format de logging corrigé dans {file_path}")
                self.fixed_issues.append(f"Format de logging dans {file_path}")
                return True
            else:
                logger.info(f"ℹ️ Aucune correction nécessaire pour le format de logging dans {file_path}")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la correction du format de logging: {str(e)}")
            logger.error(traceback.format_exc())
            self.failed_fixes.append(f"Correction du format de logging dans {file_path}")
            return False
    
    def fix_error_interceptor_imports(self):
        """Ajoute les imports manquants à error_interceptor.py"""
        file_path = "error_interceptor.py"
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ Fichier {file_path} non trouvé")
                self.failed_fixes.append(f"Correction des imports dans {file_path}")
                return False
            
            # Créer une sauvegarde
            self.backup_file(file_path)
            
            # Lire le contenu du fichier
            with open(file_path, "r") as f:
                content = f.read()
            
            # Vérifier et ajouter les imports manquants
            imports_to_add = []
            
            if "import traceback" not in content:
                imports_to_add.append("import traceback")
            
            if "import logging" not in content:
                imports_to_add.append("import logging")
            
            if "from flask import " not in content:
                imports_to_add.append("from flask import render_template, request, jsonify")
            elif not all(imp in content for imp in ["render_template", "request", "jsonify"]):
                # Remplacer l'import existant
                content = re.sub(r"from flask import .*", 
                                "from flask import render_template, request, jsonify", 
                                content)
            
            if "from app import " not in content:
                imports_to_add.append("from app import app, db")
            elif "db" not in content:
                content = re.sub(r"from app import .*", 
                                "from app import app, db", 
                                content)
            
            if "from sqlalchemy.exc import " not in content:
                imports_to_add.append("from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError")
            
            # Créer le bloc d'imports
            if imports_to_add:
                # Insérer les imports au début du fichier
                new_imports = "\n".join(imports_to_add)
                if content.startswith("\n"):
                    corrected_content = new_imports + "\n" + content
                else:
                    corrected_content = new_imports + "\n\n" + content
                
                # Ajouter le logger s'il n'existe pas
                if "logger = logging.getLogger" not in corrected_content:
                    logger_line = "\nlogger = logging.getLogger(__name__)\n"
                    insert_pos = corrected_content.find("\n\n", len(new_imports)) 
                    if insert_pos > 0:
                        corrected_content = corrected_content[:insert_pos] + logger_line + corrected_content[insert_pos:]
                    else:
                        corrected_content = new_imports + logger_line + "\n" + content
                
                # Écrire le contenu corrigé
                with open(file_path, "w") as f:
                    f.write(corrected_content)
                
                logger.info(f"✅ Imports corrigés dans {file_path}")
                self.fixed_issues.append(f"Imports dans {file_path}")
                return True
            else:
                logger.info(f"ℹ️ Aucune correction nécessaire pour les imports dans {file_path}")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la correction des imports: {str(e)}")
            logger.error(traceback.format_exc())
            self.failed_fixes.append(f"Correction des imports dans {file_path}")
            return False
    
    def fix_error_interceptor_init(self):
        """Corrige l'initialisation de ErrorInterceptor dans main.py"""
        file_path = "main.py"
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ Fichier {file_path} non trouvé")
                self.failed_fixes.append(f"Correction de l'initialisation de ErrorInterceptor dans {file_path}")
                return False
            
            # Créer une sauvegarde
            self.backup_file(file_path)
            
            # Lire le contenu du fichier
            with open(file_path, "r") as f:
                content = f.read()
            
            # Vérifier si l'initialisation est manquante
            if ("error_interceptor.initialize()" not in content and 
                "error_interceptor.ErrorInterceptor.init_app" not in content):
                
                # Chercher un endroit approprié pour insérer l'initialisation
                try_points = [
                    "if __name__ == '__main__':",
                    "# Importe les gestionnaires d'erreurs"
                ]
                
                insert_point = None
                for point in try_points:
                    if point in content:
                        insert_point = content.find(point)
                        break
                
                if insert_point is not None:
                    # Construire le bloc d'initialisation
                    init_block = """
    # Initialiser le gestionnaire d'erreurs
    try:
        import error_interceptor
        if hasattr(error_interceptor, 'initialize'):
            error_interceptor.initialize()
        elif hasattr(error_interceptor, 'ErrorInterceptor'):
            error_interceptor.ErrorInterceptor.init_app(app)
        logger.info("Gestionnaire d'erreurs initialisé avec succès")
    except ImportError:
        logger.warning("Module error_interceptor non trouvé, les erreurs ne seront pas interceptées")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du gestionnaire d'erreurs: {str(e)}")
"""
                    
                    # Trouver l'indentation appropriée
                    line_start = content.rfind("\n", 0, insert_point) + 1
                    indent = ""
                    for i in range(line_start, insert_point):
                        if content[i].isspace():
                            indent += content[i]
                        else:
                            break
                    
                    # Indenter le bloc d'initialisation
                    indented_block = "\n".join(indent + line for line in init_block.split("\n"))
                    
                    # Insérer le bloc au point approprié
                    split_pos = content.find("\n", insert_point)
                    if split_pos > 0:
                        corrected_content = content[:split_pos] + indented_block + content[split_pos:]
                    else:
                        corrected_content = content + indented_block
                    
                    # Écrire le contenu corrigé
                    with open(file_path, "w") as f:
                        f.write(corrected_content)
                    
                    logger.info(f"✅ Initialisation de ErrorInterceptor ajoutée dans {file_path}")
                    self.fixed_issues.append(f"Initialisation de ErrorInterceptor dans {file_path}")
                    return True
                else:
                    logger.error(f"❌ Impossible de trouver un point d'insertion approprié dans {file_path}")
                    self.failed_fixes.append(f"Correction de l'initialisation de ErrorInterceptor dans {file_path}")
                    return False
            else:
                logger.info(f"ℹ️ Aucune correction nécessaire pour l'initialisation de ErrorInterceptor dans {file_path}")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la correction de l'initialisation: {str(e)}")
            logger.error(traceback.format_exc())
            self.failed_fixes.append(f"Correction de l'initialisation de ErrorInterceptor dans {file_path}")
            return False
    
    def create_logs_directory(self):
        """Crée le répertoire de logs s'il n'existe pas"""
        try:
            logs_dir = os.path.join(os.getcwd(), 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
                logger.info(f"✅ Dossier de logs créé: {logs_dir}")
                self.fixed_issues.append("Création du dossier de logs")
                return True
            else:
                logger.info(f"ℹ️ Le dossier de logs existe déjà: {logs_dir}")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création du dossier de logs: {str(e)}")
            self.failed_fixes.append("Création du dossier de logs")
            return False
    
    def fix_database_url_format(self):
        """Vérifie et corrige le format de l'URL de la base de données"""
        # Vérifier la variable d'environnement DATABASE_URL
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            logger.warning("⚠️ Variable DATABASE_URL non définie dans l'environnement")
            return False
        
        try:
            # Vérifier si l'URL commence par postgres:// au lieu de postgresql://
            if db_url.startswith("postgres://"):
                corrected_url = "postgresql://" + db_url[len("postgres://"):]
                os.environ["DATABASE_URL"] = corrected_url
                logger.info("✅ Format de l'URL de la base de données corrigé (postgres:// → postgresql://)")
                self.fixed_issues.append("Format de l'URL de la base de données")
                return True
            else:
                logger.info("ℹ️ L'URL de la base de données a un format correct")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification de l'URL de la base de données: {str(e)}")
            self.failed_fixes.append("Correction du format de l'URL de la base de données")
            return False
    
    def run_all_fixes(self):
        """Exécute toutes les corrections automatiques"""
        print("\n" + "="*50)
        print(" CORRECTION AUTOMATIQUE DES ERREURS ".center(50, "="))
        print("="*50 + "\n")
        
        # Exécuter toutes les fonctions de correction
        fixes_tried = 0
        
        logger.info("🔧 Création du répertoire de logs...")
        self.create_logs_directory()
        fixes_tried += 1
        
        logger.info("\n🔧 Correction du format de logging...")
        self.fix_logging_format()
        fixes_tried += 1
        
        logger.info("\n🔧 Correction des imports dans error_interceptor.py...")
        self.fix_error_interceptor_imports()
        fixes_tried += 1
        
        logger.info("\n🔧 Correction de l'initialisation de ErrorInterceptor...")
        self.fix_error_interceptor_init()
        fixes_tried += 1
        
        logger.info("\n🔧 Correction du format de l'URL de la base de données...")
        self.fix_database_url_format()
        fixes_tried += 1
        
        # Afficher le résumé
        print("\n" + "="*50)
        print(" RÉSUMÉ DES CORRECTIONS ".center(50, "="))
        print("="*50)
        print(f"📊 Corrections tentées: {fixes_tried}")
        print(f"✅ Corrections réussies: {len(self.fixed_issues)}")
        print(f"❌ Corrections échouées: {len(self.failed_fixes)}")
        
        if self.fixed_issues:
            print("\n✅ CORRECTIONS RÉUSSIES:")
            for i, issue in enumerate(self.fixed_issues, 1):
                print(f"  {i}. {issue}")
        
        if self.failed_fixes:
            print("\n❌ CORRECTIONS ÉCHOUÉES:")
            for i, issue in enumerate(self.failed_fixes, 1):
                print(f"  {i}. {issue}")
        
        print("\n📝 PROCHAINES ÉTAPES:")
        print("  1. Exécutez python error_diagnostics.py pour vérifier s'il reste des problèmes")
        print("  2. Redémarrez l'application pour appliquer les changements")
        print("  3. Si des problèmes persistent, consultez les logs pour plus de détails")
        print("="*50)
        
        return {
            "fixed_issues": self.fixed_issues,
            "failed_fixes": self.failed_fixes
        }

if __name__ == "__main__":
    try:
        fixer = ErrorFixer()
        fixer.run_all_fixes()
    except KeyboardInterrupt:
        print("\n\nCorrection interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\n\nErreur lors de l'exécution des corrections: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
