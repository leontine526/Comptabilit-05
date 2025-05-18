
import logging
import os
import sys
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charge les variables d'environnement
load_dotenv()

# Import des modules nécessaires
from app import app, db
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def check_db_tables():
    """
    Vérifie les tables de la base de données et affiche leurs statistiques
    """
    print("=== VÉRIFICATION DES TABLES DE LA BASE DE DONNÉES ===")
    
    try:
        # Vérifier le type de base de données
        dialect = db.session.bind.dialect.name
        
        if dialect == 'postgresql':
            # Pour PostgreSQL, utiliser une requête spécifique
            query = text("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name=t.table_name) AS columns,
                       pg_relation_size(quote_ident(table_name)) AS size
                FROM information_schema.tables t
                WHERE table_schema='public'
                ORDER BY table_name;
            """)
        else:
            # Pour SQLite et autres
            query = text("""
                SELECT name AS table_name, 
                       (SELECT COUNT(*) FROM pragma_table_info(name)) AS columns,
                       0 AS size
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY table_name;
            """)
            
        result = db.session.execute(query)
        
        print(f"{'Table':<30} {'Colonnes':<10} {'Taille (KB)':<15}")
        print("-" * 60)
        
        has_tables = False
        for row in result:
            has_tables = True
            table_name = row[0]
            columns = row[1]
            size_kb = int(row[2] or 0) / 1024
            
            print(f"{table_name:<30} {columns:<10} {size_kb:<15.2f}")
        
        if not has_tables:
            print("Aucune table trouvée dans la base de données.")
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de la vérification des tables: {str(e)}")
        print(f"❌ Erreur lors de la vérification des tables.")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des tables: {str(e)}")
        print(f"❌ Erreur lors de la vérification des tables.")
        return False
        
    print("\nVérification des tables terminée.")
    return True

if __name__ == "__main__":
    with app.app_context():
        check_db_tables()
