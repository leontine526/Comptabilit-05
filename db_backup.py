
#!/usr/bin/env python
"""
Script de sauvegarde automatique de la base de données.
Crée une sauvegarde SQL de la base de données PostgreSQL.
"""
import os
import time
import logging
from datetime import datetime
import subprocess
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_backup():
    """Crée une sauvegarde de la base de données PostgreSQL."""
    # Charger les variables d'environnement depuis .env
    load_dotenv()
    
    # Récupérer l'URL de la base de données
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL n'est pas définie dans les variables d'environnement")
        return False
    
    try:
        # Extraire les informations de connexion
        # Format: postgresql://user:password@host:port/dbname
        parts = database_url.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        
        username = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        host = host_db[0].split(':')[0]
        port = host_db[0].split(':')[1] if ':' in host_db[0] else '5432'
        dbname = host_db[1].split('?')[0]
        
        # Créer le répertoire de sauvegarde s'il n'existe pas
        backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nom du fichier de sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{dbname}_{timestamp}.sql")
        
        # Variables d'environnement pour pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Commande pg_dump
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', username,
            '-d', dbname,
            '-f', backup_file,
            '--format=plain',
            '--no-owner',
            '--no-acl'
        ]
        
        logger.info(f"Création d'une sauvegarde de la base de données {dbname} vers {backup_file}")
        
        # Exécuter la commande
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Sauvegarde créée avec succès: {backup_file}")
            
            # Nettoyer les anciennes sauvegardes (conserver les 5 plus récentes)
            backup_files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) 
                           if f.startswith(f"{dbname}_") and f.endswith('.sql')]
            
            if len(backup_files) > 5:
                backup_files.sort(key=lambda x: os.path.getctime(x))
                for old_file in backup_files[:-5]:
                    os.remove(old_file)
                    logger.info(f"Ancienne sauvegarde supprimée: {old_file}")
            
            return True
        else:
            logger.error(f"Erreur lors de la sauvegarde: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la création de la sauvegarde: {str(e)}")
        return False

if __name__ == "__main__":
    create_backup()
