import requests

def consulta_documentos(codigoGeneracion, fechaEmision):
    url = f'https://admin.factura.gob.sv/prod/consultas/publica/simple/1?codigoGeneracion={codigoGeneracion}&fechaEmi={fechaEmision}&ambiente=01'

    try:
        response = requests.get(url, timeout=10)  # Tiempo límite
        response.raise_for_status()  # Lanzar error si el código de estado no es 200
        data = response.json()
        
        # Convertir las observaciones a cadena si son una lista
        observaciones = data.get("observaciones")
        if isinstance(observaciones, list):
            observaciones_str = ', '.join(observaciones)
        else:
            observaciones_str = observaciones

        return {
            "estadoDocInc": data.get("estadoDocInc"),
            "estadoDoc": data.get("estadoDoc"),
            "selloVal": data.get("selloVal"),
            "numIdenRecep": data.get("numeIdenRecep"),
            "action": data.get("action"),
            "observaciones": observaciones_str
        }
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud a la API del Ministerio de Hacienda: {e}")
        return None
    except ValueError as e:
        print(f"Error al procesar la respuesta de la API: {e}")
        return None
