
import logging
import os
from app import app

# Créer un dossier pour les logs s'il n'existe pas
log_dir = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configurer le fichier de log
log_file = os.path.join(log_dir, 'app.log')

# Ajouter un handler pour écrire les logs dans un fichier
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Ajouter le handler à l'application
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

print(f"Logs activés et enregistrés dans {log_file}")
print("Redémarrez l'application pour que les changements prennent effet")
#!/usr/bin/env python
import os
import logging
from logging.handlers import RotatingFileHandler

def setup_file_logging():
    """Configure le logging pour enregistrer les erreurs dans un fichier"""
    # Créer le dossier logs s'il n'existe pas
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurer le logger
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    file_handler.setLevel(logging.ERROR)
    
    # Formater les messages de log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Ajouter le handler au logger racine
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    print(f"Logs activés et enregistrés dans {log_file}")
    print("Redémarrez l'application pour que les changements prennent effet")

if __name__ == "__main__":
    setup_file_logging()
