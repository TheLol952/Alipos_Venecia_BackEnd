import json


def EsCombustible(data: dict) -> tuple[int, float, float]:
    """
    Verifica si la compra en el JSON es de tipo combustible:
    - Comprueba que en al menos un ítem de cuerpoDocumento existan los códigos 'D1' y 'C8' en "tributos".
    - Busca en data['resumen']['tributos'] los valores de FOVIAL (codigo 'D1') y COTRANS (codigo 'C8').
    - Devuelve:
        ES_COMBUSTIBLE: 1 si ambos códigos están presentes y tienen valor > 0, 0 en caso contrario.
        FOVIAL: valor asociado al codigo 'D1' en resumen (0.0 si no existe).
        COTRANS: valor asociado al codigo 'C8' en resumen (0.0 si no existe).
    """
    fovial = 0.0
    cotrans = 0.0
    es_combus = 0

    # Recolectar todos los códigos de tributos presentes en los ítems
    trib_codes = set()
    for item in data.get('cuerpoDocumento', []):
        trib_codes.update(item.get('tributos', []))

    # Extraer valores desde resumen
    for trib in data.get('resumen', {}).get('tributos', []):
        codigo = trib.get('codigo')
        valor = trib.get('valor', 0)
        if codigo == 'D1':
            fovial = float(valor)
        elif codigo == 'C8':
            cotrans = float(valor)

    # Determinar combustible
    if {'D1', 'C8'}.issubset(trib_codes) and fovial > 0 and cotrans > 0:
        es_combus = 1

    return es_combus, fovial, cotrans


# Punto de entrada para prueba manual
if __name__ == "__main__":
    print("🚀 Servicio EsCombustible iniciado...")
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        es, fov, cot = EsCombustible(data)
        # Mostrar los valores separados por espacios
        print(f"Es Combustible?: {es}, Fovial: {fov}, Cotrans: {cot}")
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")