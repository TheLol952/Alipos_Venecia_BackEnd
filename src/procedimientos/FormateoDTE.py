def FormatDTE(data: dict) -> str:
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
        
