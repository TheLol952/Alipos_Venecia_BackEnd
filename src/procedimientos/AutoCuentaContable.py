import sys
from src.procedimientos.CuentaSucursalesService import obtenerDatosSucursal
from src.procedimientos.CuentaBaseService import obtenerCuentaBase
from src.procedimientos.CuentaFinalService import generarCuentaFinal

def obtenerCuentaContable(data: dict) -> tuple:
    try:
        sucursal_info = obtenerDatosSucursal(data)
        if not sucursal_info:
            print("⚠️ No se obtuvieron datos de sucursal")
            
        (sucursal, cuenta, cod_contabilidad, con_entidad) = sucursal_info

        if isinstance(sucursal, str) and "DESCONOCIDA" in sucursal.upper():
            print("⚡ Sucursal desconocida detectada")

        # Obtención de cuenta base
        base_info = obtenerCuentaBase(data, cuenta)
        if not base_info:
            print("⚠️ No se obtuvieron datos de cuenta base")
        
        (cuenta_base, tipo_operacion, clasificacion, sector, tipo_costo_gasto) = base_info

        # Validación de código de contabilidad
        if cod_contabilidad is None:
            cod_contabilidad = '0'

        if con_entidad == '':
            con_entidad = None

        # Generar cuenta final y relacionada
        cuenta_final = None
        cuenta_rel = None
        final_info = generarCuentaFinal(cuenta_base, cod_contabilidad)
        # Ahora recibe tupla (cuenta_final, cuenta_relacionada)
        if isinstance(final_info, tuple) and len(final_info) == 2:
            cuenta_final, cuenta_rel = final_info
        else:
            print("⚠️ CuentaFinalService no devolvió tupla válida")

        return (
            cuenta_final,
            cuenta_rel,
            con_entidad,
            tipo_operacion,
            clasificacion,
            sector,
            tipo_costo_gasto
        )

    except Exception as ex:
        print(f"\n❌ ERROR CRÍTICO: {type(ex).__name__}: {ex}", file=sys.stderr)

