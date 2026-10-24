# Descargador de documentos por correo

Servicio de consola para descargar documentos JSON y PDF recibidos como adjuntos
en un buzón IMAP. Esta rama contiene únicamente la funcionalidad de descarga y
archivo; no realiza operaciones contables ni inserciones en base de datos.

## Documentos admitidos

### DTE del Ministerio de Hacienda

El JSON debe incluir:

- `identificacion.codigoGeneracion`
- `identificacion.numeroControl`
- `resumen`

Los archivos se guardan utilizando `codigoGeneracion` como nombre.

### Documentos internos de viáticos

El JSON debe incluir `egreso.CORRELATIVO`. Por ejemplo, un documento con el
correlativo `MV-2026-000004` se almacena como:

```text
MV-2026-000004.json
MV-2026-000004.pdf
```

## Configuración

Crear un archivo `.env` en la raíz del proyecto:

```dotenv
IMAP_SERVER=servidor.imap.example
EMAIL_ACCOUNT=cuenta@example.com
EMAIL_PASSWORD=contraseña
DOWNLOAD_FOLDER=C:\ruta\documentos
```

Los documentos se organizan bajo `DOWNLOAD_FOLDER/año/mes`. Los adjuntos
dañados se colocan en la subcarpeta `Archivos_Dañados` y los errores se anotan
en `ignored_damaged.txt` o `incomplete_files.txt`.

## Instalación y ejecución

```bash
python -m pip install -r src/core/requirements.txt
python main.py
```

Al ejecutar `python main.py` o abrir el ejecutable se muestra un menú con ambos
modos de operación:

1. Descargar los documentos del día actual.
2. Ingresar una fecha inicial y una final. Ambas fechas se incluyen en la búsqueda.

También puede ejecutarse sin interacción, por ejemplo desde el Programador de
tareas de Windows:

```bash
DocumentosDownloader.exe --automatico
DocumentosDownloader.exe --desde 2026-10-01 --hasta 2026-10-19
```

## Pruebas

```bash
python -m unittest discover -s src/tests -p "test_*.py" -v
```

## Empaquetado para Windows

```bash
pyinstaller --onefile --name DocumentosDownloader main.py
```

El archivo `.env` no se incrusta en el ejecutable porque contiene credenciales.
Debe colocarse en la misma carpeta que `DocumentosDownloader.exe`.
