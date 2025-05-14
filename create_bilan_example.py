"""
Script pour créer un exemple d'exercice sur le bilan comptable.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_example_pdf(filename, title, problem_text, solution_text):
    """
    Crée un fichier PDF d'exemple avec un énoncé et sa solution.
    
    Args:
        filename (str): Nom du fichier à créer
        title (str): Titre de l'exercice
        problem_text (str): Texte de l'énoncé
        solution_text (str): Texte de la solution
    """
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Définir les styles personnalisés
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    
    # Ajouter le style de section
    styles.add(section_style)
    
    # Conteneur pour les éléments du document
    elements = []
    
    # Titre du document
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Section de l'énoncé
    elements.append(Paragraph("ÉNONCÉ", styles['SectionTitle']))
    elements.append(Spacer(1, 8))
    
    # Texte de l'énoncé avec paragraphes
    for paragraph in problem_text.split('\n\n'):
        elements.append(Paragraph(paragraph, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(Spacer(1, 12))
    
    # Saut de page avant la solution
    elements.append(PageBreak())
    
    # Section de la solution
    elements.append(Paragraph("SOLUTION", styles['SectionTitle']))
    elements.append(Spacer(1, 8))
    
    # Texte de la solution avec paragraphes
    for paragraph in solution_text.split('\n\n'):
        elements.append(Paragraph(paragraph, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    # Construire le document
    doc.build(elements)

if __name__ == "__main__":
    # Créer le répertoire des exemples s'il n'existe pas
    examples_dir = os.path.join(os.getcwd(), 'examples')
    os.makedirs(examples_dir, exist_ok=True)
    
    # Exemple : Bilan de départ simplifié
    example1_problem = """Sujet 1 : Bilan de départ simplifié

La Compagnie XYZ, établie le 1er janvier, présente les éléments suivants au début de son activité au 1er janvier 2025:

- capital social : 250 000 €
- emprunt bancaire : 150 000 €
- matériel de bureau : 60 000 €
- immobilisations de bureau et matériel informatique : 90 000 €
- stocks de marchandises : 140 000 €
- créances clients : 25 000 €
- disponibilités (banque) : 85 000 €

Question 1 : Déterminer le montant du capital.
Question 2 : Établir le bilan de départ simplifié de l'entreprise."""

    example1_solution = """SOLUTION - BILAN DE DÉPART SIMPLIFIÉ

Question 1 : Détermination du montant du capital

Le capital est déjà donné dans l'énoncé : 250 000 €

Question 2 : Bilan de départ simplifié

BILAN DE DÉPART AU 01/01/2025

ACTIF                                          PASSIF
-------------------------------------------------------------------
ACTIF IMMOBILISÉ                              CAPITAUX PROPRES
Matériel de bureau            60 000 €         Capital social          250 000 €
Immobilisations bureau        
et matériel informatique      90 000 €
                                              
ACTIF CIRCULANT                               DETTES
Stocks de marchandises       140 000 €         Emprunt bancaire        150 000 €
Créances clients              25 000 €         
Disponibilités                85 000 €
                             
TOTAL ACTIF                  400 000 €         TOTAL PASSIF           400 000 €

Vérification : Total Actif = Total Passif, le bilan est équilibré."""

    # Exemple : Bilans successifs et détermination du résultat
    example2_problem = """Sujet 2 : Bilans successifs et détermination du résultat

Au 1er janvier, la situation des biens de l'entreprise Formalis se présente comme suit:

- immobilisations corporelles et matériel informatique : 90 000 €
- mobilier : 30 000 €
- stocks de marchandises : 45 000 €
- créances clients : 32 000 €
- disponibilités (banque) : 75 000 €
- dettes fournisseurs : 92 000 €

Au 31 décembre de la même année, la situation est la suivante:

- immobilisations corporelles et matériel informatique : 85 000 €
- mobilier : 28 000 €
- stocks de marchandises : 52 000 €
- créances clients : 38 000 €
- disponibilités (banque) : 105 000 €
- dettes fournisseurs : 82 000 €

Question 1 : Déterminer le montant du capital au 1er janvier.
Question 2 : Établir le bilan d'ouverture au 1er janvier.
Question 3 : Déterminer le montant du bénéfice ou de la perte de l'exercice.
Question 4 : Établir le bilan de clôture au 31 décembre."""

    example2_solution = """SOLUTION - BILANS SUCCESSIFS ET DÉTERMINATION DU RÉSULTAT

Question 1 : Détermination du montant du capital au 1er janvier

Total de l'actif = 90 000 + 30 000 + 45 000 + 32 000 + 75 000 = 272 000 €
Total du passif connu = 92 000 € (dettes fournisseurs)
Capital = Total actif - Dettes = 272 000 - 92 000 = 180 000 €

Question 2 : Bilan d'ouverture au 1er janvier

BILAN D'OUVERTURE AU 01/01/2025

ACTIF                                          PASSIF
-------------------------------------------------------------------
ACTIF IMMOBILISÉ                              CAPITAUX PROPRES
Immobilisations corporelles                     Capital social          180 000 €
et matériel informatique     90 000 €         
Mobilier                     30 000 €
                                              
ACTIF CIRCULANT                               DETTES
Stocks de marchandises       45 000 €         Dettes fournisseurs       92 000 €
Créances clients             32 000 €         
Disponibilités               75 000 €
                             
TOTAL ACTIF                 272 000 €         TOTAL PASSIF            272 000 €

Question 3 : Détermination du bénéfice ou de la perte de l'exercice

Total de l'actif au 31/12 = 85 000 + 28 000 + 52 000 + 38 000 + 105 000 = 308 000 €
Total du passif connu au 31/12 = 82 000 € (dettes fournisseurs) + 180 000 € (capital) = 262 000 €
Résultat = 308 000 - 262 000 = 46 000 € (bénéfice)

Question 4 : Bilan de clôture au 31 décembre

BILAN DE CLÔTURE AU 31/12/2025

ACTIF                                          PASSIF
-------------------------------------------------------------------
ACTIF IMMOBILISÉ                              CAPITAUX PROPRES
Immobilisations corporelles                     Capital social          180 000 €
et matériel informatique     85 000 €          Résultat (bénéfice)      46 000 €
Mobilier                     28 000 €
                                              
ACTIF CIRCULANT                               DETTES
Stocks de marchandises       52 000 €         Dettes fournisseurs       82 000 €
Créances clients             38 000 €         
Disponibilités              105 000 €
                             
TOTAL ACTIF                 308 000 €         TOTAL PASSIF            308 000 €"""

    # Créer les PDF
    create_example_pdf(
        os.path.join(examples_dir, 'bilan_depart.pdf'),
        "Bilan de départ simplifié",
        example1_problem,
        example1_solution
    )
    
    create_example_pdf(
        os.path.join(examples_dir, 'bilans_successifs.pdf'),
        "Bilans successifs et détermination du résultat",
        example2_problem,
        example2_solution
    )
    
    print("Deux exemples d'exercices de bilan comptable ont été créés dans le répertoire 'examples'.")