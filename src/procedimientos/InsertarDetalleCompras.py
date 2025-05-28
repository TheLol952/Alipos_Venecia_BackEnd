import json
import oracledb
from core.conexion_oracle import get_connection
from FormateoDTE import FormatearControlDTE
from Listar_InsertarProveedores import ListarInsertarProveedores
from Listar_InsertarProductos import ListarInsertarProductos

try:
    import DiccionarioSucursales as ds
except ImportError:
    from . import DiccionarioSucursales as ds

class InsertarDetallesCompras:
    @staticmethod
    def procesar(data: dict, corre_compra: int, cuenta_contable: str) -> list[int]:
        """
        Inserta detalles de compra en CO_DETCOMPRA:
        - Busca PROVEEDOR en TA_PROVEEDORES; si no existe, llama a ListarInsertarProveedores
        - Formatea correlativo DTE (COMPROB) con FormatearControlDTE
        - Determina TIPO: 'CCF' si existe IVA (código 20) en el JSON, o 'FAC' en caso contrario
        - Para cada ítem:
          * Busca PRODUCTO en TA_PRODUCTOS; si no existe, llama a ListarInsertarProductos con ese ítem
          * Inserta detalle en CO_DETCOMPRA con NOMBRE = descripción
        - Devuelve lista de IDs insertados
        """
        inserted_ids: list[int] = []

        # 1) Obtener o insertar proveedor
        nit_norm = data.get("emisor", {}).get("nit", "")
        print(f"🔍 Buscando proveedor para NIT: {nit_norm}")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT PROVEEDOR FROM TA_PROVEEDORES WHERE NIT = :nit",
                    {"nit": nit_norm}
                )
                row = cur.fetchone()
                if row and row[0]:
                    codprov = row[0]
                    print(f"✅ Proveedor encontrado: {codprov}")
                else:
                    print(f"❌ Proveedor no encontrado (NIT={nit_norm}), insertando...")
                    codprov = ListarInsertarProveedores.procesar(data)
                    print(f"✅ Proveedor insertado: {codprov}")

        # 2) Formatear correlativo DTE
        correlativo = FormatearControlDTE.procesar(data)
        print(f"🔢 Correlativo DTE formateado: {correlativo}")

        # 3) Determinar tipo de compra
        codigo_iva = '20'
        tiene_iva = any(codigo_iva in item.get('tributos', []) for item in data.get('cuerpoDocumento', []))
        tipo = 'CCF' if tiene_iva else 'FAC'
        print(f"🔖 Tipo de compra determinado: {tipo}")

        # 4) Procesar cada ítem
        with get_connection() as conn:
            with conn.cursor() as cur:
                for idx, item in enumerate(data.get("cuerpoDocumento", []), start=1):
                    cantidad = item.get("cantidad", 0)
                    preciou = item.get("precioUni", 0)
                    tot = cantidad * preciou
                    desc = item.get("descripcion", "") or ""
                    print(f"\n🛒 Ítem {idx}: '{desc[:30]}...', cant={cantidad}, pu={preciou}, tot={tot}")

                    # 4.1) Obtener o insertar producto
                    cur.execute(
                        "SELECT PRODUCTO FROM TA_PRODUCTOS WHERE UPPER(DESCRIPCION_PRODUCTO) = UPPER(:descripcion)",
                        {"descripcion": desc}
                    )
                    prod = cur.fetchone()
                    if prod and prod[0]:
                        idprod = prod[0]
                        print(f"✅ Producto encontrado ID={idprod}")
                    else:
                        print(f"❌ Producto no encontrado: {desc}, insertando...")
                        # Llamar al método para insertar este solo item
                        single_data = {**data, "cuerpoDocumento": [item]}
                        new_ids = ListarInsertarProductos.procesar(single_data)
                        idprod = int(new_ids[0]) if new_ids else None
                        print(f"✅ Producto insertado ID={idprod}")
                        if not idprod:
                            continue

                    # 4.2) Calcular siguiente ID de detalle
                    cur.execute("SELECT MAX(TO_NUMBER(ID)) FROM CO_DETCOMPRA")
                    max_det = cur.fetchone()[0] or 0
                    next_det = int(max_det) + 1
                    print(f"⚙️ Siguiente ID detalle: {next_det}")

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
                            "tipo": tipo,
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
                    print(f"✅ Detalle insertado ID={next_det}")
                    inserted_ids.append(next_det)
        return inserted_ids
    
# Prueba manual
if __name__ == "__main__":
    print("🚀 Insertar Detalle Compra")
    try:
        data = json.loads(input("Ingrese JSON de compra: "))
        corre = int(input("Ingrese CORRE_COMPRA: "))
        cuenta = input("Ingrese CUENTA_CONTABLE: ")
        ids = InsertarDetallesCompras.procesar(data, corre, cuenta) 
        print(f"IDs insertados: {ids}")       
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")

## 22831

## 41020101