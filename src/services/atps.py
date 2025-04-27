import logging
import traceback
from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.logistic import Atp, Route
from src.models.users import Log
from src.schemas.atp import AtpInput, AtpModel


class AtpService:

    @staticmethod
    def show_atps(db_session: Session) -> list[Type[Atp]]:
        """
        Выбирает модели всех АТП из базы данных
        :param db_session: сессия базы данных
        :return: список моделей АТП
        """
        try:
            atps = db_session.query(Atp).order_by(Atp.id).all()
            return atps
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def add_atp(data: AtpInput, db_session: Session, ip: str, user_id: str) -> AtpModel:
        """
        Вставляет модель АТП в базу данных
        :param data: модель нового АТП
        :param db_session: сессия базы данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return: модель вставленного АТП
        """
        try:
            atp = Atp(title=data.title,
                      about=data.about,
                      numbers=data.numbers,
                      phone=data.phone,
                      report=data.report)
            db_session.add(atp)
            log = Log(created_ip=ip,
                      level=5,
                      action='Добавил АТП',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
            return AtpModel(**atp.__dict__)
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def update_atp(data: AtpModel, db_session: Session, ip: str, user_id: str) -> None:
        """
        Обновляет модель АТП в базе данных
        :param data: модель АТП с новыми данными
        :param db_session: сессия базы данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return:
        """
        try:
            atp = db_session.query(Atp).filter_by(id=data.id).first()
            atp.title = data.title
            atp.about = data.about
            atp.numbers = data.numbers
            atp.phone = data.phone
            atp.report = data.report
            log = Log(created_ip=ip,
                      level=5,
                      action='Обновил АТП',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def delete_atp(id: int, db_session: Session, ip: str, user_id: str) -> None:
        """
        Удаляет модель АТП из базы данных.
        При этом его маршруты становятся неактивынми, но не удаляются
        :param id: айди удаляемого АТП
        :param db_session: сессия баз данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return:
        """
        try:
            atp = db_session.query(Atp).filter_by(id=id).one()
            routes = db_session.query(Route).filter_by(atp_id=id).all()
            for route in routes:
                route.atp_id = None
                route.stage = 0

            db_session.commit()
            db_session.delete(atp)
            log = Log(created_ip=ip,
                      level=5,
                      action='Удалил АТП',
                      information=str(id),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
