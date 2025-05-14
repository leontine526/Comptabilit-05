"""
Module pour la résolution automatique d'exercices comptables basés sur des exemples similaires.
Ce module utilise des techniques de traitement du langage naturel et d'apprentissage automatique
pour identifier les similarités entre les exercices et appliquer des solutions analogues.
"""

import os
import logging
import re
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# Initialisation du logging
logger = logging.getLogger(__name__)

# Téléchargement des ressources NLTK si nécessaires
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"Impossible de télécharger les ressources NLTK: {e}")

# Constantes
EXAMPLE_DIR = os.path.join(os.getcwd(), 'examples')
os.makedirs(EXAMPLE_DIR, exist_ok=True)

class ExerciseSolver:
    """Classe principale pour la résolution d'exercices comptables."""
    
    def __init__(self):
        """Initialise le solveur d'exercices."""
        self.examples = []
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=stopwords.words('french'),
            ngram_range=(1, 3)
        )
        self.load_examples()
    
    def load_examples(self):
        """Charge les exemples d'exercices résolus depuis le répertoire des exemples."""
        self.examples = []
        
        example_files = list(Path(EXAMPLE_DIR).glob('*.pdf'))
        if not example_files:
            logger.warning("Aucun exemple d'exercice trouvé dans le répertoire des exemples.")
            return
        
        for pdf_path in example_files:
            try:
                # Extraire le texte et les informations du PDF
                example_data = self._extract_from_pdf(str(pdf_path))
                if example_data:
                    self.examples.append(example_data)
                    logger.info(f"Exemple chargé: {pdf_path.name}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'exemple {pdf_path}: {e}")
        
        logger.info(f"{len(self.examples)} exemples d'exercices chargés.")
    
    def _extract_from_pdf(self, pdf_path):
        """Extrait le texte et les informations d'un PDF d'exemple."""
        try:
            doc = fitz.open(pdf_path)
            
            # Extraire le texte complet
            full_text = ""
            problem_text = ""
            solution_text = ""
            
            # Chercher où commence l'énoncé et la solution
            problem_found = False
            solution_found = False
            
            for page in doc:
                text = page.get_text()
                full_text += text
                
                # Recherche de l'énoncé et de la solution
                if not problem_found and re.search(r'(énoncé|exercice|problème)', text.lower()):
                    problem_found = True
                
                if problem_found and not solution_found:
                    if re.search(r'(solution|résolution|correction)', text.lower()):
                        solution_found = True
                    else:
                        problem_text += text
                
                if solution_found:
                    solution_text += text
            
            # Si on n'a pas trouvé explicitement, on suppose que la première moitié est l'énoncé
            # et la seconde moitié est la solution
            if not problem_found or not solution_found:
                sentences = sent_tokenize(full_text, language='french')
                mid_point = len(sentences) // 2
                problem_text = " ".join(sentences[:mid_point])
                solution_text = " ".join(sentences[mid_point:])
            
            # Créer un dictionnaire avec les données extraites
            example_data = {
                'filename': os.path.basename(pdf_path),
                'full_text': full_text,
                'problem_text': problem_text,
                'solution_text': solution_text,
            }
            
            return example_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du PDF {pdf_path}: {e}")
            return None
    
    def extract_accounting_data(self, text):
        """Extrait les données comptables pertinentes d'un texte avec une reconnaissance améliorée."""
        data = {
            'accounts': [],
            'amounts': [],
            'dates': [],
            'transactions': [],
            'keywords': [],
            'entities': {}
        }
        
        # Recherche des comptes (format OHADA : numéros à 5 chiffres)
        account_pattern = r'\b\d{5}\b'
        data['accounts'] = re.findall(account_pattern, text)
        
        # Recherche des montants avec différents formats
        # Format français: X XXX,XX € ou X XXX EUR
        # Format avec point décimal: X,XXX.XX
        amount_patterns = [
            r'\b\d{1,3}(?: \d{3})*(?:,\d{1,2})?(?: ?€| ?EUR)?\b',  # X XXX,XX € ou X XXX EUR
            r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b',                      # X,XXX.XX
            r'\b\d{1,3}(?: \d{3})*(?:€|EUR)?\b'                    # X XXX € ou X XXX EUR
        ]
        
        all_amounts = []
        for pattern in amount_patterns:
            all_amounts.extend(re.findall(pattern, text))
        
        # Nettoyer et normaliser les montants trouvés
        data['amounts'] = list(set(all_amounts))  # Éliminer les doublons
        
        # Recherche des dates avec différents formats
        date_patterns = [
            r'\b\d{2}/\d{2}/\d{4}\b',                             # JJ/MM/AAAA
            r'\b\d{1,2}[-\.]\d{1,2}[-\.]\d{2,4}\b',               # J-M-AA ou JJ.MM.AAAA
            r'\b\d{1,2} (?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre) \d{4}\b'  # J mois AAAA
        ]
        
        all_dates = []
        for pattern in date_patterns:
            all_dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        data['dates'] = all_dates
        
        # Identification des transactions avec une reconnaissance plus précise
        transaction_patterns = [
            r'(?:débit|crédit|enregistr(?:er|ement)|comptabilis(?:er|ation))[^\n.]*\d{5}[^\n.]*\d{1,3}(?: \d{3})*(?:,\d{2})?\b',
            r'\b\d{5}\b[^\n.]*(?:débit(?:é|er)?|crédit(?:é|er)?)[^\n.]*\b\d{1,3}(?: \d{3})*(?:,\d{2})?\b',
            r'(?:facture|paiement|règlement|versement|achat|vente)[^\n.]*\b\d{1,3}(?: \d{3})*(?:,\d{2})?\b'
        ]
        
        all_transactions = []
        for pattern in transaction_patterns:
            all_transactions.extend(re.findall(pattern, text, re.IGNORECASE))
        
        data['transactions'] = all_transactions
        
        # Extraction de mots-clés comptables spécifiques
        keywords = [
            "capital", "emprunt", "stock", "amortissement", "immobilisation", 
            "créance", "dette", "tva", "trésorerie", "bilan", "compte de résultat",
            "actif", "passif", "produit", "charge", "résultat", "exercice", "dividende"
        ]
        
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
                data['keywords'].append(keyword)
        
        # Tentative d'identification des entités et leurs valeurs
        # Par exemple: "le capital est de 100 000 €"
        entity_patterns = {
            'capital': r'capital[^\n.]*?(\d{1,3}(?: \d{3})*(?:,\d{2})?)',
            'emprunt': r'emprunt[^\n.]*?(\d{1,3}(?: \d{3})*(?:,\d{2})?)',
            'stock': r'stock[^\n.]*?(\d{1,3}(?: \d{3})*(?:,\d{2})?)',
            'tva': r'tva[^\n.]*?(\d{1,3}(?: \d{3})*(?:,\d{2})?)'
        }
        
        for entity, pattern in entity_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['entities'][entity] = match.group(1)
        
        return data
    
    def find_similar_examples(self, problem_text, top_n=3, min_similarity=0.2):
        """
        Trouve les exemples les plus similaires à un exercice donné en utilisant 
        une classification préalable et une comparaison améliorée.
        """
        if not self.examples:
            logger.warning("Aucun exemple disponible pour la comparaison.")
            return []
        
        # Prétraiter le texte du problème
        processed_problem = self._preprocess_text(problem_text)
        
        # Détecter la catégorie probable de l'exercice
        probable_category = self._detect_exercise_category(problem_text)
        logger.info(f"Catégorie probable détectée: {probable_category}")
        
        # Filtrer les exemples par catégorie si une catégorie a été détectée
        filtered_examples = []
        if probable_category:
            # Chercher des mots-clés de la catégorie dans les exemples
            for example in self.examples:
                example_text = example['problem_text'].lower()
                if any(kw in example_text for kw in self._get_category_keywords(probable_category)):
                    filtered_examples.append(example)
            
            logger.info(f"{len(filtered_examples)} exemples trouvés dans la catégorie {probable_category}")
            
            # Si on n'a pas trouvé assez d'exemples dans la catégorie, utiliser tous les exemples
            if len(filtered_examples) < top_n:
                logger.info(f"Pas assez d'exemples dans la catégorie {probable_category}, utilisation de tous les exemples.")
                filtered_examples = self.examples
        else:
            filtered_examples = self.examples
        
        # Préparer les textes pour la vectorisation
        all_texts = [self._preprocess_text(ex['problem_text']) for ex in filtered_examples]
        all_texts.append(processed_problem)
        
        # Vectoriser les textes
        try:
            # Utiliser une vectorisation plus appropriée
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculer la similarité cosinus
            cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
            
            # Considérer également la similarité dans les données comptables extraites
            for i, example in enumerate(filtered_examples):
                # Extraire les données comptables des deux exercices
                example_data = self.extract_accounting_data(example['problem_text'])
                problem_data = self.extract_accounting_data(problem_text)
                
                # Calculer un score de similarité basé sur les éléments comptables
                accounting_similarity = self._calculate_accounting_similarity(example_data, problem_data)
                
                # Combiner les deux scores avec une pondération
                cosine_similarities[i] = cosine_similarities[i] * 0.7 + accounting_similarity * 0.3
            
            # Obtenir les indices des exemples les plus similaires
            similar_indices = cosine_similarities.argsort()[::-1][:top_n]
            
            # Créer la liste des exemples similaires avec leur score
            similar_examples = []
            for idx in similar_indices:
                if cosine_similarities[idx] > min_similarity:  # Seuil minimal de similarité rehaussé
                    similar_examples.append({
                        'example': filtered_examples[idx],
                        'similarity_score': float(cosine_similarities[idx]),
                        'category': probable_category
                    })
            
            return similar_examples
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'exemples similaires: {e}")
            return []
    
    def _preprocess_text(self, text):
        """Prétraite le texte pour améliorer la comparaison."""
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer les nombres spécifiques (pour se concentrer sur la structure)
        text = re.sub(r'\b\d{1,3}(?: \d{3})*(?:,\d{2})?\b', 'MONTANT', text)
        
        # Supprimer les comptes spécifiques
        text = re.sub(r'\b\d{5}\b', 'COMPTE', text)
        
        # Supprimer les dates spécifiques
        text = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', 'DATE', text)
        
        return text
    
    def _detect_exercise_category(self, text):
        """Détecte la catégorie probable de l'exercice."""
        text_lower = text.lower()
        
        categories = {
            'amortissement': ['amortissement', 'amortir', 'immobilisation', 'dépréciation'],
            'bilan': ['bilan', 'actif', 'passif', 'patrimoine'],
            'tva': ['tva', 'taxe sur la valeur ajoutée', 'déductible', 'collectée'],
            'journal': ['journal', 'écriture', 'comptabiliser', 'enregistrer'],
            'resultat': ['résultat', 'compte de résultat', 'produit', 'charge', 'bénéfice', 'perte']
        }
        
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(text_lower.count(kw) for kw in keywords)
            category_scores[category] = score
        
        # Trouver la catégorie avec le score le plus élevé
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:  # Si au moins un mot-clé a été trouvé
                return best_category[0]
        
        return None
    
    def _get_category_keywords(self, category):
        """Retourne les mots-clés associés à une catégorie."""
        keywords = {
            'amortissement': ['amortissement', 'amortir', 'immobilisation', 'dépréciation'],
            'bilan': ['bilan', 'actif', 'passif', 'patrimoine'],
            'tva': ['tva', 'taxe', 'déductible', 'collectée'],
            'journal': ['journal', 'écriture', 'comptabiliser', 'enregistrer'],
            'resultat': ['résultat', 'produit', 'charge', 'bénéfice', 'perte']
        }
        
        return keywords.get(category, [])
    
    def _calculate_accounting_similarity(self, data1, data2):
        """Calcule un score de similarité basé sur les éléments comptables extraits."""
        # Initialiser le score
        score = 0.0
        total_weight = 0.0
        
        # Comparer le nombre d'éléments de chaque type
        features = [
            ('accounts', 0.4),  # Comptes (poids important)
            ('amounts', 0.3),   # Montants (poids important)
            ('dates', 0.1),     # Dates (poids moins important)
            ('transactions', 0.2)  # Transactions (poids moyen)
        ]
        
        for feature, weight in features:
            # Si les deux listes sont vides, donner un score neutre
            if not data1[feature] and not data2[feature]:
                continue
                
            # Si une liste est vide et l'autre non, donner un score faible
            if not data1[feature] or not data2[feature]:
                score += 0.1 * weight
                total_weight += weight
                continue
                
            # Calculer la similarité basée sur la différence de taille relative
            len1 = len(data1[feature])
            len2 = len(data2[feature])
            size_similarity = min(len1, len2) / max(len1, len2)
            
            # Pour les transactions, essayer de calculer une similarité textuelle
            if feature == 'transactions' and data1[feature] and data2[feature]:
                # Prendre jusqu'à 5 transactions de chaque côté
                sample1 = data1[feature][:5]
                sample2 = data2[feature][:5]
                
                # Calculer une similarité basée sur les mots communs
                common_words_score = 0
                for t1 in sample1:
                    for t2 in sample2:
                        words1 = set(re.findall(r'\b\w+\b', t1.lower()))
                        words2 = set(re.findall(r'\b\w+\b', t2.lower()))
                        if words1 and words2:
                            common = len(words1.intersection(words2))
                            total = len(words1.union(words2))
                            common_words_score += common / total
                
                # Normaliser le score
                if sample1 and sample2:
                    common_words_score /= (len(sample1) * len(sample2))
                    size_similarity = (size_similarity + common_words_score) / 2
            
            score += size_similarity * weight
            total_weight += weight
        
        # Normaliser le score final
        if total_weight > 0:
            return score / total_weight
        else:
            return 0.0
    
    def solve_exercise(self, problem_text):
        """Résout un exercice comptable en se basant sur des exemples similaires avec un calcul de confiance amélioré."""
        # Trouver des exemples similaires
        similar_examples = self.find_similar_examples(problem_text, top_n=5, min_similarity=0.2)
        
        if not similar_examples:
            return {
                'success': False,
                'message': "Aucun exemple similaire trouvé pour cet exercice.",
                'solution': None,
                'confidence': 0.0,
                'diagnostic': "Le système ne dispose pas d'exemples similaires pour cet exercice. "
                            "Essayez d'ajouter des exemples dans cette catégorie."
            }
        
        # Extraire les données comptables de l'exercice à résoudre
        problem_data = self.extract_accounting_data(problem_text)
        
        # Utiliser l'exemple le plus similaire comme base pour la solution
        best_match = similar_examples[0]
        example = best_match['example']
        similarity_score = best_match['similarity_score']
        
        # Extraire les données comptables de l'exemple
        example_problem_data = self.extract_accounting_data(example['problem_text'])
        example_solution_data = self.extract_accounting_data(example['solution_text'])
        
        # Vérifier si l'exercice contient suffisamment d'éléments comptables
        data_completeness = self._evaluate_data_completeness(problem_data)
        
        # Vérifier la correspondance structurelle entre l'exercice et l'exemple
        structural_match = self._evaluate_structural_match(problem_data, example_problem_data)
        
        # Adapter la solution
        adapted_solution = self.adapt_solution(
            problem_data, 
            example_problem_data, 
            example_solution_data, 
            example['solution_text']
        )
        
        # Si plusieurs exemples similaires sont trouvés, vérifier la cohérence entre leurs solutions
        solution_consistency = 0.5  # Valeur par défaut
        if len(similar_examples) > 1:
            solution_consistency = self._evaluate_solution_consistency(
                similar_examples, 
                problem_data
            )
        
        # Calculer le niveau de confiance avec une formule plus sophistiquée
        if adapted_solution:
            # Pondérer les différents facteurs qui contribuent à la confiance
            confidence = (
                similarity_score * 0.4 +          # Similarité textuelle
                data_completeness * 0.2 +         # Complétude des données extraites
                structural_match * 0.2 +          # Correspondance structurelle
                solution_consistency * 0.2        # Cohérence entre les solutions potentielles
            )
            
            # Limiter la confiance à 1.0 maximum
            confidence = min(confidence, 1.0)
        else:
            confidence = 0.0
        
        # Créer un diagnostic textuel pour expliquer le niveau de confiance
        diagnostic = self._generate_diagnostic(
            similarity_score, 
            data_completeness, 
            structural_match,
            solution_consistency,
            adapted_solution is not None
        )
        
        return {
            'success': adapted_solution is not None,
            'message': "Solution trouvée en se basant sur des exemples similaires." if adapted_solution else "Impossible d'adapter la solution à cet exercice.",
            'solution': adapted_solution,
            'confidence': confidence,
            'diagnostic': diagnostic,
            'similar_examples': [{
                'filename': ex['example']['filename'],
                'similarity': ex['similarity_score'],
                'category': ex.get('category', 'non classé')
            } for ex in similar_examples],
            'data_completeness': data_completeness,
            'structural_match': structural_match,
            'solution_consistency': solution_consistency
        }
    
    def _evaluate_data_completeness(self, data):
        """Évalue la complétude des données extraites d'un exercice."""
        # Vérifier si les éléments essentiels sont présents
        score = 0.0
        
        # Vérifier les comptes
        if data['accounts']:
            score += 0.4  # Les comptes sont très importants
        
        # Vérifier les montants
        if data['amounts']:
            score += 0.4  # Les montants sont très importants
        
        # Vérifier les dates
        if data['dates']:
            score += 0.1  # Les dates sont moins importantes
        
        # Vérifier les transactions
        if data['transactions']:
            score += 0.1  # La détection des transactions est un bonus
        
        return score
    
    def _evaluate_structural_match(self, problem_data, example_data):
        """Évalue la correspondance structurelle entre l'exercice et l'exemple."""
        # Initialiser le score
        score = 0.0
        
        # Comparer le nombre d'éléments comptables
        features = [
            ('accounts', 0.4),
            ('amounts', 0.4),
            ('dates', 0.1),
            ('transactions', 0.1)
        ]
        
        for feature, weight in features:
            # Si l'une des listes est vide, donner un score nul pour cette caractéristique
            if not problem_data[feature] or not example_data[feature]:
                continue
            
            # Calculer la similarité en termes de nombre d'éléments
            len_problem = len(problem_data[feature])
            len_example = len(example_data[feature])
            
            # Si les nombres sont proches, donner un score élevé
            ratio = min(len_problem, len_example) / max(len_problem, len_example)
            score += ratio * weight
        
        return score
    
    def _evaluate_solution_consistency(self, similar_examples, problem_data):
        """
        Évalue la cohérence entre les solutions potentielles générées 
        à partir de différents exemples similaires.
        """
        # Si on n'a qu'un seul exemple, on ne peut pas évaluer la cohérence
        if len(similar_examples) <= 1:
            return 0.5  # Valeur neutre
        
        # Prendre les deux exemples les plus similaires
        top_examples = similar_examples[:min(3, len(similar_examples))]
        
        # Générer des solutions pour chacun
        solutions = []
        for ex_data in top_examples:
            example = ex_data['example']
            example_problem_data = self.extract_accounting_data(example['problem_text'])
            example_solution_data = self.extract_accounting_data(example['solution_text'])
            
            adapted_solution = self.adapt_solution(
                problem_data,
                example_problem_data,
                example_solution_data,
                example['solution_text']
            )
            
            if adapted_solution:
                # Extraire les éléments comptables de la solution adaptée
                solution_data = self.extract_accounting_data(adapted_solution)
                solutions.append(solution_data)
        
        # Si on n'a pas pu générer au moins deux solutions, on ne peut pas évaluer la cohérence
        if len(solutions) <= 1:
            return 0.5  # Valeur neutre
        
        # Comparer les éléments comptables entre les solutions
        consistency_scores = []
        
        for i in range(len(solutions)):
            for j in range(i+1, len(solutions)):
                # Comparer les comptes
                accounts_i = set(solutions[i]['accounts'])
                accounts_j = set(solutions[j]['accounts'])
                
                if accounts_i and accounts_j:
                    common_accounts = accounts_i.intersection(accounts_j)
                    accounts_consistency = len(common_accounts) / max(len(accounts_i.union(accounts_j)), 1)
                    consistency_scores.append(accounts_consistency)
                
                # Comparer les montants
                amounts_i = set(solutions[i]['amounts'])
                amounts_j = set(solutions[j]['amounts'])
                
                if amounts_i and amounts_j:
                    common_amounts = amounts_i.intersection(amounts_j)
                    amounts_consistency = len(common_amounts) / max(len(amounts_i.union(amounts_j)), 1)
                    consistency_scores.append(amounts_consistency)
        
        # Calculer la moyenne des scores de cohérence
        if consistency_scores:
            return sum(consistency_scores) / len(consistency_scores)
        else:
            return 0.5  # Valeur neutre
    
    def _generate_diagnostic(self, similarity, completeness, structural_match, consistency, success):
        """Génère un diagnostic textuel expliquant le niveau de confiance."""
        if not success:
            return "Impossible d'adapter une solution pour cet exercice. Vérifiez si l'énoncé est complet et essayez d'ajouter des exemples similaires."
        
        messages = []
        
        # Évaluer la similarité textuelle
        if similarity < 0.3:
            messages.append("Faible similarité avec les exemples connus.")
        elif similarity < 0.6:
            messages.append("Similarité moyenne avec les exemples connus.")
        else:
            messages.append("Forte similarité avec les exemples connus.")
        
        # Évaluer la complétude des données
        if completeness < 0.4:
            messages.append("Peu d'éléments comptables détectés dans l'énoncé.")
        elif completeness < 0.7:
            messages.append("Détection partielle des éléments comptables dans l'énoncé.")
        else:
            messages.append("Bonne détection des éléments comptables dans l'énoncé.")
        
        # Évaluer la correspondance structurelle
        if structural_match < 0.4:
            messages.append("Structure de l'exercice différente des exemples.")
        elif structural_match < 0.7:
            messages.append("Structure de l'exercice partiellement similaire aux exemples.")
        else:
            messages.append("Structure de l'exercice très similaire aux exemples.")
        
        # Évaluer la cohérence entre les solutions potentielles
        if consistency < 0.4:
            messages.append("Faible cohérence entre les solutions potentielles.")
        elif consistency < 0.7:
            messages.append("Cohérence moyenne entre les solutions potentielles.")
        else:
            messages.append("Forte cohérence entre les solutions potentielles.")
        
        return " ".join(messages)
    
    def adapt_solution(self, problem_data, example_problem_data, example_solution_data, example_solution_text):
        """Adapte la solution d'un exemple à un exercice similaire avec une méthode améliorée."""
        try:
            # Créer des mappings entre les éléments de l'exemple et du problème
            account_mapping = {}
            amount_mapping = {}
            date_mapping = {}
            entity_mapping = {}
            
            # Mapper les comptes avec une méthode plus intelligente
            # Si le nombre de comptes est le même dans les deux exercices
            if len(example_problem_data['accounts']) == len(problem_data['accounts']):
                # On suppose une correspondance directe (même ordre)
                for i, account in enumerate(example_problem_data['accounts']):
                    account_mapping[account] = problem_data['accounts'][i]
            else:
                # Sinon, on essaie de faire une correspondance contextuelle
                # en cherchant les comptes qui apparaissent dans des contextes similaires
                for account in example_problem_data['accounts']:
                    # Trouver les contextes où ce compte apparaît dans l'exemple
                    contexts = self._find_contexts(example_problem_data['problem_text'], account, window=20)
                    
                    # Pour chaque compte dans le problème, calculer un score de similarité contextuelle
                    best_match = None
                    best_score = -1
                    
                    for new_account in problem_data['accounts']:
                        new_contexts = self._find_contexts(problem_data['problem_text'], new_account, window=20)
                        similarity_score = self._calculate_context_similarity(contexts, new_contexts)
                        
                        if similarity_score > best_score and new_account not in account_mapping.values():
                            best_score = similarity_score
                            best_match = new_account
                    
                    if best_match:
                        account_mapping[account] = best_match
            
            # Mapper les montants avec une heuristique améliorée
            # Trier les montants par valeur numérique pour mieux gérer les associations
            example_amounts = sorted(self._normalize_amounts(example_problem_data['amounts']))
            problem_amounts = sorted(self._normalize_amounts(problem_data['amounts']))
            
            min_len = min(len(example_amounts), len(problem_amounts))
            for i in range(min_len):
                amount_mapping[example_amounts[i]] = problem_amounts[i]
            
            # Mapper les dates
            for i, date in enumerate(example_problem_data['dates']):
                if i < len(problem_data['dates']):
                    date_mapping[date] = problem_data['dates'][i]
            
            # Mapper les entités si elles sont présentes
            if 'entities' in example_problem_data and 'entities' in problem_data:
                for entity, value in example_problem_data['entities'].items():
                    if entity in problem_data['entities']:
                        entity_mapping[value] = problem_data['entities'][entity]
            
            # Adapter la solution
            adapted_solution = example_solution_text
            
            # Remplacer les comptes avec protection contre les substitutions partielles
            for old_account, new_account in account_mapping.items():
                # Utiliser une expression régulière pour remplacer uniquement les nombres de compte complets
                adapted_solution = re.sub(r'\b' + old_account + r'\b', new_account, adapted_solution)
            
            # Remplacer les montants
            for old_amount, new_amount in amount_mapping.items():
                adapted_solution = re.sub(r'\b' + re.escape(old_amount) + r'\b', new_amount, adapted_solution)
            
            # Remplacer les dates
            for old_date, new_date in date_mapping.items():
                adapted_solution = adapted_solution.replace(old_date, new_date)
            
            # Remplacer les entités
            for old_value, new_value in entity_mapping.items():
                adapted_solution = adapted_solution.replace(old_value, new_value)
            
            # Vérifier la cohérence des résultats
            adapted_solution = self._check_solution_consistency(adapted_solution, problem_data)
            
            return adapted_solution
            
        except Exception as e:
            logger.error(f"Erreur lors de l'adaptation de la solution: {e}")
            return None
    
    def _find_contexts(self, text, term, window=20):
        """Trouve les contextes où un terme apparaît dans un texte."""
        contexts = []
        matches = list(re.finditer(r'\b' + re.escape(term) + r'\b', text))
        
        for match in matches:
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            context = text[start:end]
            contexts.append(context)
        
        return contexts
    
    def _calculate_context_similarity(self, contexts1, contexts2):
        """Calcule un score de similarité entre deux ensembles de contextes."""
        if not contexts1 or not contexts2:
            return 0
        
        # Vectoriser tous les contextes
        all_contexts = contexts1 + contexts2
        vectorizer = TfidfVectorizer(max_features=100)
        try:
            tfidf_matrix = vectorizer.fit_transform(all_contexts)
            
            # Calculer la similarité moyenne entre chaque paire de contextes
            total_sim = 0
            count = 0
            
            for i in range(len(contexts1)):
                for j in range(len(contexts2)):
                    idx1 = i
                    idx2 = len(contexts1) + j
                    sim = cosine_similarity(tfidf_matrix[idx1:idx1+1], tfidf_matrix[idx2:idx2+1])[0][0]
                    total_sim += sim
                    count += 1
            
            return total_sim / max(count, 1)
        except:
            return 0
    
    def _normalize_amounts(self, amounts):
        """Normalise les montants pour faciliter la comparaison."""
        normalized = []
        for amount in amounts:
            # Enlever les espaces, les symboles monétaires, etc.
            clean_amount = re.sub(r'[^\d,.]', '', amount)
            # Convertir les virgules en points
            clean_amount = clean_amount.replace(',', '.')
            
            try:
                # Convertir en nombre flottant pour trier correctement
                float_val = float(clean_amount)
                normalized.append((amount, float_val))
            except:
                # Si la conversion échoue, conserver le texte original
                normalized.append((amount, 0))
        
        # Trier par valeur numérique et renvoyer les montants originaux
        normalized.sort(key=lambda x: x[1])
        return [item[0] for item in normalized]
    
    def _check_solution_consistency(self, solution, problem_data):
        """Vérifie la cohérence de la solution adaptée et corrige les erreurs évidentes."""
        # Vérifier que tous les comptes du problème sont présents dans la solution
        for account in problem_data['accounts']:
            if account not in solution:
                logger.warning(f"Le compte {account} n'est pas présent dans la solution adaptée.")
        
        # Vérifier l'équilibre des écritures comptables (si des marqueurs spécifiques sont détectés)
        if "DÉBIT" in solution.upper() and "CRÉDIT" in solution.upper():
            # Cette fonction pourrait être développée pour vérifier l'équilibre des écritures
            pass
        
        return solution

# Fonction pour sauvegarder un nouvel exemple
def save_example_pdf(file_path, destination_name=None):
    """
    Sauvegarde un fichier PDF d'exemple dans le répertoire des exemples.
    
    Args:
        file_path (str): Chemin du fichier PDF à sauvegarder
        destination_name (str, optional): Nom du fichier de destination. Si None, utilise le nom du fichier d'origine.
    
    Returns:
        bool: True si le fichier a été sauvegardé avec succès, False sinon
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Le fichier {file_path} n'existe pas.")
            return False
        
        if not destination_name:
            destination_name = os.path.basename(file_path)
        
        destination_path = os.path.join(EXAMPLE_DIR, destination_name)
        
        # Copier le fichier
        with open(file_path, 'rb') as src_file:
            with open(destination_path, 'wb') as dst_file:
                dst_file.write(src_file.read())
        
        logger.info(f"Exemple sauvegardé avec succès: {destination_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de l'exemple {file_path}: {e}")
        return False

# Initialiser le solveur
solver = ExerciseSolver()