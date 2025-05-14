
import os
from dotenv import load_dotenv
import psycopg2
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get database connection string
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    logger.error("DATABASE_URL environment variable not set!")
    exit(1)

# Masquer les informations sensibles dans les logs
safe_url = db_url.split('@')[1] if '@' in db_url else 'Hidden for security'
logger.info(f"Attempting to connect to database: {safe_url}")

try:
    # Connect to the database using SQLAlchemy
    engine = create_engine(db_url)
    with engine.connect() as conn:
        logger.info("Successfully connected to PostgreSQL database using SQLAlchemy!")
        
        # Test query to get database version
        result = conn.execute(text("SELECT version();"))
        version = result.scalar()
        logger.info(f"Database version: {version}")
        
        # Get list of tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        tables = result.fetchall()
        
        if tables:
            logger.info("Tables in the database:")
            for table in tables:
                logger.info(f"- {table[0]}")
        else:
            logger.warning("No tables found in the database.")
    
    logger.info("Connection test completed successfully.")

except Exception as e:
    logger.error(f"Error connecting to PostgreSQL database: {e}")
    logger.error("Please check your DATABASE_URL and ensure the database is accessible from Replit.")
