import json
from procedimientos.InsertarDetalleCompras import InsertDetalleCompra

if __name__ == "__main__":
    try:
        data = json.loads(input("Ingrese JSON de compra: "))
        corre = 546
        codtipo = 'CCF'
        cuenta = None
        idDetalle = InsertDetalleCompra(data, corre,  codtipo, cuenta) 

        print(f"RESPUESTA TEST DETALLES COMPRAS: idDetalle: {idDetalle}")

    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")