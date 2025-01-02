# -*- coding: utf-8 -*-
from bookings import db
from restaurant_config import MOVILES_PERSONAL
import requests
from .models import Booking
from sqlalchemy import func
from babel.dates import format_date
import json


def send_whatsapp_message(template_object):
    url = "https://graph.facebook.com/v21.0/147172671806666/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',  # Tu token de acceso
        'Content-Type': 'application/json'
    }

    # Preparar datos comunes
    template_name = template_object.get("template_name")  # Nombre del template
    parameters = template_object.get("parameters")  # Lista de parámetros dinámicos

    # Verificar si es a un único destinatario o múltiples
    recipients = template_object.get("to_list") or [template_object.get("to")]

    for recipient in recipients:
        if template_name == "nueva_reserva":
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,  # Destinatario
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "es_ES"  # Cambiar al idioma adecuado
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [{"type": "text", "text": param} for param in parameters]
                        }
                    ]
                }
            }
        elif template_name == "recordatorio_cliente":
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,  # Destinatario
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "es_ES"  # Cambiar al idioma adecuado
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [{"type": "text", "text": param} for param in parameters]
                        }
                    ]
                }
            }

        # Enviar mensaje
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"Mensaje enviado exitosamente a {recipient}!")
        else:
            print(f"Error al enviar el mensaje a {recipient}: {response.status_code}")
            print(response.text)



# Ejemplo de uso
access_token = "EAAyKomjyK3cBOwgVbxlb8351zIUlFoPgU1ynqVp6pbuzgPtH6Nmd941VjQBCTHXY1ZC92buZAQiNgivZCfhqKB6KKeOUT9DHITXczdyIUzZBmKlOZA4ixJCqfmaEdSdXMgZBBoMoNKG6lbGpmTMfH2FRXPCXpel1R0ro0PMktpB1W335RqxaktcG4YrfqOZBHine3nkc7j1Xdz6C0LLSVWzDka7"


def generate_booking_string(booking_data, name):
    return f"{booking_data['timeslot'].strftime('%H:%M')} // {booking_data['num_people']}p // {booking_data['location']} // {name}"


def create_new_booking_template(booking_data, name):
    booking_string = generate_booking_string(booking_data, name)
    booking_count = db.session.query(func.count(Booking.id)).filter(Booking.date == booking_data['date']).scalar()
    nueva_reserva = {
        "template_name": "nueva_reserva",
        "to_list": list(MOVILES_PERSONAL.values()),  # Números del personal
        "parameters": [format_date(booking_data['date'], format="EEEE d MMM", locale="es_ES").capitalize(), booking_string, booking_count]  # Detalles de la nueva reserva y resumen del día
    }
    return nueva_reserva


def create_recordatorio_cliente_template(booking_id):
    # Obtener los datos del cliente relacionados con la reserva
    booking = db.session.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise ValueError(f"No se encontró una reserva con el ID {booking_id}")

    customer = booking.customer  # Relación entre Booking y Customer

    if not customer:
        raise ValueError(f"No se encontró un cliente asociado a la reserva con ID {booking_id}")

    # Crear el objeto de recordatorio
    recordatorio_cliente = {
        "template_name": "recordatorio_cliente",
        "to": customer.phone,  # Número de teléfono del cliente
        "parameters": [
            customer.name,  # Nombre del cliente
            booking.start_time.strftime('%H:%M'),  # Hora de la reserva
        ]
    }

    return recordatorio_cliente
