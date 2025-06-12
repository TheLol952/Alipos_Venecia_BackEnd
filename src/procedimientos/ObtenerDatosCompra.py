from src.core.conexion_oracle import get_connection
from src.procedimientos.FormateoDTE import FormatDTE
from src.servicios.clients import consulta_documentos

from datetime import datetime

def get_from_json(data: dict, paths: list[list[str]], default=None):
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
    comprob = FormatDTE(data)

    # 3) FECHA factura
    fecha_raw = data.get('identificacion', {}).get('fecEmi', '')
    fecha = None
    #Formatear fecha a dd/MM/YY
    if fecha_raw:
        try:
            fecha = datetime.strptime(fecha_raw, '%Y-%m-%d').strftime('%d/%m/%y')
        except ValueError:
            print(f"❌ Error formateando fecha: {fecha}")

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
    numero_control = (get_from_json(
        data,
        paths=[['identificacion','numeroControl']],
        default=None
    ))
    parts = numero_control.split('-')
    correlativo_dte = parts[-1] if parts else ''

    # 12) NUMERO_CONTROL (puro)
    tmp_numero_control_dte = (get_from_json(
        data,
        paths=[['identificacion','numeroControl']],
        default=None
    ))
    numero_control_dte = str(tmp_numero_control_dte) if tmp_numero_control_dte is not None else None

    #13) CODIGO_GENERACION_DTE
    tmp_codigo_generacion = str(get_from_json(
        data,
        paths=[['identificacion','codigoGeneracion']],
        default=None
    ))
    codigo_generacion = str(tmp_codigo_generacion) if tmp_codigo_generacion is not None else None

    # 14) SELLO_RECIBIDO
    tmp_sello_recibido = (get_from_json(
        data,
        paths=[['responseMH','selloRecibido'],['sello'],['selloRecibido']],
        default=None
    ))
    sello_recibido = str(tmp_sello_recibido) 

    if sello_recibido == 'None':
        try:
            sello_recibido = consulta_documentos(codigo_generacion, fecha_raw)
        except:
            print('No se pudo obtener sello...')

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

