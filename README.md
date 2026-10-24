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

La ejecución normal descarga los documentos recibidos durante el día actual.

## Pruebas

```bash
python -m unittest discover -s src/tests -p "test_*.py" -v
```

## Empaquetado para Windows

```bash
pyinstaller --onefile --add-data ".env;." --name DocumentosDownloader main.py
```
