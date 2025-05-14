"""
Script pour migrer la base de données afin d'ajouter la fonctionnalité de widgets personnalisables.
"""
import sys
from app import db, app

def migrate_database():
    """Exécute la migration pour ajouter la colonne dashboard_layout à la table user."""
    print("Démarrage de la migration pour les widgets personnalisables...")
    
    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            try:
                db.session.execute("SELECT dashboard_layout FROM \"user\" LIMIT 1")
                print("La colonne dashboard_layout existe déjà dans la table user.")
                return
            except Exception as e:
                if "column \"dashboard_layout\" does not exist" not in str(e):
                    raise e
                print("La colonne dashboard_layout n'existe pas encore, elle va être créée.")
            
            # Ajouter la colonne dashboard_layout
            db.session.execute('ALTER TABLE "user" ADD COLUMN dashboard_layout TEXT DEFAULT \'{}\';')
            db.session.commit()
            print("Migration réussie: colonne dashboard_layout ajoutée à la table user.")
        
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la migration: {e}")
            sys.exit(1)

if __name__ == "__main__":
    migrate_database()