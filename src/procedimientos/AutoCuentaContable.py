import json

try:
    from CuentaSucursalesService import CuentaSucursalesService
except ImportError:
    from .CuentaSucursalesService import CuentaSucursalesService

try:
    from CuentaBaseService import CuentaBaseService
except ImportError:
    from .CuentaBaseService import CuentaBaseService

try:
    from CuentaFinalService import CuentaFinalService
except ImportError:
    from .CuentaFinalService import CuentaFinalService


def obtenerCuentaContable(data: dict) -> tuple:
    """
    Procesa la cuenta contable a partir del JSON de compra:
    1. Obtiene datos de sucursal.
    2. Valida sucursal; si no válida, devuelve tupla de Nones.
    3. Obtiene cuenta base y datos DTE.
    4. Genera cuenta final y relación.
    5. Devuelve una tupla con:
       (CUENTA_CONTABLE, CUENTA_RELACION, CON_ENTIDAD,
        DTE_TIPO_OPERACION, DTE_CLASIFICACION, DTE_SECTOR, DTE_TIPO_COSTO_GASTO)
    """
    # 1. Servicio de sucursales
    sucursal_info = CuentaSucursalesService.obtener_datos_sucursal(data)
    nombre_sucursal = sucursal_info.get("NombreSucursal")

    # 2. Validar detección de sucursal
    if not nombre_sucursal or "DESCONOCIDA" in nombre_sucursal:
        return ('Null', 'Null', 'Null', 'Null', 'Null', 'Null', 'Null')

    # Extraer campos de sucursal
    con_entidad = sucursal_info.get("ConEntidad")
    cod_contabilidad = sucursal_info.get("CodContabilidad")

    # 3. Servicio de cuenta base
    base_info = CuentaBaseService.obtener_cuenta_base(data)
    cuenta_base = base_info.get("CuentaBase")
    tipo_op      = base_info.get("TipoOperacion")
    clasif       = base_info.get("Clasificacion")
    sector       = base_info.get("Sector")
    tipo_costo   = base_info.get("TipoCostoGasto")

    # 4. Servicio de cuenta final
    final_info = CuentaFinalService.generar_cuenta_final(cuenta_base, cod_contabilidad)
    cuenta_final = final_info.get("CuentaFinal")
    cuenta_rel   = final_info.get("CuentaRelacionada")

    # 5. Retornar tupla de valores puros
    return (
        cuenta_final,
        cuenta_rel,
        con_entidad,
        tipo_op,
        clasif,
        sector,
        tipo_costo
    )


# Prueba manual
if __name__ == "__main__":
    print("🚀 Servicio AutoCuentaContable iniciado...")
    try:
        raw = input("Ingrese el JSON de la compra: ")
        data = json.loads(raw)
        resultado = obtenerCuentaContable(data)
        # Imprimir valores puros
        print(*resultado)
    except Exception as ex:
        # Imprimir Nones si hay error
        print(*(['Null'] * 7))
        print(f"❌ Error en AutoCuentaContable: {ex}")
