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
                INSERT INTO CO_COMPRAS (
                    CODEMP, CODTIPO, COMPROB, COMPRAIE, COMPRAEE, COMPRAIG, IMPORTACIO, IVA, TOTALCOMP,
                    RETENCION, RETENCIONIVA, ANTICIPO, MESD, ANOD, COMPRAEXC, COMPRET, CDPROV, DAI,
                    IVAADUANA, TIPOPOLIZA, POLIZA, DESCUENTOS, CERRADO, TIPO_COMPRA, ID_TIPOCOMPRA,
                    CORRELATIVO_DTE, NUMERO_CONTROL_DTE, SELLO_RECIBIDO_DTE, ID_TIPO_COMPRA_O,
                    ES_COMBUSTIBLE, FOVIAL, COTRANS, CODIGO_GENERACION_DTE, IVA_PERCIBIDO,
                    CUENTA_CONTABLE, CUENTA_RELACION, HORA, CON_ENTIDAD, BLOQUEF_EXCENTAS,
                    FECHA_FACTURACION_HORA, RETENCION_2PORCIENTO, COMENTARIO, ADUANA, AGENTE_ADUANAL,
                    PROVEEDOR_EXT, CODIGO_IMPORTACION, CONCEPTO_COMPRA, CODIGO_FACTURA_CORRE,
                    DTE_TIPO_OPERACION, DTE_CLASIFICACION, DTE_SECTOR, DTE_TIPO_COSTO_GASTO,
                    TIPO_ACTIVO, PORCENTAJE, VIDA_UTIL, DEPRECIACION, TIPO_DEPRECIACION,
                    FECHA_DEPRECIACION, PRORRATEO, PROCESADO_PRORRATEO, PROCESADO_PRORRATEO_HECHO,
                    COMPRA_ORIGINAL
                )
                VALUES (
                    :CODEMP, :CODTIPO, :COMPROB, :COMPRAIE, :COMPRAEE, :COMPRAIG, :IMPORTACIO, :IVA, :TOTALCOMP,
                    :RETENCION, :RETENCIONIVA, :ANTICIPO, :MESD, :ANOD, :COMPRAEXC, :COMPRET, :CDPROV, :DAI,
                    :IVAADUANA, :TIPOPOLIZA, :POLIZA, :DESCUENTOS, :CERRADO, :TIPO_COMPRA, :ID_TIPOCOMPRA,
                    :CORRELATIVO_DTE, :NUMERO_CONTROL_DTE, :SELLO_RECIBIDO_DTE, :ID_TIPO_COMPRA_O,
                    :ES_COMBUSTIBLE, :FOVIAL, :COTRANS, :CODIGO_GENERACION_DTE, :IVA_PERCIBIDO,
                    :CUENTA_CONTABLE, :CUENTA_RELACION, :HORA, :CON_ENTIDAD, :BLOQUEF_EXCENTAS,
                    :FECHA_FACTURACION_HORA, :RETENCION_2PORCIENTO, :COMENTARIO, :ADUANA, :AGENTE_ADUANAL,
                    :PROVEEDOR_EXT, :CODIGO_IMPORTACION, :CONCEPTO_COMPRA, :CODIGO_FACTURA_CORRE,
                    :DTE_TIPO_OPERACION, :DTE_CLASIFICACION, :DTE_SECTOR, :DTE_TIPO_COSTO_GASTO,
                    :TIPO_ACTIVO, :PORCENTAJE, :VIDA_UTIL, :DEPRECIACION, :TIPO_DEPRECIACION,
                    :FECHA_DEPRECIACION, :PRORRATEO, :PROCESADO_PRORRATEO, :PROCESADO_PRORRATEO_HECHO,
                    :COMPRA_ORIGINAL
                )
            """

            columnas = [
                "CODEMP", "CODTIPO", "COMPROB", "COMPRAIE", "COMPRAEE", "COMPRAIG", "IMPORTACIO", "IVA", "TOTALCOMP",
                "RETENCION", "RETENCIONIVA", "ANTICIPO", "MESD", "ANOD", "COMPRAEXC", "COMPRET", "CDPROV", "DAI",
                "IVAADUANA", "TIPOPOLIZA", "POLIZA", "DESCUENTOS", "CERRADO", "TIPO_COMPRA", "ID_TIPOCOMPRA",
                "CORRELATIVO_DTE", "NUMERO_CONTROL_DTE", "SELLO_RECIBIDO_DTE", "ID_TIPO_COMPRA_O",
                "ES_COMBUSTIBLE", "FOVIAL", "COTRANS", "CODIGO_GENERACION_DTE", "IVA_PERCIBIDO",
                "CUENTA_CONTABLE", "CUENTA_RELACION", "HORA", "CON_ENTIDAD", "BLOQUEF_EXCENTAS",
                "FECHA_FACTURACION_HORA", "RETENCION_2PORCIENTO", "COMENTARIO", "ADUANA", "AGENTE_ADUANAL",
                "PROVEEDOR_EXT", "CODIGO_IMPORTACION", "CONCEPTO_COMPRA", "CODIGO_FACTURA_CORRE",
                "DTE_TIPO_OPERACION", "DTE_CLASIFICACION", "DTE_SECTOR", "DTE_TIPO_COSTO_GASTO",
                "TIPO_ACTIVO", "PORCENTAJE", "VIDA_UTIL", "DEPRECIACION", "TIPO_DEPRECIACION",
                "FECHA_DEPRECIACION", "PRORRATEO", "PROCESADO_PRORRATEO", "PROCESADO_PRORRATEO_HECHO",
                "COMPRA_ORIGINAL"
            ]

            params = dict(zip(columnas, args))
            self.cursor.execute(sql, params)
            self.connection.commit()

            print(f"✅ Compra insertada correctamente. Comprobante: {params.get('COMPROB')}")
            return True

        except oracledb.Error as e:
            print(f"❌ Error al insertar la compra: {e}")
            return False

    def check_invoice(self, codigo_generacion):
        """Verifica si una factura ya existe en Oracle"""
        try:
            query = "SELECT COUNT(*) FROM CO_COMPRAS WHERE CODIGO_GENERACION_DTE = :cod_gen"
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
