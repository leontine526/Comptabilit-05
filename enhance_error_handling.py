
#!/usr/bin/env python
"""
Script pour améliorer la gestion des erreurs et assurer la robustesse de l'application
"""
import os
import sys
import logging
import traceback

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("error_handler_enhancer")

def enhance_error_handing_in_main():
    """Ajoute un bloc try-except global dans main.py"""
    file_path = "main.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Fichier {file_path} introuvable!")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Vérifier si un bloc try-except global existe déjà
        if "if __name__ == '__main__':" in content and "try:" not in content:
            # Trouver la position du bloc principal
            main_block_pos = content.find("if __name__ == '__main__':")
            
            if main_block_pos > 0:
                # Séparer le contenu avant et après le bloc principal
                before_main = content[:main_block_pos]
                main_block = content[main_block_pos:]
                
                # Extraire l'indentation
                lines = main_block.split('\n')
                if len(lines) > 1:
                    indent = ""
                    for char in lines[1]:
                        if char.isspace():
                            indent += char
                        else:
                            break
                    
                    # Ajouter le bloc try-except
                    new_main_block = lines[0] + "\n"
                    new_main_block += indent + "try:\n"
                    
                    # Indenter le reste du bloc principal
                    for i in range(1, len(lines)):
                        if lines[i].strip():
                            new_main_block += indent + "    " + lines[i].lstrip() + "\n"
                        else:
                            new_main_block += "\n"
                    
                    # Ajouter le bloc except
                    new_main_block += indent + "except Exception as e:\n"
                    new_main_block += indent + "    import traceback\n"
                    new_main_block += indent + "    print(f\"Erreur critique: {str(e)}\")\n"
                    new_main_block += indent + "    logging.error(f\"Exception non gérée: {str(e)}\")\n"
                    new_main_block += indent + "    logging.error(traceback.format_exc())\n"
                    new_main_block += indent + "    sys.exit(1)\n"
                    
                    # Recombiner le contenu
                    new_content = before_main + new_main_block
                    
                    # Sauvegarder le fichier modifié
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    
                    logger.info(f"✅ Bloc try-except global ajouté à {file_path}")
                    return True
        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la modification de {file_path}: {str(e)}")
        return False

def ensure_socketio_error_handling():
    """Améliore la gestion des erreurs dans les événements socketio"""
    file_path = "socket_events.py"
    
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Vérifier si des gestionnaires d'événements socketio existent
        if "@socketio.on" in content:
            modified = False
            lines = content.split('\n')
            new_lines = []
            
            i = 0
            while i < len(lines):
                line = lines[i]
                new_lines.append(line)
                
                # Détecter les gestionnaires d'événements
                if "@socketio.on" in line and i + 1 < len(lines):
                    # Vérifier si la fonction suivante contient déjà un try-except
                    next_lines = []
                    j = i + 1
                    while j < len(lines) and (not lines[j].strip().startswith("@") or lines[j].strip().startswith("@app") or lines[j].strip().startswith("@login")):
                        next_lines.append(lines[j])
                        j += 1
                    
                    # Si aucun try-except n'est trouvé, en ajouter un
                    if not any("try:" in l for l in next_lines):
                        func_def = next_lines[0]
                        indent = ""
                        for char in func_def:
                            if char.isspace():
                                indent += char
                            else:
                                break
                        
                        # Ajouter la définition de fonction
                        new_lines.append(func_def)
                        
                        # Ajouter le bloc try
                        new_lines.append(indent + "    try:")
                        
                        # Ajouter le corps de la fonction avec indentation supplémentaire
                        for k in range(1, len(next_lines)):
                            if next_lines[k].strip():
                                new_lines.append(indent + "        " + next_lines[k].lstrip())
                            else:
                                new_lines.append("")
                        
                        # Ajouter le bloc except
                        new_lines.append(indent + "    except Exception as e:")
                        new_lines.append(indent + "        logging.error(f\"Erreur dans l'événement socketio: {str(e)}\")")
                        new_lines.append(indent + "        logging.error(traceback.format_exc())")
                        new_lines.append(indent + "        socketio.emit('error', {'message': 'Une erreur est survenue', 'details': str(e)})")
                        
                        modified = True
                        i = j - 1  # Ajuster l'index pour continuer après le bloc de fonction
                    else:
                        # Ajouter les lignes suivantes telles quelles
                        for line in next_lines:
                            new_lines.append(line)
                        i = j - 1
                
                i += 1
            
            if modified:
                # S'assurer que traceback est importé
                if "import traceback" not in content:
                    insert_pos = 0
                    for i, line in enumerate(new_lines):
                        if line.startswith("import ") or line.startswith("from "):
                            insert_pos = i + 1
                    
                    new_lines.insert(insert_pos, "import traceback")
                
                # Sauvegarder le fichier modifié
                with open(file_path, 'w') as f:
                    f.write('\n'.join(new_lines))
                
                logger.info(f"✅ Gestion d'erreurs améliorée dans les événements socketio de {file_path}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la modification de {file_path}: {str(e)}")
        return False

