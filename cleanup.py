
#!/usr/bin/env python
"""
Script pour réduire la taille de l'application OHADA Comptabilité
en éliminant les ressources linguistiques non utilisées et en optimisant les images.
"""
import os
import shutil
import logging
import sys
from pathlib import Path

try:
    import cv2
    import nltk
    from PIL import Image
except ImportError:
    print("Installation des dépendances nécessaires...")
    os.system("pip install opencv-python nltk pillow")
    import cv2
    import nltk
    from PIL import Image

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_nltk_data():
    """Supprime les langues non utilisées des données NLTK"""
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
    
    # Nettoyage des tokenizers
    punkt_dir = os.path.join(nltk_dir, 'tokenizers', 'punkt')
    py3_dir = os.path.join(punkt_dir, 'PY3')
    
    for dir_path in [punkt_dir, py3_dir]:
        if os.path.exists(dir_path):
            for lang_file in os.listdir(dir_path):
                if lang_file.endswith('.pickle') and not any(lang in lang_file for lang in keep_languages) and lang_file != 'README':
                    lang_path = os.path.join(dir_path, lang_file)
                    if os.path.isfile(lang_path):
                        os.remove(lang_path)
                        logger.info(f"Suppression du tokenizer: {lang_file}")
    
    logger.info("Nettoyage des données NLTK terminé.")

def optimize_images():
    """Optimise les images en les compressant"""
    assets_dir = os.path.join(os.getcwd(), 'attached_assets')
    if not os.path.exists(assets_dir):
        logger.warning("Dossier attached_assets non trouvé.")
        return
    
    total_saved = 0
    
    for filename in os.listdir(assets_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(assets_dir, filename)
            original_size = os.path.getsize(file_path)
            
            try:
                # Tentative avec PIL d'abord (meilleure qualité)
                try:
                    img = Image.open(file_path)
                    # Créer un fichier temporaire
                    temp_path = file_path + ".temp"
                    # Sauvegarde avec compression
                    if filename.lower().endswith('.png'):
                        img.save(temp_path, 'PNG', optimize=True)
                    else:
                        img.save(temp_path, 'JPEG', quality=85, optimize=True)
                    
                    # Si le fichier optimisé est plus petit, remplacer l'original
                    if os.path.getsize(temp_path) < original_size:
                        shutil.move(temp_path, file_path)
                        new_size = os.path.getsize(file_path)
                        saved = original_size - new_size
                        total_saved += saved
                        logger.info(f"Image optimisée: {filename} - Économie: {saved/1024:.2f} KB")
                    else:
                        os.remove(temp_path)
                        logger.info(f"Aucune optimisation possible pour: {filename}")
                except Exception as e:
                    logger.warning(f"Erreur PIL avec {filename}: {e}, essai avec OpenCV")
                    # Essai avec OpenCV
                    img = cv2.imread(file_path)
                    if img is not None:
                        # Paramètres de compression
                        if filename.lower().endswith('.png'):
                            params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
                        else:
                            params = [cv2.IMWRITE_JPEG_QUALITY, 85]
                        
                        # Créer un fichier temporaire
                        temp_path = file_path + ".temp"
                        cv2.imwrite(temp_path, img, params)
                        
                        # Si le fichier optimisé est plus petit, remplacer l'original
                        if os.path.getsize(temp_path) < original_size:
                            shutil.move(temp_path, file_path)
                            new_size = os.path.getsize(file_path)
                            saved = original_size - new_size
                            total_saved += saved
                            logger.info(f"Image optimisée (OpenCV): {filename} - Économie: {saved/1024:.2f} KB")
                        else:
                            os.remove(temp_path)
                            logger.info(f"Aucune optimisation possible pour: {filename} (OpenCV)")
            except Exception as e:
                logger.error(f"Erreur lors de l'optimisation de {filename}: {e}")
    
    logger.info(f"Total économisé: {total_saved/1024/1024:.2f} MB")

def clean_logs():
    """Nettoie les fichiers de logs obsolètes"""
    logs_dir = os.path.join(os.getcwd(), 'logs')
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            if filename.endswith('.log.1') or filename.endswith('.log.2'):
                file_path = os.path.join(logs_dir, filename)
                os.remove(file_path)
                logger.info(f"Suppression du fichier de log: {filename}")

def main():
    logger.info("Début du nettoyage de l'application OHADA Comptabilité")
    
    # Nettoyer les données NLTK
    clean_nltk_data()
    
    # Optimiser les images
    optimize_images()
    
    # Nettoyer les logs
    clean_logs()
    
    logger.info("Nettoyage terminé avec succès!")

if __name__ == "__main__":
    main()
