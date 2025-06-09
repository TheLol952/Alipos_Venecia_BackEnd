import json

class CuentaFinalService:
    # Mini diccionario de relaciones de cuentas (patrones con 'xx')
    MINI_DICCIONARIO_CUENTAS = [
        {
            "Cuenta_Contable": "4301xx30",  # patrón base
            "Nombre_Cuenta": "Combustibles y Lubricantes",
            "Cuenta_Relacionada": "4301xx41",  # patrón relacionada
            "Nombre_CuentaRelacionada": "Fovial y Cotrans"
        },
        # Agregar más entradas según necesidad
    ]

    @staticmethod
    def generar_cuenta_final(cuenta_base: str | None, cod_contabilidad: str | None) -> tuple[str | None, str | None]:
        """
        Forma la cuenta final a partir de:
            - cuenta_base: string con placeholder 'xx', p.ej. '4301xx11'
            - cod_contabilidad: código a insertar en lugar de 'xx', p.ej. '04'

        Si recibe None en cualquiera de los parámetros, lo notifica y retorna (None, None).

        Luego busca en MINI_DICCIONARIO_CUENTAS una entrada cuyo
        Cuenta_Contable (tras sustituir 'xx') coincida con la cuenta final,
        y si la hay, genera la cuenta relacionada sustituyendo 'xx'.

        Retorna una tupla:
            (cuenta_final, cuenta_relacionada)
            - cuenta_final: cadena resultante o None si no puede generarse
            - cuenta_relacionada: cadena relacionada o None si no hay análoga o en error
        """
        # Validación de entrada
        if cuenta_base is None or cod_contabilidad is None:
            #print(f"⚠️ Parámetros inválidos en generar_cuenta_final: cuenta_base={cuenta_base}, "
                #f"cod_contabilidad={cod_contabilidad}")
            return None, None

        # Si no hay placeholder 'xx', devolvemos la base tal cual
        if 'xx' not in cuenta_base:
            return cuenta_base, None

        # 1. Formar cuenta_final
        cuenta_final = cuenta_base.replace('xx', cod_contabilidad)

        # 2. Buscar cuenta relacionada en mini diccionario
        cuenta_relacionada = None
        for entry in CuentaFinalService.MINI_DICCIONARIO_CUENTAS:
            patron_base = entry['Cuenta_Contable'].replace('xx', cod_contabilidad)
            if patron_base == cuenta_final:
                cuenta_relacionada = entry['Cuenta_Relacionada'].replace('xx', cod_contabilidad)
                break

        return cuenta_final, cuenta_relacionada

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        cuenta_base = input("Ingrese CuentaBase (p.ej. '4301xx11'): ") or None
        cod_contabilidad = input("Ingrese CodContabilidad (p.ej. '04'): ") or None
        resultado = CuentaFinalService.generar_cuenta_final(cuenta_base, cod_contabilidad)
        print(f"CuentaFinal: {resultado[0]}")
        print(f"CuentaRelacionada: {resultado[1]}")
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")
