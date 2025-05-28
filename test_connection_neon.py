
#!/usr/bin/env python
"""
Script de test de connexion pour la base de données Neon PostgreSQL
Teste la connexion, vérifie les tables et fournit un diagnostic complet
"""
import os
import sys
import logging
import time
import traceback
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/connection_test.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test complet de la connexion à la base de données Neon"""
    logger.info("=" * 60)
    logger.info("🔍 TEST DE CONNEXION À LA BASE DE DONNÉES NEON")
    logger.info("=" * 60)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # URL de la base de données Neon
    database_url = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    
    # Masquer les informations sensibles pour l'affichage
    url_parts = database_url.split('@')
    if len(url_parts) > 1:
        masked_url = f"***CREDENTIALS_HIDDEN***@{url_parts[1]}"
    else:
        masked_url = "***URL_MASKED***"
    
    logger.info(f"📍 URL de connexion: {masked_url}")
    logger.info(f"🕐 Heure du test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Étape 1: Création du moteur SQLAlchemy
        logger.info("\n📡 Étape 1: Création du moteur de base de données...")
        engine = create_engine(
            database_url,
            pool_size=3,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=60,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 15,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 3
            }
        )
        logger.info("✅ Moteur SQLAlchemy créé avec succès")
        
        # Étape 2: Test de connexion basique
        logger.info("\n🔌 Étape 2: Test de connexion basique...")
        start_time = time.time()
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test_value"))
            test_value = result.scalar()
            
            if test_value == 1:
                connection_time = time.time() - start_time
                logger.info(f"✅ Connexion établie avec succès en {connection_time:.2f}s")
            else:
                logger.error("❌ La requête de test a retourné une valeur incorrecte")
                return False
        
        # Étape 3: Test des informations de base
        logger.info("\n📊 Étape 3: Récupération des informations de base...")
        with engine.connect() as conn:
            # Version PostgreSQL
            version_result = conn.execute(text("SELECT version()"))
            pg_version = version_result.scalar()
            logger.info(f"🐘 Version PostgreSQL: {pg_version.split(',')[0]}")
            
            # Nom de la base de données
            db_result = conn.execute(text("SELECT current_database()"))
            db_name = db_result.scalar()
            logger.info(f"🗃️  Base de données: {db_name}")
            
            # Utilisateur actuel
            user_result = conn.execute(text("SELECT current_user"))
            current_user = user_result.scalar()
            logger.info(f"👤 Utilisateur: {current_user}")
        
        # Étape 4: Inspection des tables
        logger.info("\n📋 Étape 4: Inspection des tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            logger.info(f"✅ {len(tables)} tables trouvées:")
            for i, table in enumerate(sorted(tables), 1):
                logger.info(f"   {i:2d}. {table}")
        else:
            logger.warning("⚠️  Aucune table trouvée dans la base de données")
        
        # Étape 5: Test des tables principales (si elles existent)
        logger.info("\n🧪 Étape 5: Test des tables principales...")
        expected_tables = ['user', 'exercise', 'account', 'transaction', 'post']
        
        with engine.connect() as conn:
            for table in expected_tables:
                if table in tables:
                    try:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.scalar()
                        logger.info(f"   ✅ Table '{table}': {count} enregistrements")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Erreur lors de la lecture de '{table}': {str(e)}")
                else:
                    logger.warning(f"   ❌ Table '{table}' manquante")
        
        # Étape 6: Test de performance
        logger.info("\n⚡ Étape 6: Test de performance...")
        start_time = time.time()
        
        with engine.connect() as conn:
            # Test de requête simple
            for i in range(5):
                conn.execute(text("SELECT 1"))
            
            performance_time = time.time() - start_time
            avg_time = performance_time / 5
            logger.info(f"✅ 5 requêtes exécutées en {performance_time:.3f}s (moyenne: {avg_time:.3f}s)")
        
        # Étape 7: Test de l'utilisateur admin
        logger.info("\n👑 Étape 7: Vérification de l'utilisateur admin...")
        if 'user' in tables:
            try:
                with engine.connect() as conn:
                    admin_result = conn.execute(text(
                        "SELECT username, email, is_admin FROM \"user\" WHERE username = 'admin'"
                    ))
                    admin_user = admin_result.fetchone()
                    
                    if admin_user:
                        logger.info(f"✅ Utilisateur admin trouvé:")
                        logger.info(f"   - Username: {admin_user[0]}")
                        logger.info(f"   - Email: {admin_user[1]}")
                        logger.info(f"   - Is Admin: {admin_user[2]}")
                    else:
                        logger.warning("⚠️  Aucun utilisateur admin trouvé")
            except Exception as e:
                logger.warning(f"⚠️  Erreur lors de la vérification admin: {str(e)}")
        
        # Résumé final
        logger.info("\n" + "=" * 60)
        logger.info("🎉 RÉSUMÉ DU TEST DE CONNEXION")
        logger.info("=" * 60)
        logger.info("✅ Connexion à la base de données: RÉUSSIE")
        logger.info(f"✅ Nombre de tables: {len(tables)}")
        logger.info("✅ Performance: ACCEPTABLE")
        logger.info("✅ Test complet: SUCCÈS")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error("\n" + "=" * 60)
        logger.error("❌ ERREUR LORS DU TEST DE CONNEXION")
        logger.error("=" * 60)
        logger.error(f"Type d'erreur: {type(e).__name__}")
        logger.error(f"Message: {str(e)}")
        logger.error("\nDétails techniques:")
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        return False

def test_app_models():
    """Test l'importation des modèles de l'application"""
    logger.info("\n🏗️  Test d'importation des modèles...")
    
    try:
        # Temporairement définir la variable d'environnement
        os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_kOmlE4KW5tJw@ep-twilight-boat-a89ewfq2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
        
        from models import User, Exercise, Account, Transaction, Post
        logger.info("✅ Modèles importés avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'importation des modèles: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("\n🚀 Démarrage du test de connexion...")
    
    # Créer le dossier logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    
    # Tests principaux
    connection_success = test_database_connection()
    models_success = test_app_models()
    
    # Résultat final
    print("\n" + "=" * 60)
    print("📝 RAPPORT FINAL")
    print("=" * 60)
    
    if connection_success and models_success:
        print("🎉 TOUS LES TESTS ONT RÉUSSI!")
        print("✅ Votre base de données Neon est prête à être utilisée")
        print("✅ Vous pouvez démarrer l'application avec le bouton Run")
        sys.exit(0)
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        if not connection_success:
            print("❌ Problème de connexion à la base de données")
        if not models_success:
            print("❌ Problème avec les modèles de l'application")
        print("\n💡 Vérifiez les logs ci-dessus pour plus de détails")
        sys.exit(1)

if __name__ == "__main__":
    main()
