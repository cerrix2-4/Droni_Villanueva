from mysql.connector import pooling, Error
from config import Config

# Ritarda l'inizializzazione del pool fino al primo utilizzo.
_pool = None

def _init_pool():
    global _pool
    if _pool is None:
        cfg = Config.DB_CONFIG
        if not cfg.get('host'):
            raise RuntimeError('Database host non configurato. Impostare DB_HOST o MYSQL_HOST in .env')
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name="droni_pool",
                pool_size=5,
                **cfg
            )
        except Error as e:
            # Rilancia con messaggio più chiaro
            raise RuntimeError(f'Impossibile inizializzare il pool DB: {e}') from e

def get_connection():
    """Ottiene una connessione dal pool, inizializzandolo al bisogno"""
    if _pool is None:
        _init_pool()
    return _pool.get_connection()

def query_one(query, params=None):
    """Esegue una query e ritorna una singola riga come dizionario"""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        cursor.close()
        return result
    finally:
        conn.close()

def query_all(query, params=None):
    """Esegue una query e ritorna tutte le righe come lista di dizionari"""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        return results
    finally:
        conn.close()

def execute(query, params=None):
    """Esegue una query INSERT/UPDATE/DELETE e ritorna l'ID dell'ultima riga"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id
    finally:
        conn.close()