def create_logs_filter():
    """Crée un filtre pour éviter le débordement des logs"""
    file_path = "log_filter.py"
    
    try:
        content = """#!/usr/bin/env python
import logging
import time
from collections import defaultdict

class RateLimitFilter(logging.Filter):
    """
    Filtre de logging pour limiter les messages répétitifs.
    Évite le remplissage rapide des fichiers de log.
    """
    def __init__(self, rate_limit_seconds=60):
        super().__init__()
        self.rate_limit_seconds = rate_limit_seconds
        self.last_log = defaultdict(lambda: 0)
        self.suppressed_count = defaultdict(lambda: 0)
    
    def filter(self, record):
        # Créer une clé unique pour ce message de log
        log_key = f"{record.levelname}:{record.module}:{record.funcName}:{record.getMessage()}"
        
        current_time = time.time()
        time_diff = current_time - self.last_log[log_key]
        
        # Si le message est répété trop rapidement
        if time_diff < self.rate_limit_seconds:
            self.suppressed_count[log_key] += 1
            return False
        
        # Si des messages ont été supprimés, ajouter cette information
        if self.suppressed_count[log_key] > 0:
            record.msg = f"{record.msg} (+ {self.suppressed_count[log_key]} messages similaires supprimés)"
            self.suppressed_count[log_key] = 0
        
        # Mettre à jour le timestamp du dernier log
        self.last_log[log_key] = current_time
        return True

def configure_rate_limited_logging():
    """Configure les filtres pour limiter les messages de log répétitifs"""
    # Configurer le filtre pour le logger racine
    root_logger = logging.getLogger()
    rate_filter = RateLimitFilter()
    root_logger.addFilter(rate_filter)
    
    # Ajouter aussi aux handlers existants
    for handler in root_logger.handlers:
        if not any(isinstance(f, RateLimitFilter) for f in handler.filters):
            handler.addFilter(rate_filter)
    
    return rate_filter

if __name__ == "__main__":
    # Test du filtre
    logging.basicConfig(level=logging.INFO)
    configure_rate_limited_logging()
    
    # Simuler des logs répétitifs
    for i in range(100):
        logging.error("Ceci est une erreur répétitive")
        time.sleep(0.1)
"""
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"✅ Filtre de limitation de logs créé: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création du filtre de logs: {str(e)}")
        return False

def main():
    """Fonction principale"""
    logger.info("Amélioration de la gestion des erreurs...")
    
    # Améliorer la gestion des erreurs dans main.py
    enhance_error_handing_in_main()
    
    # Améliorer la gestion des erreurs dans les événements socketio
    ensure_socketio_error_handling()
    
    # Créer un filtre pour les logs
    create_logs_filter()
    
    logger.info("Améliorations de la gestion d'erreurs terminées.")
    logger.info("Votre application devrait être plus robuste face aux erreurs.")

if __name__ == "__main__":
    main()
