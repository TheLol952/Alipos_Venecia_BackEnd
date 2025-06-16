from datetime import date, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from src.api.app import process_emails

# def job():
#     today = date.today()
#     start = (today - timedelta(days=1)).strftime("%Y-%m-%d")
#     end   =  today          .strftime("%Y-%m-%d")
#     process_emails(start, end)

def job():
    today = date.today()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Ejecutando proceso automático: {start_date} → {end_date}")
    process_emails(start_date, end_date)


# if __name__ == "__main__":
#     sched = BlockingScheduler(timezone="America/El_Salvador")
#     # Ejecutar cada día a la 1:00 AM
#     sched.add_job(job, 'cron', hour=1, minute=0)
#     sched.start()

if __name__ == "__main__":
    # Ejecuta el proceso automáticamente con fechas actuales
    job()

# if __name__ == "__main__":
#     # Ajusta aquí las fechas para testear
#     start_date = "2025-06-14"
#     end_date   = "2025-06-15"
#     print(f"Ejecutando proceso manual: {start_date} → {end_date}")
#     process_emails(start_date, end_date)