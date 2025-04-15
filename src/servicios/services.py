import json
from .models import Database
from .clients import consulta_documentos
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_nested_value(data, keys, default=None):
    """Acceso seguro a valores anidados usando notación de puntos"""
    if isinstance(keys, str):
        keys = keys.split('.')
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data if data is not None else default

def get_safe_value(data, possible_keys, default="No definido", max_length=None):
    """Versión mejorada que busca en múltiples rutas posibles"""
    if not isinstance(possible_keys, list):
        possible_keys = [possible_keys]
    
    for key_path in possible_keys:
        value = get_nested_value(data, key_path)
        if value is not None:
            break
    else:
        value = default
    
    if isinstance(value, str) and max_length:
        return value[:max_length]
    return value

def get_safe_number(data, possible_keys):
    """Versión mejorada para valores numéricos"""
    value = get_safe_value(data, possible_keys, 0)
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return 0.0
#-------- Funcion que busca extraer el codigo de generacion, en todos los casos posibles  ----------
def extract_codigo_generacion(json_data):
    """Búsqueda mejorada del código de generación"""
    # Buscar en múltiples rutas posibles, en caso de que una no funcione o no se encuentre,
    # se intenta con la siguiente.
    # Donde por ejemplo, "Identificacion" siendo el nodo raíz, "codigoGeneracion" el campo a buscar
    # De esta manera cubirmos los diferentes formatos de JSON que se pueden recibir
    # Ya sea que contenga nodo principal, secundario o se encuentre en el cuerpo principal del JSON
    return get_safe_value(json_data, [
        "identificacion.codigoGeneracion",
        "responseMH.codigoGeneracion",
        "dte.identificacion.codigoGeneracion",
        "codigoGeneracion"
    ], "No definido")

def extract_numero_control(json_data):
    """Búsqueda mejorada del número de control"""
    return get_safe_value(json_data, [
        "identificacion.numeroControl",
        "responseMH.numeroControl",
        "documento.numeroControl",
        "dte.identificacion.numeroControl",
        "numeroControl"
    ], "No definido")

def extract_receptor_nit(receptor):
    """Extracción mejorada del NIT con múltiples fuentes"""
    return get_safe_value(receptor, [
        "nit",
        "numDocumento",
        "documento"
    ], "Sin NIT Receptor", 20)

def extract_receptor_nrc(receptor):
    """Extracción mejorada del NRC"""
    return get_safe_value(receptor, ["nrc"], "Sin NRC Receptor", 15)

def extract_tributos(resumen):
    """Extracción robusta de tributos con múltiples validaciones"""
    iva = fovial = cotrans = 0.0
    tributos = resumen.get("tributos", []) or []

    for tributo in tributos:
        if not isinstance(tributo, dict):
            continue
            
        codigo = str(tributo.get("codigo", "")).strip().upper()
        descripcion = str(tributo.get("descripcion", "")).upper()
        valor = get_safe_number(tributo, "valor")

        # Detección por código o descripción
        if any(s in descripcion for s in {"FOVIAL", "FOVIAL"}):
            fovial = valor
        elif any(s in descripcion for s in {"COTRANS", "COTRANS"}):
            cotrans = valor
        elif codigo in ["20", "IVA"] or "IVA" in descripcion:
            iva = valor

    # Fallback a valores directos si no se encontraron en tributos
    if iva <= 0:
        iva = get_safe_number(resumen, ["totalIva", "iva", "ivaItem"])
    
    return iva, fovial, cotrans

def process_json_structure(json_data):
    """Normaliza diferencias estructurales en el JSON"""
    # Unificar campo de firma
    if "firma" in json_data and "firmaElectronica" not in json_data:
        json_data["firmaElectronica"] = json_data.pop("firma")
    
    # Normalizar respuesta de Hacienda
    if "respuestaHacienda" in json_data:
        respuesta_hacienda = json_data.get("respuestaHacienda") or {}
        json_data["responseMH"] = respuesta_hacienda
        return json_data

def validate_required_fields(json_data):
    """Valida campos mínimos requeridos"""
    required_fields = [
        "identificacion",
        "emisor",
        "receptor",
        "resumen"
    ]
    
    for field in required_fields:
        if not json_data.get(field):
            logger.error(f"Campo requerido faltante: {field}")
            return False
    return True

def recepcion_factura(json_data, year, month):
    try:
        # Validación inicial
        if not json_data or not isinstance(json_data, dict):
            raise ValueError("Datos de factura inválidos o vacíos")
        
        # Asegurar que 'resumen' existe y es un diccionario
        resumen = json_data.get("resumen", {})
        if not isinstance(resumen, dict):
            resumen = {}
            
        # Modificar la línea problemática:
        iva, fovial, cotrans = extract_tributos(resumen)

        # Extracción mejorada de datos
        sello_recibido = get_safe_value(json_data, [
            "selloRecibido",
            "responseMH.selloRecibido",
            "respuestaHacienda.selloRecibido"
        ], "No definido")


        # Construcción de datos con logging
        factura_data = (
            "Vidrieria y Aluminios Venecia",
            extract_codigo_generacion(json_data),
            get_safe_value(json_data, "identificacion.tipoDte", "No definido"),
            None,
            None,
            sello_recibido,
            extract_receptor_nrc(json_data.get("receptor", {})),
            None,
            get_safe_value(json_data, "extension.observaciones", "No definido", 500),
            extract_numero_control(json_data),
            get_safe_value(json_data, "emisor.nit", "Sin NIT Emisor", 20),
            get_safe_value(json_data, "emisor.nrc", "Sin NRC Emisor", 20),
            get_safe_value(json_data, "emisor.nombre", "No definido", 100),
            get_safe_value(json_data, "receptor.nombre", "No definido", 100),
            extract_receptor_nrc(json_data.get("receptor", {})),
            extract_receptor_nit(json_data.get("receptor", {})),
            json.dumps(json_data),
            get_safe_value(json_data, "identificacion.fecEmi", "1900-01-01"),
            year,
            month,
            "0",
            "A",
            iva,
            get_safe_number(json_data, "resumen.ivaPerci1"),
            fovial,
            cotrans,
            get_safe_number(json_data, "resumen.subTotalVentas"),
            get_safe_number(json_data, "resumen.totalPagar"),
        )

        if len(factura_data) != 28:
            logger.error("Número incorrecto de columnas")
            return False

        # Verificar si la factura ya existe en la base de datos
        codigo_generacion = factura_data[1]
        if verificar_factura_en_db(codigo_generacion):
            logger.info(f"La factura {codigo_generacion} ya existe en la base de datos.")
            return True
        
        # Insertar factura en la base de datos
        with Database() as db:
            db.insert_invoice(*factura_data)
        db.close()
        return True

    except Exception as e:
        logger.error(f"Error procesando factura: {str(e)}", exc_info=True)
        return False
    
def verificar_factura_en_db(codigo_generacion):
    with Database() as db:
        return db.check_invoice(codigo_generacion)
