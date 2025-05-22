from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.core.db import db_client
from src.models.email_codes import EmailCode
from src.utils.email_sender import send_email, generate_code

email_router = APIRouter(prefix="/email", tags=["email"])


@email_router.post("/send-code")
def send_verification_code(email: str, db: Session = db_client):
    """
    Отправка кода подтверждения на email

    :param email: адрес получателя
    :param db: сессия базы данных
    :return: сообщение об успешной отправке
    """
    code = generate_code()
    subject = "Подтверждение почты"
    body = f"Ваш код подтверждения: {code}"

    send_email(email, subject, body)

    existing = db.query(EmailCode).filter_by(email=email).first()
    if existing:
        existing.code = code
        existing.created_at = datetime.utcnow()
    else:
        new_code = EmailCode(email=email, code=code)
        db.add(new_code)

    db.commit()
    return {"message": "Код подтверждения отправлен на почту"}


@email_router.post("/verify")
def verify_email_code(email: str, code: str, db: Session = db_client):
    """
    Проверка кода подтверждения email

    :param email: адрес получателя
    :param code: проверяемый код
    :param db: сессия базы данных
    :return: сообщение об успешной проверке или ошибка
    """
    record = db.query(EmailCode).filter_by(email=email).first()
    if not record:
        raise HTTPException(404, detail="Код не найден")

    if record.code != code:
        raise HTTPException(400, detail="Неверный код")

    if datetime.utcnow() - record.created_at > timedelta(minutes=10):
        raise HTTPException(400, detail="Код истёк")

    return {"message": "Почта подтверждена"}