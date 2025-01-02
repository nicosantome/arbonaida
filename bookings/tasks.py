from celery import Celery
import logging


celery = Celery(backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')


def make_celery(app):
    celery.conf.broker_connection_retry_on_startup = True
    celery.autodiscover_tasks()  # Esto busca tareas automáticamente
    return celery


@celery.task
def enviar_recordatorio(booking_id):
    if not booking_id:
        print("Error: No se proporciono un booking_id valido.")
        return  # O manejar el error de otra manera

    from bookings.whatsapp import send_whatsapp_message, create_recordatorio_cliente_template
    mensaje = create_recordatorio_cliente_template(booking_id)
    send_whatsapp_message(mensaje)


@celery.task
def printo():
    try:
        print("Client")
        logging.info('started')
        return "Client"
    except Exception as e:
        print(f"Task error: {e}")
