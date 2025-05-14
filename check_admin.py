
from app import app
from models import User
import sys

def check_admin_users():
    """Vérifie les utilisateurs ayant des droits d'administrateur"""
    with app.app_context():
        # Récupérer tous les utilisateurs admin
        admin_users = User.query.filter_by(is_admin=True).all()
        
        print('Utilisateurs administrateurs:')
        if not admin_users:
            print('Aucun utilisateur administrateur trouvé.')
        else:
            for user in admin_users:
                print(f'- {user.username} ({user.email})')
        
        # Vérifier un utilisateur spécifique
        if len(sys.argv) > 1:
            username = sys.argv[1]
            user = User.query.filter_by(username=username).first()
            if user:
                print(f'\nUtilisateur {username}:')
                print(f'- Email: {user.email}')
                print(f'- Statut admin: {"Oui" if user.is_admin else "Non"}')
            else:
                print(f'\nUtilisateur {username} non trouvé.')

if __name__ == "__main__":
    check_admin_users()
