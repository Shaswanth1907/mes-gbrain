import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USERNAME = "shaswanthbaskaran@gmail.com"
PASSWORD = "jpdklmgttkkolfou"

server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(USERNAME, PASSWORD)
print("LOGIN SUCCESS")
server.quit()