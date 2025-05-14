
#!/usr/bin/env python
"""
Script amélioré pour réduire la taille de l'application OHADA Comptabilité
en ciblant le cache pip et les fichiers temporaires.
"""
import os
import shutil
import glob
import logging
import sys
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_pip_cache():
    """Nettoie le cache pip tout en préservant les modules actuellement installés"""
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "pip")
    
    if os.path.exists(cache_dir):
        # Conserver uniquement le répertoire http
        http_dir = os.path.join(cache_dir, "http")
        wheels_dir = os.path.join(cache_dir, "wheels")
        
        # Sauvegarde des fichiers récemment utilisés
        if os.path.exists(wheels_dir):
            # Trier par date de modification décroissante et garder les 10 plus récents
            wheel_files = sorted(
                glob.glob(os.path.join(wheels_dir, "*.whl")), 
                key=os.path.getmtime, 
                reverse=True
            )[:10]
            
            # Créer un dossier temporaire pour la sauvegarde
            temp_dir = os.path.join(cache_dir, "temp_wheels")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Copier les fichiers récents
            for wheel in wheel_files:
                shutil.copy2(wheel, temp_dir)
        
        # Nettoyer le cache
        try:
            size_before = get_dir_size(cache_dir)
            
            # Supprimer tous les sous-répertoires sauf http qui est nécessaire
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                if os.path.isdir(item_path) and item != "http" and item != "temp_wheels":
                    shutil.rmtree(item_path)
            
            # Restaurer les wheels récents
            if os.path.exists(temp_dir):
                os.makedirs(wheels_dir, exist_ok=True)
                for wheel in os.listdir(temp_dir):
                    shutil.move(os.path.join(temp_dir, wheel), wheels_dir)
                shutil.rmtree(temp_dir)
            
            size_after = get_dir_size(cache_dir)
            saved = (size_before - size_after) / (1024 * 1024)  # En MB
            
            logger.info(f"Nettoyage du cache pip: {saved:.2f} MB économisés")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du cache pip: {e}")

def clean_python_libs_cache():
    """Nettoie les fichiers de cache dans .pythonlibs"""
    python_libs_dir = os.path.join(os.getcwd(), '.pythonlibs')
    
    if os.path.exists(python_libs_dir):
        try:
            size_before = get_dir_size(python_libs_dir)
            
            # Supprimer les fichiers .pyc
            for pyc_file in glob.glob(os.path.join(python_libs_dir, "**/*.pyc"), recursive=True):
                os.remove(pyc_file)
            
            # Supprimer les dossiers __pycache__
            for pycache_dir in glob.glob(os.path.join(python_libs_dir, "**/__pycache__"), recursive=True):
                shutil.rmtree(pycache_dir)
            
            size_after = get_dir_size(python_libs_dir)
            saved = (size_before - size_after) / (1024 * 1024)  # En MB
            
            logger.info(f"Nettoyage des caches Python: {saved:.2f} MB économisés")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des caches Python: {e}")

def get_dir_size(path):
    """Calcule la taille d'un répertoire en octets"""
    total_size = 0
    
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):  # Évite les erreurs avec les liens symboliques
                total_size += os.path.getsize(fp)
    
    return total_size

def clean_nltk_data():
    """Supprime les langues non utilisées des données NLTK tout en préservant fr et en"""
    nltk_dir = os.path.join(os.getcwd(), 'nltk_data')
    if not os.path.exists(nltk_dir):
        logger.warning("Dossier nltk_data non trouvé.")
        return
    
    # Langues à conserver
    keep_languages = ['french', 'english']
    
    # Nettoyage des stopwords
    stopwords_dir = os.path.join(nltk_dir, 'corpora', 'stopwords')
    if os.path.exists(stopwords_dir):
        for lang_file in os.listdir(stopwords_dir):
            if lang_file not in keep_languages and lang_file != 'README':
                lang_path = os.path.join(stopwords_dir, lang_file)
                if os.path.isfile(lang_path):
                    os.remove(lang_path)
                    logger.info(f"Suppression du fichier de stopwords: {lang_file}")
    
    # Nettoyage des tokenizers - on ne garde que français et anglais
    punkt_dir = os.path.join(nltk_dir, 'tokenizers', 'punkt')
    py3_dir = os.path.join(punkt_dir, 'PY3')
    
    for dir_path in [punkt_dir, py3_dir]:
        if os.path.exists(dir_path):
            for lang_file in os.listdir(dir_path):
                if (lang_file.endswith('.pickle') and 
                    not any(lang in lang_file for lang in ['french', 'english']) and 
                    lang_file != 'README'):
                    lang_path = os.path.join(dir_path, lang_file)
                    if os.path.isfile(lang_path):
                        os.remove(lang_path)
                        logger.info(f"Suppression du tokenizer: {lang_file}")
    
    logger.info("Nettoyage des données NLTK terminé.")

def main():
    logger.info("Début du nettoyage avancé de l'application OHADA Comptabilité")
    
    # Nettoyer le cache pip
    clean_pip_cache()
    
    # Nettoyer les caches Python
    clean_python_libs_cache()
    
    # Nettoyer les données NLTK (garder uniquement fr et en)
    clean_nltk_data()
    
    # Afficher la taille actuelle
    os.system("du -sh")
    
    logger.info("Nettoyage avancé terminé avec succès.")
    logger.info("Note: Ce nettoyage préserve toutes les fonctionnalités essentielles de l'application.")

if __name__ == "__main__":
    main()
