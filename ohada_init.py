import csv
import os
import logging
from datetime import datetime

from app import app, db
from models import Account, Exercise

logger = logging.getLogger(__name__)

# Structure des comptes OHADA
OHADA_ACCOUNTS = [
    # Classe 1 - Comptes de ressources durables
    {"account_number": "10", "name": "Capital", "account_type": "equity", "children": [
        {"account_number": "101", "name": "Capital social", "account_type": "equity"},
        {"account_number": "104", "name": "Primes liées au capital social", "account_type": "equity"},
        {"account_number": "109", "name": "Actionnaires, capital souscrit, non appelé", "account_type": "equity"}
    ]},
    {"account_number": "11", "name": "Réserves", "account_type": "equity", "children": [
        {"account_number": "111", "name": "Réserve légale", "account_type": "equity"},
        {"account_number": "112", "name": "Réserves statutaires", "account_type": "equity"},
        {"account_number": "113", "name": "Réserves facultatives", "account_type": "equity"}
    ]},
    {"account_number": "12", "name": "Report à nouveau", "account_type": "equity", "children": [
        {"account_number": "121", "name": "Report à nouveau créditeur", "account_type": "equity"},
        {"account_number": "129", "name": "Report à nouveau débiteur", "account_type": "equity"}
    ]},
    {"account_number": "13", "name": "Résultat net de l'exercice", "account_type": "equity", "children": [
        {"account_number": "131", "name": "Résultat net : bénéfice", "account_type": "equity"},
        {"account_number": "139", "name": "Résultat net : perte", "account_type": "equity"}
    ]},
    {"account_number": "14", "name": "Subventions d'investissement", "account_type": "equity"},
    {"account_number": "15", "name": "Provisions réglementées", "account_type": "liability"},
    {"account_number": "16", "name": "Emprunts et dettes assimilées", "account_type": "liability", "children": [
        {"account_number": "161", "name": "Emprunts obligataires", "account_type": "liability"},
        {"account_number": "162", "name": "Emprunts et dettes auprès des établissements de crédit", "account_type": "liability"},
        {"account_number": "163", "name": "Avances reçues de l'État", "account_type": "liability"},
        {"account_number": "164", "name": "Avances reçues et comptes courants bloqués", "account_type": "liability"},
        {"account_number": "165", "name": "Dépôts et cautionnements reçus", "account_type": "liability"},
        {"account_number": "166", "name": "Intérêts courus", "account_type": "liability"},
        {"account_number": "167", "name": "Avances assorties de conditions particulières", "account_type": "liability"},
        {"account_number": "168", "name": "Autres emprunts et dettes", "account_type": "liability"}
    ]},
    {"account_number": "17", "name": "Dettes de crédit-bail et contrats assimilés", "account_type": "liability"},
    {"account_number": "18", "name": "Dettes liées à des participations et comptes de liaison", "account_type": "liability"},
    {"account_number": "19", "name": "Provisions financières pour risques et charges", "account_type": "liability"},
    
    # Classe 2 - Comptes d'actifs immobilisés
    {"account_number": "20", "name": "Charges immobilisées", "account_type": "asset", "children": [
        {"account_number": "201", "name": "Frais d'établissement", "account_type": "asset"},
        {"account_number": "202", "name": "Charges à répartir", "account_type": "asset"},
        {"account_number": "206", "name": "Primes de remboursement des obligations", "account_type": "asset"}
    ]},
    {"account_number": "21", "name": "Immobilisations incorporelles", "account_type": "asset", "children": [
        {"account_number": "211", "name": "Frais de recherche et de développement", "account_type": "asset"},
        {"account_number": "212", "name": "Brevets, licences, logiciels et droits similaires", "account_type": "asset"},
        {"account_number": "213", "name": "Fonds commercial", "account_type": "asset"},
        {"account_number": "214", "name": "Droit au bail", "account_type": "asset"}
    ]},
    {"account_number": "22", "name": "Terrains", "account_type": "asset", "children": [
        {"account_number": "221", "name": "Terrains agricoles et forestiers", "account_type": "asset"},
        {"account_number": "222", "name": "Terrains nus", "account_type": "asset"},
        {"account_number": "223", "name": "Terrains bâtis", "account_type": "asset"},
        {"account_number": "224", "name": "Travaux de mise en valeur des terrains", "account_type": "asset"},
        {"account_number": "228", "name": "Autres terrains", "account_type": "asset"}
    ]},
    {"account_number": "23", "name": "Bâtiments, installations techniques et agencements", "account_type": "asset", "children": [
        {"account_number": "231", "name": "Bâtiments industriels", "account_type": "asset"},
        {"account_number": "232", "name": "Bâtiments administratifs et commerciaux", "account_type": "asset"},
        {"account_number": "233", "name": "Installations techniques", "account_type": "asset"},
        {"account_number": "234", "name": "Aménagements, agencements et installations", "account_type": "asset"}
    ]},
    {"account_number": "24", "name": "Matériel", "account_type": "asset", "children": [
        {"account_number": "241", "name": "Matériel et outillage industriel et commercial", "account_type": "asset"},
        {"account_number": "242", "name": "Matériel et outillage agricole", "account_type": "asset"},
        {"account_number": "243", "name": "Matériel d'emballage récupérable et identifiable", "account_type": "asset"},
        {"account_number": "244", "name": "Matériel et mobilier", "account_type": "asset"},
        {"account_number": "245", "name": "Matériel de transport", "account_type": "asset"},
        {"account_number": "246", "name": "Immobilisations animales et agricoles", "account_type": "asset"}
    ]},
    {"account_number": "25", "name": "Avances et acomptes versés sur immobilisations", "account_type": "asset"},
    {"account_number": "26", "name": "Titres de participation", "account_type": "asset"},
    {"account_number": "27", "name": "Autres immobilisations financières", "account_type": "asset"},
    {"account_number": "28", "name": "Amortissements", "account_type": "asset", "children": [
        {"account_number": "281", "name": "Amortissements des immobilisations incorporelles", "account_type": "asset"},
        {"account_number": "282", "name": "Amortissements des terrains", "account_type": "asset"},
        {"account_number": "283", "name": "Amortissements des bâtiments, installations techniques et agencements", "account_type": "asset"},
        {"account_number": "284", "name": "Amortissements du matériel", "account_type": "asset"}
    ]},
    {"account_number": "29", "name": "Provisions pour dépréciation", "account_type": "asset"},
    
    # Classe 3 - Comptes de stocks
    {"account_number": "31", "name": "Marchandises", "account_type": "asset"},
    {"account_number": "32", "name": "Matières premières et fournitures liées", "account_type": "asset"},
    {"account_number": "33", "name": "Autres approvisionnements", "account_type": "asset"},
    {"account_number": "34", "name": "Produits en cours", "account_type": "asset"},
    {"account_number": "35", "name": "Services en cours", "account_type": "asset"},
    {"account_number": "36", "name": "Produits finis", "account_type": "asset"},
    {"account_number": "37", "name": "Produits intermédiaires et résiduels", "account_type": "asset"},
    {"account_number": "38", "name": "Stocks en cours de route, en consignation ou en dépôt", "account_type": "asset"},
    {"account_number": "39", "name": "Dépréciations des stocks", "account_type": "asset"},
    
    # Classe 4 - Comptes de tiers
    {"account_number": "40", "name": "Fournisseurs et comptes rattachés", "account_type": "liability", "children": [
        {"account_number": "401", "name": "Fournisseurs, dettes en compte", "account_type": "liability"},
        {"account_number": "402", "name": "Fournisseurs, effets à payer", "account_type": "liability"},
        {"account_number": "408", "name": "Fournisseurs, factures non parvenues", "account_type": "liability"},
        {"account_number": "409", "name": "Fournisseurs débiteurs", "account_type": "asset"}
    ]},
    {"account_number": "41", "name": "Clients et comptes rattachés", "account_type": "asset", "children": [
        {"account_number": "411", "name": "Clients, créances en compte", "account_type": "asset"},
        {"account_number": "412", "name": "Clients, effets à recevoir", "account_type": "asset"},
        {"account_number": "418", "name": "Clients, factures à établir", "account_type": "asset"},
        {"account_number": "419", "name": "Clients créditeurs", "account_type": "liability"}
    ]},
    {"account_number": "42", "name": "Personnel", "account_type": "liability", "children": [
        {"account_number": "421", "name": "Personnel, avances et acomptes", "account_type": "asset"},
        {"account_number": "422", "name": "Personnel, rémunérations dues", "account_type": "liability"},
        {"account_number": "423", "name": "Personnel, oppositions, saisies-arrêts", "account_type": "liability"},
        {"account_number": "424", "name": "Personnel, œuvres sociales internes", "account_type": "liability"},
        {"account_number": "425", "name": "Représentants du personnel", "account_type": "liability"},
        {"account_number": "426", "name": "Personnel, participation aux bénéfices", "account_type": "liability"},
        {"account_number": "427", "name": "Personnel, dépôts", "account_type": "liability"},
        {"account_number": "428", "name": "Personnel, charges à payer et produits à recevoir", "account_type": "liability"}
    ]},
    {"account_number": "43", "name": "Organismes sociaux", "account_type": "liability"},
    {"account_number": "44", "name": "État et collectivités publiques", "account_type": "liability", "children": [
        {"account_number": "441", "name": "État, impôt sur les bénéfices", "account_type": "liability"},
        {"account_number": "442", "name": "État, autres impôts et taxes", "account_type": "liability"},
        {"account_number": "443", "name": "État, TVA facturée", "account_type": "liability"},
        {"account_number": "444", "name": "État, TVA due ou crédit de TVA", "account_type": "liability"},
        {"account_number": "445", "name": "État, TVA récupérable", "account_type": "asset"},
        {"account_number": "446", "name": "État, autres taxes sur le chiffre d'affaires", "account_type": "liability"},
        {"account_number": "447", "name": "État, impôts retenus à la source", "account_type": "liability"},
        {"account_number": "448", "name": "État, charges à payer et produits à recevoir", "account_type": "liability"},
        {"account_number": "449", "name": "État, créances et dettes diverses", "account_type": "liability"}
    ]},
    {"account_number": "45", "name": "Organismes internationaux", "account_type": "liability"},
    {"account_number": "46", "name": "Associés et Groupe", "account_type": "liability"},
    {"account_number": "47", "name": "Débiteurs et créditeurs divers", "account_type": "liability"},
    {"account_number": "48", "name": "Créances et dettes hors activités ordinaires", "account_type": "liability"},
    {"account_number": "49", "name": "Dépréciations et provisions pour risques à court terme", "account_type": "liability"},
    
    # Classe 5 - Comptes de trésorerie
    {"account_number": "50", "name": "Titres de placement", "account_type": "asset"},
    {"account_number": "51", "name": "Valeurs à encaisser", "account_type": "asset"},
    {"account_number": "52", "name": "Banques", "account_type": "asset", "children": [
        {"account_number": "521", "name": "Banques locales", "account_type": "asset"},
        {"account_number": "522", "name": "Banques étrangères", "account_type": "asset"},
        {"account_number": "523", "name": "Banques, intérêts courus", "account_type": "asset"}
    ]},
    {"account_number": "53", "name": "Établissements financiers et assimilés", "account_type": "asset"},
    {"account_number": "54", "name": "Instruments de trésorerie", "account_type": "asset"},
    {"account_number": "55", "name": "Chèques postaux", "account_type": "asset"},
    {"account_number": "56", "name": "Caisse", "account_type": "asset"},
    {"account_number": "57", "name": "Fonds de caisse", "account_type": "asset"},
    {"account_number": "58", "name": "Virements de fonds", "account_type": "asset"},
    {"account_number": "59", "name": "Dépréciations et provisions pour risques à court terme", "account_type": "asset"},
    
    # Classe 6 - Comptes de charges
    {"account_number": "60", "name": "Achats et variations de stocks", "account_type": "expense", "children": [
        {"account_number": "601", "name": "Achats de marchandises", "account_type": "expense"},
        {"account_number": "602", "name": "Achats de matières premières", "account_type": "expense"},
        {"account_number": "603", "name": "Variations des stocks de biens achetés", "account_type": "expense"},
        {"account_number": "604", "name": "Achats stockés de matières et fournitures", "account_type": "expense"},
        {"account_number": "605", "name": "Autres achats", "account_type": "expense", "children": [
            {"account_number": "6051", "name": "Achats d'électricité", "account_type": "expense"},
            {"account_number": "6052", "name": "Achats d'eau", "account_type": "expense"},
            {"account_number": "6053", "name": "Achats de petits équipements et matériels", "account_type": "expense"},
            {"account_number": "6054", "name": "Fournitures de bureau", "account_type": "expense"},
            {"account_number": "6055", "name": "Fournitures informatiques", "account_type": "expense"}
        ]}
    ]},
    {"account_number": "61", "name": "Transports", "account_type": "expense", "children": [
        {"account_number": "611", "name": "Transports sur achats", "account_type": "expense", "children": [
            {"account_number": "6111", "name": "Transports sur achats de marchandises", "account_type": "expense"},
            {"account_number": "6112", "name": "Transports sur achats de matières premières", "account_type": "expense"}
        ]},
        {"account_number": "612", "name": "Transports sur ventes", "account_type": "expense"},
        {"account_number": "613", "name": "Transports pour le compte de tiers", "account_type": "expense"},
        {"account_number": "614", "name": "Transports du personnel", "account_type": "expense", "children": [
            {"account_number": "6141", "name": "Voyages et déplacements", "account_type": "expense"},
            {"account_number": "6142", "name": "Transports collectifs du personnel", "account_type": "expense"},
            {"account_number": "6143", "name": "Indemnités de transport du personnel", "account_type": "expense"},
            {"account_number": "6144", "name": "Indemnités kilométriques", "account_type": "expense"}
        ]}
    ]},
    {"account_number": "62", "name": "Services extérieurs A", "account_type": "expense", "children": [
        {"account_number": "621", "name": "Sous-traitance générale", "account_type": "expense"},
        {"account_number": "622", "name": "Locations et charges locatives", "account_type": "expense"},
        {"account_number": "623", "name": "Redevances de crédit-bail et contrats assimilés", "account_type": "expense"},
        {"account_number": "624", "name": "Entretien, réparations et maintenance", "account_type": "expense"},
        {"account_number": "625", "name": "Primes d'assurance", "account_type": "expense"},
        {"account_number": "626", "name": "Études, recherches et documentation", "account_type": "expense"},
        {"account_number": "627", "name": "Publicité, publications, relations publiques", "account_type": "expense"},
        {"account_number": "628", "name": "Frais de télécommunications", "account_type": "expense"}
    ]},
    {"account_number": "63", "name": "Services extérieurs B", "account_type": "expense", "children": [
        {"account_number": "631", "name": "Frais bancaires", "account_type": "expense"},
        {"account_number": "632", "name": "Rémunérations d'intermédiaires et de conseils", "account_type": "expense"},
        {"account_number": "633", "name": "Frais de formation du personnel", "account_type": "expense"},
        {"account_number": "634", "name": "Redevances pour brevets, licences, logiciels et droits similaires", "account_type": "expense"},
        {"account_number": "635", "name": "Cotisations", "account_type": "expense"},
        {"account_number": "637", "name": "Rémunérations de personnel extérieur à l'entreprise", "account_type": "expense"},
        {"account_number": "638", "name": "Autres charges externes", "account_type": "expense"}
    ]},
    {"account_number": "64", "name": "Impôts et taxes", "account_type": "expense"},
    {"account_number": "65", "name": "Autres charges", "account_type": "expense"},
    {"account_number": "66", "name": "Charges de personnel", "account_type": "expense", "children": [
        {"account_number": "661", "name": "Rémunérations directes versées au personnel national", "account_type": "expense"},
        {"account_number": "662", "name": "Rémunérations directes versées au personnel non national", "account_type": "expense"},
        {"account_number": "663", "name": "Indemnités forfaitaires versées au personnel", "account_type": "expense"},
        {"account_number": "664", "name": "Charges sociales", "account_type": "expense"},
        {"account_number": "665", "name": "Autres charges sociales", "account_type": "expense"},
        {"account_number": "666", "name": "Rémunérations et charges sociales de l'exploitant individuel", "account_type": "expense"},
        {"account_number": "667", "name": "Rémunérations transférées de personnel extérieur", "account_type": "expense"},
        {"account_number": "668", "name": "Autres charges de personnel", "account_type": "expense"}
    ]},
    {"account_number": "67", "name": "Frais financiers et charges assimilées", "account_type": "expense"},
    {"account_number": "68", "name": "Dotations aux amortissements", "account_type": "expense"},
    {"account_number": "69", "name": "Dotations aux provisions", "account_type": "expense"},
    
    # Classe 7 - Comptes de produits
    {"account_number": "70", "name": "Ventes", "account_type": "revenue", "children": [
        {"account_number": "701", "name": "Ventes de marchandises", "account_type": "revenue"},
        {"account_number": "702", "name": "Ventes de produits finis", "account_type": "revenue"},
        {"account_number": "703", "name": "Ventes de produits intermédiaires", "account_type": "revenue"},
        {"account_number": "704", "name": "Ventes de produits résiduels", "account_type": "revenue"},
        {"account_number": "705", "name": "Travaux facturés", "account_type": "revenue"},
        {"account_number": "706", "name": "Services vendus", "account_type": "revenue"},
        {"account_number": "707", "name": "Produits accessoires", "account_type": "revenue"},
        {"account_number": "708", "name": "Produits des activités annexes", "account_type": "revenue"}
    ]},
    {"account_number": "71", "name": "Subventions d'exploitation", "account_type": "revenue"},
    {"account_number": "72", "name": "Production immobilisée", "account_type": "revenue"},
    {"account_number": "73", "name": "Variations des stocks de biens et de services produits", "account_type": "revenue"},
    {"account_number": "74", "name": "Produits hors activités ordinaires", "account_type": "revenue"},
    {"account_number": "75", "name": "Transferts de charges", "account_type": "revenue"},
    {"account_number": "77", "name": "Revenus financiers et produits assimilés", "account_type": "revenue"},
    {"account_number": "78", "name": "Transferts de charges", "account_type": "revenue"},
    {"account_number": "79", "name": "Reprises de provisions", "account_type": "revenue"},
    
    # Classe 8 - Soldes caractéristiques de gestion
    {"account_number": "81", "name": "Valeur ajoutée", "account_type": "equity"},
    {"account_number": "82", "name": "Excédent brut d'exploitation", "account_type": "equity"},
    {"account_number": "83", "name": "Résultat d'exploitation", "account_type": "equity"},
    {"account_number": "84", "name": "Résultat hors activités ordinaires", "account_type": "equity"},
    {"account_number": "85", "name": "Résultat financier", "account_type": "equity"},
    {"account_number": "86", "name": "Résultat des activités ordinaires", "account_type": "equity"},
    {"account_number": "87", "name": "Participation des travailleurs", "account_type": "equity"},
    {"account_number": "88", "name": "Résultat avant impôt", "account_type": "equity"},
    {"account_number": "89", "name": "Résultat net", "account_type": "equity"}
]

