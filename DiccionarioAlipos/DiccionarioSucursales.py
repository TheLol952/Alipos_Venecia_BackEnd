import unicodedata
import json
import oracledb
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Agregar el directorio raíz al PATH de Python
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from conexion_oracle import get_connection

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

# Identifica la sucursal según la descripción y el diccionario
def identificar_sucursal(descripcion, diccionario):
    desc_normalizado = normalize(descripcion)
    for sucursal, claves in diccionario.items():
        for clave in claves:
            if clave in desc_normalizado:
                return sucursal
    return "SUCURSAL_DESCONOCIDA"

# En caso no detecte la sucursal en el diccionario manual, busca en la tabla de aprendizaje
def identificar_sucursal_auto(descripcion, diccionario):
    desc_normalizado = normalize(descripcion)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT SUCURSAL FROM DICCIONARIO_COMPRAS_AUTO WHERE DIRECCION = :direccion", [desc_normalizado])
                row = cur.fetchone()
                if row:
                    return row[0]
    except Exception as e:
        print("❌ Error al buscar en DICCIONARIO_COMPRAS_AUTO:", e)
    return "SUCURSAL_DESCONOCIDA_AUTO"

# Actualiza la tabla DICCIONARIO_SUCURSALES desde los datos en DICCIONARIO_COMPRAS_AUTO
def actualizar_diccionario_sucursales():
    print("\n📥 Actualizando DICCIONARIO_SUCURSALES con nuevas referencias...")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Buscar la sucursal más reciente para cada dirección
                cur.execute("""
                    SELECT DIRECCION, SUCURSAL
                    FROM (
                        SELECT DIRECCION, SUCURSAL,
                               ROW_NUMBER() OVER (PARTITION BY DIRECCION ORDER BY ULTIMA_COMPRA DESC) AS RN
                        FROM DICCIONARIO_COMPRAS_AUTO
                        WHERE SUCURSAL IS NOT NULL AND DIRECCION IS NOT NULL
                    )
                    WHERE RN = 1
                """)
                rows = cur.fetchall()

                inserts = 0
                updates = 0
                for direccion, sucursal in rows:
                    direccion_norm = normalize(direccion)
                    sucursal_norm = normalize(sucursal)

                    # Verificar si ya existe para esa palabra clave
                    cur.execute("""
                        SELECT SUCURSAL FROM DICCIONARIO_SUCURSALES
                        WHERE PALABRA_CLAVE = :direccion
                    """, [direccion_norm])
                    result = cur.fetchone()

                    if result is None:
                        # Insertar si no existe
                        cur.execute("""
                            INSERT INTO DICCIONARIO_SUCURSALES (ID, SUCURSAL, PALABRA_CLAVE)
                            VALUES (SEQ_DICC_SUCURSALES.NEXTVAL, :sucursal, :direccion)
                        """, [sucursal_norm, direccion_norm])
                        inserts += 1
                    elif result[0] != sucursal_norm:
                        # Actualizar si cambió la sucursal
                        cur.execute("""
                            UPDATE DICCIONARIO_SUCURSALES
                            SET SUCURSAL = :sucursal
                            WHERE PALABRA_CLAVE = :direccion
                        """, [sucursal_norm, direccion_norm])
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
    data_ejemplo = {
        "identificacion": {
            "version": 3,
            "ambiente": "01",
            "tipoDte": "03",
            "numeroControl": "DTE-03-S003P003-000000000042583",
            "codigoGeneracion": "1AC28DF3-6D16-4B92-A427-0174C3B9E505",
            "tipoModelo": 1,
            "tipoOperacion": 1,
            "tipoContingencia": 'null',
            "motivoContin": 'null',
            "fecEmi": "2024-11-24",
            "horEmi": "12:16:16",
            "tipoMoneda": "USD"
        },
        "documentoRelacionado": 'null',
        "emisor": {
            "nit": "06142409151044",
            "nrc": "2443968",
            "nombre": "GRUPO EDEM, S. A. DE C. V.",
            "codActividad": "47300",
            "descActividad": "VENTA DE COMBUSTIBLES, LUBRICANTES Y OTROS (GASOLINERAS)",
            "nombreComercial": "TEXACO CARRETERA DE ORO",
            "tipoEstablecimiento": "01",
            "direccion": {
            "departamento": "06",
            "municipio": "20",
            "complemento": "CARR. DE ORO KM. 8, # 3, ENTRE SAN BARTOLO Y SAN MARTIN, TONACATEPEQUE, TONACATEPEQUE"
            },
            "telefono": "77435970",
            "correo": "texacocarreteraorodte@grupofe.com.sv",
            "codEstableMH": "S003",
            "codEstable": 'null',
            "codPuntoVentaMH": "P003",
            "codPuntoVenta": 'null'
        },
        "receptor": {
            "nit": "14081511540023",
            "nrc": "1529708",
            "nombre": "BENITEZ CALISTRO",
            "codActividad": "46633",
            "descActividad": "VIDRIERIAS",
            "nombreComercial": 'null',
            "direccion": {
            "departamento": "06",
            "municipio": "20",
            "complemento": "10° CALLE OTE. # 224, CENTRO HISTORICO, MEDIA CUADRA AL NTE DE MERCADO BELLOSO, SAN SALVADOR"
            },
            "telefono": "61035096",
            "correo": " facturas@grupovenecia.net"
        },
        "otrosDocumentos": 'null',
        "ventaTercero": 'null',
        "cuerpoDocumento": [
            {
            "numItem": 1,
            "tipoItem": 1,
            "numeroDocumento": 'null',
            "cantidad": 4.336,
            "codigo": "4",
            "codTributo": 'null',
            "uniMedida": 22,
            "descripcion": "SUPER AUTO",
            "precioUni": 3.0,
            "montoDescu": 0.0,
            "ventaNoSuj": 0.0,
            "ventaExenta": 0.0,
            "ventaGravada": 13.01,
            "noGravado": 0.0,
            "tributos": [
                "20",
                "D1",
                "C8"
            ],
            "psv": 0.0
            }
        ],
        "resumen": {
            "totalNoSuj": 0.0,
            "totalExenta": 0.0,
            "totalGravada": 13.01,
            "subTotalVentas": 13.01,
            "descuNoSuj": 0.0,
            "descuExenta": 0.0,
            "descuGravada": 0.08,
            "porcentajeDescuento": 0.0,
            "totalDescu": 0.08,
            "tributos": [
            {
                "codigo": "20",
                "descripcion": "Impuesto al Valor Agregado 13%",
                "valor": 1.68
            },
            {
                "codigo": "D1",
                "descripcion": "FOVIAL ($0.20 Ctvs. por galón)",
                "valor": 0.87
            },
            {
                "codigo": "C8",
                "descripcion": "COTRANS ($0.10 Ctvs. por galón)",
                "valor": 0.43
            }
            ],
            "subTotal": 12.93,
            "ivaPerci1": 0.0,
            "ivaRete1": 0.0,
            "reteRenta": 0.0,
            "montoTotalOperacion": 15.91,
            "totalNoGravado": 0.0,
            "totalPagar": 15.91,
            "totalLetras": "QUINCE 91/100",
            "saldoFavor": 0.0,
            "condicionOperacion": 1,
            "pagos": 'null',
            "numPagoElectronico": 'null'
        },
        "extension": {
            "nombEntrega": 'null',
            "docuEntrega": 'null',
            "nombRecibe": 'null',
            "docuRecibe": 'null',
            "observaciones": "",
            "placaVehiculo": 'null'
        },
        "apendice": 'null',
        "ResponseMH": {
            "version": 2,
            "ambiente": "01",
            "versionApp": 2,
            "estado": "PROCESADO",
            "codigoGeneracion": "1AC28DF3-6D16-4B92-A427-0174C3B9E505",
            "numeroControl": 'null',
            "selloRecibido": "20245F6EC17F049F4B1A8D4B61A75A2BB71DKHIQ",
            "fhProcesamiento": "24/11/2024 12:16:19",
            "codigoMsg": "001",
            "descripcionMsg": "RECIBIDO",
            "observaciones": []
        },
        "firmaElectronica": "eyJhbGciOiJSUzUxMiJ9.ew0KICAiaWRlbnRpZmljYWNpb24iIDogew0KICAgICJ2ZXJzaW9uIiA6IDMsDQogICAgImFtYmllbnRlIiA6ICIwMSIsDQogICAgInRpcG9EdGUiIDogIjAzIiwNCiAgICAibnVtZXJvQ29udHJvbCIgOiAiRFRFLTAzLVMwMDNQMDAzLTAwMDAwMDAwMDA0MjU4MyIsDQogICAgImNvZGlnb0dlbmVyYWNpb24iIDogIjFBQzI4REYzLTZEMTYtNEI5Mi1BNDI3LTAxNzRDM0I5RTUwNSIsDQogICAgInRpcG9Nb2RlbG8iIDogMSwNCiAgICAidGlwb09wZXJhY2lvbiIgOiAxLA0KICAgICJ0aXBvQ29udGluZ2VuY2lhIiA6IG51bGwsDQogICAgIm1vdGl2b0NvbnRpbiIgOiBudWxsLA0KICAgICJmZWNFbWkiIDogIjIwMjQtMTEtMjQiLA0KICAgICJob3JFbWkiIDogIjEyOjE2OjE2IiwNCiAgICAidGlwb01vbmVkYSIgOiAiVVNEIg0KICB9LA0KICAiZG9jdW1lbnRvUmVsYWNpb25hZG8iIDogbnVsbCwNCiAgImVtaXNvciIgOiB7DQogICAgIm5pdCIgOiAiMDYxNDI0MDkxNTEwNDQiLA0KICAgICJucmMiIDogIjI0NDM5NjgiLA0KICAgICJub21icmUiIDogIkdSVVBPIEVERU0sIFMuIEEuIERFIEMuIFYuIiwNCiAgICAiY29kQWN0aXZpZGFkIiA6ICI0NzMwMCIsDQogICAgImRlc2NBY3RpdmlkYWQiIDogIlZFTlRBIERFIENPTUJVU1RJQkxFUywgTFVCUklDQU5URVMgWSBPVFJPUyAoR0FTT0xJTkVSQVMpIiwNCiAgICAibm9tYnJlQ29tZXJjaWFsIiA6ICJURVhBQ08gQ0FSUkVURVJBIERFIE9STyIsDQogICAgInRpcG9Fc3RhYmxlY2ltaWVudG8iIDogIjAxIiwNCiAgICAiZGlyZWNjaW9uIiA6IHsNCiAgICAgICJkZXBhcnRhbWVudG8iIDogIjA2IiwNCiAgICAgICJtdW5pY2lwaW8iIDogIjIwIiwNCiAgICAgICJjb21wbGVtZW50byIgOiAiQ0FSUi4gREUgT1JPIEtNLiA4LCAjIDMsIEVOVFJFIFNBTiBCQVJUT0xPIFkgU0FOIE1BUlRJTiwgVE9OQUNBVEVQRVFVRSwgVE9OQUNBVEVQRVFVRSINCiAgICB9LA0KICAgICJ0ZWxlZm9ubyIgOiAiNzc0MzU5NzAiLA0KICAgICJjb3JyZW8iIDogInRleGFjb2NhcnJldGVyYW9yb2R0ZUBncnVwb2ZlLmNvbS5zdiIsDQogICAgImNvZEVzdGFibGVNSCIgOiAiUzAwMyIsDQogICAgImNvZEVzdGFibGUiIDogbnVsbCwNCiAgICAiY29kUHVudG9WZW50YU1IIiA6ICJQMDAzIiwNCiAgICAiY29kUHVudG9WZW50YSIgOiBudWxsDQogIH0sDQogICJyZWNlcHRvciIgOiB7DQogICAgIm5pdCIgOiAiMTQwODE1MTE1NDAwMjMiLA0KICAgICJucmMiIDogIjE1Mjk3MDgiLA0KICAgICJub21icmUiIDogIkJFTklURVogQ0FMSVNUUk8iLA0KICAgICJjb2RBY3RpdmlkYWQiIDogIjQ2NjMzIiwNCiAgICAiZGVzY0FjdGl2aWRhZCIgOiAiVklEUklFUklBUyIsDQogICAgIm5vbWJyZUNvbWVyY2lhbCIgOiBudWxsLA0KICAgICJkaXJlY2Npb24iIDogew0KICAgICAgImRlcGFydGFtZW50byIgOiAiMDYiLA0KICAgICAgIm11bmljaXBpbyIgOiAiMjAiLA0KICAgICAgImNvbXBsZW1lbnRvIiA6ICIxMMKwIENBTExFIE9URS4gIyAyMjQsIENFTlRSTyBISVNUT1JJQ08sIE1FRElBIENVQURSQSBBTCBOVEUgREUgTUVSQ0FETyBCRUxMT1NPLCBTQU4gU0FMVkFET1IiDQogICAgfSwNCiAgICAidGVsZWZvbm8iIDogIjYxMDM1MDk2IiwNCiAgICAiY29ycmVvIiA6ICIgZmFjdHVyYXNAZ3J1cG92ZW5lY2lhLm5ldCINCiAgfSwNCiAgIm90cm9zRG9jdW1lbnRvcyIgOiBudWxsLA0KICAidmVudGFUZXJjZXJvIiA6IG51bGwsDQogICJjdWVycG9Eb2N1bWVudG8iIDogWyB7DQogICAgIm51bUl0ZW0iIDogMSwNCiAgICAidGlwb0l0ZW0iIDogMSwNCiAgICAibnVtZXJvRG9jdW1lbnRvIiA6IG51bGwsDQogICAgImNhbnRpZGFkIiA6IDQuMzM2LA0KICAgICJjb2RpZ28iIDogIjQiLA0KICAgICJjb2RUcmlidXRvIiA6IG51bGwsDQogICAgInVuaU1lZGlkYSIgOiAyMiwNCiAgICAiZGVzY3JpcGNpb24iIDogIlNVUEVSIEFVVE8iLA0KICAgICJwcmVjaW9VbmkiIDogMy4wLA0KICAgICJtb250b0Rlc2N1IiA6IDAuMCwNCiAgICAidmVudGFOb1N1aiIgOiAwLjAsDQogICAgInZlbnRhRXhlbnRhIiA6IDAuMCwNCiAgICAidmVudGFHcmF2YWRhIiA6IDEzLjAxLA0KICAgICJub0dyYXZhZG8iIDogMC4wLA0KICAgICJ0cmlidXRvcyIgOiBbICIyMCIsICJEMSIsICJDOCIgXSwNCiAgICAicHN2IiA6IDAuMA0KICB9IF0sDQogICJyZXN1bWVuIiA6IHsNCiAgICAidG90YWxOb1N1aiIgOiAwLjAsDQogICAgInRvdGFsRXhlbnRhIiA6IDAuMCwNCiAgICAidG90YWxHcmF2YWRhIiA6IDEzLjAxLA0KICAgICJzdWJUb3RhbFZlbnRhcyIgOiAxMy4wMSwNCiAgICAiZGVzY3VOb1N1aiIgOiAwLjAsDQogICAgImRlc2N1RXhlbnRhIiA6IDAuMCwNCiAgICAiZGVzY3VHcmF2YWRhIiA6IDAuMDgsDQogICAgInBvcmNlbnRhamVEZXNjdWVudG8iIDogMC4wLA0KICAgICJ0b3RhbERlc2N1IiA6IDAuMDgsDQogICAgInRyaWJ1dG9zIiA6IFsgew0KICAgICAgImNvZGlnbyIgOiAiMjAiLA0KICAgICAgImRlc2NyaXBjaW9uIiA6ICJJbXB1ZXN0byBhbCBWYWxvciBBZ3JlZ2FkbyAxMyUiLA0KICAgICAgInZhbG9yIiA6IDEuNjgNCiAgICB9LCB7DQogICAgICAiY29kaWdvIiA6ICJEMSIsDQogICAgICAiZGVzY3JpcGNpb24iIDogIkZPVklBTCAoJDAuMjAgQ3R2cy4gcG9yIGdhbMOzbikiLA0KICAgICAgInZhbG9yIiA6IDAuODcNCiAgICB9LCB7DQogICAgICAiY29kaWdvIiA6ICJDOCIsDQogICAgICAiZGVzY3JpcGNpb24iIDogIkNPVFJBTlMgKCQwLjEwIEN0dnMuIHBvciBnYWzDs24pIiwNCiAgICAgICJ2YWxvciIgOiAwLjQzDQogICAgfSBdLA0KICAgICJzdWJUb3RhbCIgOiAxMi45MywNCiAgICAiaXZhUGVyY2kxIiA6IDAuMCwNCiAgICAiaXZhUmV0ZTEiIDogMC4wLA0KICAgICJyZXRlUmVudGEiIDogMC4wLA0KICAgICJtb250b1RvdGFsT3BlcmFjaW9uIiA6IDE1LjkxLA0KICAgICJ0b3RhbE5vR3JhdmFkbyIgOiAwLjAsDQogICAgInRvdGFsUGFnYXIiIDogMTUuOTEsDQogICAgInRvdGFsTGV0cmFzIiA6ICJRVUlOQ0UgOTEvMTAwIiwNCiAgICAic2FsZG9GYXZvciIgOiAwLjAsDQogICAgImNvbmRpY2lvbk9wZXJhY2lvbiIgOiAxLA0KICAgICJwYWdvcyIgOiBudWxsLA0KICAgICJudW1QYWdvRWxlY3Ryb25pY28iIDogbnVsbA0KICB9LA0KICAiZXh0ZW5zaW9uIiA6IHsNCiAgICAibm9tYkVudHJlZ2EiIDogbnVsbCwNCiAgICAiZG9jdUVudHJlZ2EiIDogbnVsbCwNCiAgICAibm9tYlJlY2liZSIgOiBudWxsLA0KICAgICJkb2N1UmVjaWJlIiA6IG51bGwsDQogICAgIm9ic2VydmFjaW9uZXMiIDogIiIsDQogICAgInBsYWNhVmVoaWN1bG8iIDogbnVsbA0KICB9LA0KICAiYXBlbmRpY2UiIDogbnVsbA0KfQ.O2QFQtWvapIC-hyVt2tqQx5mv5PoODGC_8M3gxIhRA1mzI7xW1TOTVjGuuJmzhKPmlUcnONv65AttarjBPDkF0xnvIfvVcicH-1nALh9QmJ-sPi6VMVUrRS_RFfxfQUHwrz21x-dT0KgZyT7xJr9m5UjfemAUbgVBDTx7-3McbSctxRDp_p0g6Gc_HdzHgEuDS0uFDdEf2l92lvMw8yzeSQm_fVZQ4E3SsAPeXRGuLpc4wii_Ao8QgsUorSuFXI9T8_5RdCrZ8IzDUqSAZ1KLeCxQgujlebxh8fMFZYzjxzy1rXsR7wKSoSCbsD5UGuHEtECFbDgkVO4EcUC683Wdw"
    }

    # Llamar a la función de inicio del proceso}
    
    print("🚀 Iniciando prueba automática...")
    IniciarProceso(data_ejemplo)
    print("🏁 Prueba completada")