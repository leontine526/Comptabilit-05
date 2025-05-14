
import json
import os
import logging
from datetime import datetime
from models import ExerciseExample, db
from exercise_solver import solver

logger = logging.getLogger(__name__)

def import_exercises_from_json(json_path):
    """
    Importe des exercices et leurs solutions depuis un fichier JSON.
    
    Format attendu du JSON:
    [
        {
            "title": "Titre de l'exercice",
            "problem_text": "Texte de l'énoncé...",
            "solution_text": "Texte de la solution...",
            "category": "journal", 
            "difficulty": 2
        },
        ...
    ]
    
    Returns:
        tuple: (nombre d'exercices importés, erreurs éventuelles)
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            exercises_data = json.load(file)
        
        if not isinstance(exercises_data, list):
            return 0, ["Le fichier JSON doit contenir une liste d'exercices"]
        
        imported_count = 0
        errors = []
        
        for idx, exercise_data in enumerate(exercises_data):
            try:
                # Vérifier que les champs obligatoires sont présents
                required_fields = ['title', 'problem_text', 'solution_text']
                if not all(field in exercise_data for field in required_fields):
                    missing = [f for f in required_fields if f not in exercise_data]
                    errors.append(f"Exercice #{idx+1}: champs manquants: {', '.join(missing)}")
                    continue
                
                # Générer un nom de fichier unique
                filename = f"json_import_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{idx}.pdf"
                
                # Créer un nouvel exemple
                example = ExerciseExample(
                    title=exercise_data['title'],
                    filename=filename,
                    problem_text=exercise_data['problem_text'],
                    solution_text=exercise_data['solution_text'],
                    category=exercise_data.get('category', 'général'),
                    difficulty=exercise_data.get('difficulty', 3),
                    user_id=1  # ID de l'administrateur ou premier utilisateur
                )
                
                db.session.add(example)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Erreur lors de l'importation de l'exercice #{idx+1}: {str(e)}")
        
        # Commit des changements à la base de données
        if imported_count > 0:
            db.session.commit()
            
            # Recharger les exemples dans le solveur
            solver.load_examples()
            
        return imported_count, errors
        
    except json.JSONDecodeError as e:
        return 0, [f"Erreur de format JSON: {str(e)}"]
    except Exception as e:
        return 0, [f"Erreur lors de l'importation: {str(e)}"]

if __name__ == "__main__":
    # Pour tester l'importation directement
    from app import app
    with app.app_context():
        json_path = input("Chemin vers le fichier JSON à importer: ")
        if os.path.exists(json_path):
            count, errors = import_exercises_from_json(json_path)
            print(f"{count} exercices importés avec succès.")
            if errors:
                print(f"{len(errors)} erreurs rencontrées:")
                for error in errors:
                    print(f"- {error}")
        else:
            print(f"Le fichier {json_path} n'existe pas.")
