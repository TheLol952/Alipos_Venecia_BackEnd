from flask import Flask, request, jsonify
import threading
from datetime import datetime, timedelta
from app import process_emails  # Asumiendo que process_emails es la función principal de tu app
import logging
from models import Database #Importamos el modelo que maneja la base de datos

# Variables globales que se actualizan en process_emails
total_correos = 0
total_facturas_descargadas = 0
total_facturas_insertadas = 0
archivos_dañados = 0
correos_ignorados = 0
facturas_no_insertadas = {}

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Ruta inicial que ejecuta el proceso de facturación
@app.route('/descargar-facturas', methods=['POST'])
def procesar_facturas():
    data = request.get_json()
    # Validar que se hayan recibido todos los parámetros requeridos
    required_fields = ['fecha_inicio', 'fecha_fin', 'periodo_fiscal', 'mes_tributario']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Faltan los parámetros: {', '.join(missing)}"}), 400

    fecha_inicio = data['fecha_inicio']
    fecha_fin = data['fecha_fin']
    periodo_fiscal = data['periodo_fiscal']
    mes_tributario = data['mes_tributario']

    # Sumamos un día a la fecha_fin para que el proceso incluya esa fecha
    try:
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        fecha_fin_dt += timedelta(days=1)
        fecha_fin = fecha_fin_dt.strftime("%Y-%m-%d")
    except Exception as ex:
        return jsonify({"error": f"Formato de fecha_fin inválido: {str(ex)}"}), 400

    # Llamamos al proceso de facturación de forma síncrona para luego devolver el resumen.
    process_emails(fecha_inicio, fecha_fin, periodo_fiscal, mes_tributario) 

    return jsonify("Proceso Completado"), 200

# Esta Ruta procesa las facturas, mediante su cod_gen, sello_recepcion o num_control
# Se pueden procesar una o varias facturas a la vez
@app.route('/procesar-facturas', methods=['POST'])
def procesar_factura():
    data = request.get_json()
    # Validar que se haya enviado al menos uno de los parámetros de búsqueda
    required_params = ['cod_gen', 'sello_recepcion', 'num_control']
    if not any(param in data for param in required_params):
        return jsonify({
            "error": "Debe proporcionar al menos uno de los siguientes parámetros: cod_gen, sello_recepcion o num_control."
        }), 400

    # Recopilar criterios (aceptamos que "cod_gen" pueda ser una lista o un string)
    criteria = {}
    if 'cod_gen' in data:
        criteria['cod_gen'] = data['cod_gen']
    if 'sello_recepcion' in data:
        criteria['sello_recepcion'] = data['sello_recepcion']
    if 'num_control' in data:
        criteria['num_control'] = data['num_control']

    try:
        db = Database()
        field_conditions = []
        params = []
        for key, value in criteria.items():
            if isinstance(value, list):
                # Si es una lista, usamos la cláusula IN
                placeholders = ','.join(['%s'] * len(value))
                field_conditions.append(f"{key} IN ({placeholders})")
                params.extend(value)
            else:
                field_conditions.append(f"{key} = %s")
                params.append(value)
        # Actualiza solo las facturas no procesadas (procesada = 0)
        query = "UPDATE facturas SET procesada = 1 WHERE (" + " OR ".join(field_conditions) + ") AND procesada = 0"
        db.cursor.execute(query, tuple(params))
        db.connection.commit()
        updated = db.cursor.rowcount  # Número de facturas actualizadas
        db.close()
        if updated == 0:
            return jsonify({
                "status": "No se encontraron facturas para procesar, verifique de nuevo."
            }), 404
        return jsonify({
            "status": "Facturas procesadas exitosamente",
            "facturas_actualizadas": updated
        }), 200
    except Exception as e:
        logging.error(f"Error procesando facturas: {str(e)}")
        return jsonify({"error": str(e)}), 500

def row_to_dict(row, cursor):
    """Convierte una fila de la consulta a un diccionario usando los nombres de columnas."""
    return {cursor.description[i][0]: row[i] for i in range(len(row))}

@app.route('/facturas', methods=['GET'])
def obtener_facturas():
    """
    Devuelve todas las facturas insertadas en la base de datos.
    """
    try:
        db = Database()
        query = "SELECT * FROM facturas"
        db.cursor.execute(query)
        rows = db.cursor.fetchall()
        columns = [desc[0] for desc in db.cursor.description]
        facturas = [dict(zip(columns, row)) for row in rows]
        db.close()
        return jsonify(facturas), 200
    except Exception as e:
        logging.error(f"Error obteniendo facturas: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/factura', methods=['GET'])
def obtener_factura():
    """
    Devuelve una factura específica filtrada por alguno de los siguientes campos:
    - cod_gen (Código de generación)
    - sello_recepcion
    - num_control
    Al menos uno de estos parámetros debe ser proporcionado.
    """
    codigo_generacion = request.args.get('cod_gen')
    sello_recepcion = request.args.get('sello_recepcion')
    num_control = request.args.get('num_control')

    if not (codigo_generacion or sello_recepcion or num_control):
        return jsonify({"error": "Debe proporcionar al menos uno de: codigo_generacion, sello_recepcion o num_control"}), 400

    try:
        db = Database()
        conditions = []
        params = []
        if codigo_generacion:
            conditions.append("cod_gen = %s")
            params.append(codigo_generacion)
        if sello_recepcion:
            conditions.append("sello_recepcion = %s")
            params.append(sello_recepcion)
        if num_control:
            conditions.append("num_control = %s")
            params.append(num_control)
        # Se utiliza OR para buscar coincidencias en cualquiera de los campos
        query = "SELECT * FROM facturas WHERE " + " OR ".join(conditions)
        db.cursor.execute(query, tuple(params))
        row = db.cursor.fetchone()
        if row:
            columns = [desc[0] for desc in db.cursor.description]
            factura = dict(zip(columns, row))
            db.close()
            return jsonify(factura), 200
        else:
            db.close()
            return jsonify({"error": "Factura no encontrada"}), 404
    except Exception as e:
        logging.error(f"Error obteniendo factura: {str(e)}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
