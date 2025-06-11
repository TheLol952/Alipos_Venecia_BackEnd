import oracledb
import unicodedata
from core.conexion_oracle import get_connection
from procedimientos.InsertarDetalleCompras import InsertDetalleCompra
from procedimientos.CuentaSucursalesService import obtenerDatosSucursal

def InsertCompraInDb(
    corre,
    codemp,
    codtipo,
    comprob,
    fecha,
    compraie,
    compraee,
    compraig,
    exportacio,
    iva,
    totalcomp,
    retencion,
    retencioniva,
    anticipo,
    month,
    year,
    compraexc,
    fechadig,
    compret,
    codigo_nuevo,
    dai,
    ivaaduana,
    tipopoliza,
    poliza,
    descuentos,
    cerrado,
    tipocompra,
    idtipocompra,
    correlativo_dte,
    numero_control_dte,
    sello_recibido,
    idtipocompra_o,
    es_combus,
    fovial,
    cotrans,
    codigo_generacion,
    iva_perci,
    cuenta_final,
    cuenta_rel,
    hora_actual,
    con_entidad,
    bloquef_excentas,
    fecha_facturacion_fecha,
    retencion2,
    comentario,
    aduana,
    agente_aduanal,
    proveedor_ext,
    codigo_importacion,
    concepto_compra,
    codigo_factura_corre,
    tipo_op,
    clasif,
    sector,
    tipo_costo,
    tipo_activo,
    porcentaje,
    vida_util,
    depreciacion,
    tipo_depreciacion,
    fecha_depreciacion,
    prorrateo,
    procesado_prorrateo,
    procesado_prorrateo_hecho,
    compra_original, 
    data: dict
) -> None:
    """
    Inserta una fila en CO_COMPRAS o, si ya existe una compra con el mismo
    CODIGO_GENERACION_DTE, NUMERO_CONTROL_DTE y SELLO_RECIBIDO_DTE, omite la inserción.
    """
    # --- Normalizamos “None” literales a None real ---
    if codigo_generacion in (None, "", "None"):
        codigo_generacion = None
    if numero_control_dte in (None, "", "None"):
        numero_control_dte = None
    if sello_recibido in (None, "", "None"):
        sello_recibido = None

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1) Si tenemos TRES campos DTE, verificamos duplicado con AND
                if codigo_generacion and numero_control_dte and sello_recibido:
                    cur.execute("""
                            SELECT 1
                            FROM CO_COMPRAS
                            WHERE CODIGO_GENERACION_DTE = :cod_gen
                            AND NUMERO_CONTROL_DTE    = :num_ctrl
                            AND SELLO_RECIBIDO_DTE    = :sello
                    """, {
                        "cod_gen":  codigo_generacion,
                        "num_ctrl": numero_control_dte,
                        "sello":    sello_recibido
                    })
                    if cur.fetchone():
                        return 2

                # 2) Si faltó alguno de los tres, usamos fallback NIT+FECHA+TOTALCOMP
                if codigo_nuevo and fecha and totalcomp and numero_control_dte:
                    cur.execute("""
                            SELECT 1
                            FROM CO_COMPRAS
                            WHERE CDPROV    = :codprov
                            AND FECHA     = TO_DATE(:fecha_emision,'DD/MM/YYYY')
                            AND TOTALCOMP = :monto_total
                            AND NUMERO_CONTROL_DTE = :num_ctrl
                    """, {
                        "codprov":       codigo_nuevo,
                        "fecha_emision": fecha,
                        "monto_total":   totalcomp,
                        "num_ctrl": numero_control_dte
                    })
                    if cur.fetchone():
                        return 2

                # 3) Si no es duplicado, proceder a la inserción
                sql = """
                    INSERT INTO CO_COMPRAS (
                        CORRE, CODEMP, CODTIPO, COMPROB, FECHA,
                        COMPRAIE, COMPRAEE, COMPRAIG, IMPORTACIO, IVA,
                        TOTALCOMP, RETENCION, RETENCIONIVA, ANTICIPO, MESD,
                        ANOD, COMPRAEXC, FECHADIG, COMPRET, CDPROV,
                        DAI, IVAADUANA, TIPOPOLIZA, POLIZA, DESCUENTOS,
                        CERRADO, TIPO_COMPRA, ID_TIPOCOMPRA, CORRELATIVO_DTE,
                        NUMERO_CONTROL_DTE, SELLO_RECIBIDO_DTE, ID_TIPO_COMPRA_O, ES_COMBUSTIBLE,
                        FOVIAL, COTRANS, CODIGO_GENERACION_DTE, IVA_PERCIBIDO, CUENTA_CONTABLE,
                        CUENTA_RELACION, HORA, CON_ENTIDAD, BLOQUEF_EXCENTAS,
                        FECHA_FACTURACION_HORA, RETENCION_2PORCIENTO, COMENTARIO, ADUANA,
                        AGENTE_ADUANAL, PROVEEDOR_EXT, CODIGO_IMPORTACION, CONCEPTO_COMPRA,
                        CODIGO_FACTURA_CORRE, DTE_TIPO_OPERACION, DTE_CLASIFICACION, DTE_SECTOR, DTE_TIPO_COSTO_GASTO,
                        TIPO_ACTIVO, PORCENTAJE, VIDA_UTIL, DEPRECIACION,
                        TIPO_DEPRECIACION, FECHA_DEPRECIACION, PRORRATEO,
                        PROCESADO_PRORRATEO, PROCESADO_PRORRATEO_HECHO, COMPRA_ORIGINAL
                    ) VALUES (
                        :corre, :codemp, :codtipo, :comprob, TO_DATE(:fecha,'DD/MM/YYYY'),
                        :compraie, :compraee, :compraig, :exportacio, :iva,
                        :totalcomp, :retencion, :retencioniva, :anticipo, :month,
                        :year, :compraexc, TO_DATE(:fechadig,'DD/MM/YYYY'), :compret, :codigo_nuevo,
                        :dai, :ivaaduana, :tipopoliza, :poliza, :descuentos,
                        :cerrado, :tipocompra, :idtipocompra, :correlativo_dte,
                        :numero_control_dte, :sello_recibido, :idtipocompra_o, :es_combus,
                        :fovial, :cotrans, :codigo_generacion, :iva_perci, :cuenta_final,
                        :cuenta_rel, :hora_actual, :con_entidad, :bloquef_excentas,
                        TO_DATE(:fecha_facturacion_fecha,'DD/MM/YYYY HH24:MI:SS'), :retencion2, :comentario, :aduana,
                        :agente_aduanal, :proveedor_ext, :codigo_importacion, :concepto_compra,
                        :codigo_factura_corre, :tipo_op, :clasif, :sector, :tipo_costo,
                        :tipo_activo, :porcentaje, :vida_util, :depreciacion,
                        :tipo_depreciacion, TO_DATE(:fecha_depreciacion,'DD/MM/YYYY'), :prorrateo,
                        :procesado_prorrateo, :procesado_prorrateo_hecho, :compra_original
                    )
                """

                binds = {
                    'corre':                corre,
                    'codemp':               codemp,
                    'codtipo':              codtipo,
                    'comprob':              comprob,
                    'fecha':                fecha,
                    'compraie':             compraie,
                    'compraee':             compraee,
                    'compraig':             compraig,
                    'exportacio':           exportacio,
                    'iva':                  iva,
                    'totalcomp':            totalcomp,
                    'retencion':            retencion,
                    'retencioniva':         retencioniva,
                    'anticipo':             anticipo,
                    'month':                month,
                    'year':                 year,
                    'compraexc':            compraexc,
                    'fechadig':             fechadig,
                    'compret':              compret,
                    'codigo_nuevo':         codigo_nuevo,
                    'dai':                  dai,
                    'ivaaduana':            ivaaduana,
                    'tipopoliza':           tipopoliza,
                    'poliza':               poliza,
                    'descuentos':           descuentos,
                    'cerrado':              cerrado,
                    'tipocompra':           tipocompra,
                    'idtipocompra':         idtipocompra,
                    'correlativo_dte':      correlativo_dte,
                    'numero_control_dte':   numero_control_dte,
                    'sello_recibido':       sello_recibido,
                    'idtipocompra_o':       idtipocompra_o,
                    'es_combus':            es_combus,
                    'fovial':               fovial,
                    'cotrans':              cotrans,
                    'codigo_generacion':    codigo_generacion,
                    'iva_perci':            iva_perci,
                    'cuenta_final':         cuenta_final,
                    'cuenta_rel':           cuenta_rel,
                    'hora_actual':          hora_actual,
                    'con_entidad':          con_entidad,
                    'bloquef_excentas':     bloquef_excentas,
                    'fecha_facturacion_fecha': fecha_facturacion_fecha,
                    'retencion2':           retencion2,
                    'comentario':           comentario,
                    'aduana':               aduana,
                    'agente_aduanal':       agente_aduanal,
                    'proveedor_ext':        proveedor_ext,
                    'codigo_importacion':   codigo_importacion,
                    'concepto_compra':      concepto_compra,
                    'codigo_factura_corre': codigo_factura_corre,
                    'tipo_op':              tipo_op,
                    'clasif':               clasif,
                    'sector':               sector,
                    'tipo_costo':           tipo_costo,
                    'tipo_activo':          tipo_activo,
                    'porcentaje':           porcentaje,
                    'vida_util':            vida_util,
                    'depreciacion':         depreciacion,
                    'tipo_depreciacion':    tipo_depreciacion,
                    'fecha_depreciacion':   fecha_depreciacion,
                    'prorrateo':            prorrateo,
                    'procesado_prorrateo':            procesado_prorrateo,
                    'procesado_prorrateo_hecho':      procesado_prorrateo_hecho,
                    'compra_original':      compra_original
                }

                cur.execute(sql, binds)
                conn.commit()
                resultado = 1
            # Cuando se inserte la compra, se insertara sus prductos y demas en CO_DETCOMPRAS
            InsertDetalleCompra(data, corre, codtipo, cuenta_final)
            #Normalizar NIT y DIRECCION de la compra
            raw_nit  = data['emisor']['nit']
            raw_direccion  = data['emisor']['direccion']['complemento']
            # quita acentos, pasa a ascii, mayúsculas y trim
            nit_norm = raw_nit.strip()
            direccion_norm = unicodedata.normalize("NFKD", raw_direccion) \
                            .encode("ASCII", "ignore").decode() \
                            .upper().strip()

            # 3) Obtén la sucursal “correcta” de tu servicio
            svc = obtenerDatosSucursal(data) or {}
            (sucursal) = svc

            # 4) Si tenemos nit con guiones y dirección no vacía…
            if nit_norm and '-' in nit_norm and direccion_norm:
                try:
                    with get_connection() as conn:
                        with conn.cursor() as cur:
                            # 4.1) ¿Ya existe EXACTO NIT+DIRECCIÓN?
                            cur.execute("""
                                SELECT 1
                                FROM DICCIONARIO_COMPRAS_AUTO d
                                WHERE TRIM(d.NIT)       = :nit
                                AND TRIM(UPPER(d.DIRECCION)) = :dir
                            """, { 'nit': nit_norm, 'dir': direccion_norm })
                            if cur.fetchone():
                                # existe → ignoramos
                                print(f"ℹ️ Ya hay diccionario para {nit_norm} / {direccion_norm}")
                            else:
                                # no existe → INSERT con su SUCURSAL
                                cur.execute("""DICCIONARIO_COMPRAS_AUTO
                                    INSERT INTO (
                                    NIT, NOMBRE_PROVEEDOR, DIRECCION,
                                    CUENTA_CONTABLE, TIPO_OPERACION, CLASIFICACION,
                                    SECTOR, TIPO_COSTO_GASTO, SUCURSAL
                                    ) VALUES (
                                    :nit, :nom, :dir,
                                    :cta, :tipo, :clas, :sector, :tcosto, :suc
                                    )
                                """, {
                                    'nit':  nit_norm,
                                    'nom':  data['emisor']['nombre'],
                                    'dir':  direccion_norm,
                                    'cta':  cuenta_final,
                                    'tipo': tipo_op,
                                    'clas': clasif,
                                    'sector': sector,
                                    'tcosto': tipo_costo,
                                    'suc': sucursal
                                })
                                conn.commit()
                                print(f"✅ Nuevo dict para {nit_norm} / {direccion_norm} → {sucursal}")
                except oracledb.DatabaseError as e:
                    print(f"⚠️ Error diccionario: {e}")

            return resultado

    except oracledb.DatabaseError as e:
        # Extraer info del error Oracle
        error_obj, = e.args
        detalle = {
            'ORACLE_CODE':    error_obj.code,
            'ORACLE_MESSAGE': error_obj.message,
            'OFFSET':         getattr(error_obj, 'offset', None),
            'SQL_TEXT':       getattr(error_obj, 'sqltext', None)
        }
        # Lanzar excepción con toda la info para la capa superior
        raise Exception(f"Oracle Error {detalle['ORACLE_CODE']}: "
                        f"{detalle['ORACLE_MESSAGE']} "
                        f"(offset {detalle['OFFSET']})")
