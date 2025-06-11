import json
from procedimientos.CuentaSucursalesService import obtenerDatosSucursal

# Prueba manual
if __name__ == "__main__":
    raw = input("Ingrese el JSON de la compra: ")
    data = json.loads(raw)
    cuentaSuc = obtenerDatosSucursal(data)
    
    print(f"RESPUESTA TEST CUENTA SUCURSALES: {cuentaSuc}")