def create_account(exercise_id, account_data, parent_id=None):
    """Create an account and its children"""
    
    # Create the account
    account = Account(
        account_number=account_data["account_number"],
        name=account_data["name"],
        account_type=account_data["account_type"],
        parent_id=parent_id,
        exercise_id=exercise_id,
        is_system=True
    )
    db.session.add(account)
    db.session.flush()  # To get the account ID
    
    # Create children if present
    if "children" in account_data:
        for child_data in account_data["children"]:
            create_account(exercise_id, child_data, account.id)

def initialize_ohada_accounts(exercise_id):
    """Initialize OHADA accounts for an exercise"""
    
    # Check if the exercise exists
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        logger.error(f"Exercise {exercise_id} not found")
        return False
    
    try:
        # Check if accounts already exist for this exercise
        existing_accounts = Account.query.filter_by(exercise_id=exercise_id, is_system=True).count()
        if existing_accounts > 0:
            logger.info(f"OHADA accounts already exist for exercise {exercise_id}")
            return True
        
        # Create the OHADA accounts
        for account_data in OHADA_ACCOUNTS:
            create_account(exercise_id, account_data)
        
        db.session.commit()
        logger.info(f"OHADA accounts initialized for exercise {exercise_id}")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error initializing OHADA accounts: {str(e)}")
        return False