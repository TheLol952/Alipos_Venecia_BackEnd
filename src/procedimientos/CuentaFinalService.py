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
    def generar_cuenta_final(cuenta_base: str, cod_contabilidad: str) -> dict:
        """
        Forma la cuenta final a partir de:
            - cuenta_base: string con placeholder 'xx', p.ej. '4301xx11'
            - cod_contabilidad: código a insertar en lugar de 'xx', p.ej. '04'

        Luego busca en MINI_DICCIONARIO_CUENTAS una entrada cuyo
        Cuenta_Contable (tras sustituir 'xx') coincida con la cuenta final,
        y si la hay, genera la cuenta relacionada sustituyendo 'xx'.

        Retorna:
            - CuentaFinal
            - CuentaRelacionada (o None si no hay)
        """
        # Validación básica
        if 'xx' not in cuenta_base:
            return {
                'CuentaFinal': cuenta_base,
                'CuentaRelacionada': None
            }

        # 1. Formar CuentaFinal
        cuenta_final = cuenta_base.replace('xx', cod_contabilidad)

        # 2. Buscar cuenta relacionada en mini diccionario
        cuenta_relacionada = None
        for entry in CuentaFinalService.MINI_DICCIONARIO_CUENTAS:
            patron_base = entry['Cuenta_Contable'].replace('xx', cod_contabilidad)
            if patron_base == cuenta_final:
                # Coincidencia: construir la cuenta relacionada
                cuenta_relacionada = entry['Cuenta_Relacionada'].replace('xx', cod_contabilidad)
                break

        return {
            'CuentaFinal': cuenta_final,
            'CuentaRelacionada': cuenta_relacionada
        }

# Punto de entrada para prueba manual
def main():
    try:
        cuenta_base = input("Ingrese CuentaBase (p.ej. '4301xx11'): ") or ""
        cod_contabilidad = input("Ingrese CodContabilidad (p.ej. '04'): ") or ""
        resultado = CuentaFinalService.generar_cuenta_final(cuenta_base, cod_contabilidad)
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")

if __name__ == "__main__":
    main()
