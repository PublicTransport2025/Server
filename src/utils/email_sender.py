import os
from dotenv import load_dotenv
import random
import smtplib
from email.message import EmailMessage
import string

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_email(to_email: str, subject: str, body: str):
    """
    Отправка письма на указанный email

    :param to_email: адрес получателя
    :param subject: тема письма
    :param body: текст письма
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)


def generate_code(length: int = 6) -> str:
    """
    Генерация случайного числового кода

    :param length: длина кода (по умолчанию 6)
    :return: строка с кодом
    """
    return ''.join(random.choices(string.digits, k=length))