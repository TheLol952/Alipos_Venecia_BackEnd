import json
import oracledb
from core.conexion_oracle import get_connection

# Importar la función para obtener sucursal
try:
    from DiccionarioSucursales import ObtenerSucursal, normalize, normalize_nit
except ImportError:
    from .DiccionarioSucursales import ObtenerSucursal, normalize, normalize_nit

class CuentaBaseService:
    @staticmethod
    def obtener_cuenta_base(data: dict) -> dict:
        """
        Dado el JSON de compra, obtiene:
            - Sucursal identificada
            - CuentaBase (formato base de CUENTA_CONTABLE: p.ej. 4301xx11)
            - TipoOperacion
            - Clasificacion
            - Sector
            - TipoCostoGasto

        Lógica:
        1. Obtener sucursal con ObtenerSucursal
        2. Extraer descripcionProducto y nitEmpresa
        3. Si solo hay un producto y existe en DICCIONARIO_COMPRAS_AUTO (por PRODUCTO), usar esa fila
        4. Si no, buscar por NIT en la misma tabla
        """
        # 1. Obtener sucursal
        try:
            sucursal = ObtenerSucursal(data)
        except Exception as e:
            print(f"❌ Error obteniendo sucursal: {e}")
            sucursal = None

        # 2. Extraer datos del JSON
        lineas = data.get("cuerpoDocumento", [])
        descripcion_producto = None
        if len(lineas) == 1:
            descripcion_producto = lineas[0].get("descripcion", "") or ""
        nit_raw = data.get("emisor", {}).get("nit", "") or ""

        # 3. Normalizar
        descripcion_norm = normalize(descripcion_producto) if descripcion_producto else None
        nit_norm = normalize_nit(nit_raw)

        # Campos resultantes
        cuenta_base = None
        tipo_operacion = None
        clasificacion = None
        sector = None
        tipo_costo_gasto = None

        # 4. Intento por producto si hay uno solo
        if descripcion_norm:
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT CUENTA_CONTABLE, TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO"
                            " FROM DICCIONARIO_COMPRAS_AUTO"
                            " WHERE PRODUCTO = :despricion_norm",
                            [descripcion_norm]
                        )
                        fila = cur.fetchone()
                        if fila:
                            cuenta_cont, tipo_operacion, clasificacion, sector, tipo_costo_gasto = fila
                            cuenta_str = str(cuenta_cont)
                            if len(cuenta_str) >= 6:
                                cuenta_base = f"{cuenta_str[:4]}xx{cuenta_str[-2:]}"
            except Exception as e:
                print(f"❌ Error buscando por PRODUCTO '{descripcion_norm}': {e}")

        # 5. Fallback por NIT si no obtuvo con PRODUCTO
        if not cuenta_base:
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT CUENTA_CONTABLE, TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO"
                            " FROM DICCIONARIO_COMPRAS_AUTO"
                            " WHERE NIT = :nit_norm",
                            [nit_norm]
                        )
                        fila = cur.fetchone()
                        if fila:
                            cuenta_cont, tipo_operacion, clasificacion, sector, tipo_costo_gasto = fila
                            cuenta_str = str(cuenta_cont)
                            if len(cuenta_str) >= 6:
                                cuenta_base = f"{cuenta_str[:4]}xx{cuenta_str[-2:]}"
            except Exception as e:
                print(f"❌ Error buscando por NIT '{nit_norm}': {e}")

        # 6. Retornar estructura con sucursal incluida
        return {
            "Sucursal": sucursal,
            "CuentaBase": cuenta_base,
            "TipoOperacion": tipo_operacion,
            "Clasificacion": clasificacion,
            "Sector": sector,
            "TipoCostoGasto": tipo_costo_gasto
        }

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        resultado = CuentaBaseService.obtener_cuenta_base(data)
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")
