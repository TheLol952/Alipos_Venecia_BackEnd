from src.core.conexion_oracle import get_connection
import src.procedimientos.DiccionarioSucursales as ds

def proveedores(data: dict) -> str:
    emisor = data.get("emisor", {})
    nit_norm = ds.normalize_nit(emisor.get("nit", "") or "")
    direccion_raw = emisor.get("direccion", {}).get("complemento", "") or ""

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Intentar obtener proveedor existente
                cur.execute(
                    "SELECT PROVEEDOR"
                    " FROM TA_PROVEEDORES"
                    " WHERE NIT = :nit AND DIRECCION = :direccion",
                    {"nit": nit_norm, "direccion": direccion_raw}
                )
                row = cur.fetchone()
                if row and row[0] is not None:
                    código_existente = str(row[0]).strip().zfill(8)
                    return código_existente
                # No existe: calcular siguiente código
                cur.execute("SELECT MAX(TO_NUMBER(PROVEEDOR)) FROM TA_PROVEEDORES")
                max_val = cur.fetchone()[0] or 0
                next_val = int(max_val) + 1
                codigo_nuevo = str(next_val).zfill(8)
                # Insertar nuevo proveedor
                cur.execute(
                    "INSERT INTO TA_PROVEEDORES ("
                    "PROVEEDOR, NOMBRE_PROVEEDOR, DIRECCION, ESTATUS, PROVEEDOR_INTERNO, CODIGO_PROVEEDOR_INTERNO, NIT)"
                    " VALUES (:codigo, :nombre, :direccion, '1', '1', :codigo, :nit)",
                    {
                        "codigo": codigo_nuevo,
                        "nombre": emisor.get("nombre", ""),
                        "direccion": direccion_raw,
                        "nit": nit_norm
                    }
                )
                conn.commit()
                return codigo_nuevo
    except Exception as e:
        print(f"⚠️ Error al buscar/crear proveedor: {e}")
        return None
        


