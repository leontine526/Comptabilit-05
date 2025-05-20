
"""
Adaptateur pour utiliser SQLite comme base de données de test
"""
import os
import logging
import sqlite3
from contextlib import contextmanager

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemin pour la base de données SQLite
DB_PATH = os.path.join(os.getcwd(), 'test_database.db')

def get_sqlite_uri():
    """Retourne l'URI pour la connexion SQLite"""
    return f"sqlite:///{DB_PATH}"

@contextmanager
def get_sqlite_connection():
    """Obtient une connexion à la base de données SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Pour avoir des résultats sous forme de dictionnaire
        yield conn
        conn.commit()
    except Exception as e:
        logger.error(f"Erreur de connexion SQLite: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def init_sqlite_db():
    """Initialise la base de données SQLite avec des tables de base"""
    logger.info("Initialisation de la base de données SQLite...")
    
    try:
        with get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            # Créer la table utilisateur
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                avatar TEXT,
                profile_picture TEXT,
                bio TEXT,
                position TEXT,
                company TEXT,
                last_seen TIMESTAMP,
                is_online BOOLEAN DEFAULT 0,
                socket_id TEXT,
                dashboard_layout TEXT DEFAULT '{}'
            )
            ''')
            
            # Créer la table exercise
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                description TEXT,
                is_closed BOOLEAN DEFAULT 0,
                is_published BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
            ''')
            
            # Vérifier si un utilisateur admin existe déjà
            cursor.execute("SELECT COUNT(*) FROM user WHERE email = 'admin@smartohada.com'")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Créer un utilisateur admin par défaut
                from werkzeug.security import generate_password_hash
                password_hash = generate_password_hash('admin123')
                
                cursor.execute('''
                INSERT INTO user (username, email, full_name, password_hash, is_admin)
                VALUES (?, ?, ?, ?, ?)
                ''', ('admin', 'admin@smartohada.com', 'Administrateur', password_hash, 1))
                
                logger.info("Utilisateur admin créé avec succès!")
            
            logger.info("Base de données SQLite initialisée avec succès!")
            return True
    
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données SQLite: {str(e)}")
        return False
