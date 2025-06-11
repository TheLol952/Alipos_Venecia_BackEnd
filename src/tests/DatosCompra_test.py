import json
from procedimientos.ObtenerDatosCompra import ObtenerDatosCompra

if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        datosCompra = ObtenerDatosCompra(data)

        print(f"RESPUESTA TEST DATOS COMPRA: {datosCompra}")
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")