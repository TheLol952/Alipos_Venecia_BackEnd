import json
import oracledb
from datetime import datetime
from core.conexion_oracle import get_connection
from ObtenerDatosCompra import ObtenerDatosCompra
from AutoCuentaContable import obtenerCuentaContable
from Listar_InsertarProveedores import ListarInsertarProveedores
from EsCombustible import EsCombustible
from InsertCompraInDb import InsertCompraInDb


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
        compret = None
        dai = 0
        ivaaduana = 0
        tipopoliza = None
        poliza = 0
        cerrado = None
        tipocompra = 1
        idtipocompra = '00000001'
        idtipocompra_o = '00000003'
        bloquef_excentas = None
        comentario = None
        aduana = None
        agente_aduanal = None
        proveedor_ext = None
        codigo_importacion = None
        concepto_compra = None
        #Codigo interno de Alipos xx-xxxx-xxxx
        month_str = f"{month:02d}"  # Asegura que el mes tenga dos dígitos
        filtro_prefijo = f"{month_str}-{year}-%"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT MAX(
                        TO_NUMBER(
                            REGEXP_SUBSTR(CODIGO_FACTURA_CORRE, '[0-9]+$', 1)
                        )
                    )
                        FROM CO_COMPRAS
                        WHERE CODIGO_FACTURA_CORRE LIKE :prefijo
                    """,
                    {"prefijo": filtro_prefijo}
                )
                max_sufijo = cur.fetchone()[0] or 0
                next_sufijo = int(max_sufijo) + 1
        codigo_factura_corre = f"{month_str}-{year}-{next_sufijo}"
        tipo_activo = None
        porcentaje = None
        vida_util = None
        depreciacion = None
        tipo_depreciacion = None
        fecha_depreciacion = None
        prorrateo = None
        procesado_prorrateo = None
        procesado_prorrateo_hecho = None
        compra_original = None

        ## Obtener datos mediante procedimientos
        compra_datos = ObtenerDatosCompra(data)
        if not compra_datos:
            return
        
        cuenta_contable = obtenerCuentaContable(data)
        if not cuenta_contable:
            return
        
        proveedor = ListarInsertarProveedores.procesar(data)
        if not proveedor:
            return
        
        es_combustible = EsCombustible(data)
        if not es_combustible:
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

        datosCompra = (
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
            compra_original
        )

        # Insertar en la base de datos
        InsertCompraInDb(*datosCompra, data=data)
    except oracledb.DatabaseError as db_err:
        # Extraer información detallada del error Oracle
        error_obj, = db_err.args
        detalle = {
            "ORACLE_CODE":    error_obj.code,
            "ORACLE_MESSAGE": error_obj.message,
            "SQL_TEXT":       getattr(error_obj, "sqltext", None),
            "OFFSET":         getattr(error_obj, "offset", None)    
        }
        print(json.dumps({
            "STATUS": "ERROR ORACLE",
            "DETAIL":  detalle
        }, indent=2, ensure_ascii=False))

    except ValueError as ve:
        # Errores controlados ("no se pudo obtener X", etc.)
        print(json.dumps({
            "STATUS":  "ERROR de validación",
            "MESSAGE": str(ve)
        }, indent=2, ensure_ascii=False))

    except KeyError as ke:
        # Falta alguna clave esperada en el JSON
        print(json.dumps({
            "STATUS":  "ERROR de clave",
            "MESSAGE": f"Falta clave en JSON: {ke}"
        }, indent=2, ensure_ascii=False))

    except json.JSONDecodeError as je:
        # JSON mal formado
        print(json.dumps({
            "STATUS":  "ERROR JSON",
            "MESSAGE": str(je)
        }, indent=2, ensure_ascii=False))

    except Exception as e:
        # Cualquier otro error inesperado
        print(json.dumps({
            "STATUS":  "ERROR inesperado",
            "MESSAGE": str(e),
            "TYPE":     type(e).__name__
        }, indent=2, ensure_ascii=False))

# Punto de entrada para prueba manual
if __name__ == "__main__":
    try:
        entrada = input("Ingrese el JSON de compra: ")
        data = json.loads(entrada)    # aquí parseas la cadena a lista
        InsertarCompras(data)         # pasas la lista directamente
    except Exception as ex:
        print(json.dumps({
            "STATUS": "ERROR",
            "MESSAGE": str(ex)
        }, indent=2, ensure_ascii=False))