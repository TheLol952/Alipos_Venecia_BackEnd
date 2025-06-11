import json
from procedimientos.InsertarCompraMain import InsertarCompras

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de compra: ")
        data = json.loads(entrada) 
        compraResult = InsertarCompras(data)

        print(f"RESPUESTA TEST INSERTAR COMPRA: {compraResult}")
    except Exception as ex:
        print(json.dumps({
            "STATUS": "ERROR",
            "MESSAGE": str(ex)
        }, indent=2, ensure_ascii=False))