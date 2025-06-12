from src.core.conexion_oracle import get_connection
from src.procedimientos.FormateoDTE import FormatDTE
from src.procedimientos.Listar_InsertarProveedores import proveedores
from src.procedimientos.Listar_InsertarProductos import productos

def InsertDetalleCompra(data: dict, corre_compra: int, cod_tipo: str, cuenta_contable: str) -> list[int]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT CORRE_COMPRA FROM CO_DETCOMPRA WHERE CORRE_COMPRA = :corre_compra",
                {"corre_compra": corre_compra}
            )
            row = cur.fetchone()
            if row:
                inserted_ids = 'Duplicado, se omite...'
                return inserted_ids

    inserted_ids: list[int] = []

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
                codprov = proveedores(data)

    correlativo = FormatDTE(data)

    with get_connection() as conn:
        with conn.cursor() as cur:
            for idx, item in enumerate(data.get("cuerpoDocumento", []), start=1):
                cantidad = item.get("cantidad", 0)
                preciou = item.get("precioUni", 0)
                tot = cantidad * preciou
                desc = item.get("descripcion", "") or ""

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
                    new_ids = productos(single_data)
                    idprod = int(new_ids[0]) if new_ids else None
                    if not idprod:
                        continue

                cur.execute("SELECT MAX(TO_NUMBER(ID)) FROM CO_DETCOMPRA")
                max_det = cur.fetchone()[0] or 0
                next_det = int(max_det) + 1

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
    

