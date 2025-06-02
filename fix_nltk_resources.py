
#!/usr/bin/env python
"""
Script pour télécharger les ressources NLTK manquantes
"""
import os
import sys
import logging
import nltk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_nltk_resources():
    """Télécharge toutes les ressources NLTK nécessaires"""
    try:
        # Créer le dossier nltk_data s'il n'existe pas
        nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
        os.makedirs(nltk_data_dir, exist_ok=True)
        
        # Configurer NLTK pour utiliser notre dossier local
        nltk.data.path.insert(0, nltk_data_dir)
        
        # Liste des ressources nécessaires
        resources = [
            'punkt_tab',
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger'
        ]
        
        logger.info("Téléchargement des ressources NLTK...")
        
        for resource in resources:
            try:
                nltk.download(resource, download_dir=nltk_data_dir, quiet=False)
                logger.info(f"✅ {resource} téléchargé avec succès")
            except Exception as e:
                logger.warning(f"⚠️ Erreur pour {resource}: {str(e)}")
        
        logger.info("✅ Téléchargement des ressources NLTK terminé")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du téléchargement NLTK: {str(e)}")
        return False

if __name__ == "__main__":
    download_nltk_resources()
