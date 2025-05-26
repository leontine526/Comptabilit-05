
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy

# Créer l'application Flask
app = Flask(__name__)
app.secret_key = "ohada_comptabilite_secret_key"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration de la base de données
database_uri = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_Crwao4WUkt5f@ep-spring-pond-a5upovj4-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 10,
    "pool_recycle": 60,
    "pool_pre_ping": True,
    "max_overflow": 15,
    "pool_timeout": 10
}

# Initialiser SQLAlchemy
db = SQLAlchemy(app)

# Assurez-vous que la configuration est définie avant d'initialiser l'application
if not app.config.get("SQLALCHEMY_DATABASE_URI"):
    raise RuntimeError("La configuration SQLALCHEMY_DATABASE_URI n'est pas définie!")

# Configurer le gestionnaire de connexion
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    try:
        # Import local pour éviter l'import circulaire
        from models import User
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Erreur lors du chargement de l'utilisateur: {str(e)}")
        return None

# Ajouter un filtre pour convertir les retours à la ligne en balises <br>
@app.template_filter('nl2br')
def nl2br(value):
    if value:
        return value.replace('\n', '<br>')
    return value

# Importer les routes
from routes import *

# Démarrer l'application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
