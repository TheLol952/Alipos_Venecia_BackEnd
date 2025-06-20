from datetime import date, datetime, timedelta
#from apscheduler.schedulers.blocking import BlockingScheduler
from src.api.app import process_emails

def job():
    today = date.today()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Ejecutando proceso automático: {start_date} → {end_date}")
    process_emails(start_date, end_date)


if __name__ == "__main__":
    # Ejecuta el proceso automáticamente con fechas actuales
    job()

# def validar_fecha(fecha_str):
#     try:
#         return datetime.strptime(fecha_str, "%Y-%m-%d").date()
#     except ValueError:
#         print(f"ERROR: La fecha '{fecha_str}' no tiene el formato correcto 'YYYY-MM-DD' o no es una fecha válida.")
#         return None

# if __name__ == "__main__":
#     print("Ingrese las fechas en formato 'YYYY-MM-DD'")

#     start_input = input("Fecha Inicio: ")
#     end_input = input("Fecha Fin: ")

#     start_date = validar_fecha(start_input)
#     end_date   = validar_fecha(end_input)

#     if start_date and end_date:
#         end_date_adjusted = end_date + timedelta(days=1)
#         print(f"Ejecutando proceso manual: {start_date} → {end_date_adjusted}")
#         process_emails(start_date.strftime("%Y-%m-%d"), end_date_adjusted.strftime("%Y-%m-%d"))
#     else:
#         print("Proceso cancelado por error en las fechas ingresadas.")