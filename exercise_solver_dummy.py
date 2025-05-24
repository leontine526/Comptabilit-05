
"""
Version simplifiée du module exercise_solver pour permettre le démarrage de l'application.
Ce fichier contourne l'erreur d'importation de PyMuPDF (fitz).
"""

import logging

# Initialisation du logging
logger = logging.getLogger(__name__)

class ExerciseSolver:
    """Version simplifiée du solveur d'exercices."""
    
    def __init__(self):
        """Initialise le solveur d'exercices."""
        self.examples = []
        logger.info("Solveur d'exercices simplifié initialisé")
    
    def load_examples(self):
        """Version simplifiée qui ne charge pas d'exemples."""
        logger.warning("Chargement des exemples désactivé dans la version simplifiée")
        return []
    
    def solve_exercise(self, problem_text):
        """Version simplifiée qui retourne un message d'erreur."""
        return {
            'success': False,
            'message': "La fonctionnalité de résolution d'exercices est temporairement indisponible.",
            'solution': None,
            'confidence': 0.0,
            'diagnostic': "Module PyMuPDF (fitz) non disponible. Veuillez installer les dépendances requises."
        }
    
    def find_similar_examples(self, problem_text, top_n=3, min_similarity=0.2):
        """Version simplifiée qui ne trouve pas d'exemples similaires."""
        return []
    
    def extract_accounting_data(self, text):
        """Version simplifiée d'extraction de données."""
        return {
            'accounts': [],
            'amounts': [],
            'dates': [],
            'transactions': [],
            'keywords': [],
            'entities': {}
        }

# Initialiser le solveur
solver = ExerciseSolver()

def save_example_pdf(file_path, destination_name=None):
    """Version simplifiée qui ne sauvegarde pas de PDF."""
    logger.warning("Sauvegarde d'exemples désactivée dans la version simplifiée")
    return False
