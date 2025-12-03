import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    # Supporta due convenzioni di variabili d'ambiente:
    #  - DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME (usato nel README)
    #  - MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB (usato nel .env fornito)
    host = os.getenv('DB_HOST') or os.getenv('MYSQL_HOST')
    port = os.getenv('DB_PORT') or os.getenv('MYSQL_PORT')
    user = os.getenv('DB_USER') or os.getenv('MYSQL_USER')
    password = os.getenv('DB_PASSWORD') or os.getenv('MYSQL_PASSWORD')
    database = os.getenv('DB_NAME') or os.getenv('MYSQL_DB')

    try:
        port = int(port) if port is not None and port != '' else 3306
    except ValueError:
        port = 3306

    DB_CONFIG = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
