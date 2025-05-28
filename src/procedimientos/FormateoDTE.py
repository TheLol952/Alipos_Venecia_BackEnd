import json
from datetime import datetime

class FormatearControlDTE:
    @staticmethod
    def procesar(data: dict) -> str:
        """
        Formatea el numeroControl de un DTE:
        - Recibe JSON de compra con campo identificacion.numeroControl
        - Divide por '-' y extrae la última parte (control correlativo)
        - Elimina ceros a la izquierda para obtener el número real (longitud dinámica)
        - Devuelve ese texto (o "0" si era todo ceros)
        """
        try:
            numero_control = data.get("identificacion", {}).get("numeroControl", "")
            partes = numero_control.split('-')
            correlativo = partes[-1]
            # Eliminar ceros a la izquierda
            correlativo_sin_ceros = correlativo.lstrip('0')
            if correlativo_sin_ceros == '':
                correlativo_sin_ceros = '0'
            return correlativo_sin_ceros
        except Exception as e:
            print(f"❌ Error formateando numeroControl: {e}")
            return ''
        
# Punto de entrada para prueba manual
if __name__ == "__main__":
    print("🚀 Servicio Formateo DTE iniciado...")
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        resultado = FormatearControlDTE.procesar(data)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")