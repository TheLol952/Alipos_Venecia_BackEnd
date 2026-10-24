# DocumentosDownloader para Windows

`DocumentosDownloader.exe` es un ejecutable de consola para Windows de 64 bits.

Antes de usarlo, coloque en esta misma carpeta un archivo `.env` con las
credenciales IMAP descritas en el README principal. El `.env` no se incluye en
Git ni dentro del ejecutable.

Al abrirlo con doble clic se puede elegir entre descargar los documentos de hoy
o ingresar un rango de fechas. Para una ejecución programada:

```powershell
.\DocumentosDownloader.exe --automatico
```

SHA-256 del ejecutable:

```text
5fa9cdac59b5075b6b4c9ef85f0f6cdc5815690b020a6cd7abb61588a2df2c75
```
