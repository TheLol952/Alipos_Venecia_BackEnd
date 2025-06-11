import json
from procedimientos.Listar_InsertarProveedores import proveedores

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        proveedor = proveedores(data)
        
        print(f"RESPUESTA TEST PROVEEDORES: idProveedor: {proveedor}")

    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")