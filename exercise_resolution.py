import logging
from models import Exercise, ExerciseSolution, Document
from app import db
from document_generator import generate_report
from exercise_solver import solver
from datetime import datetime
import os
import json

logger = logging.getLogger(__name__)

def resolve_exercise_completely(exercise_id, problem_text):
    """
    Résout complètement un exercice en générant:
    1. La solution textuelle (écritures comptables)
    2. Le journal comptable
    3. Le grand livre
    4. Le bilan final

    Args:
        exercise_id: ID de l'exercice
        problem_text: Texte de l'énoncé de l'exercice

    Returns:
        Dict contenant les chemins vers les documents générés et les statuts
    """
    results = {
        'success': False,
        'solution': None,
        'journal': None,
        'grand_livre': None,
        'bilan': None,
        'errors': []
    }

    try:
        # 1. Vérifier si l'exercice existe
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            results['errors'].append(f"Exercice avec ID {exercise_id} non trouvé")
            return results

        # 2. Générer une solution simple en utilisant ComptableIA
        from ecriture_generator import ComptableIA
        comptable_ia = ComptableIA()
        solution_text = comptable_ia.generer_ecriture(problem_text)

        if not solution_text:
            # Fallback au solveur traditionnel si ComptableIA échoue
            solution_result = solver.solve_exercise(problem_text)
            if not solution_result['success']:
                results['errors'].append("Impossible de résoudre l'exercice: " + solution_result.get('message', 'Erreur inconnue'))
                return results
            solution_text = solution_result['solution']

        # 3. Mettre à jour les résultats
        results['success'] = True
        results['solution'] = solution_text

        # 4. Générer les documents (à implémenter plus tard)
        # results['journal'] = generate_journal_document(exercise_id, solution_text)
        # results['grand_livre'] = generate_ledger_document(exercise_id, solution_text)
        # results['bilan'] = generate_balance_sheet_document(exercise_id, solution_text)

        solution = ExerciseSolution(
            exercise_id=exercise_id,
            solution_text=solution_text,
            confidence=solution_result['confidence'],
            examples_used=json.dumps(solution_result.get('similar_examples', [])),
            user_id=exercise.user_id
        )

        db.session.add(solution)
        db.session.flush()  # Pour obtenir l'ID de la solution
        results['solution'] = solution.id

        # 2. Générer le journal comptable
        try:
            journal_path = generate_report(exercise_id, 'journal', 'html')
            results['journal'] = os.path.basename(journal_path)
        except Exception as e:
            logger.error(f"Erreur lors de la génération du journal: {str(e)}")
            results['errors'].append(f"Erreur lors de la génération du journal: {str(e)}")

        # 3. Générer le grand livre
        try:
            general_ledger_path = generate_report(exercise_id, 'general_ledger', 'html')
            results['grand_livre'] = os.path.basename(general_ledger_path)
        except Exception as e:
            logger.error(f"Erreur lors de la génération du grand livre: {str(e)}")
            results['errors'].append(f"Erreur lors de la génération du grand livre: {str(e)}")

        # 4. Générer le bilan final
        try:
            balance_sheet_path = generate_report(exercise_id, 'balance_sheet', 'html')
            results['bilan'] = os.path.basename(balance_sheet_path)
        except Exception as e:
            logger.error(f"Erreur lors de la génération du bilan: {str(e)}")
            results['errors'].append(f"Erreur lors de la génération du bilan: {str(e)}")

        # Commit les changements dans la base de données
        db.session.commit()

        # Marquer comme succès si au moins un document a été généré
        if results['journal'] or results['grand_livre'] or results['bilan']:
            results['success'] = True

        return results

    except Exception as e:
        import traceback
        logger.error(f"Erreur lors de la résolution complète de l'exercice: {str(e)}")
        results['errors'].append(f"Erreur système: {str(e)}")
        return results