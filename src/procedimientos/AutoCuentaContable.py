import json
import sys
from typing import Optional, Dict, Any

try:
    from procedimientos.CuentaSucursalesService import CuentaSucursalesService
except ImportError:
    from procedimientos.CuentaSucursalesService import CuentaSucursalesService

try:
    from procedimientos.CuentaBaseService import CuentaBaseService
except ImportError:
    from procedimientos.CuentaBaseService import CuentaBaseService

try:
    from procedimientos.CuentaFinalService import CuentaFinalService
except ImportError:
    from procedimientos.CuentaFinalService import CuentaFinalService


def obtenerCuentaContable(data: dict) -> tuple:
    """
    Versión mejorada con manejo robusto de errores y validaciones
    """
    
    try:
        sucursal_info = CuentaSucursalesService.obtener_datos_sucursal(data)
        if not sucursal_info:
            print("⚠️ No se obtuvieron datos de sucursal")
            
        (sucursal, cuenta, cod_contabilidad, con_entidad) = sucursal_info

        if isinstance(sucursal, str) and "DESCONOCIDA" in sucursal.upper():
            print("⚡ Sucursal desconocida detectada")

        # Obtención de cuenta base
        base_info = CuentaBaseService.obtener_cuenta_base(data, cuenta)
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
        final_info = CuentaFinalService.generar_cuenta_final(cuenta_base, cod_contabilidad)
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

if __name__ == "__main__":
    try:
        raw = input("Ingrese el JSON de la compra: ")
        data = json.loads(raw)
        resultado = obtenerCuentaContable(data)
        
        print("\n📊 Resultado final:")
        nombres_campos = [
            "CUENTA_CONTABLE",
            "CUENTA_RELACION",
            "CON_ENTIDAD",
            "TIPO_OPERACION",
            "CLASIFICACION",
            "SECTOR",
            "TIPO_COSTO"
        ]
        
        for nombre, valor in zip(nombres_campos, resultado):
            print(f"{nombre}: {valor}")
            
    except json.JSONDecodeError:
        print("\n❌ Error: El texto ingresado no es un JSON válido")
    except Exception as ex:
        print(f"\n❌ Error inesperado: {ex}")