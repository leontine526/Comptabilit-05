"""
Script pour télécharger les ressources NLTK nécessaires.
"""

import nltk
import sys
import os

def download_nltk_resources():
    """Télécharge les ressources NLTK nécessaires pour l'application."""
    # Ressources à télécharger
    resources = [
        'punkt',
        'stopwords'
    ]
    
    # Définir un dossier personnalisé pour les données NLTK
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Configurer NLTK pour utiliser ce dossier
    nltk.data.path.append(nltk_data_dir)
    
    # Télécharger les ressources
    for resource in resources:
        try:
            print(f"Téléchargement de {resource}...")
            nltk.download(resource, download_dir=nltk_data_dir, quiet=False)
            print(f"Ressource {resource} téléchargée avec succès.")
        except Exception as e:
            print(f"Erreur lors du téléchargement de {resource}: {e}", file=sys.stderr)
            return False
    
    print("\nToutes les ressources NLTK ont été téléchargées avec succès.")
    return True

if __name__ == "__main__":
    print("Installation des ressources NLTK pour l'application de comptabilité OHADA...")
    success = download_nltk_resources()
    sys.exit(0 if success else 1)