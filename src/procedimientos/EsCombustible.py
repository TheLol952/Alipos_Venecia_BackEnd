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
    - Busca los códigos D1 y C8 en cuerpoDocumento.tributos o en resumen.tributos.
    - Extrae FOVIAL (valor de D1) y COTRANS (valor de C8).
    - Si no hay ningún nodo o referencia a D1/C8, devuelve siempre (0, 0.0, 0.0).
    """
    # 1) Leer todos los ítems de "cuerpoDocumento" y recolectar sus códigos de tributos
    items = get_from_json(data, paths=[['cuerpoDocumento']], default=[])
    trib_codes = set()
    # Solo iterar si items es una lista no vacía
    if isinstance(items, list) and items:
        for item in items:
            # item.get('tributos', []) puede ser lista o None, así que:
            tribs = item.get('tributos') or []
            if isinstance(tribs, list):
                trib_codes.update(tribs)
                
    # 2) Leer los tributos del "resumen"
    resumen_tributos = get_from_json(data, paths=[['resumen', 'tributos']], default=[])
    fovial = 0.0
    cotrans = 0.0
    if isinstance(resumen_tributos, list) and resumen_tributos:
        for trib in resumen_tributos:
            código = trib.get('codigo')
            valor = trib.get('valor', 0)
            if código == 'D1':
                try:
                    fovial = float(valor)
                except (TypeError, ValueError):
                    fovial = 0.0
            elif código == 'C8':
                try:
                    cotrans = float(valor)
                except (TypeError, ValueError):
                    cotrans = 0.0

    # 3) Determinar si es combustible:
    #    basta con encontrar D1 o C8 en cualquiera de los nodos; si no hay, queda en 0.
    es_combus = 1 if ('D1' in trib_codes or 'C8' in trib_codes) else 0

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