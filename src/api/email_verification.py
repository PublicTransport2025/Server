from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.core.db import db_client
from src.models.email_codes import EmailCode
from src.models.users import User
from src.utils.email_sender import send_email, generate_code

email_router = APIRouter(prefix="/email", tags=["email"])


@email_router.post("/send-code")
def send_verification_code(email: EmailStr, db: Session = db_client):
    """
    Отправка кода подтверждения на email

    :param email: адрес получателя
    :param db: сессия базы данных
    :return: сообщение об успешной отправке
    """
    user = db.query(User).filter_by(login=email).one_or_none()
    if user:
        raise HTTPException(400, detail="Такой email уже зарегестрирован")

    existing = db.query(EmailCode).filter_by(email=email).first()

    if existing and datetime.utcnow() - existing.created_at < timedelta(minutes=5):
        raise HTTPException(419, detail="Код был отправлен ранее. Запросить новый можно через 5 минут")

    code = generate_code()
    subject = "Подтверждение почты"
    body = f"Ваш код подтверждения: {code}"

    send_email(email, subject, body)

    if existing:
        existing.code = code
        existing.created_at = datetime.utcnow()
    else:
        new_code = EmailCode(email=email, code=code)
        db.add(new_code)

    db.commit()
    return {"message": "Код подтверждения отправлен на почту"}


@email_router.post("/resend-code")
def send_verification_code(email: EmailStr, db: Session = db_client):
    """
    Отправка кода восстановления на email

    :param email: адрес получателя
    :param db: сессия базы данных
    :return: сообщение об успешной отправке
    """
    user = db.query(User).filter_by(login=email).one_or_none()
    if not user:
        raise HTTPException(400, detail="Такой email не был зарегестрирован")

    existing = db.query(EmailCode).filter_by(email=email).first()

    if existing and datetime.utcnow() - existing.created_at < timedelta(minutes=5):
        raise HTTPException(419, detail="Код был отправлен ранее. Запросить новый можно через 5 минут")

    code = generate_code()
    subject = "Подтверждение почты"
    body = f"Ваш код подтверждения: {code}"

    send_email(email, subject, body)

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
