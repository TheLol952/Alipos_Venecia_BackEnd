import imaplib
import email
import time
import sys
import os
import json
import logging
import socket
import sys
from datetime import date
from email import policy
from email.parser import BytesParser
from dotenv import load_dotenv
from datetime import datetime
from procedimientos.InsertarCompraMain import InsertarCompras
from pathlib import Path
#from servicios.services import recepcion_factura
#from core.conexion_oracle import get_connection

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Cargar variables de entorno
load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
PASSWORD = os.getenv("EMAIL_PASSWORD")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "facturas_test")

# Configuración de reconexión y tiempo de espera
MAX_RETRIES = 5
WAIT_TIME = 5
MAX_FAILED_CONNECTIONS = 10  # Si la conexión falla 10 veces seguidas, cerramos la sesión

# Contadores
total_correos = 0
correos_procesados = 0
archivos_dañados = 0
correos_ignorados = 0
total_facturas_descargadas = 0
total_facturas_insertadas = 0
failed_connections = 0  # Contador de fallos consecutivos en la conexión

# ---------------------------- Conectar al servidor IMAP ----------------------------
def connect_to_email():
    global failed_connections
    retries = 0
    while retries < MAX_RETRIES:
        try:
            logging.info("🟢 Intentando conectar al servidor IMAP...")
            mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993, timeout=60)  # Puerto 993 y timeout 60s
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            mail.select("INBOX")
            logging.info("✅ Conexión IMAP establecida con éxito.")
            failed_connections = 0
            return mail
        except Exception as e:  # Captura todos los errores
            retries += 1
            logging.warning(f"⚠️ Error en la conexión IMAP ({retries}/{MAX_RETRIES}): {str(e)}")
            time.sleep(WAIT_TIME * retries)
    logging.error("❌ No se pudo conectar después de varios intentos.")
    raise Exception("Error IMAP")

# ---------------------------- Obtener un correo específico ----------------------------
def fetch_email(mail, email_uid):
    """Obtiene un correo usando UID y maneja reconexiones."""
    global failed_connections
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Se utiliza la conexión 'mail' que ya se pasó como argumento.
            status, data = mail.uid('fetch', email_uid, "(BODY.PEEK[])")
            if status == "OK" and data != [None]:
                time.sleep(0.5)  # Tiempo de espera
                return data, mail
            else:
                logging.warning(f"⚠️ Fallo al recuperar UID {email_uid}. Reintentando...")
        except (imaplib.IMAP4.abort, socket.error, EOFError, imaplib.IMAP4.error) as e:
            logging.warning("La conexión IMAP se ha perdido, intentando reconectar...")
            mail = connect_to_email()
            mail.select("INBOX")
        retries += 1
        time.sleep(WAIT_TIME * retries)
    logging.error(f"❌ No se pudo recuperar el correo UID {email_uid}.")
    return None, mail

# ---------------------------- Formatear fecha para búsqueda en IMAP ----------------------------
def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%b-%Y")

# ---------------------------- Extraer código de generación y número de control ----------------------------
def extract_codigo_generacion(json_text, uid_str):
    """Extrae el código de generación y número de control desde el JSON del DTE."""
    try:
        # Intentar cargar como JSON estándar
        json_data = json.loads(json_text)
        
        # Fallback para JSON con BOM (caracteres especiales al inicio)
        if not isinstance(json_data, dict):
            json_text_clean = json_text.lstrip('\ufeff')  # Eliminar BOM
            json_data = json.loads(json_text_clean)
            
        return json_data["identificacion"]["codigoGeneracion"], json_data["identificacion"]["numeroControl"]
    except Exception as e:
        logging.error(f"🚨 Error procesando JSON en UID {uid_str}: {str(e)}")
        return f"Archivo_Dañado_{uid_str}", f"Archivo_Dañado_{uid_str}"

# ---------------------------- Crear estructura de carpetas ----------------------------
def ensure_folder_structure(year, month):
    path = os.path.join(DOWNLOAD_FOLDER, str(year), f"{month:02d}")
    os.makedirs(path, exist_ok=True)
    return path
# ---------------------------- Crear carpeta para archivos dañados, segun el año y periodo ----------------------------
def ensure_damaged_folder(year, month):
    folder_path = ensure_folder_structure(year, month)
    path = os.path.join(folder_path, "Archivos_Dañados")
    os.makedirs(path, exist_ok=True)
    return path

# ---------------------------- Crear carpeta para compras pendientes (Que no se insertaron en la DB), segun el año y periodo ----------------------------
def ensure_pending_folder(year, month):
    base = ensure_folder_structure(year, month)
    pending = os.path.join(base, "Compras_Pendientes")
    os.makedirs(pending, exist_ok=True)
    return pending  

