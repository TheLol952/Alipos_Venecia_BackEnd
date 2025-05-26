import json

# Importar servicios previos
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


def main():
    """
    Punto de entrada para proceso automático de cuenta contable.

    1. Lee el JSON de compra desde input.
    2. Obtiene datos de sucursal (CuentaSucursalesService).
    3. Si no se detecta sucursal válida, retorna todos los campos a null.
    4. De lo contrario, obtiene:
       - CuentaBase y datos DTE (CuentaBaseService).
       - CuentaFinal y CuentaRelacionada (CuentaFinalService).
    5. Imprime un JSON con los campos:
       CUENTA_CONTABLE, CUENTA_RELACION, CON_ENTIDAD,
       DTE_TIPO_OPERACION, DTE_CLASIFICACION, DTE_SECTOR, DTE_TIPO_COSTO_GASTO
    """
    try:
        # 1. Leer JSON de la compra
        raw = input("Ingrese el JSON de la compra: ")
        data = json.loads(raw)

        # 2. Servicio de sucursales
        sucursal_info = CuentaSucursalesService.obtener_datos_sucursal(data)
        nombre_sucursal = sucursal_info.get("NombreSucursal")

        # 3. Validar detección de sucursal
        if not nombre_sucursal or "DESCONOCIDA" in nombre_sucursal:
            # No se detectó sucursal; devolver todo null
            result = {
                "CUENTA_CONTABLE": None,
                "CUENTA_RELACION": None,
                "CON_ENTIDAD": None,
                "DTE_TIPO_OPERACION": None,
                "DTE_CLASIFICACION": None,
                "DTE_SECTOR": None,
                "DTE_TIPO_COSTO_GASTO": None
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        # Extraer con_entidad y cod_contabilidad
        con_entidad = sucursal_info.get("ConEntidad")
        cod_contabilidad = sucursal_info.get("CodContabilidad")

        # 4. Servicio de cuenta base
        base_info = CuentaBaseService.obtener_cuenta_base(data)
        cuenta_base = base_info.get("CuentaBase")
        tipo_op = base_info.get("TipoOperacion")
        clasif = base_info.get("Clasificacion")
        sector = base_info.get("Sector")
        tipo_costo = base_info.get("TipoCostoGasto")

        # 5. Servicio de cuenta final
        final_info = CuentaFinalService.generar_cuenta_final(cuenta_base, cod_contabilidad)
        cuenta_final = final_info.get("CuentaFinal")
        cuenta_rel = final_info.get("CuentaRelacionada")

        # 6. Armar resultado
        result = {
            "CUENTA_CONTABLE": cuenta_final,
            "CUENTA_RELACION": cuenta_rel,
            "CON_ENTIDAD": con_entidad,
            "DTE_TIPO_OPERACION": tipo_op,
            "DTE_CLASIFICACION": clasif,
            "DTE_SECTOR": sector,
            "DTE_TIPO_COSTO_GASTO": tipo_costo
        }

        # 7. Imprimir JSON final
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        # En caso de error, todos null
        error_result = {
            "CUENTA_CONTABLE": None,
            "CUENTA_RELACION": None,
            "CON_ENTIDAD": None,
            "DTE_TIPO_OPERACION": None,
            "DTE_CLASIFICACION": None,
            "DTE_SECTOR": None,
            "DTE_TIPO_COSTO_GASTO": None
        }
        print(json.dumps(error_result, indent=2, ensure_ascii=False))
        print(f"❌ Error en AutoCuentaContable: {e}")


if __name__ == "__main__":
    main()
