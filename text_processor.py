
# Module temporaire pour éviter les erreurs d'importation NLTK
def process_text(text, summarize=True, split_paragraphs=True, analyze=True, compression_rate=0.3):
    return {
        'original': text,
        'summary': "La fonctionnalité de résumé n'est pas disponible pour le moment.",
        'paragraphs': text.split('\n\n'),
        'analysis': {
            'complexity': 'Non disponible',
            'sentiment': 'Non disponible',
            'keywords': ['Non disponible']
        }
    }
