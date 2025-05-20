
"""
Gestionnaire de connexion à la base de données avec retry et health check
"""
import time
import logging
import threading
from sqlalchemy import create_engine
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
        self.connection_string = connection_string
        self.max_retries = kwargs.get('max_retries', 5)
        self.retry_delay = kwargs.get('retry_delay', 1)
        self.health_check_interval = kwargs.get('health_check_interval', 300)
        
        # Créer le moteur SQLAlchemy
        self.engine = create_engine(
            self.connection_string,
            echo=kwargs.get('echo', False),
            pool_size=kwargs.get('pool_size', 10),
            max_overflow=kwargs.get('max_overflow', 15),
            pool_recycle=kwargs.get('pool_recycle', 1800),
            pool_pre_ping=True
        )
        
        # Vérifier la connexion initiale
        self.check_health()
        
        # Démarrer le thread de surveillance si activé
        if kwargs.get('enable_monitoring', True):
            self._start_monitoring()
    
    def check_health(self):
        """Vérifie l'état de la connexion à la base de données"""
        try:
            # Exécuter une requête simple pour vérifier la connexion
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.is_healthy = True
            self.last_health_check = time.time()
            return True
        except Exception as e:
            self.is_healthy = False
            logger.error(f"Échec de la vérification de santé de la base de données: {str(e)}")
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
            
            except SQLAlchemyError as e:
                logger.error(f"Erreur SQLAlchemy: {str(e)}")
                raise
    
    def _start_monitoring(self):
        """Démarre un thread de surveillance de la santé de la base de données"""
        def health_check_loop():
            while True:
                time.sleep(self.health_check_interval)
                try:
                    self.check_health()
                except Exception as e:
                    logger.error(f"Erreur lors de la surveillance de la base de données: {str(e)}")
        
        monitoring_thread = threading.Thread(target=health_check_loop, daemon=True)
        monitoring_thread.start()

# Créer l'instance singleton
db_manager = DBConnectionManager()
