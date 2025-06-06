import json
import oracledb
from core.conexion_oracle import get_connection
from procedimientos.FormateoDTE import FormatearControlDTE
from procedimientos.Listar_InsertarProveedores import ListarInsertarProveedores
from procedimientos.Listar_InsertarProductos import ListarInsertarProductos

try:
    import procedimientos.DiccionarioSucursales as ds
except ImportError:
    from . import DiccionarioSucursales as ds

class InsertarDetallesCompras:
    @staticmethod
    def procesar(data: dict, corre_compra: int, cod_tipo: str, cuenta_contable: str) -> list[int]:
        """
        Inserta detalles de compra en CO_DETCOMPRA:
        - Busca PROVEEDOR en TA_PROVEEDORES; si no existe, llama a ListarInsertarProveedores
        - Formatea correlativo DTE (COMPROB) con FormatearControlDTE
        - Para cada ítem:
          * Busca PRODUCTO en TA_PRODUCTOS; si no existe, llama a ListarInsertarProductos con ese ítem
          * Inserta detalle en CO_DETCOMPRA con NOMBRE = descripción
        - Devuelve lista de IDs insertados
        """
        inserted_ids: list[int] = []

        # 1) Obtener o insertar proveedor
        nit_norm = data.get("emisor", {}).get("nit", "")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT PROVEEDOR FROM TA_PROVEEDORES WHERE NIT = :nit",
                    {"nit": nit_norm}
                )
                row = cur.fetchone()
                if row and row[0]:
                    codprov = row[0]
                else:
                    codprov = ListarInsertarProveedores.procesar(data)

        # 2) Formatear correlativo DTE
        correlativo = FormatearControlDTE.procesar(data)

        # 4) Procesar cada ítem
        with get_connection() as conn:
            with conn.cursor() as cur:
                for idx, item in enumerate(data.get("cuerpoDocumento", []), start=1):
                    cantidad = item.get("cantidad", 0)
                    preciou = item.get("precioUni", 0)
                    tot = cantidad * preciou
                    desc = item.get("descripcion", "") or ""

                    # 4.1) Obtener o insertar producto
                    cur.execute(
                        "SELECT PRODUCTO FROM TA_PRODUCTOS WHERE UPPER(DESCRIPCION_PRODUCTO) = UPPER(:descripcion)",
                        {"descripcion": desc}
                    )
                    prod = cur.fetchone()
                    if prod and prod[0]:
                        idprod = prod[0]
                    else:
                        # Llamar al método para insertar este solo item
                        single_data = {**data, "cuerpoDocumento": [item]}
                        new_ids = ListarInsertarProductos.procesar(single_data)
                        idprod = int(new_ids[0]) if new_ids else None
                        if not idprod:
                            continue

                    # 4.2) Calcular siguiente ID de detalle
                    cur.execute("SELECT MAX(TO_NUMBER(ID)) FROM CO_DETCOMPRA")
                    max_det = cur.fetchone()[0] or 0
                    next_det = int(max_det) + 1

                    # 4.3) Insertar detalle
                    cur.execute(
                        "INSERT INTO CO_DETCOMPRA ("
                        "ID, CODEMP, CODPROV, TIPO, COMPROB, CANTIDAD, NOMBRE, PRECIOU, TOT,"
                        " IDPRODUCTO, CORRE_COMPRA, PARA_INVENTARIO, CUENTA_CONTABLE, EXCENTA)"
                        " VALUES ("
                        ":detid, 'ALIPOS2025', :codprov, :tipo, :comprob, :cantidad, :nombre, :preciou, :tot,"
                        " :idprod, :corre, '0', :cuenta, 0)",
                        {
                            "detid": next_det,
                            "codprov": codprov,
                            "tipo": cod_tipo,
                            "comprob": correlativo,
                            "cantidad": cantidad,
                            "nombre": desc,
                            "preciou": preciou,
                            "tot": tot,
                            "idprod": idprod,
                            "corre": corre_compra,
                            "cuenta": cuenta_contable
                        }
                    )
                    conn.commit()
                    inserted_ids.append(next_det)
        return inserted_ids
    
# Prueba manual
if __name__ == "__main__":
    try:
        data = json.loads(input("Ingrese JSON de compra: "))
        corre = 22848
        codtipo = 'CCF'
        cuenta = 43011330
        ids = InsertarDetallesCompras.procesar(data, corre,  codtipo, cuenta) 
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")

## 22831

## 41020101