# ---------------------------- Procesar correos electrónicos ----------------------------
def process_emails(start_date, end_date):
    global total_correos, total_facturas_descargadas, total_facturas_insertadas, archivos_dañados, correos_ignorados

    # Obtener fecha actual mes y año
    today = date.today()
    year = today.year
    month = today.month

    print(f"🗓️ Año tributario detectado automáticamente: {year}")
    print(f"🗓️ Mes tributario detectado automáticamente: {str(month).zfill(2)}")

    try:
        mail = connect_to_email()
    except Exception as e:
        logging.error(f"No se pudo conectar al correo: {e}")
        return

    since_date = format_date(start_date)
    before_date = format_date(end_date)
    
    try:
        status, messages = mail.uid('search', None, f"(SINCE {since_date} BEFORE {before_date})")
        if status != "OK":
            logging.error("Error buscando correos en IMAP.")
            return

        email_uids = messages[0].split()
        total_correos = len(email_uids)

        for i, uid_bytes in enumerate(email_uids):
            sys.stdout.write("\rProcesando facturas ...")
            sys.stdout.flush()
            try:
                uid = uid_bytes.decode('utf-8')
            except UnicodeDecodeError:
                uid = uid_bytes.hex()  # Fallback para UIDs no UTF-8

            try:
                # Obtener correo manteniendo la conexión
                data, mail = fetch_email(mail, uid)
                if not data or not data[0]:
                    continue

                msg = BytesParser(policy=policy.default).parsebytes(data[0][1])
                json_candidates = []
                pdf_candidates = []

                # Recorrer todas las partes (adjuntos)
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    filename = (part.get_filename() or "").strip()
                    # Recopilar candidatos para JSON (usando filename en minúsculas)
                    if filename.lower().endswith(".json") or "json" in part.get_content_type().lower():
                        json_candidates.append(part)
                    # Recopilar candidatos para PDF (detectados con extensión ".pdf" o content-type)
                    if filename.lower().endswith(".pdf") or "pdf" in part.get_content_type().lower():
                        pdf_candidates.append(part)

                # Si el correo no tiene ningún candidato JSON, se asume que no es una factura electrónica.
                if not json_candidates:
                    correos_ignorados += 1
                    continue

                # Intentar obtener un candidato JSON válido
                valid_json_part = None
                json_content = None
                json_data = None
                json_error = ""
                for candidate in json_candidates:
                    try:
                        candidate_content = candidate.get_payload(decode=True)
                        candidate_text = candidate_content.decode("utf-8-sig", errors="replace").strip()
                        candidate_data = json.loads(candidate_text)
                        # Validar campos requeridos
                        required_fields = {
                            "identificacion": ["codigoGeneracion", "numeroControl"],
                            "resumen": []
                        }
                        for section, fields in required_fields.items():
                            if section not in candidate_data:
                                raise ValueError(f"Falta la sección: {section}")
                            for field in fields:
                                if field not in candidate_data[section]:
                                    raise ValueError(f"Falta el campo: {section}.{field}")
                        valid_json_part = candidate
                        json_content = candidate_content
                        json_data = candidate_data
                        break
                    except Exception as ex:
                        json_error = str(ex)
                        continue

                # Intentar obtener un candidato PDF válido
                valid_pdf_part = None
                pdf_content = None
                for candidate in pdf_candidates:
                    candidate_payload = candidate.get_payload(decode=True)
                    if candidate_payload and candidate_payload.startswith(b"%PDF-"):
                        valid_pdf_part = candidate
                        pdf_content = candidate_payload
                        break

                # Si hay candidatos JSON pero ninguno es válido (y hay al menos un PDF),
                # se considera que la factura tiene JSON corrupto y se descarga el PDF como dañado.
                if not valid_json_part:
                    archivos_dañados += 1
                    message = f"UID {uid}: Error crítico en JSON: {json_error}\n"
                    logging.error(message)
                    with open("ignored_damaged.txt", "a", encoding="utf-8") as f:
                        f.write(message)
                    if pdf_candidates:
                        for candidate in pdf_candidates:
                            candidate_payload = candidate.get_payload(decode=True)
                            if candidate_payload and candidate_payload.startswith(b"%PDF-"):
                                damaged_pdf = candidate_payload
                                break
                        else:
                            damaged_pdf = pdf_candidates[0].get_payload(decode=True)
                        damaged_folder = ensure_damaged_folder(year, month)
                        damaged_pdf_path = os.path.join(damaged_folder, f"Archivo_dañado_{uid}.pdf")
                        with open(damaged_pdf_path, 'wb') as f:
                            f.write(damaged_pdf)
                        logging.info(f"PDF corrupto guardado en: {damaged_pdf_path}")
                    continue

                # Si no se encontró un PDF válido, se registra y se guarda el primero como dañado.
                if not valid_pdf_part:
                    with open("incomplete_files.txt", "a", encoding="utf-8") as f:
                        f.write(f"UID {uid}: No se encontró PDF válido.\n")
                    if pdf_candidates:
                        damaged_folder = ensure_damaged_folder(year, month)
                        damaged_pdf_path = os.path.join(damaged_folder, f"Archivo_dañado_{uid}.pdf")
                        with open(damaged_pdf_path, 'wb') as f:
                            f.write(pdf_candidates[0].get_payload(decode=True))
                    continue

                # Guardar archivos en disco (para facturas válidas se guardan ambos archivos)
                folder_path = ensure_folder_structure(year, month)
                codigo_generacion = json_data["identificacion"]["codigoGeneracion"]

                # Guardar JSON
                json_filename = f"{codigo_generacion}.json"
                json_path = os.path.join(folder_path, json_filename)
                with open(json_path, 'wb') as f:
                    f.write(json_content)
                logging.info(f"JSON guardado en: {json_path}")

                # Guardar PDF
                pdf_filename = f"{codigo_generacion}.pdf"
                pdf_path = os.path.join(folder_path, pdf_filename)
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                logging.info(f"PDF guardado en: {pdf_path}")

                total_facturas_descargadas += 1

                # Insertar en BD solo si ambos archivos son válidos
                try:
                    resultado = InsertarCompras(json_data)
                    #print(f"→ Resultado de InsertarCompras: {resultado!r}")

                    if resultado == 1:
                        total_facturas_insertadas += 1
                        print(f"✅ [INSERTADA] CódigoGeneración={json_data['identificacion']['codigoGeneracion']} → factura #{total_facturas_insertadas}")
                        try:
                            mail.uid('STORE', uid, '+FLAGS', '\\Seen')
                        except Exception as e:
                            logging.error(f"❌ Error marcando como visto el correo UID {uid}: {e}")
                    elif resultado == 2:
                        print(f"⚠️ [OMITIDA] CódigoGeneración={json_data['identificacion']['codigoGeneracion']}  (motivo: Duplicada)")
                        # Opcional: marcamos también como leído si queremos saltar ese correo
                        try:
                            mail.uid('STORE', uid, '+FLAGS', '\\Seen')
                        except:
                            pass
                    else:
                        # Si NO se pudo insertar por error o validación, movemos ambos archivos a “Compras Pendientes”
                        pending_folder = ensure_pending_folder(year, month)

                        # Construimos las rutas destino usando el mismo nombre de archivo
                        dest_json = os.path.join(pending_folder, os.path.basename(json_path))
                        dest_pdf  = os.path.join(pending_folder, os.path.basename(pdf_path))

                            # Renombramos (mueve) los archivos
                        os.replace(json_path, dest_json)
                        os.replace(pdf_path,  dest_pdf)

                        logging.warning(
                            f"→ Factura {json_data['identificacion']['codigoGeneracion']} "
                            f"no insertada (estado={resultado}), movida a: {pending_folder}"
                        )

                except Exception as e:
                    logging.error(f"❌ Error insertando factura: {str(e)}")
                    continue

                # Mantener conexión activa
                if i % 5 == 0:
                    try:
                        mail.noop()
                    except Exception:
                        mail = connect_to_email()

            except Exception as e:
                logging.error(f"🔥 Error procesando UID {uid}: {str(e)}")
    finally:
        try:
            mail.close()
            mail.logout()
        except Exception:
            pass

#----------------------------- Guardar archivos ----------------------------
def save_file(filepath, file_data):
    """Guarda archivos en la ruta especificada."""
    try:
        with open(filepath, "wb") as f:
            f.write(file_data.get_payload(decode=True))
    except Exception as e:
        logging.error(f"Error guardando archivo {filepath}: {e}")

#----------------------------- Inicio del script ----------------------------
if __name__ == "__main__":
    start_date = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
    end_date = input("Ingrese la fecha de fin (YYYY-MM-DD): ")

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    process_emails(start_date, end_date)

    # 📌 **Resumen detallado**
    logging.info("\n--- Resumen del procesamiento ---")
    logging.info(f"📩 Total de correos revisados: {total_correos}")
    logging.info(f"📥 Total de facturas descargadas: {total_facturas_descargadas}")
    logging.info(f"✅ Facturas insertadas en la BD: {total_facturas_insertadas}")
    logging.info(f"📛 Archivos dañados: {archivos_dañados}")
    logging.info(f"🚫 Correos ignorados o no válidos: {correos_ignorados or 0}")
