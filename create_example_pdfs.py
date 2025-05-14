"""
Script pour créer des exemples de PDF d'exercices comptables.
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
    
    # Modifier les styles existants plutôt que d'ajouter
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
    
    # Ajouter le style de section uniquement (le style titre est modifié)
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
    
    # Créer les exemples d'exercices
    
    # Exemple 1: Exercice sur les écritures comptables de base
    example1_problem = """Une entreprise commerciale réalise les opérations suivantes au cours du mois de mars 2025:

1. Le 5 mars : Achat de marchandises à crédit pour 150 000 FCFA (HT) + TVA 19,25%.
2. Le 10 mars : Vente de marchandises au comptant pour 200 000 FCFA (HT) + TVA 19,25%.
3. Le 15 mars : Règlement du loyer mensuel par chèque pour 50 000 FCFA.
4. Le 20 mars : Versement des salaires du mois pour un montant total de 300 000 FCFA.
5. Le 25 mars : Encaissement d'un prêt bancaire de 1 000 000 FCFA.
6. Le 30 mars : Remboursement partiel du fournisseur pour 100 000 FCFA.

Enregistrez ces opérations dans le journal de l'entreprise."""

    example1_solution = """SOLUTION - ÉCRITURES AU JOURNAL

05/03/2025 - Achat de marchandises à crédit
601 Achats de marchandises                   150 000
4455 TVA récupérable                          28 875
401 Fournisseurs                                     178 875
(Achat de marchandises à crédit, facture du 05/03/2025)

10/03/2025 - Vente de marchandises au comptant
57 Caisse                                     238 500
701 Ventes de marchandises                            200 000
4456 TVA collectée                                     38 500
(Vente de marchandises au comptant)

15/03/2025 - Règlement du loyer
626 Loyers                                    50 000
5121 Banques                                          50 000
(Règlement du loyer du mois de mars)

20/03/2025 - Versement des salaires
661 Salaires                                  300 000
5121 Banques                                         300 000
(Règlement des salaires du mois de mars)

25/03/2025 - Encaissement d'un prêt bancaire
5121 Banques                                1 000 000
164 Emprunts auprès des établissements de crédit   1 000 000
(Encaissement du prêt bancaire)

30/03/2025 - Remboursement partiel du fournisseur
401 Fournisseurs                             100 000
5121 Banques                                         100 000
(Règlement partiel de la dette fournisseur)"""

    create_example_pdf(
        os.path.join(examples_dir, 'ecritures_base.pdf'),
        "Exercice sur les écritures comptables de base",
        example1_problem,
        example1_solution
    )
    
    # Exemple 2: Exercice sur les amortissements
    example2_problem = """La société ALPHA a acquis le 1er janvier 2023 une machine-outil pour 2 400 000 FCFA. Cette immobilisation est amortissable sur 5 ans selon le mode linéaire. La valeur résiduelle est estimée à zéro.

Sachant que l'exercice comptable coïncide avec l'année civile:

1. Calculez l'annuité d'amortissement annuelle.
2. Établissez le tableau d'amortissement sur toute la durée de vie de l'immobilisation.
3. Passez les écritures d'amortissement au 31/12/2023 et au 31/12/2024.
4. Calculez la valeur nette comptable au 31/12/2025."""

    example2_solution = """SOLUTION - AMORTISSEMENTS

1. Calcul de l'annuité d'amortissement annuelle:
   Taux d'amortissement linéaire = 100% / 5 ans = 20%
   Annuité d'amortissement = 2 400 000 × 20% = 480 000 FCFA

2. Tableau d'amortissement:

   | Année | Base amortissable | Taux | Amortissement | Amortissements cumulés | VNC fin d'exercice |
   |-------|-------------------|------|---------------|------------------------|-------------------|
   | 2023  | 2 400 000         | 20%  | 480 000       | 480 000                | 1 920 000        |
   | 2024  | 2 400 000         | 20%  | 480 000       | 960 000                | 1 440 000        |
   | 2025  | 2 400 000         | 20%  | 480 000       | 1 440 000              | 960 000          |
   | 2026  | 2 400 000         | 20%  | 480 000       | 1 920 000              | 480 000          |
   | 2027  | 2 400 000         | 20%  | 480 000       | 2 400 000              | 0                |

3. Écritures d'amortissement:

   31/12/2023
   6811 Dotations aux amortissements des immobilisations             480 000
   2815 Amortissements des installations techniques, matériel et outillage    480 000
   (Dotation aux amortissements exercice 2023)

   31/12/2024
   6811 Dotations aux amortissements des immobilisations             480 000
   2815 Amortissements des installations techniques, matériel et outillage    480 000
   (Dotation aux amortissements exercice 2024)

4. Valeur nette comptable au 31/12/2025:
   VNC = Valeur d'origine - Amortissements cumulés
   VNC = 2 400 000 - 1 440 000 = 960 000 FCFA"""

    create_example_pdf(
        os.path.join(examples_dir, 'amortissements.pdf'),
        "Exercice sur les amortissements",
        example2_problem,
        example2_solution
    )
    
    # Exemple 3: Exercice sur la TVA
    example3_problem = """La société BETA présente les opérations suivantes pour le mois d'avril 2025:

Opérations soumises à la TVA:
- Ventes de marchandises: 3 500 000 FCFA (HT)
- Prestations de services facturées: 750 000 FCFA (HT)
- Achats de marchandises: 2 100 000 FCFA (HT)
- Frais généraux: 450 000 FCFA (HT)
- Acquisition d'immobilisations: 800 000 FCFA (HT)

Le taux de TVA applicable est de 19,25%.

1. Calculez la TVA collectée sur les ventes et prestations.
2. Calculez la TVA déductible sur les achats et frais.
3. Déterminez le montant de TVA à payer pour le mois d'avril.
4. Passez l'écriture de déclaration de TVA."""

    example3_solution = """SOLUTION - TVA

1. Calcul de la TVA collectée:
   - Ventes de marchandises: 3 500 000 × 19,25% = 673 750 FCFA
   - Prestations de services: 750 000 × 19,25% = 144 375 FCFA
   Total TVA collectée: 818 125 FCFA

2. Calcul de la TVA déductible:
   - Achats de marchandises: 2 100 000 × 19,25% = 404 250 FCFA
   - Frais généraux: 450 000 × 19,25% = 86 625 FCFA
   - Immobilisations: 800 000 × 19,25% = 154 000 FCFA
   Total TVA déductible: 644 875 FCFA

3. TVA à payer:
   TVA à payer = TVA collectée - TVA déductible
   TVA à payer = 818 125 - 644 875 = 173 250 FCFA

4. Écriture de déclaration de TVA (au 30/04/2025):

   4456 TVA collectée                         818 125
   44562 TVA déductible sur immobilisations           154 000
   44566 TVA déductible sur autres biens et services   490 875
   4457 TVA à payer                                    173 250
   (Déclaration de TVA du mois d'avril 2025)"""

    create_example_pdf(
        os.path.join(examples_dir, 'tva.pdf'),
        "Exercice sur la TVA",
        example3_problem,
        example3_solution
    )
    
    print(f"Trois exemples d'exercices ont été créés dans le répertoire 'examples'.")