import json
import oracledb
from core.conexion_oracle import get_connection
import unicodedata

try:
    import procedimientos.DiccionarioSucursales as ds
except ImportError:
    from . import DiccionarioSucursales as ds

class CuentaSucursalesService:
    @staticmethod
    def obtener_datos_sucursal(data: dict) -> dict:

        nit_raw = data.get("emisor", {}).get("nit", "") or ""
        nit = ds.normalize_nit(nit_raw)

        con_entidad = ''
        cod_contabilidad = ''
        sucursal = ''
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM DICCIONARIO_COMPRAS_AUTO WHERE NIT = :nit",
                        { "nit": nit }
                    )
                    if not cur.fetchone():
                        con_entidad = None
                        cod_contabilidad = None
                        sucursal = None

        except oracledb.DatabaseError as e:
            print(f"⚠️ Error verificando NIT en diccionario automático: {e}")
            return None
        
        descripcion = data.get("emisor", {}).get("direccion", {}).get("complemento", "") or ""
        descripcion_norm = ds.normalize(descripcion)

        dicc = ds.cargar_diccionario_sucursales()
        sucursal = ds.identificar_sucursal(descripcion, dicc)

        auto_detectado = False
        if sucursal == "SUCURSAL_DESCONOCIDA":
            sucursal_auto = ds.identificar_sucursal_auto(descripcion, dicc)
            if sucursal_auto != "SUCURSAL_DESCONOCIDA_AUTO":
                sucursal = sucursal_auto
                auto_detectado = True

        if auto_detectado:
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT SUCURSAL, CUENTA_CONTABLE
                              FROM DICCIONARIO_COMPRAS_AUTO
                             WHERE NIT       = :nit
                               AND DIRECCION = :dir
                            """,
                            { "nit": nit, "dir": descripcion_norm }
                        )
                        row = cur.fetchone()
                        if row:
                            sucursal, cuenta = row
                            cod_contabilidad = str(cuenta).zfill(2)
            except oracledb.DatabaseError as e:
                print(f"❌ Error leyendo dict. auto para '{descripcion_norm}': {e}")

        if sucursal not in ("SUCURSAL_DESCONOCIDA", "SUCURSAL_DESCONOCIDA_AUTO"):
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT CON_ENTIDAD, COD_CONTABILIDAD
                              FROM CON_ENTIDADES
                             WHERE NOMBRE_CON_ENTIDAD = :suc
                            """,
                            { "suc": sucursal }
                        )
                        row2 = cur.fetchone()
                        if row2:
                            con_entidad, cuenta2 = row2
                            if cuenta2 is not None:
                                cod_contabilidad = str(cuenta2).zfill(2)
            except oracledb.DatabaseError as e:
                print(f"⚠️ Error consultando CON_ENTIDADES para '{sucursal}': {e}")
        else:
            # Si la sucursal es el marcador de “desconocida”, devolvemos None
            return None
        
        return {
            "NombreSucursal": sucursal,
            "ConEntidad": con_entidad,
            "CodContabilidad": cod_contabilidad
        }

# Punto de entrada para recibir input manual
if __name__ == "__main__":
    try:
        json_str = input("Ingrese el JSON de la compra: ")
        payload = json.loads(json_str)
        resultado = CuentaSucursalesService.obtener_datos_sucursal(payload)
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")
