import json
import oracledb
from core.conexion_oracle import get_connection
from datetime import datetime

# Función de normalización reutilizada
try:
    import procedimientos.DiccionarioSucursales as ds
except ImportError:
    from . import DiccionarioSucursales as ds

class ListarInsertarProductos:
    @staticmethod
    def procesar(data: dict) -> list[str]:
        """
        Para cada ítem en cuerpoDocumento:
        - Obtiene numItem, descripcion y precio unitario
        - Busca en TA_PRODUCTOS por NOMBRE_PRODUCTO (case-insensitive exact match)
        - Si existe, agrega su ID (8 dígitos string) a la lista
        - Si no existe, calcula NEXT_ID = MAX(ID)+1, inserta con:
            PRODUCTO, UNIDAD_MEDIDA='00000001', NOMBRE_PRODUCTO,
            DESCRIPCION_PRODUCTO, PRECIO_UNITARIO, USUARIO_CREACION='ALIPOS2025',
            USUARIO_CREACION_FECHA=SYSDATE,
            CODIGO_BARRAS=NULL, COD_PRODUC=NULL, COLUMNA=:columna,
            FORMULA=NULL, MODIFICADOR=NULL, TIPO_CREACION=NULL
            y agrega NEXT_ID formateado a lista
        Retorna lista de strings con los IDs de productos procesados
        """
        items = data.get("cuerpoDocumento", [])
        result_ids: list[str] = []
        current_date = datetime.now().strftime('%d-%b-%y').upper()  # e.g. '05-APR-25'
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for idx, item in enumerate(items, start=1):
                        num_item = item.get("numItem", idx)
                        desc = item.get("descripcion", "") or ""
                        precio = item.get("precioUni") or item.get("precio_unitario") or 0
                        # 1) Buscar producto existente
                        cur.execute(
                            "SELECT PRODUCTO"
                            " FROM TA_PRODUCTOS"
                            " WHERE UPPER(NOMBRE_PRODUCTO) = UPPER(:nombre)",
                            {"nombre": desc}
                        )
                        row = cur.fetchone()
                        if row and row[0] is not None:
                            prod_code = str(row[0]).strip().zfill(8)
                            result_ids.append(prod_code)
                        else:
                            # 2) Calcular siguiente ID
                            cur.execute("SELECT MAX(TO_NUMBER(PRODUCTO)) FROM TA_PRODUCTOS")
                            max_val = cur.fetchone()[0] or 0
                            next_id = int(max_val) + 1
                            code_str = str(next_id).zfill(8)
                            # 3) Insertar nuevo producto
                            cur.execute(
                                "INSERT INTO TA_PRODUCTOS ("
                                "PRODUCTO, UNIDAD_MEDIDA, NOMBRE_PRODUCTO, DESCRIPCION_PRODUCTO, PRECIO_UNITARIO, "
                                "USUARIO_CREACION, USUARIO_CREACION_FECHA, CODIGO_BARRAS, COD_PRODUC, COLUMNA, FORMULA, MODIFICADOR, TIPO_CREACION)"
                                " VALUES (:prod, '00000001', :nombre, :descripcion, :precio, 'ALIPOS2025', SYSDATE, :prod, :prod, :columna, 1, 0, 'COMPRAS')",
                                {
                                    "prod": code_str,
                                    "nombre": desc,
                                    "descripcion": desc,
                                    "precio": precio,
                                    "columna": num_item
                                }
                            )
                            conn.commit()
                            result_ids.append(code_str)
        except Exception as e:
            return []

        return result_ids

# Prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        resultado = ListarInsertarProductos.procesar(data)
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")