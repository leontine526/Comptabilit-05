#!/usr/bin/env python
"""
Script pour vérifier les tables de la base de données
"""
import os
import sys
import logging
from sqlalchemy import text
from app import app, db

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_tables():
    """Vérifier les tables dans la base de données"""
    print("=== VÉRIFICATION DES TABLES DE LA BASE DE DONNÉES ===")

    try:
        # Requête SQL pour obtenir les tables et le nombre de colonnes sans pg_total_relation_size
        # qui n'est pas disponible dans Neon PostgreSQL
        query = text("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name=t.table_name) AS columns
                FROM information_schema.tables t
                WHERE table_schema='public'
                ORDER BY table_name;
            """)

        with db.engine.connect() as conn:
            result = conn.execute(query)
            tables = result.fetchall()

        # Afficher les résultats
        if tables:
            print("\nTables trouvées dans la base de données:")
            print(f"{'Nom de la table':<30} {'Colonnes':<10}")
            print("-" * 50)

            for table in tables:
                print(f"{table[0]:<30} {table[1]:<10}")

            print(f"\nNombre total de tables: {len(tables)}")
        else:
            print("\nAucune table trouvée dans la base de données!")

        return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des tables: {str(e)}")
        print(f"\n❌ Erreur lors de la vérification des tables.")
        return False

if __name__ == "__main__":
    with app.app_context():
        check_tables()