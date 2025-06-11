import json
from procedimientos.CuentaBaseService import obtenerCuentaBase

# Prueba manual
if __name__ == "__main__":
    entrada = input("Ingrese el JSON de la compra: ")
    data = json.loads(entrada)
    # Ejemplo de llamada: requiere sucursal y cuenta existentes
    cuentaBase = obtenerCuentaBase(data, 43011040)

    print(f"RESPUESTA TEST CUENTA BASE: {cuentaBase}")