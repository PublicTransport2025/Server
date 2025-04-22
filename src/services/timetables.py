import logging
import traceback

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.logistic import Timetable
from src.schemas.timetable import TimetableInput, TimetableModel


class TimetableService:
    @staticmethod
    def add_timetable(data: TimetableInput, db_session: Session) -> TimetableModel:
        """
        Добавляет график в базу данных
        :param data: модель нового графика
        :param db_session: сессия базы данных
        :return: модель добавленного графика
        """
        try:
            timetable = Timetable(start=data.start,
                                  lap=data.lap,
                                  route_id=data.route_id)
            db_session.add(timetable)
            db_session.commit()
            return TimetableModel(**timetable.__dict__)
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def delete_timetable(id: int, db_session: Session) -> None:
        """
        Удаляет график из расписания.
        :param id: айди удаляемого графика
        :param db_session: сессия баз данных
        :return:
        """
        try:
            timetable = db_session.get(Timetable, id)
            db_session.delete(timetable)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
