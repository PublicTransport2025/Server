import logging
import traceback

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.logistic import Timetable
from src.models.users import Log
from src.schemas.timetable import TimetableInput, TimetableModel


class TimetableService:
    @staticmethod
    def add_timetable(data: TimetableInput, db_session: Session, ip: str, user_id: str) -> TimetableModel:
        """
        Добавляет график в базу данных
        :param data: модель нового графика
        :param db_session: сессия базы данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return: модель добавленного графика
        """
        try:
            timetable = Timetable(start=data.start,
                                  lap=data.lap,
                                  route_id=data.route_id)
            db_session.add(timetable)
            log = Log(created_ip=ip,
                      level=3,
                      action='Добавил график',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
            return TimetableModel(**timetable.__dict__)
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def delete_timetable(id: int, db_session: Session, ip: str, user_id: str) -> None:
        """
        Удаляет график из расписания.
        :param id: айди удаляемого графика
        :param db_session: сессия баз данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return:
        """
        try:
            timetable = db_session.get(Timetable, id)
            db_session.delete(timetable)
            log = Log(created_ip=ip,
                      level=3,
                      action='Удалил график',
                      information=str(id),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
