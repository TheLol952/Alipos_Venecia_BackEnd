import json
import oracledb
from core.conexion_oracle import get_connection

try:
    import DiccionarioSucursales as ds
except ImportError:
    from . import DiccionarioSucursales as ds

class CuentaBaseService:
    @staticmethod
    def obtener_cuenta_base(data: dict) -> dict:
        """
        Dado el JSON de compra, obtiene:
            - CuentaBase (formato base de CUENTA_CONTABLE: p.ej. 4301xx11)
            - TipoOperacion
            - Clasificacion
            - Sector
            - TipoCostoGasto

        Lógica:
        1. Extraer descripcionProducto y nitEmpresa
        2. Si solo hay un producto y existe en DICCIONARIO_COMPRAS_AUTO (por PRODUCTO), usar esa fila
        3. Si no, buscar por NIT en la misma tabla
        """
        # 1. Extraer datos del JSON
        lineas = data.get("cuerpoDocumento", [])
        descripcion_producto = None
        if len(lineas) == 1:
            descripcion_producto = lineas[0].get("descripcion", "") or ""
        nit_raw = data.get("emisor", {}).get("nit", "") or ""

        # 2. Normalizar
        descripcion_norm = ds.normalize(descripcion_producto) if descripcion_producto else None
        nit_norm = ds.normalize_nit(nit_raw)

        # Campos resultantes
        cuenta_base = None
        tipo_operacion = None
        clasificacion = None
        sector = None
        tipo_costo_gasto = None

        # 3. Intento por producto si hay uno solo
        if descripcion_norm:
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT NOMBRE_CUENTA, CUENTA_CONTABLE, TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO"
                            " FROM DICCIONARIO_COMPRAS_AUTO"
                            " WHERE PRODUCTO = :prod_norm",
                            [descripcion_norm]
                        )
                        fila = cur.fetchone()
                        if fila:
                            _, cuenta_cont, tipo_operacion, clasificacion, sector, tipo_costo_gasto = fila
                            # Asegurar que sea string para slicing
                            cuenta_str = str(cuenta_cont)
                            # Formatear cuenta base: p.ej. 43010411 -> 4301xx11
                            if len(cuenta_str) >= 6:
                                cuenta_base = f"{cuenta_str[:4]}xx{cuenta_str[-2:]}"
            except Exception as e:
                print(f"❌ Error buscando por PRODUCTO '{descripcion_norm}': {e}")

        # 4. Fallback por NIT si no obtuvo con PRODUCTO
        if not cuenta_base:
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT NOMBRE_CUENTA, CUENTA_CONTABLE, TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO"
                            " FROM DICCIONARIO_COMPRAS_AUTO"
                            " WHERE NIT = :nit_norm",
                            [nit_norm]
                        )
                        fila = cur.fetchone()
                        if fila:
                            _, cuenta_cont, tipo_operacion, clasificacion, sector, tipo_costo_gasto = fila
                            cuenta_str = str(cuenta_cont)
                            if len(cuenta_str) >= 6:
                                cuenta_base = f"{cuenta_str[:4]}xx{cuenta_str[-2:]}"
            except Exception as e:
                print(f"❌ Error buscando por NIT '{nit_norm}': {e}")

        # 5. Retornar estructura
        return {
            "CuentaBase": cuenta_base,
            "TipoOperacion": tipo_operacion,
            "Clasificacion": clasificacion,
            "Sector": sector,
            "TipoCostoGasto": tipo_costo_gasto
        }

# Punto de entrada para prueba manual
if __name__ == "__main__":
    print("🚀 Servicio CuentaBase iniciado...")
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        resultado = CuentaBaseService.obtener_cuenta_base(data)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")
