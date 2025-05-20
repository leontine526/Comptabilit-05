"""
Gestionnaire de connexion à la base de données avec retry et health check
"""
import time
import logging
import threading
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DBConnectionManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DBConnectionManager, cls).__new__(cls)
                cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.engine = None
        self.connection_string = None
        self.max_retries = 5
        self.retry_delay = 1  # seconde
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = 0
        self.is_healthy = False
        self.initialized = True

    def initialize(self, connection_string, **kwargs):
        """Initialise le gestionnaire avec la chaîne de connexion"""
        if '-pooler' not in connection_string:
            connection_string = connection_string.replace('.us-east-2', '-pooler.us-east-2')
        if '?' not in connection_string:
            connection_string += "?sslmode=require&connect_timeout=10"

        self.connection_string = connection_string
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = kwargs.get('retry_delay', 2)
        self.health_check_interval = kwargs.get('health_check_interval', 60)

        # Créer le moteur SQLAlchemy
        self.engine = create_engine(
            self.connection_string,
            echo=kwargs.get('echo', False),
            pool_size=kwargs.get('pool_size', 5),
            max_overflow=kwargs.get('max_overflow', 10),
            pool_timeout=kwargs.get('pool_timeout', 30),
            pool_recycle=kwargs.get('pool_recycle', 60),
            pool_pre_ping=kwargs.get('pool_pre_ping', True),
        )

        # Vérifier la santé de la connexion
        self.check_health()

        logger.info(f"Gestionnaire de connexion initialisé avec succès")

    def check_health(self):
        """Vérifie la santé de la connexion à la base de données"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.is_healthy = True
            self.last_health_check = time.time()
            return True
        except Exception as e:
            self.is_healthy = False
            logger.error(f"Erreur de vérification de santé: {str(e)}")
            return False

    @contextmanager
    def get_connection(self):
        """Fournit une connexion à la base de données avec gestion des erreurs et retry"""
        retry_count = 0

        while retry_count < self.max_retries:
            try:
                # Vérifier la santé si nécessaire
                current_time = time.time()
                if current_time - self.last_health_check > self.health_check_interval:
                    self.check_health()

                # Obtenir une connexion
                connection = self.engine.connect()
                try:
                    yield connection
                    return  # Sortir du contexte si tout va bien
                finally:
                    connection.close()

            except OperationalError as e:
                retry_count += 1
                logger.warning(f"Erreur de connexion DB (tentative {retry_count}/{self.max_retries}): {str(e)}")

                if retry_count < self.max_retries:
                    # Attendre avant de réessayer avec backoff exponentiel
                    wait_time = self.retry_delay * (2 ** (retry_count - 1))
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Nombre maximum de tentatives atteint, impossible de se connecter à la base de données")
                    raise

            except Exception as e:
                logger.error(f"Erreur non gérée lors de la connexion: {str(e)}")
                raise

# Singleton pour utilisation globale
db_manager = DBConnectionManager()