import mysql.connector
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER_O'),
                password=os.getenv('DB_PASSWORD_O'),
                database=os.getenv('DB_NAME'),
                connect_timeout=10  # Establecer un tiempo de espera en la conexión
            )
            self.cursor = self.connection.cursor()  # Inicializar cursor aquí
        except mysql.connector.Error as e:
            print(f"❌ Error al conectar con la base de datos: {e}")
            raise
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def fetch_one(self, query, params=None):
        """Ejecuta una consulta y devuelve una sola fila (para verificación de duplicados)"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"❌ Error al verificar duplicados: {e}")
            return None

    def insert_invoice(self, *args):
        try:
            #Se debe de poner tal cual la estructura de la tabla en la base de datos
            # y los valores deben de ir en el mismo orden que la tabla
            sql = """
                INSERT INTO facturas (
                    nom_empresa, cod_gen, tipo_dte, estado_doc, estado_doc_inc, sello_recepcion, 
                    num_iden_recep, accion, observaciones, num_control, nit_emisor, nrc_emisor, 
                    nom_emisor, nom_receptor, nrc_receptor, nit_receptor, dte, fecha_emision, 
                    Periodo_tributario, Mes_tributario, procesada, estado, iva, iva_percepcion, 
                    fovial, cotrans, subtotal, monto
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            self.cursor.execute(sql, args)
            self.connection.commit()
            print(f"✅ Factura {args[1]} insertada correctamente en la base de datos.")
            return True
        except mysql.connector.Error as e:
            print(f"❌ Error al insertar la factura {args[1]} en la BD: {e}")
            return False
        
    def check_invoice(self, codigo_generacion):
        """Verifica si una factura con el código ya existe en la BD."""
        try:
            query = "SELECT COUNT(*) FROM facturas WHERE cod_gen = %s"
            self.cursor.execute(query, (codigo_generacion,))
            result = self.cursor.fetchone()
            return result[0] > 0  # Retorna True si ya existe, False si no
        except mysql.connector.Error as e:
            print(f"⚠️ Error al verificar existencia de factura en BD: {e}")
            return False  # En caso de error, asumimos que no existe
    
    def close(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()
