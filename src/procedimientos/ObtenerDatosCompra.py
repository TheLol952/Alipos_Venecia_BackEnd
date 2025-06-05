import json
import oracledb
from core.conexion_oracle import get_connection
from FormateoDTE import FormatearControlDTE
from datetime import datetime


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

def ObtenerDatosCompra(data: dict) -> tuple:
    """
    Extrae campos clave de una compra JSON, usando mapeos de rutas alternativas:
    - CODTIPO: consulta SQL por tipoDte
    - COMPROB: correlativo sin ceros
    - FECHA: fecEmi
    - COMPRAIE, COMPRAEE: 0
    - COMPRAIG: totalGravada o totalSujetoRetencion
    - IVA: valor tributo código '20'
    - TOTALCOMP: totalPagar o montoTotalOperacion
    - RETENCION: ivaRete1 o totalIVAretenido
    - DESCUENTOS: totalDescu o descuGravada
    - IVA_PERCIBIDO: ivaPerci1
    - IVA_PERCIBIDO_2: cuerpoDocumento.ivaPercibido (percepción)
    - CORRELATIVO_DTE: parte final de numeroControl con ceros
    - HORA: hora actual de procesamiento HH:mm:ss
    - FECHA_FACTURACION_FECHA: fecha y hora de procesamiento dd/MM/YYYY HH:mm:ss
    """
    # 1) CODTIPO via SQL
    tipo_dte = data.get('identificacion', {}).get('tipoDte')
    codtipo = ''
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT TIPO_DOCUMENTO FROM DTE_TIPO_DOCUMENTO_002"
                    " WHERE CODIGO_MH = :codigo_mh",
                    {"codigo_mh": tipo_dte}
                )
                row = cur.fetchone()
                if row and row[0] is not None:
                    codtipo = str(row[0])
    except Exception as e:
        print(f"❌ Error obteniendo CODTIPO: {e}")

    # 2) COMPROB
    comprob = FormatearControlDTE.procesar(data)

    # 3) FECHA factura
    fecha = data.get('identificacion', {}).get('fecEmi', '')
    #Formatear fecha a dd/MM/YY
    if fecha:
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%y')
        except ValueError:
            print(f"❌ Error formateando fecha: {fecha}")
            fecha = ''


    # Campos fijos
    compraie = 0
    compraee = 0

    # 4) COMPRAIG
    compraig = float(get_from_json(
        data,
        paths=[['resumen','totalGravada'], ['resumen','totalSujetoRetencion'], ['cuerpoDocumento','montoSujetoPercepcion']],
        default=0.0
    ))

    # 5) IVA (orígenes múltiples)
    iva = 0.0
    # Primero, buscar resumen.totalIva
    iva_candidate = get_from_json(
        data,
        paths=[['resumen','totalIva']],
        default=None
    )
    if iva_candidate is not None:
        iva = float(iva_candidate)
    else:
        # Luego, buscar cuerpoDocumento.iva
        for trib in data.get('resumen', {}).get('tributos', []):
            if trib.get('codigo') == '20':
                iva = float(trib.get('valor', 0))
                break

    # 6) TOTALCOMP
    totalcomp = float(get_from_json(
        data,
        paths=[['resumen','totalPagar'], ['resumen','montoTotalOperacion'], ['resumen','totalSujetoRetencion']],
        default=0.0
    ))

    # 7) RETENCION
    retencion = float(get_from_json(
        data,
        paths=[['resumen','ivaRete1'], ['resumen','totalIVAretenido']],
        default=0.0
    ))

    # 8) DESCUENTOS
    descuentos = float(get_from_json(
        data,
        paths=[['resumen','totalDescu'], ['resumen','descuGravada']],
        default=0.0
    ))

    # 9) IVA_PERCIBIDO
    iva_perci = float(get_from_json(
        data,
        paths=[['resumen','ivaPerci1']],
        default=0.0
    ))

    # 10) IVA_PERCEPCION (2%)
    cd = data.get('cuerpoDocumento')
    if isinstance(cd, dict):
        retencion2 = float(cd.get('ivaPercibido', 0))
    elif isinstance(cd, list) and cd:
        retencion2 = float(cd[0].get('ivaPercibido', 0))
    else:
        retencion2 = float(0)

    # 11) CORRELATIVO_DTE (con ceros)
    numero_control = str(get_from_json(
        data,
        paths=[['identificacion','numeroControl']],
        default=None
    ))
    parts = numero_control.split('-')
    correlativo_dte = parts[-1] if parts else ''

    # 12) NUMERO_CONTROL (puro)
    numero_control_dte = str(get_from_json(
        data,
        paths=[['identificacion','numeroControl']],
        default=None
    ))

    # 13) SELLO_RECIBIDO
    sello_recibido = str(get_from_json(
        data,
        paths=[['responseMH','selloRecibido'],['sello'],['selloRecibido']],
        default=None
    ))

    #14) CODIGO_GENERACION_DTE
    codigo_generacion = str(get_from_json(
        data,
        paths=[['identificacion','codigoGeneracion']],
        default=None
    ))

    #  & ) Hora y fecha de procesamiento
    now = datetime.now()
    hora_actual = now.strftime('%H:%M:%S')
    fecha_facturacion_fecha = now.strftime('%d/%m/%Y %H:%M:%S')

    return (
        codtipo,
        comprob,
        fecha,
        compraie,
        compraee,
        compraig,
        iva,
        totalcomp,
        retencion,
        descuentos,
        iva_perci,
        retencion2,
        correlativo_dte,
        numero_control_dte,
        sello_recibido,
        codigo_generacion,
        hora_actual,
        fecha_facturacion_fecha
    )

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de la compra: ")
        data = json.loads(entrada)
        valores = ObtenerDatosCompra(data)
    except Exception as ex:
        print(f"❌ Error en ejecución: {ex}")