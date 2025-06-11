from procedimientos.CuentaFinalService import generarCuentaFinal

if __name__ == "__main__":
    try:
        cuenta_base = '4301xx40'
        cod_contabilidad = '01'
        cuentaFinal = generarCuentaFinal(cuenta_base, cod_contabilidad)

        print(f"CuentaFinal: {cuentaFinal[0]}")
        print(f"CuentaRelacionada: {cuentaFinal[1]}")
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")