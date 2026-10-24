import argparse
from datetime import date, datetime, timedelta

from src.api.app import process_emails


FORMATO_FECHA = "%Y-%m-%d"


def convertir_fecha(valor: str) -> date:
    try:
        return datetime.strptime(valor, FORMATO_FECHA).date()
    except ValueError as exc:
        raise ValueError(
            f"La fecha '{valor}' no es válida. Use el formato YYYY-MM-DD."
        ) from exc


def ejecutar_rango(fecha_inicio: date, fecha_fin: date) -> None:
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")

    # IMAP usa BEFORE de forma exclusiva; se suma un día para incluir fecha_fin.
    limite_exclusivo = fecha_fin + timedelta(days=1)
    print(
        "Descargando documentos del correo desde "
        f"{fecha_inicio.isoformat()} hasta {fecha_fin.isoformat()}..."
    )
    resumen = process_emails(
        fecha_inicio.strftime(FORMATO_FECHA),
        limite_exclusivo.strftime(FORMATO_FECHA),
    )

    if resumen:
        print("\nProceso finalizado:")
        print(f"  Correos revisados: {resumen['correos_revisados']}")
        print(f"  Documentos descargados: {resumen['documentos_descargados']}")
        print(f"  Archivos dañados: {resumen['archivos_danados']}")
        print(f"  Correos ignorados: {resumen['correos_ignorados']}")


def ejecutar_automatico() -> None:
    hoy = date.today()
    ejecutar_rango(hoy, hoy)


def ejecutar_manual() -> None:
    print("\nIngrese el rango de fechas en formato YYYY-MM-DD.")
    fecha_inicio = convertir_fecha(input("Fecha inicial: ").strip())
    fecha_fin = convertir_fecha(input("Fecha final:   ").strip())
    ejecutar_rango(fecha_inicio, fecha_fin)


def mostrar_menu() -> int:
    print("\nDescargador de documentos por correo")
    print("1. Descargar documentos de hoy")
    print("2. Descargar documentos por rango de fechas")
    print("0. Salir")

    opcion = input("Seleccione una opción: ").strip()
    if opcion == "1":
        ejecutar_automatico()
    elif opcion == "2":
        ejecutar_manual()
    elif opcion == "0":
        return 0
    else:
        print("Opción no válida.")
        return 2

    input("\nPresione Enter para cerrar...")
    return 0


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Descarga documentos DTE e internos desde un buzón IMAP."
    )
    parser.add_argument(
        "--automatico",
        action="store_true",
        help="procesa los documentos recibidos durante el día actual",
    )
    parser.add_argument("--desde", help="fecha inicial inclusiva (YYYY-MM-DD)")
    parser.add_argument("--hasta", help="fecha final inclusiva (YYYY-MM-DD)")
    return parser


def main(argv=None) -> int:
    parser = crear_parser()
    args = parser.parse_args(argv)

    if args.automatico and (args.desde or args.hasta):
        parser.error("--automatico no se puede combinar con --desde o --hasta")

    if args.automatico:
        ejecutar_automatico()
        return 0

    if args.desde or args.hasta:
        if not args.desde or not args.hasta:
            parser.error("debe indicar --desde y --hasta juntos")
        try:
            ejecutar_rango(convertir_fecha(args.desde), convertir_fecha(args.hasta))
        except ValueError as exc:
            parser.error(str(exc))
        return 0

    try:
        return mostrar_menu()
    except (EOFError, KeyboardInterrupt):
        print("\nProceso cancelado.")
        return 130
    except ValueError as exc:
        print(f"\nError: {exc}")
        input("Presione Enter para cerrar...")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
