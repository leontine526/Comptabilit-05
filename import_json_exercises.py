
import os
import json
import sys
from datetime import datetime
from app import app, db
from models import ExerciseExample
from exercise_solver import solver

def import_exercises_from_json(json_path, admin_id=1):
    """
    Importe des exercices depuis le fichier JSON fourni.
    
    Args:
        json_path (str): Chemin vers le fichier JSON
        admin_id (int): ID de l'administrateur qui importe les exercices
    
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
        
        with app.app_context():
            for idx, exercise_data in enumerate(exercises_data):
                try:
                    # Vérifier la structure de l'exercice
                    if 'exercice' not in exercise_data or 'resolution' not in exercise_data:
                        errors.append(f"Exercice #{idx+1}: structure incorrecte, 'exercice' ou 'resolution' manquant")
                        continue
                    
                    # Générer un nom de fichier unique
                    filename = f"json_import_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{idx}.json"
                    
                    # Préparer les données d'exercice
                    problem_text = exercise_data['exercice']
                    
                    # Convertir la résolution en texte
                    resolution = exercise_data.get('resolution', {})
                    solution_text = json.dumps(resolution, indent=2, ensure_ascii=False)
                    
                    # Créer un titre à partir du début de l'exercice
                    title = f"Exercice importé #{idx+1}"
                    if len(problem_text) > 50:
                        title = problem_text[:50] + "..."
                    
                    # Créer un nouvel exemple
                    example = ExerciseExample(
                        title=title,
                        filename=filename,
                        problem_text=problem_text,
                        solution_text=solution_text,
                        category="comptabilité ohada",
                        difficulty=3,
                        user_id=admin_id
                    )
                    
                    db.session.add(example)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Erreur lors de l'importation de l'exercice #{idx+1}: {str(e)}")
            
            # Commit des changements à la base de données si des exercices ont été importés
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
    if len(sys.argv) < 2:
        # Utiliser le chemin par défaut du fichier téléchargé
        json_path = os.path.join("attached_assets", "tous_les_exercices_comptabilite_ohada.json")
        if not os.path.exists(json_path):
            print(f"Fichier JSON introuvable: {json_path}")
            print("Usage: python import_json_exercises.py [chemin_du_fichier_json] [admin_id]")
            sys.exit(1)
    else:
        json_path = sys.argv[1]
    
    admin_id = 1
    if len(sys.argv) >= 3:
        admin_id = int(sys.argv[2])
    
    count, errors = import_exercises_from_json(json_path, admin_id)
    print(f"{count} exercices importés avec succès.")
    
    if errors:
        print(f"{len(errors)} erreurs rencontrées:")
        for error in errors:
            print(f"- {error}")
