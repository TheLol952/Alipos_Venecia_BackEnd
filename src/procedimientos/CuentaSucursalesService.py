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
        """
        Dado el JSON de compra, identifica la sucursal y obtiene los campos
        ConEntidad y CodContabilidad, ya sea de la tabla CON_ENTIDADES
        o del diccionario automático (DICCIONARIO_COMPRAS_AUTO).

        Retorna un diccionario con:
            - NombreSucursal
            - ConEntidad
            - CodContabilidad
        """
        # 1. Extraer descripción y normalizar
        descripcion = data.get("emisor", {}).get("direccion", {}).get("complemento", "") or ""
        descripcion_norm = ds.normalize(descripcion)

        # 2. Normalizar NIT
        nit_raw = data.get("emisor", {}).get("nit", "") or ""
        nit = ds.normalize_nit(nit_raw)

        # 3. Intento de identificación principal
        dicc = ds.cargar_diccionario_sucursales()
        sucursal = ds.identificar_sucursal(descripcion, dicc)

        # 4. Si no se encuentra, se usa el diccionario automático,
        auto_detectado = False
        if sucursal == "SUCURSAL_DESCONOCIDA":
            sucursal_auto = ds.identificar_sucursal_auto(descripcion, dicc)
            if sucursal_auto != "SUCURSAL_DESCONOCIDA_AUTO":
                sucursal = sucursal_auto
                auto_detectado = True

        # 5. Variables de salida
        con_entidad = None
        cod_contabilidad = None

        # 6. Si fue detectada vía diccionario automático,
        #    obtengo directamente su info contable desde esa tabla
        if auto_detectado:
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT SUCURSAL, CON_ENTIDAD, COD_CONTABILIDAD"
                            " FROM DICCIONARIO_COMPRAS_AUTO"
                            " WHERE DIRECCION = :dir_norm"
                            "   AND NIT = :nit_norm",
                            dir_norm=descripcion_norm,
                            nit_norm=nit
                        )
                        row = cur.fetchone()
                        if row:
                            sucursal, con_entidad, cod_contabilidad = row
            except Exception as e:
                print(f"❌ Error obteniendo datos automáticos para '{descripcion_norm}': {e}")
        else:
            # 7. Si no fue automático, consulto en CON_ENTIDADES
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT CON_ENTIDAD, COD_CONTABILIDAD"
                            " FROM CON_ENTIDADES"
                            " WHERE NOMBRE_CON_ENTIDAD = :nombre",
                            [sucursal]
                        )
                        row = cur.fetchone()
                        if row:
                            con_entidad, cod_contabilidad = row
            except Exception as e:
                print(f"❌ Error consultando CON_ENTIDADES para '{sucursal}': {e}")

        # 8. Formatear CodContabilidad a dos dígitos (1->'01', etc.)
        if cod_contabilidad is not None:
            cod_contabilidad = str(cod_contabilidad).zfill(2)

        # 9. Devolver resultado
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
