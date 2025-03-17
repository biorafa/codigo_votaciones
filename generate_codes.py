import pandas as pd
import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración del servidor de correo
SMTP_SERVER = ""
SMTP_PORT = 587
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""

# Archivos CSV
INPUT_CSV = "correos.csv"  # Lista de correos
PRINCIPIOS_CSV = "principios_activos.csv"  # Lista de principios activos
OUTPUT_CODES_CSV = "codigos_generados.csv"  # Códigos generados

# Cargar lista de principios activos desde un archivo CSV
df_principios = pd.read_csv(PRINCIPIOS_CSV)
principios_activos = df_principios["principio_activo"].drop_duplicates().tolist()

# Leer y procesar correos
df = pd.read_csv(INPUT_CSV)
emails = df["email"].drop_duplicates().tolist()

# Generar códigos únicos
codes = {}
used_codes = set()  # Para evitar duplicados

for email in emails:
    while True:
        principio = random.choice(principios_activos)  # Elegir un principio activo al azar
        numero = random.randint(1000, 9999)  # Generar número de 4 dígitos
        codigo = f"{principio}{numero}"  # Formato del código

        if codigo not in used_codes:  # Asegurar que sea único
            used_codes.add(codigo)
            codes[email] = codigo
            break

# Guardar códigos sin relación con los correos
df_codes = pd.DataFrame({"codigo": list(codes.values())})
df_codes.to_csv(OUTPUT_CODES_CSV, index=False)

# Función para enviar correos y borrar el registro de enviados
def send_email(recipient, code):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient
    msg["Subject"] = "Tu código de votación secreto"

    body = f"""
    Estimado/a usuario,

    Aquí tienes tu código único para la votación:
    
    **{code}**

    Este código es secreto y no puede ser recuperado. Úsalo con responsabilidad.

    Saludos,
    El equipo de votación
    """
    
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, recipient, msg.as_string())
        server.quit()
        print(f"Correo enviado a {recipient}")

        # Eliminar el correo enviado de la carpeta "Enviados" 
        delete_sent_email()

    except Exception as e:
        print(f"Error enviando correo a {recipient}: {e}")

# Función para eliminar correos enviados (requiere IMAP)
def delete_sent_email():
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_SENDER, EMAIL_PASSWORD)
        mail.select('"[Gmail]/Sent Mail"')  # Carpeta de enviados en Gmail
        result, data = mail.search(None, "ALL")

        if result == "OK":
            for num in data[0].split():
                mail.store(num, "+FLAGS", "\\Deleted")
            mail.expunge()

        mail.logout()
        print("Correos enviados eliminados.")
    except Exception as e:
        print("Error eliminando correos enviados:", e)

# Enviar correos
for email in emails:
    send_email(email, codes[email])

print("Todos los correos han sido enviados y eliminados de enviados, se puede proceder a la votación.")
