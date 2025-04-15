import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración inicial del cliente Oracle
oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\app\oracle\instantclient_23_7")

# Crear DSN
dsn = f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SERVICE')}"

def get_connection():
    """Establece y verifica la conexión a la base de datos Oracle"""
    try:
        # Crear conexión
        conn = oracledb.connect(
            user=os.getenv('DB_USER_O'),
            password=os.getenv('DB_PASSWORD_O'),
            dsn=dsn
        )
            
        return conn
        
    except oracledb.Error as e:
        print(f"❌ Error de conexión: {e}")
        raise  # Relanzar la excepción para manejo externo

