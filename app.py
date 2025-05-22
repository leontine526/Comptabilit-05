import os
import logging
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Imports de Flask et ses extensions
try:
    from flask import Flask, request, session, render_template, jsonify
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.orm import DeclarativeBase
    from flask_login import LoginManager, current_user
    from werkzeug.middleware.proxy_fix import ProxyFix
    from flask_socketio import SocketIO, emit, join_room, leave_room
    from flask_caching import Cache
except ImportError as e:
    logger.error(f"Erreur d'importation: {str(e)}")
    sys.exit(1)

class Base(DeclarativeBase):
    pass


# Initialiser SQLAlchemy avant de créer l'application
db = SQLAlchemy(model_class=Base)

# Créer l'application Flask
app = Flask(__name__)

# Configurer l'application
app.secret_key = os.environ.get("SESSION_SECRET", "ohada_comptabilite_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Pour la génération d'URL avec https

# Configurer la base de données
database_uri = os.environ.get("DATABASE_URL")
if not database_uri:
    logger.error("DATABASE_URL non définie dans les variables d'environnement")
    # Utiliser une URL par défaut si non définie
    database_uri = "postgresql://neondb_owner:npg_Crwao4WUkt5f@ep-spring-pond-a5upovj4-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    logger.warning(f"Utilisation de l'URL de base de données par défaut: {database_uri}")

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 10,
    "pool_recycle": 60,
    "pool_pre_ping": True,
    "max_overflow": 15,
    "pool_timeout": 10
}

# Initialiser le gestionnaire de connexion amélioré
from db_connection_manager import db_manager
db_manager.initialize(
    database_uri,
    max_retries=5,
    pool_size=10,
    max_overflow=15,
    pool_recycle=600,
    enable_monitoring=True
)

# Configurer les uploads de fichiers
uploads_folder = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(uploads_folder):
    try:
        os.makedirs(uploads_folder)
        logger.info(f"Dossier d'uploads créé: {uploads_folder}")
    except Exception as e:
        logger.error(f"Impossible de créer le dossier d'uploads: {str(e)}")

app.config['UPLOAD_FOLDER'] = uploads_folder
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialiser les extensions
db.init_app(app)

# Configurer les hooks pour gérer automatiquement les transactions avortées
@app.teardown_request
def teardown_request(exception=None):
    if exception:
        try:
            # Annuler la transaction en cours si une exception s'est produite
            db.session.rollback()
            logger.info("Transaction annulée automatiquement après une erreur")
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation de la transaction: {str(e)}")

    # Toujours nettoyer la session DB à la fin de la requête
    db.session.remove()

# Importer le gestionnaire d'erreurs
from error_handlers import register_error_handlers
register_error_handlers(app)

from flask import Flask, request, session, render_template, jsonify

# Le gestionnaire d'erreur global est maintenant géré par error_handlers.py

# Initialiser Socket.IO avec gestion d'erreur
try:
    import eventlet
    socketio = SocketIO(app, async_mode='eventlet', 
                       logger=True, engineio_logger=False,
                       ping_timeout=60, ping_interval=25,
                       cors_allowed_origins="*")
    logger.info("Socket.IO initialisé avec succès (mode eventlet)")
except ImportError:
    try:
        socketio = SocketIO(app, async_mode=None, 
                           logger=True, 
                           cors_allowed_origins="*")
        logger.info("Socket.IO initialisé avec succès (mode threading)")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Socket.IO: {str(e)}")
        socketio = SocketIO(app)
        logger.warning("Socket.IO initialisé en mode de secours")

# Configurer le gestionnaire de connexion
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"

# Importer le modèle d'utilisateur après l'initialisation de db pour éviter les imports circulaires
from models import User

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Erreur lors du chargement de l'utilisateur: {str(e)}")
        return None

# Les tables seront créées dans db_initialize.py

# Pas besoin d'importer routes ici, cela sera fait dans main.py

# Route welcome désactivée pour rediriger directement vers le dashboard
# @app.route('/welcome')
# @login_required
# def welcome():
#     return render_template('welcome.html', title="Bienvenue")