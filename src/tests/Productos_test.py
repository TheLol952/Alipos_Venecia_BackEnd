import json
from procedimientos.Listar_InsertarProductos import productos

if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        productos = productos(data)
        n = 1
        for producto in productos:
            print(f"RESPUESTA TEST PRODUCTOS: N:{n} idProducto: {producto}")
            n = n + 1
        
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")