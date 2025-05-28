import json
import oracledb
from datetime import datetime
from core.conexion_oracle import get_connection
from ObtenerDatosCompra import ObtenerDatosCompra
from AutoCuentaContable import obtenerCuentaContable
from Listar_InsertarProveedores import ListarInsertarProveedores
from EsCombustible import EsCombustible


def InsertarCompras(data: dict) -> None:
    try:
        #Obtener datos generales de la compra

        ##Obtener id de la compra
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COALESCE(MAX(CORRE), 0) + 1 FROM CO_COMPRAS")
                corre = cur.fetchone()[0]
                data['corre'] = corre

        # Obtener año actual mediante datetime
        year = datetime.now().year
        month = datetime.now().month
        data['year'] = year
        codemp = (f"ALIPOS{year}")

        exportacio = 0
        retencioniva = 0
        anticipo = 0
        compraexc = 0
        fechadig = datetime.now().strftime("%d/%m/%y")
        compret = 'null'
        dai = 0
        ivaaduana = 0
        tipopoliza = 'null'
        poliza = 0
        cerrado = 'null'
        tipocompra = 1
        idtipocompra = '00000001'
        idtipocompra_o = '00000003'
        bloquef_excentas = 'null'
        comentario = 'null'
        aduana = 'null'
        agente_aduanal = 0
        proveedor_ext = 0
        codigo_importacion = 'null'
        concepto_compra = 0
        codigo_factura_corre = 0
        tipo_activo = 'null'
        porcentaje = 'null'
        vida_util = 'null'
        depreciacion = 'null'
        tipo_depreciacion = 'null'
        fecha_depreciacion = 'null'
        prorrateo = 'null'
        procesado_prorrateo = 'null'
        procesado_prorrateo_hecho = 'null'
        compra_original = 'null'

        ## Obtener datos mediante procedimientos
        compra_datos = ObtenerDatosCompra(data)
        if not compra_datos:
            print(json.dumps({"STATUS": "ERROR Compras", "MESSAGE": "No se pudieron obtener los datos de la compra."},
                indent=2, ensure_ascii=False))
            return
        
        cuenta_contable = obtenerCuentaContable(data)
        if not cuenta_contable:
            print(json.dumps({"STATUS": "ERROR Cuenta Contable", "MESSAGE": "No se pudo obtener la cuenta contable."},
                indent=2, ensure_ascii=False))
            return
        
        proveedor = ListarInsertarProveedores.procesar(data)
        if not proveedor:
            print(json.dumps({"STATUS": "ERROR Proveedores", "MESSAGE": "No se pudo obtener o insertar el proveedor."},
                indent=2, ensure_ascii=False))
            return
        
        es_combustible = EsCombustible(data)
        if not es_combustible:
            print(json.dumps({"STATUS": "ERROR Combustible", "MESSAGE": "No se pudo determinar si es combustible."},
                indent=2, ensure_ascii=False))
            return
            

        # Extraer datos de la compra
        (codtipo, comprob, fecha, compraie, compraee,
            compraig, iva, totalcomp, retencion,
            descuentos, iva_perci, retencion2,
            correlativo_dte, numero_control_dte, sello_recibido, codigo_generacion, hora_actual, fecha_facturacion_fecha) = compra_datos
        
        # Extraer datos de la cuenta contable
        (cuenta_final, cuenta_rel, con_entidad, tipo_op, clasif, sector, tipo_costo) = cuenta_contable
        
        # Extraer datos del proveedor
        (codigo_nuevo) = proveedor

        # Extraer datos de combustible
        (es_combus, fovial, cotrans) = es_combustible

        if codtipo == '8':
            codtipo = "DCT"
            totalcomp = compraig + retencion2
        elif codtipo == '2':
            codtipo = "CCF"
        else:
            codtipo = "FAC"
            iva = 0
            compraig = totalcomp

        datosCompra = {
            "CORRE": corre,
            "CODEMP": codemp,
            "CODTIPO": codtipo,
            "COMPROB": comprob,
            "FECHA": fecha,
            "COMPRAIE": compraie,
            "COMPRAEE": compraee,
            "COMPRAIG": compraig,
            "EXPORTACIO": exportacio,
            "IVA": iva,
            "TOTALCOMP": totalcomp,
            "RETENCION": retencion,
            "RETENCIONIVA": retencioniva,
            "ANTICIPO": anticipo,
            "MESD": month,
            "ANOD": year,
            "COMPRAEXC": compraexc,
            "FECHADIG": fechadig,
            "COMPRET": compret,
            'CDPROV': codigo_nuevo,
            "DAI": dai,
            "IVAADUANA": ivaaduana,
            "TIPOPOLIZA": tipopoliza,
            "POLIZA": poliza,
            "DESCUENTOS": descuentos,
            "CERRADO": cerrado,
            "TIPOCOMPRA": tipocompra,
            'ID_TIPOCOMPRA': idtipocompra,
            "CORRELATIVO_DTE": correlativo_dte,
            "NUMERO_CONTROL_DTE": numero_control_dte,
            "SELLO_RECIBIDO": sello_recibido,
            'ID_TIPOCOMPRA_O': idtipocompra_o,
            "ES_COMBUSTIBLE": es_combus,
            "FOVIAL": fovial,
            "COTRANS": cotrans,
            "CODIGO_GENERACION_DTE": codigo_generacion,
            "IVA_PERCIBIDO": iva_perci,
            "CUENTA_CONTABLE": cuenta_final,
            "CUENTA_RELACION": cuenta_rel,
            "HORA": hora_actual,
            "CON_ENTIDAD": con_entidad,
            "BLOQUEF_EXCENTAS": bloquef_excentas,
            "FECHA_FACTURACION_HORA": fecha_facturacion_fecha,
            "RETENCION2": retencion2,
            "COMENTARIO": comentario,
            "ADUANA": aduana,
            "AGENTE_ADUANAL": agente_aduanal,
            "PROVEEDOR_EXT": proveedor_ext,
            "CODIGO_IMPORTACION": codigo_importacion,
            "CONCEPTO_COMPRA": concepto_compra,
            "CODIGO_FACTURA_CORRE": codigo_factura_corre,
            "DTE_TIPO_OPERACION": tipo_op,
            "DTE_CLASIFICACION": clasif,
            "DTE_SECTOR": sector,
            "DTE_TIPO_COSTO_GASTO": tipo_costo,
            "TIPO_ACTIVO": tipo_activo,
            "PORCENTAJE": porcentaje,
            "VIDA_UTIL": vida_util,
            "DEPRECIACION": depreciacion,
            "TIPO_DEPRECIACION": tipo_depreciacion,
            "FECHA_DEPRECIACION": fecha_depreciacion,
            "PRORRATEO": prorrateo,
            "PROCESADO_PRORRATEO": procesado_prorrateo,
            "PROCESADO_PRORRATEO_HECHO": procesado_prorrateo_hecho,
            "COMPRA_ORIGINAL": compra_original
        }

        datosDetalleCompra = {

        }

        print(json.dumps(datosCompra, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({"STATUS": "ERROR inesperado", "MESSAGE": str(e)}, indent=2, ensure_ascii=False))

# Punto de entrada para prueba manual
if __name__ == "__main__":
    print("🚀 Servicio InsertarCompras iniciado...")
    try:
        entrada = input("Ingrese el JSON de compra: ")
        data = json.loads(entrada)
        InsertarCompras(data)
    except Exception as ex:
        print(json.dumps({"STATUS": "ERROR", "MESSAGE": str(ex)}, indent=2, ensure_ascii=False))
