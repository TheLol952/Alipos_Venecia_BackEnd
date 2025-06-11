import json
from procedimientos.EsCombustible import EsCombustible

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        es, fov, cot = EsCombustible(data)
        if es == 0:
            es = 'NO'
        else:
            es = 'SI'

        print(f"RESPUESTA TEST COMBUSTIBLE: Es Combustible?: {es}, Fovial: {fov}, Cotrans: {cot}")
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")