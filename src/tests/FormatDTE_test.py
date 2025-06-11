import json
from procedimientos.FormateoDTE import FormatDTE

if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        formatedDTE = FormatDTE(data)

        print(f"RESPUESTA TEST FORMAT DTE: {formatedDTE}")
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")