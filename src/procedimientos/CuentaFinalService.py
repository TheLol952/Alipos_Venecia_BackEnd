MINI_DICCIONARIO_CUENTAS = [
    {
        "Cuenta_Contable": "4301xx30",  # patrón base
        "Nombre_Cuenta": "Combustibles y Lubricantes",
        "Cuenta_Relacionada": "4301xx41",  # patrón relacionada
        "Nombre_CuentaRelacionada": "Fovial y Cotrans"
    },
]

def generarCuentaFinal(cuenta_base: str | None, cod_contabilidad: str | None) -> tuple[str | None, str | None]:
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
    for entry in MINI_DICCIONARIO_CUENTAS:
        patron_base = entry['Cuenta_Contable'].replace('xx', cod_contabilidad)
        if patron_base == cuenta_final:
            cuenta_relacionada = entry['Cuenta_Relacionada'].replace('xx', cod_contabilidad)
            break

    return cuenta_final, cuenta_relacionada


