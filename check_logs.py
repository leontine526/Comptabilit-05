#!/usr/bin/env python
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_error_logs():
    """Vérifie les logs d'erreur et affiche les plus récents"""
    print("=== VÉRIFICATION DES LOGS D'ERREUR ===")

    # Vérifier si le dossier logs existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("Dossier logs créé. Aucun fichier de log trouvé.")
        return

    # Rechercher le fichier app.log
    log_file = os.path.join('logs', 'app.log')
    if not os.path.exists(log_file):
        print("Aucun fichier de log trouvé.")
        return

    # Lire les 50 dernières lignes du fichier de log
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            error_lines = [line for line in lines if 'ERROR' in line]
            if error_lines:
                print("Dernières erreurs dans les logs:")
                for i in range(min(10, len(error_lines))):
                    print(error_lines[-i-1].strip())
            else:
                print("Aucune erreur trouvée dans les logs.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de log: {str(e)}")

def check_database_connection():
    """Vérifier la connexion à la base de données Neon"""
    print("\n=== DIAGNOSTIC DE CONNEXION À LA BASE DE DONNÉES ===")

    # Charger les variables d'environnement
    load_dotenv()

    # URL de la base de données Neon
    database_url = os.environ.get("DATABASE_URL", 
                                "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")

    print(f"URL de base de données utilisée: {database_url.split('@')[1] if '@' in database_url else 'URL masquée'}")

    try:
        # Import sécurisé des modules nécessaires
        try:
            from sqlalchemy import create_engine, text, inspect

            # Créer un moteur SQLAlchemy avec des paramètres optimisés pour Neon
            engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=60,
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": 10,
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 3
                }
            )

            # Tester la connexion
            print("Test de connexion en cours...")
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                row = result.fetchone()
                if row and row[0] == 1:
                    print("✅ Connexion réussie à la base de données Neon!")

                    # Vérifier les tables existantes
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()

                    if tables:
                        print(f"✅ Tables trouvées ({len(tables)}): {', '.join(tables)}")
                    else:
                        print("⚠️ Aucune table n'existe dans la base de données. Initialisation nécessaire.")

                    # Vérifier les paramètres de connexion
                    print("\nInformations de connexion:")
                    conn_info = conn.connection.info
                    print(f"Serveur: {conn_info.dsn_parameters.get('host', 'N/A') if hasattr(conn_info, 'dsn_parameters') else 'N/A'}")
                    print(f"Base de données: {conn_info.dsn_parameters.get('dbname', 'N/A') if hasattr(conn_info, 'dsn_parameters') else 'N/A'}")
                    print(f"Utilisateur: {conn_info.dsn_parameters.get('user', 'N/A') if hasattr(conn_info, 'dsn_parameters') else 'N/A'}")

                    return True
                else:
                    print("❌ La requête de test a échoué")
                    return False
        except ImportError as e:
            print(f"❌ Module manquant pour la connexion à la base de données: {str(e)}")
            print("Installez SQLAlchemy avec: pip install sqlalchemy")
            return False

    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

def check_missing_modules():
    """Vérifie les modules nécessaires à l'application"""
    print("\n=== VÉRIFICATION DES MODULES REQUIS ===")

    required_modules = [
        "flask", 
        "flask_login", 
        "flask_sqlalchemy", 
        "sqlalchemy", 
        "flask_socketio", 
        "dotenv"
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module.replace("_", "."))
            print(f"✅ Module {module} disponible")
        except ImportError:
            formatted_name = module.replace("_", "-")
            if module == "dotenv":
                formatted_name = "python-dotenv"
            print(f"❌ Module {module} manquant")
            missing_modules.append(formatted_name)

    if missing_modules:
        print("\nInstallation des modules manquants:")
        print(f"pip install {' '.join(missing_modules)}")
    else:
        print("\n✅ Tous les modules requis sont disponibles")

if __name__ == "__main__":
    print("=== DIAGNOSTIC DE L'APPLICATION SMARTOHADA ===")
    check_error_logs()
    check_missing_modules()
    check_database_connection()

    print("\n=== DIAGNOSTIC TERMINÉ ===")
    print("Si des problèmes persistent, exécutez 'python error_diagnostics.py' pour une analyse plus approfondie.")