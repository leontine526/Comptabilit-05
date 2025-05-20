
import logging
import traceback
from app import app
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=== VÉRIFICATION DES LOGS D'ERREUR ===")
print("Dernière erreur 500 (Internal Server Error):")

# Affichage des logs stockés en mémoire
if hasattr(app, 'logger') and app.logger.handlers:
    for handler in app.logger.handlers:
        if hasattr(handler, 'baseFilename'):
            print(f"Fichier de log: {handler.baseFilename}")
            try:
                with open(handler.baseFilename, 'r') as f:
                    logs = f.readlines()
                    # Filtrer les lignes avec ERROR ou CRITICAL
                    error_logs = [log for log in logs if "ERROR" in log or "CRITICAL" in log]
                    # Afficher les 10 dernières erreurs
                    if error_logs:
                        for log in error_logs[-10:]:
                            print(log.strip())
                    else:
                        print("Aucune erreur trouvée dans les logs.")
            except Exception as e:
                print(f"Impossible de lire le fichier de log: {str(e)}")

# Vérifier les erreurs dans Werkzeug
try:
    from werkzeug.serving import run_simple
    print("\nDernières erreurs Werkzeug (serveur de développement):")
    # Werkzeug stocke généralement ses logs dans stderr
    print("Les erreurs Werkzeug sont généralement affichées dans la console.")
except ImportError:
    print("Werkzeug n'est pas disponible.")

# Tester la route de connexion pour voir si elle génère une erreur
print("\n=== TEST DE LA ROUTE DE CONNEXION ===")
try:
    with app.test_client() as client:
        response = client.get('/login')
        print(f"Statut: {response.status_code}")
        if response.status_code == 500:
            print("La route /login génère une erreur 500!")
        else:
            print("La route /login semble fonctionner correctement.")
except Exception as e:
    print(f"Erreur lors du test: {str(e)}")
    traceback.print_exc()

print("\n=== CONSEILS DE DÉBOGAGE ===")
print("1. Vérifiez la connexion à la base de données")
print("2. Assurez-vous que les tables nécessaires sont créées")
print("3. Vérifiez que les imports sont corrects")
print("4. Regardez s'il y a des erreurs dans les formulaires")
print("5. Pour plus de détails, activez le mode DEBUG dans main.py")
#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime

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
                print("Dernière erreur 500 (Internal Server Error):")
                for i in range(min(10, len(error_lines))):
                    print(error_lines[-i-1].strip())
            else:
                print("Aucune erreur trouvée dans les logs.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de log: {str(e)}")
    
    # Vérifier les erreurs Werkzeug (serveur de développement)
    print("\nDernières erreurs Werkzeug (serveur de développement):")
    print("Les erreurs Werkzeug sont généralement affichées dans la console.")
    
    # Test fonctionnel de la route login
    print("\n=== TEST DE LA ROUTE DE CONNEXION ===")
    try:
        import requests
        response = requests.get("http://localhost:5000/login")
        print(f"Statut: {response.status_code}")
        if response.status_code == 200:
            print("La route /login semble fonctionner correctement.")
        else:
            print(f"La route /login renvoie un code d'erreur: {response.status_code}")
    except Exception as e:
        print(f"Impossible de tester la route /login: {str(e)}")
    
    # Conseils de débogage
    print("\n=== CONSEILS DE DÉBOGAGE ===")
    print("1. Vérifiez la connexion à la base de données")
    print("2. Assurez-vous que les tables nécessaires sont créées")
    print("3. Vérifiez que les imports sont corrects")
    print("4. Regardez s'il y a des erreurs dans les formulaires")
    print("5. Pour plus de détails, activez le mode DEBUG dans main.py")

if __name__ == "__main__":
    check_error_logs()
import os
import logging
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_connection():
    """Vérifier la connexion à la base de données Neon"""
    print("=== DIAGNOSTIC DE CONNEXION À LA BASE DE DONNÉES ===")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # URL de la base de données Neon
    database_url = os.environ.get("DATABASE_URL", 
                                "postgresql://neondb_owner:npg_APBmGjkT0y1H@ep-rough-truth-a5ntheq6-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
    
    print(f"URL de base de données utilisée: {database_url.split('@')[1] if '@' in database_url else 'URL masquée'}")
    
    try:
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
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

if __name__ == "__main__":
    if check_database_connection():
        print("\n✅ DIAGNOSTIC TERMINÉ: Connexion à la base de données Neon établie avec succès.")
        print("Vous pouvez maintenant utiliser l'application normalement.")
        sys.exit(0)
    else:
        print("\n❌ DIAGNOSTIC TERMINÉ: Échec de connexion à la base de données Neon.")
        print("Vérifiez les paramètres de connexion et réessayez.")
        sys.exit(1)
