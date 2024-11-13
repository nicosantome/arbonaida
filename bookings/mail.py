from email.message import EmailMessage
from email.utils import formataddr
import ssl
import smtplib

PASS = 'hryf oovm otdl gxuj'
PORT = 465
SERVER = 'smtp.gmail.com'

email_sender = 'nicosantome@gmail.com'
email_receiver = 'nicosantome@gmail.com'

context = ssl.create_default_context()


def send_email(recipient_address, recipient_name, booking_date, booking_time):
    msg = EmailMessage()
    msg['Subject'] = "Reserva confirmada. Te esperamos!!!"
    msg['From'] = formataddr(('Arbonaida Bar', email_sender))
    msg['To'] = recipient_address

    msg.set_content(f'''
        Hola {recipient_name}, tu reserva está confirmada para el {booking_date} a las {booking_time}.
        Te esperamos.
    ''')

    msg.add_alternative(f'''
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; background: url('https://ih1.redbubble.net/image.2875862781.4468/flat,750x,075,f-pad,750x1000,f8f8f8.jpg') no-repeat center center; background-size: cover;">
                <div style="background-color: rgba(255, 255, 255, 0.85); padding: 20px; border-radius: 10px; max-width: 600px; margin: 30px auto; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="background-color: #FFFFFF; padding: 20px; text-align: center; font-size: 24px; color: #004085; border-radius: 10px 10px 0 0;">
                                    Reserva Confirmada
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="padding: 20px; text-align: center;">
                                    <h1 style="margin: 0; font-size: 20px; color: #004085;">Hola {recipient_name},</h1>
                                    <p style="font-size: 16px; line-height: 1.5; margin: 10px 0;">
                                        Tu reserva está confirmada para el:
                                    </p>
                                    <p style="font-size: 18px; font-weight: bold; margin: 10px 0; color: #0056b3;">
                                        {booking_date} a las {booking_time}
                                    </p>
                                    <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">
                                        Te esperamos en <strong>Arbonaida Bar</strong>. Si tienes alguna consulta, no dudes en contactarnos.
                                    </p>
                                    <a href="https://arbonaidabar.com" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px; font-size: 16px;">
                                        Más Información
                                    </a>
                                </td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td style="padding: 20px; background-color: #E3F2FD; text-align: center; font-size: 14px; color: #555; border-radius: 0 0 10px 10px;">
                                    © 2024 Arbonaida Bar. Todos los derechos reservados.
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </body>
        </html>
    ''', subtype='html')

    with smtplib.SMTP_SSL(SERVER, PORT, context=context) as server:
        server.login(email_sender, PASS)
        server.sendmail(email_sender, recipient_address, msg.as_string())

