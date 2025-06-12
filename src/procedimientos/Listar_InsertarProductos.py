from src.core.conexion_oracle import get_connection

def productos(data: dict) -> list[str]:
    items = data.get("cuerpoDocumento", [])
    result_ids: list[str] = []
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