
import os
import random
from app import app, db
from models import User

def add_profile_pictures():
    """Ajoute des photos de profil aléatoires aux utilisateurs"""
    # Liste des avatars par défaut (utilisons des URLs d'avatars génériques)
    default_avatars = [
        "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka", 
        "https://api.dicebear.com/7.x/avataaars/svg?seed=Binx",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=Tiger",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=Lily",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=Max"
    ]

    with app.app_context():
        users = User.query.all()
        for user in users:
            # Assigne un avatar aléatoire
            user.avatar = random.choice(default_avatars)
            # Utilise le même avatar comme photo de profil
            user.profile_picture = user.avatar

        db.session.commit()
        print(f"Photos de profil ajoutées pour {len(users)} utilisateurs")

if __name__ == "__main__":
    add_profile_pictures()
