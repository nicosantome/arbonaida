from email.message import EmailMessage
from email.utils import formataddr
import ssl
import smtplib

PASS = 'hryf oovm otdl gxuj'
PORT = 465
SERVER ='smtp.gmail.com'

email_sender = 'nicosantome@gmail.com'
email_receiver = 'nicosantome@gmail.com'

# subject = 'Test'
#
# body = '''
# Testing'''

# em = EmailMessage()
# em['From'] = email_sender
# em['To'] = email_receiver
# em['Subject'] = subject
# em.set_content(body)

context = ssl.create_default_context()
#
# with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#     smtp.login(email_sender, PASS)
#     smtp.sendmail(email_sender, email_receiver, em.as_string())


def send_email(recipient_address, recipient_name, booking_date, booking_time):
    msg = EmailMessage()
    msg['Subject'] = "Reserva confirmada. Te esperamos!!!"
    msg['From'] = formataddr(('Arbonaida Bar', email_sender))
    msg['To'] = recipient_address
    msg.set_content(f'''
        Hola {recipient_name}, tu reserva esta confirmada para el {booking_date} a las {booking_time}
        te esperamos''')
    msg.add_alternative(f'''
        <html>
            <body>
                <h1>Hola {recipient_name}</h1>
                <p>Tu reserva esta confirmada para el {booking_date} a las {booking_time}</p>
                <p>Te esperamos</p>
            </body>    
        </html>''',
                        subtype='html',
                        )
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(email_sender, PASS)
        server.sendmail(email_sender, recipient_address, msg.as_string())


send_email('nicosantome@gmail.com', 'Nico', 'Sept 11', '11:00')