import json

def get_from_json(data: dict, paths: list[list[str]], default=None):
    """
    Intenta extraer un valor de `data` usando rutas alternativas.
    Cada ruta es una lista de llaves anidadas. Retorna el primer valor encontrado o `default`.
    """
    for path in paths:
        current = data
        try:
            for key in path:
                current = current[key]
            return current
        except (KeyError, TypeError):
            continue
    return default

def EsCombustible(data: dict) -> tuple[int, float, float]:
    """
    Verifica si la compra en el JSON es de tipo combustible:
    - Usa get_from_json para extraer cuerpoDocumento y resumen.tributos
    - Devuelve (ES_COMBUSTIBLE, FOVIAL, COTRANS)
    """
    # 1) Leer todos los ítems
    items = get_from_json(data, paths=[['cuerpoDocumento']], default=[])
    trib_codes = set()
    if isinstance(items, list):
        for item in items:
            trib_codes.update(item.get('tributos', []))

    # 2) Leer los tributos del resumen
    resumen_tributos = get_from_json(data, paths=[['resumen','tributos']], default=[])
    fovial = 0.0
    cotrans = 0.0
    if isinstance(resumen_tributos, list):
        for trib in resumen_tributos:
            if trib.get('codigo') == 'D1':
                fovial = float(trib.get('valor', 0))
            elif trib.get('codigo') == 'C8':
                cotrans = float(trib.get('valor', 0))

    # 3) Determinar si es combustible
    es_combus = 1 if {'D1','C8'}.issubset(trib_codes) and fovial > 0 and cotrans > 0 else 0

    return es_combus, fovial, cotrans

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        es, fov, cot = EsCombustible(data)
        # Mostrar los valores separados por espacios
        print(f"Es Combustible?: {es}, Fovial: {fov}, Cotrans: {cot}")
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")