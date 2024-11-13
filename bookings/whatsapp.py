# -*- coding: utf-8 -*-
import requests
import json


def send_whatsapp_message(access_token, phone_number, customer_name, reservation_date):
    url = "https://graph.facebook.com/v21.0/147172671806666/messages"

    headers = {
        'Authorization': f'Bearer {access_token}',  # Tu token de acceso
        'Content-Type': 'application/json'
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,  # Número de teléfono al que se enviará el mensaje (con código de país)
        "type": "template",
        "template": {
            "name": "recordatorio_de_reserva",  # Nombre de la plantilla previamente configurada en WhatsApp Business
            "language": {
                "code": "es_ES"  # Código de idioma
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},  # Nombre del cliente
                        {"type": "text", "text": reservation_date}  # Fecha de la reserva
                    ]
                }
            ]
        }
    }

    # Enviar la solicitud POST
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Mensaje enviado exitosamente!")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}")
        print(response.text)


# Ejemplo de uso
access_token = "EAAyKomjyK3cBO4GNEajGiPgBoMMb1ecnwNBnz3DZBrMHFsPabEXFZAUq3LprnrytRt6pKubZARVKpJ08XMnkRNC4a0Wz4gM3RNzZBi8ZAFqfn8bfZBnGQj8oMMJqd1kijA3290eM3htqtJrOLqxhI1tyAkVuiXDqZArcYd0ereLMc6Qqa0AhddpM8LEvqaYarnKmyn5xVTg2bUNyyNwiBSpgf2kCQZDZD"
phone_number = "34644246736"  # Número de teléfono del destinatario con el código de país
customer_name = "Juan Pérez"  # Nombre del cliente
reservation_date = "2024-11-20 19:00"  # Fecha y hora de la reserva

send_whatsapp_message(access_token, phone_number, customer_name, reservation_date)
