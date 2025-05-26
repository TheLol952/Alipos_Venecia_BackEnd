import json
import oracledb
from core.conexion_oracle import get_connection

try:
    import DiccionarioSucursales as ds
except ImportError:
    from . import DiccionarioSucursales as ds

class ListarInsertarProveedores:
    @staticmethod
    def procesar(data: dict) -> str:
        """
        Busca un proveedor en TA_PROVEEDORES por NIT y DIRECCION.
        Si existe, devuelve su CODIGO_PROVEEDOR;
        si no, calcula el siguiente código (MAX+1), lo inserta y devuelve el nuevo código.

        Retorna:
            - String con el CodigoProveedor (8 dígitos)"""
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
                        return str(row[0]).strip().zfill(8)
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
        except Exception:
            # En caso de error, devolver None o cadena vacía
            return None

# Punto de entrada para prueba manual
if __name__ == "__main__":
    print("🚀 Listar/Insertar Proveedores iniciado...")
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        resultado = ListarInsertarProveedores.procesar(data)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")
