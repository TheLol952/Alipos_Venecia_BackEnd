import json
from procedimientos.AutoCuentaContable import obtenerCuentaContable

if __name__ == "__main__":
    try:
        raw = input("Ingrese el JSON de la compra: ")
        data = json.loads(raw)
        resultado = obtenerCuentaContable(data)
        
        print("\n📊 Resultado final:")
        nombres_campos = [
            "CUENTA_CONTABLE",
            "CUENTA_RELACION",
            "CON_ENTIDAD",
            "TIPO_OPERACION",
            "CLASIFICACION",
            "SECTOR",
            "TIPO_COSTO"
        ]
        
        for nombre, valor in zip(nombres_campos, resultado):
            print(f"{nombre}: {valor}")
            
    except json.JSONDecodeError:
        print("\n❌ Error: El texto ingresado no es un JSON válido")
    except Exception as ex:
        print(f"\n❌ Error inesperado: {ex}")