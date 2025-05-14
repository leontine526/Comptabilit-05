"""
Module pour le traitement et l'analyse de textes.
Fournit des fonctionnalités de résumé et de restructuration de textes.
"""

import re
import logging
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

# Initialisation des ressources NLTK
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"Impossible de télécharger les ressources NLTK: {e}")

def preprocess_text(text):
    """
    Prétraite le texte pour l'analyse (suppression ponctuation excessive, normalisation, etc.)
    """
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text)
    
    # Normaliser les sauts de ligne
    text = re.sub(r'\n+', '\n', text)
    
    # Supprimer les caractères spéciaux en excès
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\'\"\-]', '', text)
    
    return text.strip()

def split_into_paragraphs(text, max_sentences_per_paragraph=5):
    """
    Divise un texte en paragraphes plus courts et structurés.
    """
    # Prétraiter le texte
    text = preprocess_text(text)
    
    # Tokenizer les phrases
    sentences = sent_tokenize(text, language='french')
    
    paragraphs = []
    current_paragraph = []
    
    # Regrouper les phrases en paragraphes
    for sentence in sentences:
        current_paragraph.append(sentence)
        
        # Si le paragraphe atteint la taille maximale ou contient une phrase qui semble conclure un paragraphe
        if (len(current_paragraph) >= max_sentences_per_paragraph or 
            any(marker in sentence.lower() for marker in ['enfin', 'finalement', 'en conclusion', 'ainsi', 'par conséquent'])):
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    
    # Ajouter le dernier paragraphe s'il reste des phrases
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    return paragraphs

def summarize_text(text, compression_rate=0.3):
    """
    Résume un texte français en conservant environ 30% du texte original.
    """
    # Prétraiter le texte
    text = preprocess_text(text)
    
    # Tokenizer les phrases
    sentences = sent_tokenize(text, language='french')
    
    # Si le texte est trop court, le retourner tel quel
    if len(sentences) <= 3:
        return text
    
    try:
        # Calculer la matrice TF-IDF
        vectorizer = TfidfVectorizer(stop_words=stopwords.words('french'))
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        # Calculer les scores pour chaque phrase
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            # Score basé sur TF-IDF
            sentence_scores[i] = sum(tfidf_matrix[i].toarray()[0])
            
            # Bonus pour les phrases d'introduction et de conclusion
            if i == 0 or i == len(sentences) - 1:
                sentence_scores[i] *= 1.25
            
            # Bonus pour les phrases contenant des marqueurs importants
            important_markers = ['important', 'essentiel', 'clé', 'principal', 'crucial', 'significatif']
            if any(marker in sentence.lower() for marker in important_markers):
                sentence_scores[i] *= 1.2
        
        # Sélectionner les phrases avec les scores les plus élevés
        num_sentences_in_summary = max(1, int(len(sentences) * compression_rate))
        top_sentences = sorted(sentence_scores.items(), key=lambda item: item[1], reverse=True)[:num_sentences_in_summary]
        top_sentences = sorted(top_sentences, key=lambda item: item[0])  # Trier par position originale
        
        # Construire le résumé
        summary = ' '.join([sentences[i] for i, _ in top_sentences])
        return summary
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du résumé: {e}")
        # Fallback: retourner les premières phrases
        fallback_size = max(1, int(len(sentences) * compression_rate))
        return ' '.join(sentences[:fallback_size])

def analyze_text_complexity(text):
    """
    Analyse la complexité d'un texte (longueur, richesse du vocabulaire, etc.)
    """
    # Prétraiter le texte
    text = preprocess_text(text)
    
    # Tokenizer
    sentences = sent_tokenize(text, language='french')
    words = word_tokenize(text, language='french')
    
    # Filtrer les mots vides
    french_stopwords = set(stopwords.words('french'))
    words_no_stopwords = [word.lower() for word in words if word.isalpha() and word.lower() not in french_stopwords]
    
    # Calculer les statistiques
    sentence_count = len(sentences)
    word_count = len(words)
    average_sentence_length = word_count / max(1, sentence_count)
    unique_words = len(set([word.lower() for word in words if word.isalpha()]))
    lexical_diversity = unique_words / max(1, len([word for word in words if word.isalpha()]))
    
    return {
        'sentence_count': sentence_count,
        'word_count': word_count,
        'average_sentence_length': round(average_sentence_length, 2),
        'unique_words': unique_words,
        'lexical_diversity': round(lexical_diversity, 2)
    }

def process_text(text, summarize=True, split_paragraphs=True, analyze=True, compression_rate=0.3):
    """
    Traite un texte avec plusieurs options (résumé, division en paragraphes, analyse)
    
    Args:
        text (str): Le texte à traiter
        summarize (bool): Indique si le texte doit être résumé
        split_paragraphs (bool): Indique si le texte doit être divisé en paragraphes
        analyze (bool): Indique si la complexité du texte doit être analysée
        compression_rate (float): Taux de compression pour le résumé (0.1 à 1.0)
    
    Returns:
        dict: Résultat du traitement avec les clés correspondant aux options activées
    """
    result = {
        'original_text': text,
        'processed_text': preprocess_text(text)
    }
    
    if summarize:
        result['summary'] = summarize_text(text, compression_rate=compression_rate)
    
    if split_paragraphs:
        result['paragraphs'] = split_into_paragraphs(text)
    
    if analyze:
        result['complexity'] = analyze_text_complexity(text)
    
    return result