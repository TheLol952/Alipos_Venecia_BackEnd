import imaplib
import time
import sys
import os
import json
import logging
import socket
from datetime import date, datetime
from email import policy
from email.parser import BytesParser
from dotenv import load_dotenv
from src.servicios.documentos import identificar_documento, nombre_archivo_seguro

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

# Contadores
total_correos = 0
archivos_dañados = 0
correos_ignorados = 0
total_documentos_descargados = 0

# ---------------------------- Conectar al servidor IMAP ----------------------------
def connect_to_email():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            #logging.info("🟢 Intentando conectar al servidor IMAP...")
            mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993, timeout=60)  # Puerto 993 y timeout 60s
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            mail.select("INBOX")
            #logging.info("✅ Conexión IMAP establecida con éxito.")
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
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Se utiliza la conexión 'mail' que ya se pasó como argumento.
            status, data = mail.uid('fetch', email_uid, "(BODY.PEEK[])")
            if status == "OK" and data != [None]:
                time.sleep(0.5)  # Tiempo de espera x correo
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

# ---------------------------- Procesar correos electrónicos ----------------------------
def process_emails(start_date, end_date):
    global total_correos, total_documentos_descargados, archivos_dañados, correos_ignorados

    # Obtener fecha actual mes y año
    today = date.today()
    year = today.year
    month = today.month

    #print(f"🗓️ Año tributario detectado automáticamente: {year}")
    #print(f"🗓️ Mes tributario detectado automáticamente: {str(month).zfill(2)}")

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
            sys.stdout.write("\rProcesando documentos ...")
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
                tipo_documento = None
                identificador_documento = None
                json_error = ""
                for candidate in json_candidates:
                    try:
                        candidate_content = candidate.get_payload(decode=True)
                        candidate_text = candidate_content.decode("utf-8-sig", errors="replace").strip()
                        candidate_data = json.loads(candidate_text)
                        tipo_candidato, identificador_candidato = identificar_documento(candidate_data)
                        valid_json_part = candidate
                        json_content = candidate_content
                        tipo_documento = tipo_candidato
                        identificador_documento = identificador_candidato
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
                nombre_base = nombre_archivo_seguro(identificador_documento)

                # Guardar JSON
                json_filename = f"{nombre_base}.json"
                json_path = os.path.join(folder_path, json_filename)
                with open(json_path, 'wb') as f:
                    f.write(json_content)
                logging.info(f"JSON guardado en: {json_path}")

                # Guardar PDF
                pdf_filename = f"{nombre_base}.pdf"
                pdf_path = os.path.join(folder_path, pdf_filename)
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                logging.info(f"PDF guardado en: {pdf_path}")

                total_documentos_descargados += 1
                logging.info(
                    f"Documento descargado: tipo={tipo_documento}, "
                    f"identificador={identificador_documento}"
                )
                mail.uid('STORE', uid, '+FLAGS', '\\Seen')

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
