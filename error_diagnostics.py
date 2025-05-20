
#!/usr/bin/env python
"""
Script de diagnostic pour détecter et analyser les erreurs dans l'application SmartOHADA
"""
import os
import sys
import logging
import importlib
import traceback
import datetime
import json
from collections import defaultdict

# Configuration du logging pour le diagnostic
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnostics")

class ErrorDiagnostics:
    def __init__(self):
        self.error_summary = defaultdict(list)
        self.error_count = 0
        self.warning_count = 0
        self.start_time = datetime.datetime.now()
        self.log_file = "logs/app.log"
        self.issues_found = []
        
        # Créer le dossier de logs s'il n'existe pas
        os.makedirs("logs", exist_ok=True)
        
    def check_environment(self):
        """Vérifie les variables d'environnement essentielles"""
        logger.info("🔍 Vérification des variables d'environnement...")
        
        # Liste des variables d'environnement critiques
        env_vars = ["DATABASE_URL", "FLASK_ENV", "PORT", "SESSION_SECRET"]
        
        for var in env_vars:
            if var in os.environ:
                # Masquer les informations sensibles dans les logs
                if var == "DATABASE_URL" or var == "SESSION_SECRET":
                    value_preview = os.environ[var][:10] + "..." if os.environ[var] else "Non définie"
                    logger.info(f"✅ {var}: {value_preview}")
                else:
                    logger.info(f"✅ {var}: {os.environ[var]}")
            else:
                logger.warning(f"⚠️ {var} non définie")
                self.warning_count += 1
                self.issues_found.append(f"Variable d'environnement manquante: {var}")
    
    def check_modules(self):
        """Vérifie si les modules essentiels peuvent être importés"""
        logger.info("\n🔍 Vérification des modules Python...")
        
        essential_modules = [
            "flask", "flask_login", "flask_sqlalchemy", "flask_socketio", 
            "sqlalchemy", "dotenv", "werkzeug", "jinja2"
        ]
        
        for module in essential_modules:
            try:
                importlib.import_module(module)
                logger.info(f"✅ Module {module} importé avec succès")
            except ImportError as e:
                error_msg = f"❌ Erreur d'importation du module {module}: {str(e)}"
                logger.error(error_msg)
                self.error_count += 1
                self.error_summary["modules"].append(error_msg)
                self.issues_found.append(f"Module manquant: {module}")
            except Exception as e:
                error_msg = f"❌ Erreur inattendue lors de l'importation de {module}: {str(e)}"
                logger.error(error_msg)
                self.error_count += 1
                self.error_summary["modules"].append(error_msg)
    
    def check_key_files(self):
        """Vérifie la présence des fichiers clés de l'application"""
        logger.info("\n🔍 Vérification des fichiers essentiels...")
        
        key_files = [
            "app.py", "main.py", "db_helper.py", "error_handlers.py", 
            "error_interceptor.py", "models.py", "routes.py", "wsgi.py",
            "db_initialize.py", "templates/base.html", "templates/errors/500.html"
        ]
        
        for file_path in key_files:
            if os.path.exists(file_path):
                logger.info(f"✅ Fichier {file_path} trouvé")
            else:
                error_msg = f"❌ Fichier {file_path} manquant"
                logger.error(error_msg)
                self.error_count += 1
                self.error_summary["files"].append(error_msg)
                self.issues_found.append(f"Fichier manquant: {file_path}")
    
    def check_logs(self):
        """Analyse les fichiers de logs pour trouver des erreurs récentes"""
        logger.info("\n🔍 Analyse des logs d'erreur...")
        
        if not os.path.exists(self.log_file):
            logger.warning(f"⚠️ Fichier de log non trouvé: {self.log_file}")
            self.warning_count += 1
            self.issues_found.append("Fichier de log manquant")
            return
        
        try:
            # Récupérer les dernières erreurs dans le fichier de log
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                
                # Compter les erreurs des dernières 24 heures
                recent_errors = []
                error_types = defaultdict(int)
                today = datetime.datetime.now().date()
                
                for line in lines:
                    if "ERROR" in line:
                        try:
                            # Extraire la date du log (format: 2023-05-26 14:30:45)
                            date_str = line.split(' - ')[0]
                            log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
                            
                            # Si l'erreur est récente (dernières 24h)
                            if (today - log_date).days <= 1:
                                recent_errors.append(line.strip())
                                
                                # Classifier le type d'erreur
                                if "ImportError" in line:
                                    error_types["ImportError"] += 1
                                elif "ModuleNotFoundError" in line:
                                    error_types["ModuleNotFoundError"] += 1
                                elif "SQLAlchemyError" in line or "DatabaseError" in line:
                                    error_types["DatabaseError"] += 1
                                elif "TemplateNotFound" in line:
                                    error_types["TemplateNotFound"] += 1
                                elif "KeyError" in line:
                                    error_types["KeyError"] += 1
                                else:
                                    error_types["Other"] += 1
                        except Exception:
                            pass
                
                # Afficher les statistiques d'erreurs
                logger.info(f"📊 {len(recent_errors)} erreurs trouvées dans les logs récents")
                
                if error_types:
                    logger.info("Types d'erreurs les plus fréquents:")
                    for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                        logger.info(f"  - {error_type}: {count} occurrences")
                
                # Afficher les 5 dernières erreurs
                if recent_errors:
                    logger.info("5 dernières erreurs:")
                    for error in recent_errors[-5:]:
                        logger.info(f"  {error}")
                        
                    self.error_summary["logs"] = recent_errors[-10:]  # Garder les 10 dernières erreurs
                    self.issues_found.append(f"{len(recent_errors)} erreurs récentes dans les logs")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des logs: {str(e)}")
            logger.error(traceback.format_exc())
            self.error_count += 1
    
    def check_database_connection(self):
        """Vérifie la connexion à la base de données"""
        logger.info("\n🔍 Vérification de la connexion à la base de données...")
        
        try:
            # Importer les modules nécessaires
            from db_helper import init_db_connection
            
            # Tenter d'établir une connexion
            if init_db_connection():
                logger.info("✅ Connexion à la base de données établie avec succès")
            else:
                error_msg = "❌ Échec de la connexion à la base de données"
                logger.error(error_msg)
                self.error_count += 1
                self.error_summary["database"].append(error_msg)
                self.issues_found.append("Problème de connexion à la base de données")
                
                # Afficher l'URL de la base de données (masquée)
                db_url = os.environ.get("DATABASE_URL", "Non définie")
                if db_url != "Non définie":
                    # Masquer les informations sensibles
                    masked_url = db_url.split('@')[1] if '@' in db_url else 'Hidden'
                    logger.info(f"URL de la base de données: ...@{masked_url}")
        except ImportError:
            logger.warning("⚠️ Module db_helper non trouvé, vérification de la BDD ignorée")
            self.warning_count += 1
            self.issues_found.append("Module db_helper manquant")
        except Exception as e:
            error_msg = f"❌ Erreur lors de la vérification de la base de données: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.error_count += 1
            self.error_summary["database"].append(error_msg)
            self.issues_found.append("Erreur lors de la connexion à la BDD")
    
    def check_error_handlers(self):
        """Vérifie si les gestionnaires d'erreur sont correctement configurés"""
        logger.info("\n🔍 Vérification des gestionnaires d'erreur...")
        
        # Vérifier les importations dans error_interceptor.py
        try:
            with open("error_interceptor.py", "r") as f:
                content = f.read()
                
                # Vérifier les imports manquants
                missing_imports = []
                required_imports = ["request", "jsonify", "render_template", "logger", "SQLAlchemyError"]
                
                for imp in required_imports:
                    if imp not in content:
                        missing_imports.append(imp)
                
                if missing_imports:
                    error_msg = f"❌ Imports manquants dans error_interceptor.py: {', '.join(missing_imports)}"
                    logger.error(error_msg)
                    self.error_count += 1
                    self.error_summary["error_handlers"].append(error_msg)
                    self.issues_found.append("Imports manquants dans error_interceptor.py")
                else:
                    logger.info("✅ Tous les imports nécessaires sont présents dans error_interceptor.py")
                
                # Vérifier l'initialisation de ErrorInterceptor dans main.py
                try:
                    with open("main.py", "r") as main_file:
                        main_content = main_file.read()
                        if "error_interceptor.initialize()" not in main_content and "error_interceptor.ErrorInterceptor.init_app" not in main_content:
                            error_msg = "❌ ErrorInterceptor n'est pas initialisé dans main.py"
                            logger.error(error_msg)
                            self.error_count += 1
                            self.error_summary["error_handlers"].append(error_msg)
                            self.issues_found.append("ErrorInterceptor non initialisé dans main.py")
                        else:
                            logger.info("✅ ErrorInterceptor est correctement initialisé dans main.py")
                except Exception as e:
                    error_msg = f"❌ Erreur lors de la vérification de main.py: {str(e)}"
                    logger.error(error_msg)
                    self.error_count += 1
                    self.error_summary["error_handlers"].append(error_msg)
        except FileNotFoundError:
            error_msg = "❌ Fichier error_interceptor.py non trouvé"
            logger.error(error_msg)
            self.error_count += 1
            self.error_summary["error_handlers"].append(error_msg)
            self.issues_found.append("Fichier error_interceptor.py manquant")
        except Exception as e:
            error_msg = f"❌ Erreur lors de la vérification des gestionnaires d'erreur: {str(e)}"
            logger.error(error_msg)
            self.error_count += 1
            self.error_summary["error_handlers"].append(error_msg)
    
    def check_logging_configuration(self):
        """Vérifie si la configuration du logging est correcte"""
        logger.info("\n🔍 Vérification de la configuration du logging...")
        
        try:
            with open("app.py", "r") as f:
                content = f.read()
                
                # Vérifier le format de logging
                if "%(message.s" in content:
                    error_msg = "❌ Format de logging incorrect dans app.py: %(message.s au lieu de %(message)s"
                    logger.error(error_msg)
                    self.error_count += 1
                    self.error_summary["logging"].append(error_msg)
                    self.issues_found.append("Format de logging incorrect dans app.py")
                else:
                    logger.info("✅ Format de logging correct dans app.py")
                
                # Vérifier la création du dossier de logs
                if "os.makedirs" in content and "logs" in content:
                    logger.info("✅ Création du dossier de logs présente dans app.py")
                else:
                    logger.warning("⚠️ Création du dossier de logs potentiellement manquante dans app.py")
                    self.warning_count += 1
        except FileNotFoundError:
            error_msg = "❌ Fichier app.py non trouvé"
            logger.error(error_msg)
            self.error_count += 1
            self.error_summary["logging"].append(error_msg)
            self.issues_found.append("Fichier app.py manquant")
        except Exception as e:
            error_msg = f"❌ Erreur lors de la vérification de la configuration du logging: {str(e)}"
            logger.error(error_msg)
            self.error_count += 1
            self.error_summary["logging"].append(error_msg)
    
    def generate_report(self):
        """Génère un rapport détaillé des problèmes détectés"""
        logger.info("\n📋 Génération du rapport de diagnostic...")
        
        end_time = datetime.datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": f"{duration:.2f} secondes",
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues_found": self.issues_found,
            "detailed_errors": dict(self.error_summary)
        }
        
        # Enregistrer le rapport au format JSON
        report_path = "logs/diagnostic_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Rapport enregistré dans {report_path}")
        
        # Afficher un résumé
        print("\n" + "="*50)
        print(" RÉSUMÉ DU DIAGNOSTIC SMARTOHADA ".center(50, "="))
        print("="*50)
        print(f"🕒 Date et heure: {report['timestamp']}")
        print(f"⏱️ Durée: {report['duration']}")
        print(f"❌ Erreurs: {self.error_count}")
        print(f"⚠️ Avertissements: {self.warning_count}")
        print("\n🚨 PROBLÈMES DÉTECTÉS:")
        
        if self.issues_found:
            for i, issue in enumerate(self.issues_found, 1):
                print(f"  {i}. {issue}")
        else:
            print("  Aucun problème majeur détecté!")
        
        print("\n📝 RECOMMANDATIONS:")
        if self.error_count > 0:
            if "ModuleNotFoundError" in str(self.error_summary):
                print("  • Installez les modules manquants avec pip install")
            if "DatabaseError" in str(self.error_summary):
                print("  • Vérifiez la connexion à la base de données et ses paramètres")
            if "error_handlers" in self.error_summary:
                print("  • Corrigez la configuration des gestionnaires d'erreur")
            if "logging" in self.error_summary:
                print("  • Corrigez la configuration du logging dans app.py")
            print("  • Consultez le rapport détaillé dans logs/diagnostic_report.json")
        else:
            print("  • L'application semble correctement configurée!")
            if self.warning_count > 0:
                print("  • Quelques avertissements à surveiller, voir logs/diagnostic_report.json")
        
        print("="*50)
        
        return report
    
    def run_all_checks(self):
        """Exécute tous les tests de diagnostic"""
        print("\n" + "="*50)
        print(" DIAGNOSTIC SMARTOHADA EN COURS ".center(50, "="))
        print("="*50 + "\n")
        
        self.check_environment()
        self.check_modules()
        self.check_key_files()
        self.check_logs()
        self.check_database_connection()
        self.check_error_handlers()
        self.check_logging_configuration()
        
        return self.generate_report()

if __name__ == "__main__":
    try:
        diagnostics = ErrorDiagnostics()
        diagnostics.run_all_checks()
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrompu par l'utilisateur.")
    except Exception as e:
        print(f"\n\nErreur lors de l'exécution du diagnostic: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
