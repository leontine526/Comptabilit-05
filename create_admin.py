
import os
import sys
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user(username, email, password, full_name):
    """Créer un utilisateur administrateur"""
    with app.app_context():
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"L'utilisateur {username} existe déjà.")
            return False
        
        # Créer un nouvel utilisateur administrateur
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=generate_password_hash(password),
            is_admin=True  # Définir comme administrateur
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"Administrateur {username} créé avec succès!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'administrateur: {str(e)}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python create_admin.py <username> <email> <password> <full_name>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    full_name = sys.argv[4]
    
    create_admin_user(username, email, password, full_name)
import sys
import os
from app import app, db
from models import User

def create_admin(username):
    """Promote user to admin role."""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Utilisateur {username} non trouvé.")
            return False
        
        user.is_admin = True
        db.session.commit()
        print(f"L'utilisateur {username} est maintenant administrateur.")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_admin.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    create_admin(username)
