import json
import sys
from typing import Optional, Dict, Any

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
    Versión mejorada con manejo robusto de errores y validaciones
    """
    
    try:
        sucursal_info = CuentaSucursalesService.obtener_datos_sucursal(data)
        if not sucursal_info:
            print("⚠️ No se obtuvieron datos de sucursal")
            
        nombre_sucursal = sucursal_info.get("NombreSucursal")

        # Validación de sucursal desconocida
        if nombre_sucursal is None:
            print("⚡ Sucursal es None, usando valores por defecto")
            
        if isinstance(nombre_sucursal, str) and "DESCONOCIDA" in nombre_sucursal.upper():
            print("⚡ Sucursal desconocida detectada")

        # Procesamiento para sucursal conocida
        con_entidad = sucursal_info.get("ConEntidad")
        cod_contabilidad = sucursal_info.get("CodContabilidad")

        # Obtención de cuenta base
        base_info = CuentaBaseService.obtener_cuenta_base(data)
        if not base_info:
            print("⚠️ No se obtuvieron datos de cuenta base")
        
        cuenta_base = base_info.get("CuentaBase")
        if cuenta_base is None:
            cuenta_base = "00000000"  # Valor por defecto si no se obtiene

        # Validación de código de contabilidad
        if not cod_contabilidad:
            print("⚠️ CodContabilidad es inválido")

        # Generación de cuenta final
        final_info = CuentaFinalService.generar_cuenta_final(cuenta_base, cod_contabilidad)
        if not final_info:
            print("⚠️ No se generó la cuenta final")
        
        cuenta_final = final_info.get("CuentaFinal")
        cuenta_rel = final_info.get("CuentaRelacionada")

        # Obtención de datos adicionales
        tipo_op = base_info.get("TipoOperacion")
        clasif = base_info.get("Clasificacion")
        sector = base_info.get("Sector")
        tipo_costo = base_info.get("TipoCostoGasto")

        return (
            cuenta_final,
            cuenta_rel,
            con_entidad,
            tipo_op,
            clasif,
            sector,
            tipo_costo
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