from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_required

# Créer l'application Flask
app = Flask(__name__)
app.secret_key = "ohada_comptabilite_secret_key"

# Configurer le gestionnaire de connexion
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Importer le modèle User après l'initialisation de login_manager
from models import User

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Erreur lors du chargement de l'utilisateur: {str(e)}")
        return None

# Importer les routes
from routes import *

# Démarrer l'application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)