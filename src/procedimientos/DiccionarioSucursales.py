import unicodedata
import json
import oracledb
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from core.conexion_oracle import get_connection
from rapidfuzz import fuzz, process

# Cargar configuración de entorno
load_dotenv()

# Proveedores generales con una sola dirección, que pueden llegar a ofrecer servicios en diferentes sucursales
PROVEEDORES_GENERALES = [
    "06140107911039",  # COSASE
    "06140312931018",  # BANCO DE AMÉRICA
    "02100501991017",  # COSELSA
    # Agrega más si es necesario
]

# Normalizador de texto
def normalize(text):
    if not text:
        return ""
    text = text.upper()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    return text

# Normalizador de NIT, agrega los guiones al nit del json, siguiendo esta estructura
# 0614-021203-108-6
def normalize_nit(nit):
    if not nit:
        return ""
    # Eliminar caracteres no numéricos
    nit = ''.join(filter(str.isdigit, nit))
    # Formatear el NIT con guiones
    if len(nit) == 14:
        return f"{nit[:4]}-{nit[4:10]}-{nit[10:13]}-{nit[13:]}"
    return nit

# Cargar diccionario de sucursales desde la BD
def cargar_diccionario_sucursales():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT SUCURSAL, PALABRA_CLAVE FROM DICCIONARIO_SUCURSALES")
                rows = cur.fetchall()
                
                diccionario = {}
                for sucursal, palabra_clave in rows:
                    sucursal_norm = normalize(sucursal)
                    palabra_clave_norm = normalize(palabra_clave)
                    diccionario.setdefault(sucursal_norm, []).append(palabra_clave_norm)
                
                return diccionario
    except Exception as e:
        print("❌ Error al cargar el diccionario de sucursales:", e)
        return {}

# Identifica la sucursal según la descripción y el diccionario, usando fuzzy matching
def identificar_sucursal(descripcion, diccionario, umbral=80):
    """
    descripcion: str
    diccionario: dict[str, list[str]] donde la clave es la sucursal y el valor lista de palabras clave normalizadas
    umbral: int (0-100), porcentaje mínimo de similitud para aceptar un fuzzy match
    """
    desc_normalizado = normalize(descripcion)

    # 1) Coincidencia exacta parcial (keyword in description)
    for sucursal, claves in diccionario.items():
        for clave in claves:
            if clave in desc_normalizado:
                return sucursal

    # 2) Fuzzy matching: evaluar cada clave y tomar la mejor puntuación
    mejor_sucursal = None
    mejor_puntaje = 0
    for sucursal, claves in diccionario.items():
        for clave in claves:
            puntaje = fuzz.partial_ratio(desc_normalizado, clave)
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_sucursal = sucursal

    if mejor_puntaje >= umbral:
        return mejor_sucursal

    return "SUCURSAL_DESCONOCIDA"

# En caso no detecte la sucursal en el diccionario manual, busca en la tabla de aprendizaje
# (sin cambios en fuzzy logic aquí)
def identificar_sucursal_auto(descripcion, diccionario):
    desc_normalizado = normalize(descripcion)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT SUCURSAL FROM DICCIONARIO_COMPRAS_AUTO WHERE DIRECCION = :direccion",
                    [desc_normalizado]
                )
                row = cur.fetchone()
                if row:
                    return row[0]
    except Exception as e:
        print("❌ Error al buscar en DICCIONARIO_COMPRAS_AUTO:", e)
    return "SUCURSAL_DESCONOCIDA_AUTO"

# Actualiza la tabla DICCIONARIO_SUCURSALES desde los datos en DICCIONARIO_COMPRAS_AUTO
def actualizar_diccionario_sucursales():
    """
    Actualiza la tabla DICCIONARIO_SUCURSALES con la sucursal más reciente por cada dirección
    registrada en DICCIONARIO_COMPRAS_AUTO.
    """
    print("📥 Actualizando DICCIONARIO_SUCURSALES con nuevas referencias...")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Obtener la sucursal más reciente para cada dirección
                cur.execute("""
                    SELECT DIRECCION, SUCURSAL
                    FROM (
                        SELECT DIRECCION,
                                SUCURSAL,
                                ROW_NUMBER() OVER (
                                    PARTITION BY DIRECCION
                                    ORDER BY ULTIMA_COMPRA DESC
                                ) AS RN
                        FROM DICCIONARIO_COMPRAS_AUTO
                    ) sub
                    WHERE RN = 1
                """)
                rows = cur.fetchall()

                inserts = 0
                updates = 0
                for direccion, sucursal in rows:
                    direccion_norm = normalize(direccion)
                    sucursal_norm = normalize(sucursal)

                    # Verificar existencia en DICCIONARIO_SUCURSALES
                    cur.execute(
                        """
                        SELECT SUCURSAL
                        FROM DICCIONARIO_SUCURSALES
                        WHERE PALABRA_CLAVE = :direccion
                        """,
                        direccion=direccion_norm
                    )
                    result = cur.fetchone()

                    if result is None:
                        # Insertar nueva entrada
                        cur.execute(
                            """
                            INSERT INTO DICCIONARIO_SUCURSALES (
                                ID, SUCURSAL, PALABRA_CLAVE
                            ) VALUES (
                                SEQ_DICC_SUCURSALES.NEXTVAL,
                                :sucursal,
                                :direccion
                            )
                            """,
                            sucursal=sucursal_norm,
                            direccion=direccion_norm
                        )
                        inserts += 1
                    elif result[0] != sucursal_norm:
                        # Actualizar sucursal existente
                        cur.execute(
                            """
                            UPDATE DICCIONARIO_SUCURSALES
                            SET SUCURSAL = :sucursal
                            WHERE PALABRA_CLAVE = :direccion
                            """,
                            sucursal=sucursal_norm,
                            direccion=direccion_norm
                        )
                        updates += 1

                conn.commit()
                print(f"✅ Diccionario actualizado. Inserciones: {inserts}, Actualizaciones: {updates}")
    except Exception as e:
        print("❌ Error actualizando el diccionario de sucursales:", e)

