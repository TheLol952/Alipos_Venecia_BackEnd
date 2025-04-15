import oracledb
from core.conexion_oracle import get_connection

class Database:
    def __init__(self):
        try:
            self.connection = get_connection()
            self.cursor = self.connection.cursor()
        except oracledb.Error as e:
            print(f"❌ Error al conectar con Oracle DB: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def fetch_one(self, query, params=None):
        """Ejecuta una consulta y devuelve una sola fila"""
        try:
            self.cursor.execute(query, params or {})
            return self.cursor.fetchone()
        except oracledb.Error as e:
            print(f"❌ Error al ejecutar la consulta: {e}")
            return None

    def insert_invoice(self, *args):
        try:
            sql = """
                INSERT INTO facturas (
                    nom_empresa, cod_gen, tipo_dte, estado_doc, estado_doc_inc, sello_recepcion, 
                    num_iden_recep, accion, observaciones, num_control, nit_emisor, nrc_emisor, 
                    nom_emisor, nom_receptor, nrc_receptor, nit_receptor, dte, fecha_emision, 
                    Periodo_tributario, Mes_tributario, procesada, estado, iva, iva_percepcion, 
                    fovial, cotrans, subtotal, monto
                ) 
                VALUES (
                    :nom_empresa, :cod_gen, :tipo_dte, :estado_doc, :estado_doc_inc, :sello_recepcion,
                    :num_iden_recep, :accion, :observaciones, :num_control, :nit_emisor, :nrc_emisor,
                    :nom_emisor, :nom_receptor, :nrc_receptor, :nit_receptor, :dte, :fecha_emision,
                    :Periodo_tributario, :Mes_tributario, :procesada, :estado, :iva, :iva_percepcion,
                    :fovial, :cotrans, :subtotal, :monto
                )
            """

            keys = [
                "nom_empresa", "cod_gen", "tipo_dte", "estado_doc", "estado_doc_inc", "sello_recepcion",
                "num_iden_recep", "accion", "observaciones", "num_control", "nit_emisor", "nrc_emisor",
                "nom_emisor", "nom_receptor", "nrc_receptor", "nit_receptor", "dte", "fecha_emision",
                "Periodo_tributario", "Mes_tributario", "procesada", "estado", "iva", "iva_percepcion",
                "fovial", "cotrans", "subtotal", "monto"
            ]
            params = dict(zip(keys, args))

            self.cursor.execute(sql, params)
            self.connection.commit()

            print(f"✅ Factura {params['cod_gen']} insertada correctamente.")
            return True
        except oracledb.Error as e:
            print(f"❌ Error al insertar la factura {params.get('cod_gen')}: {e}")
            return False

    def check_invoice(self, codigo_generacion):
        """Verifica si una factura ya existe en Oracle"""
        try:
            query = "SELECT COUNT(*) FROM facturas WHERE cod_gen = :cod_gen"
            self.cursor.execute(query, {"cod_gen": codigo_generacion})
            result = self.cursor.fetchone()
            return result[0] > 0
        except oracledb.Error as e:
            print(f"⚠️ Error al verificar existencia de factura: {e}")
            return False

    def close(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()
