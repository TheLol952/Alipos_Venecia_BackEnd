import oracledb
from src.core.conexion_oracle import get_connection
from src.procedimientos.DiccionarioSucursales import normalize_nit

def obtenerDatosSucursal(data: dict) -> dict:
    # 1) Extraer y normalizar NIT
    nit_raw = data.get("emisor", {}).get("nit", "") or ""
    nit = normalize_nit(nit_raw)
    sucursal = None
    cuenta = None
    cod_contabilidad = None    
    con_entidad = None

    # 2) Extraer la dirección directamente del JSON (sin normalizar)
    raw_direccion = data.get("emisor", {}) \
                        .get("direccion", {}) \
                        .get("complemento", "") or ""

    # 3) Intento directo usando la dirección tal cual viene
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT SUCURSAL, CUENTA_CONTABLE
                        FROM DICCIONARIO_COMPRAS_AUTO
                    WHERE NIT       = :nit
                        AND DIRECCION = :direccion
                """, {
                    "nit": nit,
                    "direccion": raw_direccion
                })
                row = cur.fetchone()
                if row:
                    sucursal, cuenta = row
    except oracledb.DatabaseError as e:
        print(f"⚠️ Error leyendo diccionario auto: {e}")

    # 4) Obtener el codigo contable
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT CON_ENTIDAD, COD_CONTABILIDAD
                    FROM CON_ENTIDADES
                    WHERE NOMBRE_CON_ENTIDAD = :sucursal
                """, {
                    "sucursal": sucursal,
                })
                row = cur.fetchone()
                if row:
                    con_entidad, cod_conta, = row
                    if cod_conta is not None:
                        cod_contabilidad = str(cod_conta).zfill(2)
    except oracledb.DatabaseError as e:
        print("⚠️ Error al consultar COD_CONTABILIDAD:", e)
                
    return sucursal, cuenta, cod_contabilidad, con_entidad


