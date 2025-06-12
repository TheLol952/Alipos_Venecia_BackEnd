from src.core.conexion_oracle import get_connection
from src.procedimientos.DiccionarioSucursales import normalize_nit

def obtenerCuentaBase(data: dict, cuenta: str) -> tuple:
    # 1) Extraer y normalizar NIT
    nit_raw = data.get("emisor", {}).get("nit", "") or ""
    nit_norm = normalize_nit(nit_raw)

    # 2) Extraer dirección tal cual del JSON
    direccion = data.get("emisor", {}) \
                    .get("direccion", {}) \
                    .get("complemento", "") or ""

    # Inicializar resultados
    cuenta_base = None
    tipo_operacion = None
    clasificacion = None
    sector = None
    tipo_costo_gasto = None

    # 3) Consultar el diccionario automático
    if cuenta:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT TIPO_OPERACION, CLASIFICACION, SECTOR, TIPO_COSTO_GASTO
                            FROM DICCIONARIO_COMPRAS_AUTO
                        WHERE NIT = :nit
                            AND DIRECCION = :direccion
                        """,
                        [nit_norm, direccion]
                    )
                    fila = cur.fetchone()
                    if fila:
                        tipo_operacion, clasificacion, sector, tipo_costo_gasto = fila
                        # Construir cuenta_base a partir de la cadena 'cuenta'
                        cuenta_str = str(cuenta)
                        if len(cuenta_str) >= 6:
                            cuenta_base = f"{cuenta_str[:4]}xx{cuenta_str[-2:]}"
        except Exception as e:
            print(f"❌ Error buscando por NIT y Direccion '{nit_raw + direccion}': {e}")

    # 4) Mostrar cuenta_base y devolver tupla
    return (
        cuenta_base,
        tipo_operacion,
        clasificacion,
        sector,
        tipo_costo_gasto
    )

