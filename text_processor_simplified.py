
# Version simplifiée du processeur de texte qui ne dépend pas de NLTK
import re

def process_text(text, summarize=True, split_paragraphs=True, analyze=True, compression_rate=0.3):
    """
    Traite un texte en le résumant et le structurant.
    Version simplifiée qui ne dépend pas de bibliothèques externes.
    """
    result = {
        'original': text,
        'summary': '',
        'paragraphs': [],
        'analysis': {
            'complexity': 'Moyenne',
            'sentiment': 'Neutre',
            'keywords': []
        }
    }
    
    # Découpage en paragraphes
    if split_paragraphs:
        result['paragraphs'] = [p for p in text.split('\n\n') if p.strip()]
        if not result['paragraphs']:
            result['paragraphs'] = [p for p in text.split('\n') if p.strip()]
    
    # Création d'un résumé simple (premières phrases)
    if summarize:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        num_sentences = max(1, int(len(sentences) * compression_rate))
        result['summary'] = ' '.join(sentences[:num_sentences])
    
    # Analyse simplifiée
    if analyze:
        # Calcul de la complexité basée sur la longueur des phrases
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        if avg_sentence_length > 20:
            result['analysis']['complexity'] = 'Élevée'
        elif avg_sentence_length < 10:
            result['analysis']['complexity'] = 'Basse'
        
        # Extraction de quelques mots-clés (mots les plus fréquents)
        words = re.findall(r'\b\w{3,}\b', text.lower())
        word_count = {}
        for word in words:
            if word not in ['les', 'des', 'une', 'est', 'que', 'qui', 'pour', 'dans', 'avec', 'par']:
                word_count[word] = word_count.get(word, 0) + 1
        
        # Trier par fréquence et prendre les 5 premiers
        result['analysis']['keywords'] = [w for w, c in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    return result
