
#!/usr/bin/env python
"""
Script pour vérifier les tables dans la base de données.
"""
import os
import logging
from app import app, db
from sqlalchemy import text

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_tables():
    """Vérifie les tables dans la base de données et leur contenu"""
    with app.app_context():
        try:
            # Liste toutes les tables
            result = db.session.execute(text("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name=t.table_name) AS columns,
                       pg_total_relation_size(table_name) AS size
                FROM information_schema.tables t
                WHERE table_schema='public'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            print(f"Nombre de tables dans la base de données: {len(tables)}")
            
            if tables:
                print("\nListe des tables:")
                for table in tables:
                    print(f"- {table[0]} ({table[1]} colonnes, taille: {table[2]} octets)")
                
                # Vérifier le nombre d'enregistrements dans certaines tables importantes
                important_tables = ['user', 'exercise', 'transaction', 'workgroup', 'document']
                print("\nNombre d'enregistrements dans les tables principales:")
                
                for table_name in important_tables:
                    if any(table[0] == table_name for table in tables):
                        count = db.session.execute(text(f"SELECT COUNT(*) FROM \"{table_name}\"")).scalar()
                        print(f"- {table_name}: {count} enregistrements")
            else:
                print("Aucune table trouvée dans la base de données.")
                
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des tables: {str(e)}")
            return False

if __name__ == "__main__":
    print("=== VÉRIFICATION DES TABLES DE LA BASE DE DONNÉES ===")
    if check_tables():
        print("\n✅ Vérification des tables terminée avec succès.")
    else:
        print("\n❌ Erreur lors de la vérification des tables.")