# Esta funcion se encargara de verificar si la direccion dentro del json, es la direccion de un proveedor que tiene una
# Sola direccion, pero ofrece productos en diferentes sucursales, por lo que se verificara de otra manera
def identificar_sucursal_por_descripcion(data):
    """
    Identifica la sucursal a partir de la descripción del ítem en el JSON,
    buscando coincidencias con nombres de sucursales o municipios relacionados.
    """
    descripcion = ""
    try:
        descripcion = data["cuerpoDocumento"][0]["descripcion"]
    except (KeyError, IndexError):
        print("⚠️ No se encontró la descripción en 'cuerpoDocumento[0] → descripcion'.")
        return "SUCURSAL_DESCONOCIDA_POR_DESCRIPCION"

    desc_normalizado = normalize(descripcion)

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                # Buscar coincidencias con nombres de sucursales
                cursor.execute("SELECT NOMBRE_CON_ENTIDAD FROM CON_ENTIDADES")
                sucursales = cursor.fetchall()
                for (nombre_sucursal,) in sucursales:
                    if nombre_sucursal and normalize(nombre_sucursal) in desc_normalizado:
                        return nombre_sucursal

                # Buscar coincidencias con nombres de municipios
                cursor.execute("SELECT VALOR FROM DTE_MUNICIPIOS_013")
                municipios = cursor.fetchall()
                for (nombre_municipio,) in municipios:
                    if nombre_municipio and normalize(nombre_municipio) in desc_normalizado:
                        return nombre_municipio

    except Exception as e:
        print("❌ Error al buscar en las tablas de sucursales o municipios:", e)

    return "SUCURSAL_DESCONOCIDA_POR_DESCRIPCION"

# Analiza un JSON de compra
def analizar_json_dict(data):
    # Extraer descripción desde el campo correcto
    descripcion = data.get("emisor", {}).get("direccion", {}).get("complemento", "")

    # Extraer NIT
    nit = data.get("emisor", {}).get("nit", "")
    # Normalizar nit (Se le extraeron los guiones y espacios)
    nit = normalize_nit(nit)
    print(f"🔍 NIT del proveedor: {nit}")

    # Cargar diccionario desde la base de datos
    diccionario = cargar_diccionario_sucursales()

    # Identificar sucursal por diccionario principal
    sucursal = identificar_sucursal(descripcion, diccionario)

    # Si no se encuentra, buscar por dirección en la tabla de aprendizaje
    if sucursal == "SUCURSAL_DESCONOCIDA":
        print("🔍 No se encontró coincidencia en DICCIONARIO_SUCURSALES. Buscando en DICCIONARIO_COMPRAS_AUTO...")
        sucursal = identificar_sucursal_auto(descripcion, diccionario)

    # Si aún no se encuentra, y el proveedor es general, analizar por descripción del ítem
    if sucursal == "SUCURSAL_DESCONOCIDA_AUTO" and nit in PROVEEDORES_GENERALES:
        print("🔍 Proveedor general detectado. Intentando identificar sucursal desde la descripción del ítem...")
        sucursal = identificar_sucursal_por_descripcion(data)

    # Resultado final
    print("\n✅ Resultado del análisis:")
    print(f"➡️ Sucursal detectada: {sucursal}")
    print(f"➡️ Descripción detectada:\n{descripcion.strip()}")

    # Actualizar diccionario con nuevas entradas
    actualizar_diccionario_sucursales()
    
# 🚀 Punto de entrada público
def IniciarProceso(data):
    try:
        if not isinstance(data, dict):
            raise ValueError("⚠️ El argumento debe ser un diccionario JSON (objeto de Python).")
        analizar_json_dict(data)
    except Exception as e:
        print("❌ Error al ejecutar el proceso:", e)

# 🔌 Ejecutar prueba automática si se corre el script directamente
if __name__ == "__main__":
    # Datos de prueba
    data_ejemplo = json.loads(input("Ingrese el JSON a analizar: ")) 

    # Llamar a la función de inicio del proceso}
    
    print("🚀 Iniciando prueba automática...")
    IniciarProceso(data_ejemplo)
    print("🏁 Prueba completada")