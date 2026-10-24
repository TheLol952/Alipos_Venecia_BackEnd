import re
from typing import Any


TIPO_DTE = "DTE"
TIPO_DOCUMENTO_INTERNO = "DOCUMENTO_INTERNO"


def identificar_documento(data: Any) -> tuple[str, str]:
    """Valida un JSON admitido y retorna su tipo e identificador único."""
    if not isinstance(data, dict):
        raise ValueError("La raíz del JSON debe ser un objeto")

    identificacion = data.get("identificacion")
    if isinstance(identificacion, dict):
        codigo_generacion = identificacion.get("codigoGeneracion")
        numero_control = identificacion.get("numeroControl")
        if codigo_generacion and numero_control and "resumen" in data:
            return TIPO_DTE, str(codigo_generacion)

    egreso = data.get("egreso")
    if isinstance(egreso, dict):
        correlativo = egreso.get("CORRELATIVO")
        if correlativo:
            return TIPO_DOCUMENTO_INTERNO, str(correlativo)

    raise ValueError(
        "El JSON no tiene una estructura DTE válida ni un "
        "documento interno con egreso.CORRELATIVO"
    )


def nombre_archivo_seguro(identificador: str) -> str:
    """Convierte el identificador del documento en un nombre de archivo seguro."""
    nombre = re.sub(r"[^\w.-]+", "_", identificador.strip(), flags=re.UNICODE)
    nombre = nombre.strip("._")
    if not nombre:
        raise ValueError("El identificador no permite construir un nombre de archivo")
    return nombre[:180]
