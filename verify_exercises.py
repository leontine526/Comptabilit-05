
import json
from app import app
from models import ExerciseExample

def verify_imported_exercises():
    """Vérifie si les exercices ont été correctement importés dans la base de données"""
    try:
        # Ouvrir le fichier JSON original
        with open('attached_assets/tous_les_exercices_comptabilite_ohada.json', 'r', encoding='utf-8') as f:
            original_exercises = json.load(f)
        
        print(f"Le fichier JSON contient {len(original_exercises)} exercices")
        
        # Vérifier dans la base de données
        with app.app_context():
            examples = ExerciseExample.query.filter_by(category='comptabilité ohada').all()
            
            if examples:
                print(f"Trouvé {len(examples)} exercices de comptabilité OHADA dans la base de données")
                
                # Afficher un exemple pour comparaison
                example = examples[0]
                print(f"\nExemple dans la base de données:")
                print(f"Titre: {example.title}")
                print(f"Texte du problème (début): {example.problem_text[:150]}...")
                
                # Trouver l'exercice correspondant dans le JSON original
                original = next((o for o in original_exercises if o.get("exercice", "")[:50] == example.problem_text[:50]), None)
                
                if original:
                    print(f"\nExercice original correspondant trouvé:")
                    print(f"Texte: {original.get('exercice', '')[:150]}...")
                    print("\nLes exercices semblent avoir été importés correctement")
                else:
                    print("\nAucun exercice correspondant trouvé dans le fichier JSON original")
            else:
                print("Aucun exercice de comptabilité OHADA trouvé dans la base de données")
        
    except FileNotFoundError:
        print("Le fichier JSON n'a pas été trouvé")
    except Exception as e:
        print(f"Erreur lors de la vérification: {str(e)}")

if __name__ == "__main__":
    verify_imported_exercises()
